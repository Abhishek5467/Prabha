import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.photodetector import (
    Photodetector
)


Q_E = 1.602176634e-19


print(
    "========== "
    "Photodetector Shot-Noise Validation "
    "=========="
)


# PARAMETERS
responsivity = 1.0

P0_W = 1e-3

dark_current_A = 5e-9

bandwidth_Hz = 10e9

N = 1_000_000

seed = 1


# DETECTOR
pd = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=dark_current_A,
    seed=seed
)


# CONSTANT OPTICAL INPUT
P = np.full(
    N,
    P0_W
)


# DETECT WITH SHOT NOISE
I_out = pd.detect(
    P,
    bandwidth_Hz=bandwidth_Hz,
    include_dark_current=True,
    include_shot_noise=True
)



# THEORY
I_ph = (
    responsivity
    *
    P0_W
)

I_mean_expected = (
    I_ph
    +
    dark_current_A
)


sigma_theory = np.sqrt(
    2.0
    *
    Q_E
    *
    I_mean_expected
    *
    bandwidth_Hz
)


# MEASURE
mean_measured = np.mean(
    I_out
)

noise = (
    I_out
    -
    I_mean_expected
)

sigma_measured = np.std(
    noise
)


mean_error = (
    mean_measured
    -
    I_mean_expected
)

relative_sigma_error = (
    abs(
        sigma_measured
        -
        sigma_theory
    )
    /
    sigma_theory
)


# PRINT

print()

print("Parameters")
print("----------------------------------------")

print(
    f"Optical power          : "
    f"{P0_W * 1e3:.6f} mW"
)

print(
    f"Responsivity           : "
    f"{responsivity:.6f} A/W"
)

print(
    f"Photocurrent           : "
    f"{I_ph * 1e3:.6f} mA"
)

print(
    f"Dark current           : "
    f"{dark_current_A:.6e} A"
)

print(
    f"Bandwidth              : "
    f"{bandwidth_Hz / 1e9:.6f} GHz"
)

print(
    f"Samples                : "
    f"{N}"
)


print()

print("Shot-Noise Validation")
print("----------------------------------------")

print(
    f"Expected mean current  : "
    f"{I_mean_expected:.12e} A"
)

print(
    f"Measured mean current  : "
    f"{mean_measured:.12e} A"
)

print(
    f"Mean error             : "
    f"{mean_error:.12e} A"
)

print(
    f"Theoretical shot RMS   : "
    f"{sigma_theory:.12e} A"
)

print(
    f"Measured shot RMS      : "
    f"{sigma_measured:.12e} A"
)

print(
    f"Relative RMS error     : "
    f"{100 * relative_sigma_error:.6f} %"
)


# ============================================================
# VALIDATION
# ============================================================

mean_pass = (
    abs(mean_error)
    <
    5.0
    *
    sigma_theory
    /
    np.sqrt(N)
)

rms_pass = (
    relative_sigma_error
    <
    0.01
)


print()

print("Validation")
print("----------------------------------------")

print(
    "Mean current preserved : "
    f"{'PASS' if mean_pass else 'FAIL'}"
)

print(
    "Shot-noise RMS         : "
    f"{'PASS' if rms_pass else 'FAIL'}"
)


assert mean_pass
assert rms_pass


# HISTOGRAM

plt.figure(
    figsize=(8, 5)
)

plt.hist(
    noise,
    bins=100,
    density=True
)

plt.xlabel(
    "Shot-noise current [A]"
)

plt.ylabel(
    "Probability density"
)

plt.title(
    "Photodetector Shot-Noise Distribution"
)

plt.grid(
    True
)

plt.tight_layout()

plt.savefig(
    "photodetector_shot_noise_histogram.png",
    dpi=300
)

plt.close()


print()

print(
    "PASS: Photodetector shot-noise "
    "model validated."
)

print(
    "Saved: "
    "photodetector_shot_noise_histogram.png"
)