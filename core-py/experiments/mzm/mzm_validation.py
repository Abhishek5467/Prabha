import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator

P_in = 1e-3
V_pi = 1.0
phi_bias = 0.0

V = np.linspace(-2.0*V_pi, 2.0*V_pi, 1000)

mzm = MachZehnderModulator(V_pi=V_pi, phi_bias=phi_bias,)

T = mzm.transfer(V)

P_out = mzm.modulate(P_in,V)

T_theory = np.cos(np.pi*V/(2*V_pi)+phi_bias/2.0)**2

P_theory = P_in*T_theory

max_transfer_error = np.max(np.abs(T - T_theory))

max_power_error = np.max(np.abs(P_out - P_theory))

print()
print("========== MZM VALIDATION ==========")

print()
print(f"Input power      = {P_in * 1e3:.6f} mW")
print(f"V_pi             = {V_pi:.6f} V")
print(f"Bias phase       = {phi_bias:.6f} rad")

print()
print(f"Maximum transfer error = {max_transfer_error:.6e}")
print(f"Maximum power error    = {max_power_error:.6e}")

test_voltages = np.array([
    0.0, 
    V_pi/2.0,
    V_pi,
])

test_power = mzm.modulate(P_in, test_voltages)

print()
print("Operating point validation")

for voltage, power in zip(test_voltages, test_power):
    print(
        f"V = {voltage:.3f} V"
        f" | P_out = {power * 1e3:.6f} mW"
    )
    
plt.figure(figsize=(9,5))

plt.plot(V, T, label="MZM Transfer")

plt.xlabel("Applied Voltage [V]")
plt.ylabel("Power transmission")

plt.title("MZM Transfer Function")

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()

if np.allclose(T, T_theory):
    print()
    print("Transfer function validation PASSED")
else:
    print()
    print("Transfer function validation FAILED")