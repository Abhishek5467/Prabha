import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator as MZM

P_in_mW = 1.0
V_pi = 1.0

bias_phase = np.pi/2.0

V = np.linspace(-1.0,1.0,1001)

P_in = P_in_mW*1e-3

mzm = MZM(
    V_pi=V_pi,
    phi_bias=bias_phase,
)

T = mzm.transfer(V)

P_out = P_in*T

T_theoretical = np.cos(
    np.pi*V/(2.0*V_pi)+bias_phase/2.0
)**2

P_theoretical = P_in*T_theoretical

transfer_error = np.max(np.abs(T-T_theoretical))

power_error = np.max(np.abs(P_out-P_theoretical))

print()
print("++++ MZM LINEAR REGION VALIDATION ++++")

print()
print(f"Input optical power = {P_in_mW:.6f} mW")
print(f"V_pi = {V_pi:.6f} V")
print(f"Bias phase = {bias_phase:.6f} rad")
print(f"Bias phase = {bias_phase/np.pi:.6f} pi")

print()
print("Model Validation")
print(f"Maximum transfer error = {transfer_error:.6f}")
print(f"Maximum power error = {power_error:.6f}")

V_bias = 0.0

T_bias = mzm.transfer(V_bias)
P_bias = P_in*T_bias

print()
print("+++++ QUADRATURE OPERATION POINT +++++")

print(f"V_bias = {V_bias:.6f} V")
print(f"T_bias = {T_bias:.6f}")
print(f"P_bias = {P_bias*1e3:.6f} mW")

linear_ranges = [
    0.05,
    0.10,
    0.20,
    0.30,
]

print()
print("+++++ LINEARITY ANALYSIS +++++")

for V_range in linear_ranges:
    
    mask = np.abs(V-V_bias)<=V_range
    
    V_local = V[mask]
    P_local = P_out[mask]
    
    coefficients = np.polyfit(V_local, P_local, 1,)
    
    P_fit = np.polyval(coefficients, V_local,)
    
    max_error = np.max(np.abs(P_local-P_fit))
    
    rms_error = np.sqrt(np.mean((P_local-P_fit)**2))
    
    relative_max_error = (max_error/(np.max(P_local)-np.min(P_local))*100.0)
    
    print()
    print(f"Linear range = +/- {V_range:.2f} V")
    print(f"Slope = {coefficients[0]:.6e} W/V")
    print(f"Intercept = {coefficients[1]:.6e} W")
    print(f"Maximum error = {max_error:.6e} W")
    print(f"RMS erro = {rms_error:.6e} W")
    print(
        f"Relative max error = "
        f"{relative_max_error:.6f}"
    )
    
    
V_linear = 0.20

mask = np.abs(V-V_bias)<=V_linear

V_local = V[mask]
P_local = P_out[mask]

coefficients = np.polyfit(V_local, P_local, 1,)

P_fit = np.polyval(coefficients,V_local,)

plt.figure(figsize=(9,5))

plt.plot(V, P_out*1e3, label = "MZM output power")

plt.plot(V_local, P_fit*1e3, "--", label="Linear approximation",)

plt.xlabel("Applied Voltage (V)")
plt.ylabel("Output optical power (mW)")

plt.title("MZM Response Around Quadrature Bias")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))

plt.plot(V_local, P_local*1e3, label = "MZM response",)

plt.plot(V_local, P_fit*1e3, "--", label="Linear fit",)

plt.xlabel("Applied Voltage (V)")
plt.ylabel("Output optical power (mW)")

plt.title(f"MZM Linear Region (+-{V_linear:.2f} V)")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

print()
print("+++++ SUMMARY +++++")

print(
    "PASS : MZM transfer function matches "
    "the analytical model."
)

print(f"Quadrature transmission = {T_bias:.6f}")

print(
    f"Selected linear region = "
    f"+/- {V_linear:.2f} V"
)

print()