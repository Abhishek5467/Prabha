import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator


# ============================================================
# SYSTEM PARAMETERS
# ============================================================

P0_mW = 1.0
V_pi = 1.0
phi_bias = np.pi / 2

# Small voltage range around quadrature
V_scale = 0.1

x = np.array([0.9, 0.3, 0.7, 0.5])

w = np.array([
    0.8,
    -0.6,
    0.4,
    -0.9
])

expected_mac = np.dot(x, w)


# ============================================================
# MZM
# ============================================================

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
    insertion_loss_dB=0.0
)


# ============================================================
# MZM TRANSFER FUNCTION
# ============================================================

def mzm_transfer(V):
    """
    MZM power transmission.

    T(V) = cos^2(
        pi*V/(2*V_pi) + phi_bias/2
    )
    """

    phase = (
        np.pi * V / (2.0 * V_pi)
        + phi_bias / 2.0
    )

    return np.cos(phase) ** 2


# ============================================================
# LINEAR TARGET
# ============================================================

# Around quadrature:
#
# T(V) ~= 0.5 - (pi/2)*(V/V_pi)
#
# We want:
#
# V_linear = V_scale*x
#
# Therefore the desired optical transmission is
#
# T_target = 0.5 - (pi/2)*(V_scale/V_pi)*x
#
# But instead of applying V_linear directly to the MZM,
# we calculate the exact inverse MZM voltage which produces
# T_target.
# ============================================================

K = np.pi / (2.0 * V_pi)

T_bias = 0.5

T_target = T_bias - K * V_scale * x


# ============================================================
# INVERSE MZM
# ============================================================

def inverse_mzm_voltage(T):
    """
    Solve the MZM transfer function for V.

        T = cos^2(
            pi V/(2 V_pi) + phi_bias/2
        )

    We select the branch around the quadrature operating point.
    """

    T = np.asarray(T, dtype=float)

    if np.any(T < 0.0) or np.any(T > 1.0):
        raise ValueError(
            "Target transmission must lie between 0 and 1."
        )

    phase = np.arccos(np.sqrt(T))

    V = (
        2.0 * V_pi / np.pi
        * (phase - phi_bias / 2.0)
    )

    return V


V_inverse = inverse_mzm_voltage(T_target)


# ============================================================
# ACTUAL MZM OUTPUT
# ============================================================

T_actual = mzm_transfer(V_inverse)

P_target_mW = P0_mW * T_target
P_actual_mW = P0_mW * T_actual


# ============================================================
# INPUT RECOVERY
# ============================================================

x_recovered = (
    T_actual - T_bias
) / (
    -K * V_scale
)


# ============================================================
# OPTICAL MAC
# ============================================================

# The MZM output contains a DC bias:
#
#     P_i = P_bias + Delta_P_i
#
# The useful information carrying the input x_i is Delta_P_i.

P_bias_mW = P0_mW * 0.5

Delta_P_mW = P_actual_mW - P_bias_mW


# Linear MZM scale factor:
#
#     Delta_P = -P0 * K * V_scale * x
#
# where
#
#     K = pi / (2 V_pi)

K = np.pi / (2.0 * V_pi)

optical_scale_mW = (
    P0_mW * K * V_scale
)


# ------------------------------------------------------------
# Positive and negative weight branches
# ------------------------------------------------------------

w_plus = np.maximum(w, 0.0)
w_minus = np.maximum(-w, 0.0)


# Weighted MODULATED optical powers

Delta_P_plus_channels_mW = (
    Delta_P_mW * w_plus
)

Delta_P_minus_channels_mW = (
    Delta_P_mW * w_minus
)


Delta_P_plus_mW = np.sum(
    Delta_P_plus_channels_mW
)

Delta_P_minus_mW = np.sum(
    Delta_P_minus_channels_mW
)


# Differential optical accumulation

Delta_P_diff_mW = (
    Delta_P_plus_mW
    - Delta_P_minus_mW
)


# Recover the mathematical MAC.
#
# Delta_P_diff =
#       -P0*K*V_scale*sum(x_i*w_i)
#
# therefore:
#
# MAC = -Delta_P_diff / optical_scale

mac_recovered = (
    -Delta_P_diff_mW
    / optical_scale_mW
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("========== MZM INVERSE-ENCODED PHOTONIC MAC ==========")

print()
print("System parameters")
print(f"Input optical power = {P0_mW:.6f} mW")
print(f"V_pi                = {V_pi:.6f} V")
print(f"Bias phase           = {phi_bias:.6f} rad")
print(f"Voltage scale        = {V_scale:.6f} V")

print()
print("Input vector:")
print(x)

print()
print("Weight vector:")
print(w)

print()
print("Expected mathematical MAC")
print(f"y = {expected_mac:.12f}")


# ============================================================
# ENCODING RESULTS
# ============================================================

print()
print("========== INVERSE MZM ENCODING ==========")

for i in range(len(x)):

    print(
        f"Channel {i}: "
        f"x = {x[i]: .6f} | "
        f"T_target = {T_target[i]:.9f} | "
        f"V = {V_inverse[i]: .9f} V | "
        f"T_actual = {T_actual[i]:.9f} | "
        f"P_out = {P_actual_mW[i]:.9f} mW | "
        f"x_recovered = {x_recovered[i]: .9f}"
    )


# ============================================================
# INPUT RECOVERY VALIDATION
# ============================================================

input_error = x_recovered - x

max_input_error = np.max(np.abs(input_error))
rms_input_error = np.sqrt(np.mean(input_error ** 2))

print()
print("========== INPUT RECOVERY ==========")

print(
    f"Maximum input error = "
    f"{max_input_error:.6e}"
)

print(
    f"RMS input error     = "
    f"{rms_input_error:.6e}"
)

print()
print("Recovered input:")
print(x_recovered)


print()
print("========== OPTICAL MAC VALIDATION ==========")

print(
    f"MZM bias power = "
    f"{P_bias_mW:.12f} mW"
)

print()
print("Modulated optical powers:")

for i in range(len(x)):
    print(
        f"Channel {i}: "
        f"P = {P_actual_mW[i]:.12f} mW | "
        f"Delta P = {Delta_P_mW[i]: .12f} mW"
    )

print()
print(
    f"Positive modulated branch = "
    f"{Delta_P_plus_mW:.12f} mW"
)

print(
    f"Negative modulated branch = "
    f"{Delta_P_minus_mW:.12f} mW"
)

print(
    f"Differential modulated output = "
    f"{Delta_P_diff_mW:.12f} mW"
)

print()
print(
    f"Optical scale = "
    f"{optical_scale_mW:.12f} mW"
)

print(
    f"Expected MAC  = "
    f"{expected_mac:.12f}"
)

print(
    f"Recovered MAC = "
    f"{mac_recovered:.12f}"
)

mac_error = abs(
    mac_recovered - expected_mac
)

relative_mac_error = (
    mac_error / abs(expected_mac) * 100.0
)

print(
    f"MAC error     = "
    f"{mac_error:.6e}"
)

print(
    f"Relative error = "
    f"{relative_mac_error:.6f} %"
)


# ============================================================
# PLOT 1: TARGET VS ACTUAL OPTICAL ENCODING
# ============================================================

x_plot = np.linspace(-1.0, 1.0, 1000)

T_target_plot = (
    0.5
    - K * V_scale * x_plot
)

V_inverse_plot = inverse_mzm_voltage(
    T_target_plot
)

T_actual_plot = mzm_transfer(
    V_inverse_plot
)

P_target_plot = P0_mW * T_target_plot
P_actual_plot = P0_mW * T_actual_plot


plt.figure(figsize=(10, 6))

plt.plot(
    x_plot,
    P_actual_plot,
    label="MZM optical output"
)

plt.plot(
    x_plot,
    P_target_plot,
    "--",
    label="Target linear encoding"
)

plt.xlabel("Normalized input x")
plt.ylabel("Optical power (mW)")
plt.title("Inverse-MZM Photonic Input Encoding")

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()


# ============================================================
# PLOT 2: CHANNEL OPTICAL CONTRIBUTIONS
# ============================================================

indices = np.arange(len(x))

plt.figure(figsize=(10, 6))

plt.bar(
    indices - 0.15,
    P_plus_channels_mW,
    width=0.3,
    label="Positive contribution"
)

plt.bar(
    indices + 0.15,
    P_minus_channels_mW,
    width=0.3,
    label="Negative contribution"
)

plt.xlabel("MAC channel i")
plt.ylabel("Optical power (mW)")
plt.title("Inverse-MZM Photonic MAC Contributions")

plt.xticks(indices)

plt.grid(axis="y")
plt.legend()

plt.tight_layout()
plt.show()


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("========== FINAL VALIDATION ==========")

if np.isclose(
    mac_recovered,
    expected_mac,
    rtol=1e-10,
    atol=1e-12
):

    print(
        "PASS: Inverse MZM encoding reproduces "
        "the mathematical MAC."
    )

else:

    print(
        "FAIL: Inverse MZM encoding does not "
        "reproduce the mathematical MAC."
    )

print()