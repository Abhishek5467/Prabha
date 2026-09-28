import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator as MZM


P0_mW = 1.0
V_pi = 1.0
bias_phase = np.pi / 2

V_scale = 0.10


x = np.array([
    0.9,
    0.3,
    0.7,
    0.5
])

w = np.array([
    0.8,
    -0.6,
    0.4,
    -0.9
])

expected = np.dot(x, w)


mzm = MZM(
    V_pi=V_pi,
    phi_bias=bias_phase,
)


V_bias = 0.0

P_bias = P0_mW * mzm.transfer(
    np.array([V_bias])
)[0]

delta_V = 1e-6

P_plus = P0_mW * mzm.transfer(
    np.array([V_bias + delta_V])
)[0]

P_minus = P0_mW * mzm.transfer(
    np.array([V_bias - delta_V])
)[0]

K = (P_plus - P_minus) / (2.0 * delta_V)


V = V_scale * x

T = mzm.transfer(V)

P_out_mW = P0_mW * T


# ============================================================
# REFERENCE DIFFERENTIAL DETECTION
# ============================================================
#
# Our MZM has negative slope around the selected
# quadrature point:
#
# P_out = P_bias + K V
#
# where K < 0.
#
# Therefore:
#
# P_bias - P_out ≈ |K| V
#
# and because V = V_scale*x:
#
# x_hat =
#     (P_bias - P_out)
#     -----------------
#          |K| V_scale


P_diff_mW = P_bias - P_out_mW

x_recovered = (
    P_diff_mW
    / (abs(K) * V_scale)
)

input_error = x_recovered - x

max_input_error = np.max(
    np.abs(input_error)
)

rms_input_error = np.sqrt(
    np.mean(input_error**2)
)


mac_recovered = np.dot(
    x_recovered,
    w
)


mac_error = abs(
    mac_recovered - expected
)


relative_mac_error = (
    mac_error / abs(expected)
) * 100.0


print()
print("========== MZM PHOTONIC MAC VALIDATION ==========")

print()
print("System parameters")

print(f"Input optical power = {P0_mW:.6f} mW")
print(f"V_pi                = {V_pi:.6f} V")
print(f"Bias phase          = {bias_phase:.6f} rad")
print(f"Voltage scale       = {V_scale:.6f} V")


print()
print("Input vector:")
print(x)

print()
print("Weight vector:")
print(w)


print()
print("Expected mathematical MAC")
print(f"y = {expected:.12f}")


print()
print("========== MZM OPERATING POINT ==========")

print(f"Bias voltage        = {V_bias:.6f} V")
print(f"Bias transmission   = {mzm.transfer(np.array([V_bias]))[0]:.12f}")
print(f"Bias optical power  = {P_bias:.12f} mW")
print(f"MZM slope K         = {K:.12e} mW/V")


print()
print("========== MZM ENCODING ==========")

for i in range(len(x)):

    print(
        f"Channel {i}: "
        f"x = {x[i]: .6f} | "
        f"V = {V[i]: .6f} V | "
        f"T = {T[i]: .9f} | "
        f"P_out = {P_out_mW[i]: .9f} mW | "
        f"x_recovered = {x_recovered[i]: .9f}"
    )


print()
print("========== INPUT RECOVERY ==========")

print(f"Maximum input error = {max_input_error:.6e}")
print(f"RMS input error     = {rms_input_error:.6e}")


print()
print("Recovered input:")
print(x_recovered)


print()
print("========== MAC VALIDATION ==========")

print(f"Expected MAC        = {expected:.12f}")
print(f"Recovered MAC       = {mac_recovered:.12f}")
print(f"MAC error           = {mac_error:.6e}")
print(f"Relative MAC error  = {relative_mac_error:.6f} %")


expected_contributions = x * w
recovered_contributions = x_recovered * w

print()
print("========== CHANNEL CONTRIBUTIONS ==========")

for i in range(len(x)):

    print(
        f"Channel {i}: "
        f"expected = {expected_contributions[i]: .12f} | "
        f"recovered = {recovered_contributions[i]: .12f}"
    )


plt.figure(figsize=(9, 5))

plt.bar(
    np.arange(len(x)) - 0.18,
    P_out_mW,
    width=0.36,
    label="MZM output power",
)

plt.bar(
    np.arange(len(x)) + 0.18,
    np.full(len(x), P_bias),
    width=0.36,
    label="Reference power",
)

plt.xlabel("MAC channel i")
plt.ylabel("Optical power (mW)")
plt.title("MZM Optical Encoding of MAC Inputs")

plt.xticks(np.arange(len(x)))

plt.legend()
plt.grid(axis="y")

plt.tight_layout()
plt.show()


plt.figure(figsize=(9, 5))

indices = np.arange(len(x))

plt.plot(
    indices,
    x,
    "o-",
    label="Original input",
)

plt.plot(
    indices,
    x_recovered,
    "s--",
    label="Recovered optical input",
)

plt.xlabel("MAC channel i")
plt.ylabel("Normalized input")

plt.title("MZM Input Encoding and Optical Recovery")

plt.xticks(indices)

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()


plt.figure(figsize=(9, 5))

plt.bar(
    indices - 0.18,
    expected_contributions,
    width=0.36,
    label="Mathematical contribution",
)

plt.bar(
    indices + 0.18,
    recovered_contributions,
    width=0.36,
    label="MZM recovered contribution",
)

plt.xlabel("MAC channel i")
plt.ylabel("Contribution to MAC")

plt.title("MZM-Based MAC Channel Contributions")

plt.xticks(indices)

plt.legend()
plt.grid(axis="y")

plt.tight_layout()
plt.show()


print()
print("========== VALIDATION SUMMARY ==========")

if np.isclose(
    mac_recovered,
    expected,
    rtol=1e-3,
    atol=1e-6,
):

    print(
        "PASS: MZM-based optical encoding "
        "reproduces the mathematical MAC."
    )

else:

    print(
        "FAIL: MZM-based optical encoding "
        "does not reproduce the mathematical MAC."
    )

print()