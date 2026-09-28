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
bias_phase = np.pi / 2

# Normalized input range
x = np.linspace(-1.0, 1.0, 1001)

# Voltage scale used previously
V_scale = 0.1


# ============================================================
# MZM
# ============================================================

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=bias_phase,
)


# ============================================================
# 1. DEFINE DESIRED LINEAR OPTICAL RESPONSE
# ============================================================

# At quadrature:
#
# P_bias = P0 / 2
#
# dP/dV = -P0 * pi/(2 V_pi)
#
# Therefore:
#
# P_target(x) = P_bias + slope * V_scale * x

P_bias_mW = P0_mW * 0.5

slope_mW_per_V = (
    -P0_mW * np.pi / (2.0 * V_pi)
)

P_target_mW = (
    P_bias_mW
    + slope_mW_per_V * V_scale * x
)

T_target = P_target_mW / P0_mW


# ============================================================
# 2. INVERSE MZM
# ============================================================

# MZM:
#
# T = cos^2(
#       pi V/(2 V_pi)
#       + bias_phase/2
#     )
#
# Therefore:
#
# theta = acos(sqrt(T))
#
# V = 2 V_pi/pi *
#     (theta - bias_phase/2)

theta = np.arccos(np.sqrt(T_target))

V_required = (
    (2.0 * V_pi / np.pi)
    * (theta - bias_phase / 2.0)
)


# ============================================================
# 3. PASS VOLTAGES THROUGH ACTUAL MZM
# ============================================================

T_actual = mzm.transfer(V_required)

P_actual_mW = P0_mW * T_actual


# ============================================================
# 4. RECOVER INPUT
# ============================================================

x_recovered = (
    (P_actual_mW - P_bias_mW)
    / (slope_mW_per_V * V_scale)
)


# ============================================================
# 5. ERROR ANALYSIS
# ============================================================

transfer_error = np.max(
    np.abs(T_actual - T_target)
)

power_error = np.max(
    np.abs(P_actual_mW - P_target_mW)
)

input_error = np.abs(
    x_recovered - x
)

max_input_error = np.max(input_error)

rms_input_error = np.sqrt(
    np.mean(input_error ** 2)
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("========== MZM INVERSE ENCODING VALIDATION ==========")

print()
print("System parameters")

print(f"Input optical power = {P0_mW:.6f} mW")
print(f"V_pi                = {V_pi:.6f} V")
print(f"Bias phase          = {bias_phase:.6f} rad")
print(f"Voltage scale       = {V_scale:.6f} V")

print()
print("Quadrature operating point")

print(f"Bias voltage        = 0.000000 V")
print(f"Bias transmission   = 0.500000")
print(f"Bias optical power  = {P_bias_mW:.6f} mW")

print()
print("Linear target response")

print(
    f"Slope               = "
    f"{slope_mW_per_V:.12e} mW/V"
)

print(
    f"Target power range  = "
    f"[{P_target_mW.min():.6f}, "
    f"{P_target_mW.max():.6f}] mW"
)

print(
    f"Target transmission = "
    f"[{T_target.min():.6f}, "
    f"{T_target.max():.6f}]"
)

print()
print("========== INVERSE MZM VALIDATION ==========")

print(
    f"Maximum transfer error = "
    f"{transfer_error:.6e}"
)

print(
    f"Maximum power error    = "
    f"{power_error:.6e} mW"
)

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


# ============================================================
# SAMPLE INPUTS
# ============================================================

sample_x = np.array([
    -1.0,
    -0.5,
    0.0,
    0.5,
    1.0,
])

sample_T = np.interp(
    sample_x,
    x,
    T_target,
)

sample_V = np.interp(
    sample_x,
    x,
    V_required,
)

sample_P = P0_mW * sample_T

sample_recovered = np.interp(
    sample_x,
    x,
    x_recovered,
)


print()
print("========== SAMPLE INPUTS ==========")

for i in range(len(sample_x)):

    print(
        f"x = {sample_x[i]: .2f} | "
        f"V = {sample_V[i]: .6f} V | "
        f"T_target = {sample_T[i]:.9f} | "
        f"P_target = {sample_P[i]:.9f} mW | "
        f"x_recovered = {sample_recovered[i]:.9f}"
    )


# ============================================================
# PLOT 1: TARGET VS ACTUAL
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    P_actual_mW,
    label="MZM optical output",
)

plt.plot(
    x,
    P_target_mW,
    "--",
    label="Target linear encoding",
)

plt.xlabel("Normalized input x")
plt.ylabel("Output optical power (mW)")
plt.title("MZM Inverse Encoding")

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()


# ============================================================
# PLOT 2: REQUIRED VOLTAGE
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    V_required,
)

plt.xlabel("Normalized input x")
plt.ylabel("Required MZM voltage (V)")
plt.title("Inverse-MZM Voltage Encoding")

plt.grid()

plt.tight_layout()
plt.show()


# ============================================================
# PLOT 3: ENCODING ERROR
# ============================================================

plt.figure(figsize=(10, 6))

plt.plot(
    x,
    P_actual_mW - P_target_mW,
)

plt.xlabel("Normalized input x")
plt.ylabel("Power encoding error (mW)")
plt.title("Inverse-MZM Encoding Error")

plt.grid()

plt.tight_layout()
plt.show()


# ============================================================
# FINAL VALIDATION
# ============================================================

passed = (
    np.allclose(
        P_actual_mW,
        P_target_mW,
        rtol=1e-10,
        atol=1e-12,
    )
    and
    np.allclose(
        x_recovered,
        x,
        rtol=1e-10,
        atol=1e-12,
    )
)

print()
print("========== VALIDATION SUMMARY ==========")

print(
    "PASS: Inverse MZM reproduces the desired "
    "linear optical encoding."
    if passed
    else
    "FAIL: Inverse MZM encoding does not "
    "match the target."
)

print()