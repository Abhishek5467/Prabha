"""Linear MAC through the existing physical blocks, without neuron activation.

The deterministic component convention is unchanged. Noise support here is
experimental until matched native INTERCONNECT trials have been compared.
"""
from dataclasses import dataclass
import numpy as np
from ..blocks.cw_laser import CWLaser
from ..blocks.dac import DAC
from ..blocks.adc import ADC
from ..blocks.mzm import MachZehnderModulator
from ..blocks.photodetector import Photodetector
from ..blocks.capacitor import Capacitor
from ..blocks.amplifier import Amplifier


@dataclass(frozen=True)
class MACConfig:
    dac_bits: int | None = 12
    adc_bits: int | None = None
    adc_full_scale: float = 64.0
    tile_size: int = 64
    samples_per_symbol: int = 16
    sample_rate_hz: float = 16e9
    power_mw: float = 1.0
    responsivity: float = 1.0
    capacitance_f: float = 1e-12
    rin_enabled: bool = False
    rin_db_hz: float = -150.0
    linewidth_enabled: bool = False
    linewidth_hz: float = 0.0
    shot_enabled: bool = False
    dark_current_a: float = 0.0
    seed: int = 12345
    dac_rounding: str = 'nearest_even'
    mzm_extinction_ratio_db: float | None = None
    weight_extinction_ratio_db: float | None = None

    def __post_init__(self):
        if self.dac_rounding not in ('nearest_even', 'nearest_lower'):
            raise ValueError('dac_rounding must be nearest_even or nearest_lower.')
        for name in ('mzm_extinction_ratio_db', 'weight_extinction_ratio_db'):
            value = getattr(self, name)
            if value is not None and (not np.isfinite(value) or value < 0):
                raise ValueError(f'{name} must be None or finite and nonnegative.')
        for name in ('dac_bits', 'adc_bits'):
            v = getattr(self, name)
            if v is not None and (isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 24):
                raise ValueError(f'{name} must be None or an integer in [1,24].')
        for name in ('tile_size', 'samples_per_symbol'):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise ValueError(f'{name} must be a positive integer.')
        for name in ('sample_rate_hz', 'power_mw', 'responsivity', 'capacitance_f', 'adc_full_scale'):
            v = getattr(self, name)
            if not np.isfinite(v) or v <= 0:
                raise ValueError(f'{name} must be finite and positive.')
        for name in ('dark_current_a', 'linewidth_hz'):
            if not np.isfinite(getattr(self, name)) or getattr(self, name) < 0:
                raise ValueError(f'{name} must be finite and nonnegative.')
        if not np.isfinite(self.rin_db_hz):
            raise ValueError('rin_db_hz must be finite.')
        if isinstance(self.seed, bool) or not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError('seed must be a nonnegative integer.')


class PhysicalMAC:
    """A stateful noise stream and reusable linear physical MAC.

    Signed inputs use two nonnegative input passes; signed weights use the
    existing complementary optical branches. Longer vectors use reset tiles
    with digital summation. Automatic normalization is software preprocessing,
    not a claim of a free or fixed-gain hardware operation. Supply fixed scales
    explicitly when evaluating a fixed-range implementation.
    """
    def __init__(self, config=None):
        self.config = config or MACConfig()
        self.rng = np.random.default_rng(self.config.seed)
        self.calls = 0
        self.device_passes = 0
        self.waveform_samples = 0
        self.last_trace = []

    def _positive_pass(self, x, w, record):
        c = self.config
        sps = c.samples_per_symbol
        n = len(x) * sps
        drive = 2 / np.pi * (np.arccos(np.sqrt(x)) - np.pi / 4)
        if c.dac_bits is not None:
            _, drive = DAC(c.dac_bits, -.5, .5, rounding=c.dac_rounding).quantize(drive)
        drive_wave = np.repeat(drive, sps)
        seeds = [int(v) for v in self.rng.integers(1, 2**32 - 1, 3)]
        p0 = c.power_mw * 1e-3
        if c.rin_enabled or c.linewidth_enabled:
            source = CWLaser(P0_mW=c.power_mw, fs=c.sample_rate_hz,
                             duration=np.nextafter(n / c.sample_rate_hz, np.inf),
                             rin_db_hz=c.rin_db_hz, linewidth_hz=c.linewidth_hz,
                             seed=seeds[0])
            _, field = source.generate(c.rin_enabled, c.linewidth_enabled)
            if len(field) != n:
                raise ValueError('Laser sample count does not match the symbol grid.')
            power = source.power(field)
        else:
            power = np.full(n, p0)
        modulated = MachZehnderModulator(V_pi=1., phi_bias=np.pi / 2,
            extinction_ratio_dB=c.mzm_extinction_ratio_db).modulate(power, drive_wave)
        wp = np.repeat((1 + w) / 2, sps)
        wm = np.repeat((1 - w) / 2, sps)
        if c.weight_extinction_ratio_db is not None:
            floor = 10**(-c.weight_extinction_ratio_db/10)
            wp, wm = floor+(1-floor)*wp, floor+(1-floor)*wm
        p_plus, p_minus = .5 * modulated * wp, .5 * modulated * wm
        currents = []
        for branch, seed in zip((p_plus, p_minus), seeds[1:]):
            detector = Photodetector(c.responsivity, c.dark_current_a, seed)
            currents.append(detector.detect_white_shot(
                branch, c.sample_rate_hz, include_dark_current=True,
                include_shot_noise=c.shot_enabled))
        current = currents[0] - currents[1]
        capacitor = Capacitor(capacitance_F=c.capacitance_f)
        voltage = capacitor.integrate_currents(current, 1 / c.sample_rate_hz, reset=True)
        symbol_time = sps / c.sample_rate_hz
        gain = 2 * c.capacitance_f / (p0 * c.responsivity * symbol_time)
        value = float(Amplifier(gain=gain).amplify(voltage))
        if c.adc_bits is not None:
            adc = ADC(c.adc_bits, -c.adc_full_scale, c.adc_full_scale)
            value = float(adc.code_to_voltage(adc.convert(value)))
        self.device_passes += 1
        self.waveform_samples += n
        if record:
            self.last_trace.append({
                'input_normalized': x.copy(), 'weight_normalized': w.copy(),
                'interval_end_s': (np.arange(n) + 1) / c.sample_rate_hz,
                'drive_voltage_v': drive_wave, 'p_plus_w': p_plus, 'p_minus_w': p_minus,
                'i_plus_a': currents[0], 'i_minus_a': currents[1], 'i_delta_a': current,
                'v_cap_derived_v': np.cumsum(current) / c.sample_rate_hz / c.capacitance_f,
                'pre_readout_v': float(gain * voltage), 'readout': value})
        return value

    @staticmethod
    def _scale(a, supplied, name):
        scale = (float(np.max(np.abs(a))) or 1.0) if supplied is None else float(supplied)
        if not np.isfinite(scale) or scale <= 0 or np.any(np.abs(a) > scale):
            raise ValueError(f'{name} must be finite, positive and cover the vector range.')
        return scale

    def dot(self, x, w, *, input_scale=None, weight_scale=None, record=False):
        x, w = np.asarray(x, dtype=float), np.asarray(w, dtype=float)
        if x.ndim != 1 or w.shape != x.shape or not x.size:
            raise ValueError('MAC requires equal, nonempty one-dimensional vectors.')
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(w)):
            raise ValueError('MAC inputs and weights must be finite.')
        sx = self._scale(x, input_scale, 'input_scale')
        sw = self._scale(w, weight_scale, 'weight_scale')
        xn, wn = x / sx, w / sw
        self.last_trace = []
        self.calls += 1
        total = 0.0
        size = self.config.tile_size
        for start in range(0, len(x), size):
            xx, ww = xn[start:start + size], wn[start:start + size]
            positive = self._positive_pass(np.maximum(xx, 0), ww, record)
            if record:
                self.last_trace[-1].update(sign=1, normalization_factor=sx * sw)
            total += positive
            if np.any(xx < 0):
                total -= self._positive_pass(np.maximum(-xx, 0), ww, record)
                if record:
                    self.last_trace[-1].update(sign=-1, normalization_factor=sx * sw)
        return float(total * sx * sw)


def mac(x, w, config=None, **kwargs):
    """Convenience call; reuse PhysicalMAC for a continuing noise stream."""
    return PhysicalMAC(config).dot(x, w, **kwargs)
