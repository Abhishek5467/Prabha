import sys
from pathlib import Path

Root = Path(__file__).resolve().parents[2]
sys.path.append(str(Root))

import numpy as np

from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC


print("========== DAC → MZM → PD → TIA → ADC ==========")

P0_mW = 1.0

V_pi = 1.0
phi_bias = np.pi / 2

responsivity = 1.0       # A/W
tia_gain = 1000.0        # Ohm

resolution_bits = 8
v_min = 0.0
v_max = 1.0

fs = 160e9

laser = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=1550.0,
    fs=fs,
    duration=1e-9,
    seed=1
)

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)

pd = Photodetector(
    responsivity_A_per_W=responsivity
)

tia = TIA(
    R_f=tia_gain
)

dac = DAC(
    bits=resolution_bits,
    V_min=v_min,
    V_max=v_max
)

adc = ADC(
    resolution_bits=resolution_bits,
    v_min=v_min,
    v_max=v_max
)

digital_input = np.array([
    0.00,
    0.10,
    0.25,
    0.37,
    0.50,
    0.63,
    0.75,
    0.90,
    1.00
])


print()
print("System parameters")
print("----------------------------------------")
print(f"Laser power          : {P0_mW:.6f} mW")
print(f"Laser wavelength     : 1550.0 nm")
print(f"MZM V_pi             : {V_pi:.6f} V")
print(f"MZM bias phase       : {phi_bias:.6f} rad")
print(f"PD responsivity      : {responsivity:.6f} A/W")
print(f"TIA gain             : {tia_gain:.6f} Ohm")
print(f"ADC/DAC resolution   : {resolution_bits} bits")
print(f"Voltage range        : {v_min:.6f} → {v_max:.6f} V")


dac_code = dac.voltage_to_code(digital_input)
dac_voltage = dac.code_to_voltage(dac_code)


print()
print("DAC")
print("----------------------------------------")

for x, code, voltage in zip(
    digital_input,
    dac_code,
    dac_voltage
):
    print(
        f"Input = {x:.6f}"
        f" → Code = {code:3d}"
        f" → V_DAC = {voltage:.9f} V"
    )

t, E = laser.generate()

P_laser = laser.power(E)

mean_laser_power = np.mean(P_laser)


P_mzm = np.array([
    np.mean(
        mzm.modulate(
            P_laser,
            V
        )
    )
    for V in dac_voltage
])


I_pd = pd.detect(
    P_mzm
)


V_tia = tia.amplify(
    I_pd
)


adc_code = adc.convert(
    V_tia
)

V_recovered = adc.code_to_voltage(
    adc_code
)


print()
print("End-to-End Conversion")
print("----------------------------------------")

print(
    "Input       DAC V        MZM P[mW]     "
    "PD I[mA]      TIA V         ADC Code"
)

print("-" * 90)


for i in range(len(digital_input)):

    print(
        f"{digital_input[i]:.6f}     "
        f"{dac_voltage[i]:.9f}   "
        f"{P_mzm[i] * 1e3:.9f}   "
        f"{I_pd[i] * 1e3:.9f}   "
        f"{V_tia[i]:.9f}   "
        f"{adc_code[i]:3d}"
    )


print()
print("Validation")
print("----------------------------------------")



expected_mzm_power = np.array([
    np.mean(
        mzm.modulate(
            np.full_like(P_laser, P0_mW * 1e-3),
            V
        )
    )
    for V in dac_voltage
])

mzm_error = np.max(
    np.abs(P_mzm - expected_mzm_power)
)

pd_expected = responsivity * P_mzm

pd_error = np.max(
    np.abs(I_pd - pd_expected)
)

tia_expected = tia_gain * I_pd

tia_error = np.max(
    np.abs(V_tia - tia_expected)
)

adc_range_pass = (
    np.min(adc_code) >= 0
    and
    np.max(adc_code) < adc.n_codes
)


print(
    f"MZM maximum power error : "
    f"{mzm_error:.6e} W"
)

print(
    f"PD maximum current error: "
    f"{pd_error:.6e} A"
)

print(
    f"TIA maximum voltage error: "
    f"{tia_error:.6e} V"
)

print(
    f"ADC code range          : "
    f"{'PASS' if adc_range_pass else 'FAIL'}"
)


assert mzm_error < 1e-15
assert pd_error < 1e-15
assert tia_error < 1e-15
assert adc_range_pass


print()
print("PASS: Complete ideal electro-optical chain validated.")


