import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA


Q_E = 1.602176634e-19


print(
    "========== "
    "Photodetector + TIA Combined Noise Validation "
    "=========="
)


# PARAMETERS
P0_W = 3e-6

responsivity = 1.0

dark_current_A = 5e-9

R_f = 1000.0

bandwidth_Hz = 10e9

fs = 160e9

tia_noise_density = 1e-12

N = 500_000


# DETECTOR
pd = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=dark_current_A,
    seed=101
)


# CONSTANT OPTICAL INPUT
P = np.full(
    N,
    P0_W
)


# MEAN CURRENT
I_ph = (
    responsivity
    *
    P0_W
)

I_mean = (
    I_ph
    +
    dark_current_A
)


# SHOT-NOISE DENSITY
shot_density = np.sqrt(
    2.0
    *
    Q_E
    *
    I_mean
)


# DISCRETE TIA BANDWIDTH MODEL
dt = 1.0 / fs

tau = (
    1.0
    /
    (
        2.0
        *
        np.pi
        *
        bandwidth_Hz
    )
)

alpha = (
    dt
    /
    (
        tau
        +
        dt
    )
)


ENBW = (
    fs
    /
    2.0
    *
    alpha
    /
    (
        2.0
        -
        alpha
    )
)


# THEORETICAL OUTPUT NOISE
sigma_shot_theory = (
    shot_density
    *
    R_f
    *
    np.sqrt(ENBW)
)

sigma_tia_theory = (
    tia_noise_density
    *
    R_f
    *
    np.sqrt(ENBW)
)

total_density = np.sqrt(
    shot_density ** 2
    +
    tia_noise_density ** 2
)

sigma_total_theory = (
    total_density
    *
    R_f
    *
    np.sqrt(ENBW)
)


# CASE 1
# SHOT NOISE ONLY
I_shot = pd.detect_white_shot(
    P,
    fs=fs,
    include_dark_current=True,
    include_shot_noise=True
)


tia_shot = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
    noise_current_density_A_per_sqrtHz=0.0,
    seed=201
)


V_shot = tia_shot.amplify(
    I_shot,
    fs=fs,
    include_noise=False
)


# CASE 2
# TIA NOISE ONLY
I_clean = pd.detect_white_shot(
    P,
    fs=fs,
    include_dark_current=True,
    include_shot_noise=False
)


tia_only = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
    noise_current_density_A_per_sqrtHz=tia_noise_density,
    seed=202
)


V_tia_only = tia_only.amplify(
    I_clean,
    fs=fs,
    include_noise=True
)


# CASE 3
# SHOT + TIA NOISE

# New PD instance gives the same defined shot realization
# independently from the TIA RNG.
pd_combined = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=dark_current_A,
    seed=101
)


I_combined = pd_combined.detect_white_shot(
    P,
    fs=fs,
    include_dark_current=True,
    include_shot_noise=True
)


tia_combined = TIA(
    R_f=R_f,
    bandwidth_Hz=bandwidth_Hz,
    noise_current_density_A_per_sqrtHz=tia_noise_density,
    seed=202
)


V_combined = tia_combined.amplify(
    I_combined,
    fs=fs,
    include_noise=True
)


# REMOVE INITIAL FILTER TRANSIENT
settling_samples = int(
    np.ceil(
        10.0
        *
        tau
        *
        fs
    )
)


V_shot_ss = V_shot[
    settling_samples:
]

V_tia_ss = V_tia_only[
    settling_samples:
]

V_combined_ss = V_combined[
    settling_samples:
]

# DC OUTPUT
V_dc_expected = (
    R_f
    *
    I_mean
)

# MEASURED NOISE
noise_shot = (
    V_shot_ss
    -
    V_dc_expected
)

noise_tia = (
    V_tia_ss
    -
    V_dc_expected
)

noise_combined = (
    V_combined_ss
    -
    V_dc_expected
)


sigma_shot_measured = np.std(
    noise_shot
)

sigma_tia_measured = np.std(
    noise_tia
)

sigma_total_measured = np.std(
    noise_combined
)


# THEORY ERROR
shot_relative_error = (
    abs(
        sigma_shot_measured
        -
        sigma_shot_theory
    )
    /
    sigma_shot_theory
)

tia_relative_error = (
    abs(
        sigma_tia_measured
        -
        sigma_tia_theory
    )
    /
    sigma_tia_theory
)

total_relative_error = (
    abs(
        sigma_total_measured
        -
        sigma_total_theory
    )
    /
    sigma_total_theory
)


# VARIANCE ADDITION TEST
variance_sum_measured = (
    sigma_shot_measured ** 2
    +
    sigma_tia_measured ** 2
)

variance_combined_measured = (
    sigma_total_measured ** 2
)


variance_relative_error = (
    abs(
        variance_combined_measured
        -
        variance_sum_measured
    )
    /
    variance_sum_measured
)


# PRINT PARAMETERS

print()

print("Receiver Parameters")
print("----------------------------------------")

print(
    f"Optical power              : "
    f"{P0_W * 1e6:.6f} uW"
)

print(
    f"Photocurrent               : "
    f"{I_ph * 1e6:.6f} uA"
)

print(
    f"Dark current               : "
    f"{dark_current_A * 1e9:.6f} nA"
)

print(
    f"Mean detector current      : "
    f"{I_mean * 1e6:.6f} uA"
)

print(
    f"TIA gain                   : "
    f"{R_f:.6f} Ohm"
)

print(
    f"TIA bandwidth              : "
    f"{bandwidth_Hz / 1e9:.6f} GHz"
)

print(
    f"Sampling frequency         : "
    f"{fs / 1e9:.6f} GHz"
)

print(
    f"Equivalent noise bandwidth : "
    f"{ENBW / 1e9:.6f} GHz"
)



# PRINT INPUT NOISE DENSITIES

print()

print("Input-Referred Noise Densities")
print("----------------------------------------")

print(
    f"Shot-noise density         : "
    f"{shot_density:.12e} A/sqrt(Hz)"
)

print(
    f"TIA noise density          : "
    f"{tia_noise_density:.12e} A/sqrt(Hz)"
)

print(
    f"Combined density           : "
    f"{total_density:.12e} A/sqrt(Hz)"
)



# PRINT OUTPUT RMS
print()

print("Output Noise RMS")
print("----------------------------------------")

print(
    f"Shot theory                : "
    f"{sigma_shot_theory:.12e} V"
)

print(
    f"Shot measured              : "
    f"{sigma_shot_measured:.12e} V"
)

print(
    f"Shot relative error        : "
    f"{100*shot_relative_error:.6f} %"
)

print()

print(
    f"TIA theory                 : "
    f"{sigma_tia_theory:.12e} V"
)

print(
    f"TIA measured               : "
    f"{sigma_tia_measured:.12e} V"
)

print(
    f"TIA relative error         : "
    f"{100*tia_relative_error:.6f} %"
)

print()

print(
    f"Combined theory            : "
    f"{sigma_total_theory:.12e} V"
)

print(
    f"Combined measured          : "
    f"{sigma_total_measured:.12e} V"
)

print(
    f"Combined relative error    : "
    f"{100*total_relative_error:.6f} %"
)


# VARIANCE CHECK
print()

print("Variance Addition")
print("----------------------------------------")

print(
    f"sigma_shot^2 + sigma_TIA^2 : "
    f"{variance_sum_measured:.12e} V^2"
)

print(
    f"sigma_combined^2           : "
    f"{variance_combined_measured:.12e} V^2"
)

print(
    f"Relative variance error    : "
    f"{100*variance_relative_error:.6f} %"
)


# VALIDATION
shot_pass = (
    shot_relative_error
    <
    0.02
)

tia_pass = (
    tia_relative_error
    <
    0.02
)

combined_pass = (
    total_relative_error
    <
    0.02
)

variance_pass = (
    variance_relative_error
    <
    0.02
)


print()

print("Validation")
print("----------------------------------------")

print(
    "Shot-noise RMS             : "
    f"{'PASS' if shot_pass else 'FAIL'}"
)

print(
    "TIA-noise RMS              : "
    f"{'PASS' if tia_pass else 'FAIL'}"
)

print(
    "Combined RMS               : "
    f"{'PASS' if combined_pass else 'FAIL'}"
)

print(
    "Variance addition          : "
    f"{'PASS' if variance_pass else 'FAIL'}"
)


assert shot_pass
assert tia_pass
assert combined_pass
assert variance_pass


# PLOT 1
# RMS COMPARISON

labels = [
    "Shot",
    "TIA",
    "Combined"
]

theory = [
    sigma_shot_theory,
    sigma_tia_theory,
    sigma_total_theory
]

measured = [
    sigma_shot_measured,
    sigma_tia_measured,
    sigma_total_measured
]


x_pos = np.arange(
    len(labels)
)

width = 0.36


plt.figure(
    figsize=(8, 5)
)

plt.bar(
    x_pos - width / 2,
    theory,
    width,
    label="Theory"
)

plt.bar(
    x_pos + width / 2,
    measured,
    width,
    label="Measured"
)

plt.xticks(
    x_pos,
    labels
)

plt.ylabel(
    "Output noise RMS [V]"
)

plt.title(
    "Receiver Noise RMS: "
    "Theory vs Measurement"
)

plt.grid(
    True,
    axis="y"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "pd_tia_noise_rms_comparison.png",
    dpi=300
)

plt.close()


# PLOT 2
# TIME-DOMAIN COMBINED NOISE

plot_samples = 3000

t = (
    np.arange(plot_samples)
    /
    fs
)


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    t * 1e9,
    noise_combined[
        :plot_samples
    ]
)

plt.xlabel(
    "Time [ns]"
)

plt.ylabel(
    "Noise voltage [V]"
)

plt.title(
    "Combined Photodetector + TIA Noise"
)

plt.grid(
    True
)

plt.tight_layout()

plt.savefig(
    "pd_tia_combined_noise_waveform.png",
    dpi=300
)

plt.close()


print()

print(
    "PASS: Photodetector + TIA "
    "combined noise validated."
)

print()

print("Saved:")
print(
    "  pd_tia_noise_rms_comparison.png"
)
print(
    "  pd_tia_combined_noise_waveform.png"
)