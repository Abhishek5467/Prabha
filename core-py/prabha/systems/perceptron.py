"""The B22 deterministic neuron, extracted without changing its calibration.

The original experiment remains the independent numerical regression reference.
The behavioural activation precedes the ADC in this standalone model.
"""
from dataclasses import dataclass
import numpy as np
from ..blocks.mzm import MachZehnderModulator
from ..blocks.dac import DAC
from ..blocks.adc import ADC
from ..blocks.photodetector import Photodetector
from ..blocks.capacitor import Capacitor
from ..blocks.amplifier import Amplifier
from ..blocks.activation import Activation


@dataclass(frozen=True)
class NeuronConfig:
    dac_bits: int = 12
    adc_bits: int = 12

    def __post_init__(self):
        for name in ('dac_bits', 'adc_bits'):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, int) or not 3 <= v <= 16:
                raise ValueError(f'{name} must be an integer from 3 to 16.')


def vector(value, name, low, high, size=None):
    a = np.asarray(value, dtype=float)
    if a.ndim != 1 or not 1 <= len(a) <= 64 or not np.all(np.isfinite(a)):
        raise ValueError(f'{name} must be a finite nonempty vector of at most 64 values.')
    if size is not None and len(a) != size:
        raise ValueError(f'{name} must have {size} values.')
    if np.any(a < low) or np.any(a > high):
        raise ValueError(f'{name} values must be in [{low}, {high}].')
    return a


def physical_neuron(inputs, weights, bias, config=None):
    config = config or NeuronConfig()
    x = vector(inputs, 'Inputs', 0, 1)
    w = vector(weights, 'Weights', -1, 1, len(x))
    bias = float(bias)
    if not np.isfinite(bias) or abs(bias) > 10:
        raise ValueError('Bias must be finite and between -10 and 10.')
    v_pi, phi_bias, p0, responsivity = 1., np.pi / 2., 1e-3, 1.
    v_ideal = (2 * v_pi / np.pi) * (np.arccos(np.sqrt(x)) - phi_bias / 2)
    codes, v_dac = DAC(bits=config.dac_bits, V_min=-.5, V_max=.5).quantize(v_ideal)
    power = MachZehnderModulator(V_pi=v_pi, phi_bias=phi_bias).modulate(np.full_like(x, p0), v_dac)
    t_plus, t_minus = (1 + w) / 2, (1 - w) / 2
    pd = Photodetector(responsivity_A_per_W=responsivity, dark_current_A=0., seed=1)
    i_plus = pd.detect(.5 * power * t_plus, include_dark_current=False, include_shot_noise=False)
    i_minus = pd.detect(.5 * power * t_minus, include_dark_current=False, include_shot_noise=False)
    current = i_plus - i_minus
    v_cap = Capacitor(capacitance_F=1e-12).integrate_currents(current, integration_time_s=1e-9, reset=True)
    pre = float(Amplifier(gain=2., offset_V=bias).amplify(v_cap))
    analog = float(Activation(kind='sigmoid').activate(pre))
    adc = ADC(resolution_bits=config.adc_bits, v_min=0., v_max=1.)
    code = int(adc.convert(analog))
    output = float(adc.code_to_voltage(code))
    ideal_pre = float(w @ x + bias)
    ideal = float(1 / (1 + np.exp(-ideal_pre)))
    return {'output': output, 'ideal': ideal, 'error': output - ideal,
            'pre_activation': pre, 'ideal_pre_activation': ideal_pre,
            'analog_activation': analog, 'adc_code': code,
            'capacitor_voltage_V': float(v_cap), 'dac_codes': codes.tolist(),
            'drive_voltage_V': v_dac.tolist(), 'optical_power_W': power.tolist(),
            'differential_current_A': current.tolist(),
            'products': (2 * current / (p0 * responsivity)).tolist(),
            'ideal_products': (x * w).tolist(), 'bias': bias}
