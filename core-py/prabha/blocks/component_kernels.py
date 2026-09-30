"""Designer adapters for the component classes used by the experiments.

model_* definitions use these adapters. Historical PEMAN implementations remain
available under their original IDs so saved designs keep their original meaning.
Signals are sampled in time; optical adapters preserve the input envelope phase
and implement the established POWER transfer, not an interferometer field model.
"""
import numpy as np
from ..engine import Kernel as BaseKernel, kernel
from ..signal import Signal, Channel
from .cw_laser import CWLaser
from .mzm import MachZehnderModulator
from .photodetector import Photodetector
from .tia import TIA
from .capacitor import Capacitor
from .amplifier import Amplifier
from .activation import Activation
from .adc import ADC
from .dac import DAC

MODEL_REVISION = 'components-1'


def integer(value, name, low=1, high=16):
    if isinstance(value, bool) or not np.isfinite(value) or int(value) != value or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low}, {high}].')
    return int(value)


class Kernel(BaseKernel):
    def __init__(self, params, ctx, instance_id=''):
        if 'seed' in params:
            integer(params['seed'], 'Block seed', 0, 2**32-1)
        super().__init__(params, ctx, instance_id)


def bounded(data, lo, hi, name):
    a = np.asarray(data, dtype=float)
    if not np.all(np.isfinite(a)) or np.any(a < lo) or np.any(a > hi):
        raise ValueError(f'{name} must be finite and in [{lo}, {hi}].')
    return a


def inverse_mzm(x, vpi, bias):
    return (2 * vpi / np.pi) * (np.arccos(np.sqrt(bounded(x, 0, 1, 'Normalized input'))) - bias / 2)


def ranged(data, p):
    if p['v_max'] <= p['v_min']:
        raise ValueError('v_max must exceed v_min.')
    return np.clip(data, p['v_min'], p['v_max']) if p['clip'] else data


@kernel('ComponentSource')
class Source(Kernel):
    def process(self, inputs):
        p = self.p
        sps = integer(p['sps'], 'sps', 1, 256)
        parts = p['values'].split(',')
        if not 1 <= len(parts) <= 256 or any(not v.strip() for v in parts):
            raise ValueError('Supply 1 to 256 comma-separated source values.')
        values = bounded([float(v) for v in parts], -1e6, 1e6, 'Source values')
        if p['kind'] == 'digital' and (np.any(values < 0) or np.any(values != np.rint(values))):
            raise ValueError('Digital source values must be nonnegative integers.')
        fs = p['rate'] * 1e9 * sps
        n = int(fs * self.ctx.duration)
        if not 1 <= n <= 20000:
            raise ValueError('Source must produce 1 to 20,000 samples.')
        data = values[np.minimum(np.arange(n) // sps, len(values) - 1)]
        return {'out': Signal(p['kind'], fs, data)}


@kernel('ComponentLaser')
class Laser(Kernel):
    def process(self, inputs):
        p = self.p
        laser = CWLaser(P0_mW=p['power_mW'], wavelength_nm=p['wavelength_nm'],
            fs=p['fs'], duration=self.ctx.duration, phase0=p['phase_rad'],
            rin_db_hz=p['rin_db_hz'], linewidth_hz=p['linewidth_hz'], seed=self.seed)
        _, e = laser.generate(include_rin=self.ctx.noise and p['rin_enabled'],
                              include_linewidth=self.ctx.noise and p['linewidth_enabled'])
        return {'out': Signal('optical', p['fs'], e, channels=[Channel(laser.f0)])}


@kernel('ComponentEncoder')
class Encoder(Kernel):
    def process(self, inputs):
        s = inputs['x']
        return {'out': Signal('voltage', s.fs, inverse_mzm(s.data, self.p['v_pi'], self.p['bias_rad']))}


@kernel('ComponentDACQuantizer')
class DACQuantizer(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        dac = DAC(integer(p['bits'], 'bits'), p['v_min'], p['v_max'])
        code, voltage = dac.quantize(ranged(s.data, p))
        return {'code': Signal('digital', s.fs, code), 'out': Signal('voltage', s.fs, voltage)}


@kernel('ComponentDAC')
class DigitalDAC(Kernel):
    def process(self, inputs):
        s, p = inputs['code'], self.p
        bits = integer(p['bits'], 'bits')
        values = bounded(s.data, 0, 2**bits - 1, 'DAC code')
        if np.any(values != np.rint(values)):
            raise ValueError('DAC codes must be integers.')
        return {'out': Signal('voltage', s.fs, DAC(bits, p['v_min'], p['v_max']).code_to_voltage(values))}


@kernel('ComponentMZM')
class MZM(Kernel):
    def process(self, inputs):
        light, p = inputs['light'], self.p
        tr = MachZehnderModulator(p['v_pi'], p['bias_rad'], p['loss_dB']).transfer(inputs['drive'].data)
        return {'out': light.like(light.single_channel() * np.sqrt(tr))}


@kernel('ComponentSplitter')
class Splitter(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        e = s.single_channel() * np.sqrt(10**(-p['loss_dB'] / 10))
        return {'upper': s.like(e * np.sqrt(p['ratio'])), 'lower': s.like(e * np.sqrt(1 - p['ratio']))}


@kernel('ComponentTransmission')
class Transmission(Kernel):
    def process(self, inputs):
        light = inputs['light']
        t = bounded(inputs['transmission'].data, 0, 1, 'Power transmission')
        return {'out': light.like(light.single_channel() * np.sqrt(t))}


@kernel('ComponentWeights')
class Weights(Kernel):
    def process(self, inputs):
        s = inputs['in']
        w = bounded(s.data, -1, 1, 'Weights')
        return {'upper': Signal('voltage', s.fs, (1+w)/2), 'lower': Signal('voltage', s.fs, (1-w)/2)}


def detect(power, fs, p, seed, noise):
    pd = Photodetector(p['responsivity'], p['dark_current_A'], seed)
    return pd.detect_white_shot(power, fs, include_dark_current=p['dark_enabled'],
                               include_shot_noise=noise and p['shot_enabled'])


@kernel('ComponentPD')
class Detector(Kernel):
    def process(self, inputs):
        s = inputs['in']
        out = detect(np.abs(s.single_channel())**2, s.fs, self.p, self.seed, self.ctx.noise)
        return {'out': Signal('current', s.fs, out)}


@kernel('ComponentBalance')
class Balance(Kernel):
    def process(self, inputs):
        a, b = inputs['upper'], inputs['lower']
        return {'out': Signal('current', a.fs, a.data - b.data)}


@kernel('ComponentTIA')
class Transimpedance(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        model = TIA(p['resistance_ohm'], p['bandwidth_Hz'] if p['bandwidth_enabled'] else None,
                    p['noise_A_sqrtHz'], self.seed)
        return {'out': Signal('voltage', s.fs, model.amplify(s.data, s.fs, self.ctx.noise and p['noise_enabled']))}


@kernel('ComponentCapacitor')
class Integrator(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        cap = Capacitor(p['capacitance_pF'] * 1e-12,
                        p['leakage_ohm'] if p['leakage_enabled'] else None, p['initial_V'])
        # Each sample is a held current over ONE dt. State is fresh for every run.
        out = np.array([cap.integrate_current(i, 1/s.fs) for i in s.data])
        return {'out': Signal('voltage', s.fs, out)}


@kernel('ComponentAmplifier')
class VoltageAmplifier(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        model = Amplifier(p['gain'], p['offset_V'], p['v_min'] if p['lower_rail_enabled'] else None,
                          p['v_max'] if p['upper_rail_enabled'] else None)
        return {'out': s.like(model.amplify(s.data))}


@kernel('ComponentActivation')
class Nonlinearity(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        return {'out': s.like(Activation(p['kind'], p['gain'], p['threshold_V']).activate(s.data))}


@kernel('ComponentADC')
class Converter(Kernel):
    def process(self, inputs):
        s, p = inputs['in'], self.p
        adc = ADC(integer(p['bits'], 'bits'), p['v_min'], p['v_max'])
        codes = adc.convert(ranged(s.data, p))
        return {'code': Signal('digital', s.fs, codes), 'voltage': Signal('voltage', s.fs, adc.code_to_voltage(codes))}


@kernel('ComponentMAC')
class PhotonicMAC(Kernel):
    """Compact version of the exposed encoder/DAC/MZM/weight/PD chain.

    Input x is normalized; w is signed. Neither weights nor the splitter gain
    additional device physics beyond the ideal transmissions established in B22.
    Independent detector substreams use the same ID-derived seeds as expansion.
    """
    def process(self, inputs):
        import zlib
        light, p = inputs['light'], self.p
        x = bounded(inputs['x'].data, 0, 1, 'Normalized input')
        w = bounded(inputs['w'].data, -1, 1, 'Weights')
        v = inverse_mzm(x, p['v_pi'], p['bias_rad'])
        dac = DAC(integer(p['dac_bits'], 'dac_bits'), p['v_min'], p['v_max'])
        _, v = dac.quantize(ranged(v, p))
        power = MachZehnderModulator(p['v_pi'], p['bias_rad'], p['loss_dB']).modulate(
            np.abs(light.single_channel())**2, v)
        powers = [power * p['ratio'] * (1+w)/2, power * (1-p['ratio']) * (1-w)/2]
        currents = []
        for suffix, optical_power in zip(('pd_upper', 'pd_lower'), powers):
            seed = (zlib.crc32(f'{self.instance_id}/{suffix}'.encode()) + self.ctx.seed + int(p['seed'])) & 0xffffffff
            currents.append(detect(optical_power, light.fs, p, seed, self.ctx.noise))
        return {'out': Signal('current', light.fs, currents[0]-currents[1]),
                'drive': Signal('voltage', light.fs, v)}
