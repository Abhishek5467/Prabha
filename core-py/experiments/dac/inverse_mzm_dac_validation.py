import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator 
from prabha.blocks.dac import DAC

P_in_mW = 1.0

V_pi = 1.0
phi_bias = np.pi / 2

dac_bits = 3
V_min = -0.5
V_max = 0.5

x = np.linspace(-1.0, 1.0, 9)

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
)

dac = DAC(
    bits=dac_bits,
    V_min=V_min,
    V_max=V_max,
)

T_target = 0.5-0.5*x

theta = np.arccos(np.sqrt(T_target))

V_ideal = (2.0*V_pi/np.pi*(theta-phi_bias/2.0))

codes, V_actual = dac.quantize(V_ideal)

T_ideal = mzm.transfer(V_ideal)

P_ideal = P_in_mW*T_ideal

T_dac = mzm.transfer(V_actual)

P_dac = P_in_mW*T_dac

voltage_error = V_actual - V_ideal
transmission_error = T_dac - T_ideal
power_error = P_dac - P_ideal

print("========== Inverse MZM → DAC → MZM Validation ==========")
print()

print("Parameters")
print("----------------------------------------")
print(f"Input optical power : {P_in_mW:.6f} mW")
print(f"MZM V_pi            : {V_pi:.6f} V")
print(f"MZM bias            : {phi_bias:.6f} rad")
print(f"DAC resolution      : {dac_bits} bits")
print(f"DAC range           : {V_min:.6f} → {V_max:.6f} V")
print(f"DAC LSB             : {dac.lsb:.9f} V")
print()

print(
    "x       V_ideal       Code   V_actual      "
    "V_error       T_ideal      T_DAC        T_error"
)
print("-" * 105)

for i in range(len(x)):
    print(
        f"{x[i]:+.3f}   "
        f"{V_ideal[i]:+.9f}   "
        f"{codes[i]:4d}   "
        f"{V_actual[i]:+.9f}   "
        f"{voltage_error[i]:+.9f}   "
        f"{T_ideal[i]:.9f}   "
        f"{T_dac[i]:.9f}   "
        f"{transmission_error[i]:+.9f}"
    )

print()

print("Error Summary")
print("----------------------------------------")
print(
    f"Maximum voltage error      : "
    f"{np.max(np.abs(voltage_error)):.9e} V"
)

print(
    f"RMS voltage error          : "
    f"{np.sqrt(np.mean(voltage_error**2)):.9e} V"
)

print(
    f"Maximum transmission error : "
    f"{np.max(np.abs(transmission_error)):.9e}"
)

print(
    f"RMS transmission error     : "
    f"{np.sqrt(np.mean(transmission_error**2)):.9e}"
)

print(
    f"Maximum optical power error: "
    f"{np.max(np.abs(power_error)):.9e} mW"
)

print(
    f"RMS optical power error    : "
    f"{np.sqrt(np.mean(power_error**2)):.9e} mW"
)

print()


assert np.all(V_actual >= V_min)
assert np.all(V_actual <= V_max)

assert np.all(codes >= 0)
assert np.all(codes <= dac.max_code)

assert np.max(np.abs(T_ideal - T_target)) < 1e-12

print("Validation")
print("----------------------------------------")
print("Inverse-MZM target transmission : PASS")
print("DAC code range                  : PASS")
print("DAC voltage range               : PASS")
print("DAC quantization                : ACTIVE")
print("MZM response to quantized V     : ACTIVE")
print()
print("========== Validation Complete ==========")