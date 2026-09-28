import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC

print(
    "=========="
    "Inverse-MZM Calibrated End-to-End Validation "
    "=========="
)

P0_W = 1e-3

V_pi = 1.0
phi_bias=np.pi/2

responsivity=1.0
R_f=1000.0

dac_bits=8
adc_bits=8

dac_v_min=-0.5
dac_v_max=0.5

adc_v_min=0.0
adc_v_max=1.0


mzm=MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)

pd=Photodetector(responsivity_A_per_W=responsivity)

tia=TIA(R_f=R_f)

dac=DAC(
    bits=dac_bits,
    V_max=dac_v_max,
    V_min=dac_v_min
)

adc=ADC(
    resolution_bits=adc_bits,
    v_max=adc_v_max,
    v_min=adc_v_min
)


N=10001

x=np.linspace(
    -1.0,
    1.0,
    N
)

T_target=0.5-0.5*x

V_ideal=(
    (2.0*V_pi/np.pi)*(np.arccos(np.sqrt(T_target))-phi_bias/2.0)
)

dac_code,V_dac = dac.quantize(V_ideal)

P_in=np.full_like(
    x,
    P0_W
)

P_mzm=mzm.modulate(
    P_in,
    V_dac
)

T_actual=P_mzm/P0_W

I_pd=pd.detect(P_mzm)

V_tia=tia.amplify(I_pd)

adc_code=adc.convert(V_tia)

V_adc=adc.code_to_voltage(adc_code)


T_recovered=V_adc

x_recovered=(1.0-2.0*T_recovered)

dac_voltage_error=(V_dac-V_ideal)

transmission_error=(T_actual-T_target)

adc_voltage_error=(V_adc-V_tia)

x_error=(x_recovered-x)

max_dac_error=np.max(np.abs(dac_voltage_error))

rms_dac_error=np.sqrt(np.mean(dac_voltage_error**2))

max_transmission_error=np.max(np.abs(transmission_error))

rms_transmission_error=np.sqrt(np.mean(transmission_error**2))

max_adc_error=np.max(np.abs(adc_voltage_error))

rms_adc_error=np.sqrt(np.mean(adc_voltage_error**2))

max_x_error=np.max(np.abs(x_error))

rms_x_error=np.sqrt(np.mean(x_error**2))

mean_x_error=np.mean(x_error)


expected_pd_current=(responsivity*P_mzm)

pd_error=np.max(np.abs(I_pd-expected_pd_current))

expected_tia_voltage=(R_f*I_pd)

tia_error=np.max(np.abs(V_tia-expected_tia_voltage))


print()

print("System Parameters")
print("----------------------------------------")

print(
    f"Input samples              : {N}"
)

print(
    f"MZM V_pi                  : "
    f"{V_pi:.6f} V"
)

print(
    f"MZM bias                  : "
    f"{phi_bias:.9f} rad"
)

print(
    f"Laser power               : "
    f"{P0_W * 1e3:.6f} mW"
)

print(
    f"PD responsivity           : "
    f"{responsivity:.6f} A/W"
)

print(
    f"TIA gain                  : "
    f"{R_f:.6f} Ohm"
)

print(
    f"DAC resolution            : "
    f"{dac_bits} bits"
)

print(
    f"ADC resolution            : "
    f"{adc_bits} bits"
)


print()

print("Inverse-MZM Voltage Range")
print("----------------------------------------")

print(
    f"Minimum ideal voltage     : "
    f"{np.min(V_ideal):.9f} V"
)

print(
    f"Maximum ideal voltage     : "
    f"{np.max(V_ideal):.9f} V"
)

print(
    f"Minimum DAC voltage       : "
    f"{np.min(V_dac):.9f} V"
)

print(
    f"Maximum DAC voltage       : "
    f"{np.max(V_dac):.9f} V"
)

print()

print("DAC Error")
print("----------------------------------------")

print(
    f"Maximum voltage error     : "
    f"{max_dac_error:.12e} V"
)

print(
    f"RMS voltage error         : "
    f"{rms_dac_error:.12e} V"
)


print()

print("Optical Transmission Error")
print("----------------------------------------")

print(
    f"Maximum transmission error: "
    f"{max_transmission_error:.12e}"
)

print(
    f"RMS transmission error    : "
    f"{rms_transmission_error:.12e}"
)


print()

print("Receiver Interface")
print("----------------------------------------")

print(
    f"Maximum PD current error  : "
    f"{pd_error:.12e} A"
)

print(
    f"Maximum TIA voltage error : "
    f"{tia_error:.12e} V"
)


print()

print("ADC Error")
print("----------------------------------------")

print(
    f"Maximum ADC voltage error : "
    f"{max_adc_error:.12e} V"
)

print(
    f"RMS ADC voltage error     : "
    f"{rms_adc_error:.12e} V"
)


print()


print("Recovered Input Error")
print("----------------------------------------")

print(
    f"Maximum |x_hat - x|       : "
    f"{max_x_error:.12e}"
)

print(
    f"RMS x error               : "
    f"{rms_x_error:.12e}"
)

print(
    f"Mean x error              : "
    f"{mean_x_error:.12e}"
)


indices = np.linspace(
    0,
    N - 1,
    9,
    dtype=int
)


print()

print("Representative Samples")
print("-" * 105)

print(
    "x        T_target    "
    "V_ideal      V_DAC        "
    "T_actual     ADC V        "
    "x_recovered"
)

print("-" * 105)


for i in indices:

    print(
        f"{x[i]: .5f}   "
        f"{T_target[i]:.7f}    "
        f"{V_ideal[i]: .7f}   "
        f"{V_dac[i]: .7f}    "
        f"{T_actual[i]:.7f}    "
        f"{V_adc[i]:.7f}    "
        f"{x_recovered[i]: .7f}"
    )
    

voltage_range_pass = (
    np.min(V_ideal) >= dac_v_min
    and
    np.max(V_ideal) <= dac_v_max
)

transmission_range_pass = (
    np.min(T_actual) >= 0.0
    and
    np.max(T_actual) <= 1.0
)

pd_pass = (
    pd_error < 1e-15
)

tia_pass = (
    tia_error < 1e-15
)

adc_range_pass = (
    np.min(adc_code) >= 0
    and
    np.max(adc_code) < adc.n_codes
)

recovery_pass = (
    max_x_error < 0.012
)


print()


print("Validation")
print("----------------------------------------")

print(
    "Inverse-MZM voltage range : "
    f"{'PASS' if voltage_range_pass else 'FAIL'}"
)

print(
    "Optical transmission range: "
    f"{'PASS' if transmission_range_pass else 'FAIL'}"
)

print(
    "Photodetector conversion  : "
    f"{'PASS' if pd_pass else 'FAIL'}"
)

print(
    "TIA conversion            : "
    f"{'PASS' if tia_pass else 'FAIL'}"
)

print(
    "ADC code range            : "
    f"{'PASS' if adc_range_pass else 'FAIL'}"
)

print(
    "End-to-end recovery       : "
    f"{'PASS' if recovery_pass else 'FAIL'}"
)


assert voltage_range_pass
assert transmission_range_pass
assert pd_pass
assert tia_pass
assert adc_range_pass
assert recovery_pass


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    x,
    x,
    label="Ideal"
)

plt.plot(
    x,
    x_recovered,
    label="Recovered",
    alpha=0.8
)

plt.xlabel(
    "Original normalized input x"
)

plt.ylabel(
    "Recovered normalized input"
)

plt.title(
    "Inverse-MZM Calibrated "
    "End-to-End Recovery"
)

plt.grid(
    True
)

plt.legend()


plt.tight_layout()

plt.savefig(
    "inverse_mzm_end_to_end_recovery.png",
    dpi=300
)

plt.close()


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    x,
    x_error
)

plt.xlabel(
    "Normalized input x"
)

plt.ylabel(
    "Recovery error"
)

plt.title(
    "End-to-End Recovery Error"
)

plt.grid(
    True
)

plt.tight_layout()

plt.savefig(
    "inverse_mzm_end_to_end_error.png",
    dpi=300
)

plt.close()


print()

print(
    "PASS: Inverse-MZM calibrated "
    "electro-optical chain validated."
)

print(
    "Saved: "
    "inverse_mzm_end_to_end_recovery.png"
)

print(
    "Saved: "
    "inverse_mzm_end_to_end_error.png"
)

