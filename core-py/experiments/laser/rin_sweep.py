import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser

P0_values_mW = [0.1, 1.0, 10.0]

fs = 160e9
duration = 10e-9
rin_db_hz = -150.0

plt.figure()

for P0_mW in P0_values_mW:
    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=1550.0,
        fs=fs,
        duration=duration,
        rin_db_hz=rin_db_hz,
        seed=1,
    )

    t, E = laser.generate(include_rin=True)

    P = laser.power(E)

    mean_P = np.mean(P)
    std_P = np.std(P)

    relative_rms = std_P / mean_P

    theoretical_std = laser.P0 * np.sqrt(
        laser.rin_linear * (fs / 2.0)
    )

    print()
    print(f"P0 = {P0_mW:.1f} mW")
    print(f"Measured mean       = {mean_P * 1e3:.6f} mW")
    print(f"Measured std        = {std_P * 1e3:.6f} mW")
    print(f"Theoretical std     = {theoretical_std * 1e3:.6f} mW")
    print(f"Relative RMS        = {relative_rms:.6%}")

    plt.plot(
        t * 1e9,
        P * 1e3,
        label=f"P0 = {P0_mW} mW"
    )

plt.xlabel("Time (ns)")
plt.ylabel("Power (mW)")
plt.title("CW Laser Power with RIN")
plt.legend()

plt.grid()
plt.show()