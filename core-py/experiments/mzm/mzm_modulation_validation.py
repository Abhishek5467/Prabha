import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator as MZM


P_in_mW = 1.0
V_pi = 1.0
bias_phase = 0.0

V = np.linspace(-2.0, 2.0, 1000)

mzm = MZM(V_pi=V_pi, phi_bias=bias_phase)

P_in = P_in_mW * 1e-3

T = mzm.transfer(V)

P_out = P_in * T

T_theoretical = np.cos(
    np.pi * V / (2.0 * V_pi)
    + bias_phase / 2.0
) ** 2

P_theoretical = P_in * T_theoretical

transfer_error = np.max(np.abs(T - T_theoretical))

power_error = np.max(np.abs(P_out - P_theoretical))

print()
print("========== MZM MODULATION VALIDATION ==========")

print()
print(f"Input optical power = {P_in_mW:.6f} mW")
print(f"V_pi                = {V_pi:.6f} V")
print(f"Bias phase          = {bias_phase:.6f} rad")

print()
print("Maximum transfer error")
print(f"{transfer_error:.6e}")

print()
print("Maximum optical power error")
print(f"{power_error:.6e}")

test_voltages = np.array([
    -1.0,
    -0.5,
    0.0,
    0.5,
    1.0,
])

print()
print("Operating point validation")

for voltage in test_voltages:

    transmission = mzm.transfer(voltage)
    output_power = P_in * transmission

    theoretical_transmission = np.cos(
        np.pi * voltage / (2.0 * V_pi)
        + bias_phase / 2.0
    ) ** 2

    theoretical_power = (
        P_in * theoretical_transmission
    )

    print(
        f"V = {voltage: .3f} V"
        f" | T = {transmission:.6f}"
        f" | P_out = {output_power * 1e3:.6f} mW"
        f" | theory = {theoretical_power * 1e3:.6f} mW"
    )
    
plt.figure(figsize=(9, 5))

plt.plot(
    V,
    T,
    label="MZM transfer"
)

plt.plot(
    V,
    T_theoretical,
    "--",
    label="Analytical transfer"
)

plt.xlabel("Applied Voltage (V)")
plt.ylabel("Power transmission")

plt.title("MZM Optical Modulation")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

plt.figure(figsize=(9, 5))

plt.plot(
    V,
    P_out * 1e3,
    label="MZM output power"
)

plt.xlabel("Applied Voltage (V)")
plt.ylabel("Output optical power (mW)")

plt.title("MZM Output Optical Power")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

passed = (
    np.isclose(
        transfer_error,
        0.0,
        atol=1e-12,
    )
    and
    np.isclose(
        power_error,
        0.0,
        atol=1e-15,
    )
)

print()
print("========== VALIDATION SUMMARY ==========")

if passed:
    print("PASS: MZM optical modulation matches analytical model.")
else:
    print("FAIL: MZM optical modulation does not match analytical model.")

print()