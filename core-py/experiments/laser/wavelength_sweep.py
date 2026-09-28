import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser


wavelengths_nm = np.array([
    1260.0,
    1310.0,
    1490.0,
    1550.0,
    1625.0,
])

P0_mW = 1.0
fs = 160e9
duration = 10e-9


frequencies_hz = []

for wavelength_nm in wavelengths_nm:

    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=wavelength_nm,
        fs=fs,
        duration=duration,
    )

    frequencies_hz.append(laser.f0)

    print(
        f"lambda = {wavelength_nm:.1f} nm"
        f" | f0 = {laser.f0:.6e} Hz"
        f" | f0 = {laser.f0 / 1e12:.6f} THz"
    )


frequencies_hz = np.array(frequencies_hz)


C = 299_792_458.0

theoretical_frequencies = (
    C / (wavelengths_nm * 1e-9)
)

error = np.abs(
    frequencies_hz - theoretical_frequencies
)


print()
print("========== WAVELENGTH VALIDATION ==========")

for i in range(len(wavelengths_nm)):

    print(
        f"lambda = {wavelengths_nm[i]:.1f} nm"
        f" | calculated = {frequencies_hz[i] / 1e12:.6f} THz"
        f" | theoretical = {theoretical_frequencies[i] / 1e12:.6f} THz"
        f" | error = {error[i]:.3e} Hz"
    )

plt.figure(figsize=(9, 5))

plt.plot(
    wavelengths_nm,
    frequencies_hz / 1e12,
    "o-"
)

plt.xlabel("Wavelength (nm)")
plt.ylabel("Optical frequency (THz)")
plt.title("CW Laser Optical Frequency vs Wavelength")

plt.grid()
plt.tight_layout()
plt.show()