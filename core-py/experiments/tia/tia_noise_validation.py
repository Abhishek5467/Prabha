import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.tia import TIA


print("========== TIA NOISE VALIDATION ==========")


R_f = 1000.0

bandwidth_Hz = 10e9

fs = 160e9

duration = 10e-9

noise_density = 1e-12

I_dc = 0.5e-3

seed = 1


n_samples = int(fs * duration)

t = np.arange(n_samples) / fs

tia = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
    noise_current_density_A_per_sqrtHz=noise_density,
    seed=seed,
)

I = np.full(
    n_samples,
    I_dc,
)

V_clean = tia.amplify(
    I,
    fs=fs,
    include_noise=False,
)

V_noisy = tia.amplify(
    I,
    fs=fs,
    include_noise=True,
)

settle_samples = int(
    10 * fs / (
        2.0 * np.pi * bandwidth_Hz
    )
)

if settle_samples >= n_samples:
    settle_samples = n_samples // 10


V_clean_ss = V_clean[settle_samples:]
V_noisy_ss = V_noisy[settle_samples:]


noise = V_noisy_ss - V_clean_ss

measured_noise_rms = np.sqrt(
    np.mean(noise ** 2)
)

measured_noise_mean = np.mean(noise)

tau = 1.0 / (
    2.0 * np.pi * bandwidth_Hz
)

dt = 1.0 / fs

alpha = dt / (tau + dt)

enbw = (
    fs / 2.0
    * alpha
    / (2.0 - alpha)
)

theoretical_noise_rms = (
    noise_density
    * R_f
    * np.sqrt(enbw)
)

expected_voltage = I_dc * R_f

measured_voltage = np.mean(
    V_noisy_ss
)


dc_error = abs(
    measured_voltage
    - expected_voltage
)

print()
print("Parameters")
print("----------------------------------------")
print(
    f"Transimpedance gain : "
    f"{R_f:.6f} Ohm"
)

print(
    f"Bandwidth           : "
    f"{bandwidth_Hz / 1e9:.6f} GHz"
)

print(
    f"Sampling frequency  : "
    f"{fs / 1e9:.6f} GHz"
)

print(
    f"Noise density       : "
    f"{noise_density:.6e} A/sqrt(Hz)"
)

print(
    f"Input current       : "
    f"{I_dc * 1e3:.6f} mA"
)

print()
print("DC Output")
print("----------------------------------------")
print(
    f"Expected voltage    : "
    f"{expected_voltage:.9f} V"
)

print(
    f"Measured voltage    : "
    f"{measured_voltage:.9f} V"
)

print(
    f"DC error            : "
    f"{dc_error:.6e} V"
)


print()
print("Noise")
print("----------------------------------------")
print(
    f"Equivalent noise BW : "
    f"{enbw / 1e9:.6f} GHz"
)

print(
    f"Measured noise RMS  : "
    f"{measured_noise_rms:.6e} V"
)

print(
    f"Theoretical noise   : "
    f"{theoretical_noise_rms:.6e} V"
)

print(
    f"Noise mean          : "
    f"{measured_noise_mean:.6e} V"
)

noise_pass = np.isclose(
    measured_noise_rms,
    theoretical_noise_rms,
    rtol=0.10,
)

dc_pass = np.isclose(
    measured_voltage,
    expected_voltage,
    rtol=0.01,
    atol=1e-3,
)

zero_noise_tia = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
    noise_current_density_A_per_sqrtHz=0.0,
)

V_zero = zero_noise_tia.amplify(
    I,
    fs=fs,
    include_noise=True,
)

zero_noise_pass = np.allclose(
    V_zero,
    V_clean,
)

print()
print("Validation")
print("----------------------------------------")
print(
    "DC gain preserved       : "
    + ("PASS" if dc_pass else "FAIL")
)

print(
    "Noise RMS validation    : "
    + ("PASS" if noise_pass else "FAIL")
)

print(
    "Zero-noise behavior     : "
    + (
        "PASS"
        if zero_noise_pass
        else "FAIL"
    )
)


all_pass = (
    dc_pass
    and noise_pass
    and zero_noise_pass
)


print()

if all_pass:
    print(
        "PASS: TIA noise model validated."
    )
else:
    print(
        "FAIL: TIA noise validation failed."
    )
    
plt.figure(figsize=(9, 5))

plt.plot(
    t * 1e9,
    V_noisy * 1e3,
    label="TIA output with noise"
)

plt.axhline(
    expected_voltage * 1e3,
    linestyle="--",
    label="Ideal DC output"
)

plt.xlabel("Time [ns]")
plt.ylabel("TIA Output Voltage [mV]")

plt.title(
    "TIA Output Noise"
)

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()