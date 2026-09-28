import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Allow importing from core-py
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(str(ROOT))

from prabha.blocks.cw_laser import CwLaser


laser = CwLaser(
    P0_mW=1.0,
    wavelength_nm=1550.0,
    fs=160e9,
    duration=1e-9,
)

t, E = laser.generate()

P = laser.power(E)

print("P0 =", laser.P0, "W")
print("lambda =", laser.wavelength, "m")
print("f0 =", laser.f0, "Hz")
print("Number of samples =", len(t))

print("Mean power =", np.mean(P), "W")
print("Minimum power =", np.min(P), "W")
print("Maximum power =", np.max(P), "W")

plt.plot(t * 1e12, P * 1e3)

plt.xlabel("Time (ps)")
plt.ylabel("Optical Power (mW)")
plt.title("Ideal CW Laser")

plt.grid()
plt.show()