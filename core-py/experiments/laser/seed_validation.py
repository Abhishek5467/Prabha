import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser


P0_mW = 1.0
wavelength_nm = 1550.0

fs = 160e9
duration = 10e-9

rin_db_hz = -150.0
linewidth_hz = 1e6

phase0 = 0.0


laser_1 = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=wavelength_nm,
    fs=fs,
    duration=duration,
    rin_db_hz=rin_db_hz,
    linewidth_hz=linewidth_hz,
    phase0=phase0,
    seed=1,
)

laser_2 = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=wavelength_nm,
    fs=fs,
    duration=duration,
    rin_db_hz=rin_db_hz,
    linewidth_hz=linewidth_hz,
    phase0=phase0,
    seed=1,
)


t1, E1 = laser_1.generate(
    include_rin=True,
    include_linewidth=True
)

t2, E2 = laser_2.generate(
    include_rin=True,
    include_linewidth=True
)


same_realization = np.array_equal(E1, E2)


print()
print("========== SEED REPRODUCIBILITY ==========")
print()

print(f"Seed 1 vs Seed 1 identical = {same_realization}")


seeds = [1, 2, 3]

fields = []
powers = []

for seed in seeds:

    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=wavelength_nm,
        fs=fs,
        duration=duration,
        rin_db_hz=rin_db_hz,
        linewidth_hz=linewidth_hz,
        phase0=phase0,
        seed=seed,
    )

    t, E = laser.generate(
        include_rin=True,
        include_linewidth=True
    )

    P = laser.power(E)

    fields.append(E)
    powers.append(P)

print()
print("========== DIFFERENT SEED TEST ==========")
print()

for i, seed in enumerate(seeds):

    print(
        f"Seed = {seed} | "
        f"mean = {np.mean(powers[i]) * 1e3:.6f} mW | "
        f"std = {np.std(powers[i]) * 1e3:.6f} mW"
    )


corr_12 = np.corrcoef(
    powers[0],
    powers[1]
)[0, 1]

corr_13 = np.corrcoef(
    powers[0],
    powers[2]
)[0, 1]

corr_23 = np.corrcoef(
    powers[1],
    powers[2]
)[0, 1]


print()
print("Power correlation between different seeds")

print(f"Seed 1 vs Seed 2 = {corr_12:.6f}")
print(f"Seed 1 vs Seed 3 = {corr_13:.6f}")
print(f"Seed 2 vs Seed 3 = {corr_23:.6f}")


plt.figure(figsize=(10, 5))

for i, seed in enumerate(seeds):

    plt.plot(
        t * 1e9,
        powers[i] * 1e3,
        label=f"Seed = {seed}"
    )

plt.xlabel("Time (ns)")
plt.ylabel("Power (mW)")
plt.title("CW Laser Output for Different Random Seeds")

plt.legend()
plt.grid()
plt.tight_layout()

plt.show()