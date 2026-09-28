import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CwLaser


laser = CwLaser(
    P0_mW=1.0,
    wavelength_nm=1550.0,
    fs=160e9,
    duration=10e-9,
    rin_db_hz=-150.0,
    seed=1,
)

t, E = laser.generate(include_rin=True)

P = laser.power(E)

print("P0 =", laser.P0, "W")
print("RIN =", laser.rin_db_hz, "dB/Hz")
print("RIN linear =", laser.rin_linear, "1/Hz")

print("Mean power =", np.mean(P), "W")
print("Std power =", np.std(P), "W")

print(
    "Relative RMS fluctuation =",
    np.std(P) / np.mean(P)
)

plt.figure()

plt.plot(
    t * 1e9,
    P * 1e3
)

plt.xlabel("Time (ns)")
plt.ylabel("Optical Power (mW)")
plt.title("CW Laser with RIN")

plt.grid()
plt.show()