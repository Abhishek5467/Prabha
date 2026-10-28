"""Linear MAC through the existing physical blocks, without neuron activation.

The deterministic component convention is unchanged. Stationary RIN validation
is documented in validation/release_evidence; noisy networks and dynamics need
separate evidence. Symbol execution integrates noiseless constant symbols.
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


class DigitalMAC:
    """Unquantized reference backend with the same vector/matrix contract."""
    supports_matrix = True

    def dot(self, x, w):
        return float(np.dot(x, w))

    def matrix(self, x, w):
        return np.asarray(x, dtype=float) @ np.asarray(w, dtype=float).T


class PhysicalMAC:
    """A stateful noise stream and reusable linear physical MAC.

    Signed inputs use two nonnegative input passes; signed weights use the
    existing complementary optical branches. Longer vectors use reset tiles
    with digital summation. Automatic normalization is software preprocessing,
    not a claim of a free or fixed-gain hardware operation. Supply fixed scales
    explicitly when evaluating a fixed-range implementation.
    """
    def __init__(self, config=None, *, execution='waveform'):
        self.config = config or MACConfig()
        if execution not in ('auto', 'symbol', 'waveform'):
            raise ValueError('execution must be auto, symbol or waveform.')
        stochastic = any((self.config.rin_enabled, self.config.linewidth_enabled, self.config.shot_enabled))
        if execution == 'symbol' and stochastic:
            raise ValueError('Symbol execution requires noise and linewidth to be disabled.')
        self.execution_mode = 'symbol' if execution == 'symbol' or (execution == 'auto' and not stochastic) else 'waveform'
        self.supports_matrix = self.execution_mode == 'symbol'
        self.rng = np.random.default_rng(self.config.seed)
        self.calls = 0
        self.device_passes = 0
        # Kept as the equivalent sample-grid count for existing exported runs.
        self.waveform_samples = 0
        self.materialized_waveform_samples = 0
        self.last_trace = []
        c = self.config
        self._dac = None if c.dac_bits is None else DAC(c.dac_bits, -.5, .5, rounding=c.dac_rounding)
        self._adc = None if c.adc_bits is None else ADC(c.adc_bits, -c.adc_full_scale, c.adc_full_scale)
        self._mzm = MachZehnderModulator(V_pi=1., phi_bias=np.pi / 2, extinction_ratio_dB=c.mzm_extinction_ratio_db)

    def _positive_pass(self, x, w, record):
        c = self.config
        sps = c.samples_per_symbol
        n = len(x) * sps
        drive = 2 / np.pi * (np.arccos(np.sqrt(x)) - np.pi / 4)
        if self._dac is not None:
            _, drive = self._dac.quantize(drive)
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
        modulated = self._mzm.modulate(power, drive_wave)
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
        if self._adc is not None:
            value = float(self._adc.code_to_voltage(self._adc.convert(value)))
        self.device_passes += 1
        self.waveform_samples += n
        self.materialized_waveform_samples += n
        if record:
            self.last_trace.append({
                'input_normalized': x.copy(), 'weight_normalized': w.copy(),
                'interval_end_s': (np.arange(n) + 1) / c.sample_rate_hz,
                'drive_voltage_v': drive_wave, 'p_plus_w': p_plus, 'p_minus_w': p_minus,
                'i_plus_a': currents[0], 'i_minus_a': currents[1], 'i_delta_a': current,
                'v_cap_derived_v': np.cumsum(current) / c.sample_rate_hz / c.capacitance_f,
                'pre_readout_v': float(gain * voltage), 'readout': value})
        return value

    def _symbol_power(self, x):
        drive = 2 / np.pi * (np.arccos(np.sqrt(x)) - np.pi / 4)
        if self._dac is not None:
            _, drive = self._dac.quantize(drive)
        return self._mzm.modulate(self.config.power_mw * 1e-3, drive)

    def _symbol_readout(self, power, weights):
        """Integrate constant symbols using the configured component equations.

        No noise, transient response, receiver bandwidth or capacitor leakage is
        approximated here: those effects are absent from this configured MAC.
        ADC half-code/range boundaries use the original sample reduction order.
        """
        c = self.config
        wp, wm = (1 + weights) / 2, (1 - weights) / 2
        if c.weight_extinction_ratio_db is not None:
            floor = 10 ** (-c.weight_extinction_ratio_db / 10)
            wp, wm = floor + (1 - floor) * wp, floor + (1 - floor) * wm
        plus = c.responsivity * (.5 * power[:, None, :] * wp[None, :, :]) + c.dark_current_a
        minus = c.responsivity * (.5 * power[:, None, :] * wm[None, :, :]) + c.dark_current_a
        current = plus - minus
        p0 = c.power_mw * 1e-3
        gain = 2 * c.capacitance_f / (p0 * c.responsivity * (c.samples_per_symbol / c.sample_rate_hz))
        values = (current.sum(axis=-1) * c.samples_per_symbol) * (1 / c.sample_rate_hz) / c.capacitance_f * gain
        if self._adc is not None:
            normalized = (values - self._adc.v_min) / (self._adc.v_max - self._adc.v_min) * (self._adc.n_codes - 1)
            epsilon = 64 * np.finfo(float).eps
            boundary = np.abs(normalized - (np.floor(normalized) + .5)) <= epsilon * np.maximum(1., np.abs(normalized))
            boundary |= np.minimum(np.abs(values - self._adc.v_min), np.abs(values - self._adc.v_max)) <= epsilon * max(1., c.adc_full_scale)
            for row, column in np.argwhere(boundary):
                samples = np.repeat(current[row, column], c.samples_per_symbol)
                values[row, column] = samples.sum() * (1 / c.sample_rate_hz) / c.capacitance_f * gain
                self.materialized_waveform_samples += len(samples)
            values = self._adc.code_to_voltage(self._adc.convert(values))
        self.device_passes += values.size
        self.waveform_samples += values.size * power.shape[1] * c.samples_per_symbol
        return values

    @staticmethod
    def _scales(values, supplied, name):
        if supplied is None:
            scales = np.max(np.abs(values), axis=1)
            return np.where(scales == 0, 1., scales)
        scale = float(supplied)
        if not np.isfinite(scale) or scale <= 0 or np.any(np.abs(values) > scale):
            raise ValueError(f'{name} must be finite, positive and cover the vector range.')
        return np.full(len(values), scale)

    def matrix(self, x, w, *, input_scale=None, weight_scale=None):
        """All row/filter dot products, with bounded temporary allocations.

        Symbol execution retains DAC/MZM transfer, signed optical branches,
        detector current, capacitor/gain calibration, tile reset and per-pass
        ADC conversion. The waveform path preserves scalar execution order.
        """
        x, w = np.asarray(x, dtype=float), np.asarray(w, dtype=float)
        if x.ndim != 2 or w.ndim != 2 or not all(x.shape) or not all(w.shape) or x.shape[1] != w.shape[1]:
            raise ValueError('MAC matrix expects nonempty [rows,features] and [outputs,features].')
        if not np.isfinite(x).all() or not np.isfinite(w).all():
            raise ValueError('MAC inputs and weights must be finite.')
        if not self.supports_matrix:
            return np.array([[self.dot(row, filt, input_scale=input_scale, weight_scale=weight_scale) for filt in w] for row in x])
        sx = self._scales(x, input_scale, 'input_scale')
        sw = self._scales(w, weight_scale, 'weight_scale')
        xn, wn = x / sx[:, None], w / sw[:, None]
        output = np.zeros((len(x), len(w)))
        self.last_trace = []
        self.calls += output.size
        for first in range(0, len(x), 256):
            last = min(first + 256, len(x))
            for start in range(0, x.shape[1], self.config.tile_size):
                stop = start + self.config.tile_size
                xx = xn[first:last, start:stop]
                positive = self._symbol_power(np.maximum(xx, 0))
                negative_rows = np.flatnonzero(np.any(xx < 0, axis=1))
                negative = self._symbol_power(np.maximum(-xx[negative_rows], 0)) if len(negative_rows) else None
                for left in range(0, len(w), 64):
                    right = min(left + 64, len(w))
                    weights = wn[left:right, start:stop]
                    output[first:last, left:right] += self._symbol_readout(positive, weights)
                    if negative is not None:
                        output[first + negative_rows, left:right] -= self._symbol_readout(negative, weights)
        return output * sx[:, None] * sw[None, :]

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
        if self.supports_matrix and not record:
            return float(self.matrix(x[None], w[None], input_scale=input_scale, weight_scale=weight_scale)[0, 0])
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


def mac(x, w, config=None, *, execution='waveform', **kwargs):
    """Convenience call; reuse PhysicalMAC for a continuing noise stream."""
    return PhysicalMAC(config, execution=execution).dot(x, w, **kwargs)
