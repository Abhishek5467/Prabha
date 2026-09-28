import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import csv
import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.photodetector import Photodetector


Q_E = 1.602176634e-19


print(
    "========== "
    "Photodetector Shot-Noise Power Sweep "
    "=========="
)

# PARAMETERS
responsivity = 1.0

dark_current_A = 5e-9

bandwidth_Hz = 10e9

N = 200_000


# OPTICAL-POWER SWEEP
# 1 pW --> 10 mW
# This crosses the dark-current transition:
# P_cross = I_dark / R = 5 nW

P_values_W = np.logspace(
    -12,
    -2,
    31
)


sigma_theory_array = []

sigma_measured_array = []

mean_theory_array = []

mean_measured_array = []

relative_error_array = []


# ZERO-LIGHT CASE
sigma_dark_theory = np.sqrt(
    2.0
    *
    Q_E
    *
    dark_current_A
    *
    bandwidth_Hz
)


print()

print("Dark-current shot-noise floor")
print("----------------------------------------")

print(
    f"Theoretical floor : "
    f"{sigma_dark_theory:.12e} A"
)


# POWER SWEEP
for i, P0_W in enumerate(P_values_W):

    pd = Photodetector(
        responsivity_A_per_W=responsivity,
        dark_current_A=dark_current_A,
        seed=100 + i
    )


    P = np.full(
        N,
        P0_W
    )


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

    I_mean_theory = (
        I_ph
        +
        dark_current_A
    )


    sigma_theory = np.sqrt(
        2.0
        *
        Q_E
        *
        I_mean_theory
        *
        bandwidth_Hz
    )


    # MEASURED
    I_mean_measured = np.mean(
        I_out
    )

    noise = (
        I_out
        -
        I_mean_theory
    )

    sigma_measured = np.std(
        noise
    )


    relative_error = (
        abs(
            sigma_measured
            -
            sigma_theory
        )
        /
        sigma_theory
    )


    # STORE
    sigma_theory_array.append(
        sigma_theory
    )

    sigma_measured_array.append(
        sigma_measured
    )

    mean_theory_array.append(
        I_mean_theory
    )

    mean_measured_array.append(
        I_mean_measured
    )

    relative_error_array.append(
        relative_error
    )


    print(
        f"P = {P0_W:.3e} W | "
        f"I = {I_mean_theory:.3e} A | "
        f"sigma theory = {sigma_theory:.3e} A | "
        f"sigma measured = {sigma_measured:.3e} A | "
        f"error = {100*relative_error:.3f} %"
    )


# ARRAYS
sigma_theory_array = np.asarray(
    sigma_theory_array
)

sigma_measured_array = np.asarray(
    sigma_measured_array
)

relative_error_array = np.asarray(
    relative_error_array
)


# VALIDATION METRICS
max_relative_error = np.max(
    relative_error_array
)

rms_relative_error = np.sqrt(
    np.mean(
        relative_error_array ** 2
    )
)


print()

print("Sweep Validation")
print("----------------------------------------")

print(
    f"Maximum relative RMS error : "
    f"{100*max_relative_error:.6f} %"
)

print(
    f"RMS relative error         : "
    f"{100*rms_relative_error:.6f} %"
)



# log(sigma) = 0.5 log(P) + constant

P_cross = (
    dark_current_A
    /
    responsivity
)

high_power_mask = (
    P_values_W
    >
    100.0 * P_cross
)


slope, intercept = np.polyfit(
    np.log10(
        P_values_W[
            high_power_mask
        ]
    ),
    np.log10(
        sigma_measured_array[
            high_power_mask
        ]
    ),
    1
)


print()

print("High-Power Scaling")
print("----------------------------------------")

print(
    f"Dark-current crossover : "
    f"{P_cross:.12e} W"
)

print(
    f"Measured log-log slope : "
    f"{slope:.6f}"
)

print(
    "Expected slope         : "
    "0.500000"
)


# VALIDATION
rms_pass = (
    max_relative_error
    <
    0.02
)

slope_pass = (
    abs(
        slope
        -
        0.5
    )
    <
    0.03
)


print()

print("Validation")
print("----------------------------------------")

print(
    "RMS agreement          : "
    f"{'PASS' if rms_pass else 'FAIL'}"
)

print(
    "sqrt(P) scaling        : "
    f"{'PASS' if slope_pass else 'FAIL'}"
)


assert rms_pass
assert slope_pass


# SAVE CSV
with open(
    "photodetector_shot_noise_power_sweep.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "optical_power_W",
            "mean_current_theory_A",
            "mean_current_measured_A",
            "sigma_theory_A",
            "sigma_measured_A",
            "relative_sigma_error",
        ]
    )


    for row in zip(
        P_values_W,
        mean_theory_array,
        mean_measured_array,
        sigma_theory_array,
        sigma_measured_array,
        relative_error_array
    ):

        writer.writerow(
            row
        )


# PLOT 1: NOISE VS OPTICAL POWER
plt.figure(
    figsize=(8, 5)
)

plt.loglog(
    P_values_W,
    sigma_theory_array,
    label="Theory"
)

plt.loglog(
    P_values_W,
    sigma_measured_array,
    "o",
    markersize=4,
    label="Measured"
)

plt.axhline(
    sigma_dark_theory,
    linestyle="--",
    label="Dark-current floor"
)

plt.axvline(
    P_cross,
    linestyle=":",
    label="I_ph = I_dark"
)

plt.xlabel(
    "Optical power [W]"
)

plt.ylabel(
    "Shot-noise RMS current [A]"
)

plt.title(
    "Photodetector Shot Noise vs Optical Power"
)

plt.grid(
    True,
    which="both"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "photodetector_shot_noise_power_sweep.png",
    dpi=300
)

plt.close()


# PLOT 2: RELATIVE THEORY ERROR
plt.figure(
    figsize=(8, 5)
)

plt.semilogx(
    P_values_W,
    100.0
    *
    relative_error_array
)

plt.xlabel(
    "Optical power [W]"
)

plt.ylabel(
    "Theory-measurement RMS difference [%]"
)

plt.title(
    "Shot-Noise Validation Error"
)

plt.grid(
    True,
    which="both"
)

plt.tight_layout()

plt.savefig(
    "photodetector_shot_noise_power_error.png",
    dpi=300
)

plt.close()


print()

print(
    "PASS: Photodetector shot-noise "
    "power sweep validated."
)