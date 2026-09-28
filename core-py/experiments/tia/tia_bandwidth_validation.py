import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.tia import TIA


print("========== TIA BANDWIDTH VALIDATION ==========")

R_f = 1000.0

bandwidth_Hz = 10e9

fs = 160e9

duration = 2e-9

I_dc_mA = 0.5

I_dc = I_dc_mA * 1e-3

tia = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
)

V_dc = tia.amplify(I_dc, fs=fs)

expected_dc = I_dc * R_f

dc_error = abs(V_dc - expected_dc)


print()
print("Parameters")
print("----------------------------------------")
print(f"Transimpedance gain : {R_f:.6f} Ohm")
print(f"Bandwidth           : {bandwidth_Hz / 1e9:.6f} GHz")
print(f"Sampling frequency  : {fs / 1e9:.6f} GHz")


print()
print("DC Validation")
print("----------------------------------------")
print(f"Input current       : {I_dc_mA:.6f} mA")
print(f"TIA output          : {V_dc:.9f} V")
print(f"Expected output     : {expected_dc:.9f} V")
print(f"DC error            : {dc_error:.6e} V")

n_samples = int(fs * duration)

t = np.arange(n_samples) / fs

I = np.zeros(n_samples)

step_index = n_samples // 4

I[step_index:] = I_dc


V = tia.amplify(I, fs=fs)

V_final = expected_dc

post_step = V[step_index:]

target_10 = 0.1 * V_final
target_90 = 0.9 * V_final

idx_10 = np.where(post_step >= target_10)[0]
idx_90 = np.where(post_step >= target_90)[0]

if len(idx_10) > 0 and len(idx_90) > 0:

    t10 = idx_10[0] / fs
    t90 = idx_90[0] / fs

    rise_time = t90 - t10

else:

    rise_time = np.nan


final_error = abs(V[-1] - V_final)


tau = 1.0 / (2.0 * np.pi * bandwidth_Hz)

theoretical_rise_time = 2.2 * tau


print()
print("Step Response")
print("----------------------------------------")
print(f"Final output        : {V[-1]:.9f} V")
print(f"Expected final      : {V_final:.9f} V")
print(f"Final error         : {final_error:.6e} V")

print()
print("Bandwidth Metrics")
print("----------------------------------------")
print(f"Time constant       : {tau:.6e} s")
print(f"Measured 10-90% rise: {rise_time:.6e} s")
print(f"Theoretical rise    : {theoretical_rise_time:.6e} s")

dc_pass = np.isclose(
    V_dc,
    expected_dc,
    rtol=1e-12,
    atol=1e-15,
)

final_pass = np.isclose(
    V[-1],
    V_final,
    rtol=1e-3,
    atol=1e-6,
)

rise_pass = np.isclose(
    rise_time,
    theoretical_rise_time,
    rtol=0.1,
)


print()
print("Validation")
print("----------------------------------------")
print(
    "DC gain validation          : "
    + ("PASS" if dc_pass else "FAIL")
)

print(
    "Finite bandwidth response   : "
    + ("PASS" if final_pass else "FAIL")
)

print(
    "Rise-time validation        : "
    + ("PASS" if rise_pass else "FAIL")
)


all_pass = dc_pass and final_pass and rise_pass

print()

if all_pass:
    print("PASS: TIA finite-bandwidth model validated.")
else:
    print("FAIL: TIA finite-bandwidth validation failed.")
    
plt.figure(figsize=(9, 5))

plt.plot(
    t * 1e9,
    I * 1e3,
    label="Input current"
)

plt.plot(
    t * 1e9,
    V,
    label="TIA output voltage"
)

plt.xlabel("Time [ns]")
plt.ylabel("Amplitude")
plt.title("TIA Finite-Bandwidth Step Response")

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()