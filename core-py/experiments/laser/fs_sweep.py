import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser


P0_mW = 1.0
wavelength_nm = 1550.0

duration = 10e-9

rin_db_hz = -150.0
seed = 1


fs_values = np.array([
    10e9,
    20e9,
    40e9,
    80e9,
    160e9,
    320e9,
])

samples = []
sample_periods = []
mean_powers = []
std_powers = []
relative_rms = []
theoretical_std = []



for fs in fs_values:

    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=wavelength_nm,
        fs=fs,
        duration=duration,
        rin_db_hz=rin_db_hz,
        seed=seed,
    )

    t, E = laser.generate(include_rin=True)

    P = laser.power(E)

    N = len(t)

    Ts = 1.0 / fs

    mean_P = np.mean(P)
    std_P = np.std(P)

    # Theoretical RIN-induced power standard deviation
    bandwidth = fs / 2.0

    sigma_theory = (
        laser.P0
        * np.sqrt(laser.rin_linear * bandwidth)
    )

    rms = std_P / mean_P

    samples.append(N)
    sample_periods.append(Ts)
    mean_powers.append(mean_P)
    std_powers.append(std_P)
    relative_rms.append(rms)
    theoretical_std.append(sigma_theory)

    print(
        f"fs = {fs/1e9:7.1f} GHz | "
        f"Ts = {Ts*1e12:8.3f} ps | "
        f"N = {N:5d} | "
        f"mean = {mean_P*1e3:.6f} mW | "
        f"std = {std_P*1e3:.6f} mW | "
        f"theory = {sigma_theory*1e3:.6f} mW | "
        f"RMS = {rms*100:.4f}%"
    )


samples = np.array(samples)
sample_periods = np.array(sample_periods)
mean_powers = np.array(mean_powers)
std_powers = np.array(std_powers)
relative_rms = np.array(relative_rms)
theoretical_std = np.array(theoretical_std)


plt.figure()

plt.plot(
    fs_values / 1e9,
    samples,
    marker="o"
)

plt.xlabel("Sampling frequency (GHz)")
plt.ylabel("Number of samples")
plt.title("CW Laser Number of Samples vs Sampling Frequency")

plt.grid()
plt.tight_layout()


plt.figure()

plt.plot(
    fs_values / 1e9,
    std_powers * 1e3,
    marker="o",
    label="Measured"
)

plt.plot(
    fs_values / 1e9,
    theoretical_std * 1e3,
    "--",
    label="Theoretical"
)

plt.xlabel("Sampling frequency (GHz)")
plt.ylabel("Power standard deviation (mW)")
plt.title("RIN Power Fluctuation vs Sampling Frequency")

plt.legend()
plt.grid()
plt.tight_layout()



plt.figure()

plt.plot(
    fs_values / 1e9,
    relative_rms * 100,
    marker="o"
)

plt.xlabel("Sampling frequency (GHz)")
plt.ylabel("Relative RMS fluctuation (%)")
plt.title("Relative RIN Fluctuation vs Sampling Frequency")

plt.grid()
plt.tight_layout()

plt.show()