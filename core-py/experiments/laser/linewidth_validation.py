import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PATH = Path(__file__).resolve().parents[2]
sys.path.append(str(PATH))

from prabha.blocks.cw_laser import CWLaser

P0_mW = 1.0
wavelength_nm = 1550.0
fs = 160e9
duration = 10e-9
linewidth_hz = 1e6
phase0 = 0.0

n_realizations = 1000

n_samples = int(fs*duration)
t=np.arange(n_samples)/fs

phase = np.zeros((n_realizations, n_samples))

for k in range(n_realizations):
    
    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=wavelength_nm,
        fs=fs,
        duration=duration,
        linewidth_hz=linewidth_hz,
        phase0=phase0,
        seed=k+1,
    )
    
    _, E = laser.generate(
        include_linewidth=True
    )
    
    phase[k,:]=np.unwrap(np.angle(E)) # it reconstructs the phase from the complex field E, and unwraps it to avoid discontinuities.
    
measured_variance = np.var(
    phase, axis=0
)

theoretical_variance = (
    2.0*np.pi*linewidth_hz*t
)

measured_final = measured_variance[-1]
theoretical_final = theoretical_variance[-1]

relative_error = (
    abs(measured_final - theoretical_final)/theoretical_final
)

slope, intercept = np.polyfit(
    t,
    measured_variance,
    1
)

measured_linewidth = slope/(2.0*np.pi)

theoretical_slope = (
    2.0*np.pi*linewidth_hz
)

slope_error = (
    abs(slope-theoretical_slope)/theoretical_slope
)

print()
print("Phase diffusion slope")
print(f"Measured slope      = {slope:.6e} rad^2/s")
print(f"Theoretical slope   = {theoretical_slope:.6e} rad^2/s")

print()
print("Recovered linewidth")
print(f"Measured linewidth  = {measured_linewidth:.6e} Hz")
print(f"Input linewidth     = {linewidth_hz:.6e} Hz")
print(f"Slope relative error = {slope_error * 100:.3f} %")

print()
print("========== LINEWIDTH ENSEMBLE VALIDATION ==========")

print(f"P0              = {P0_mW:.6f} mW")
print(f"wavelength      = {wavelength_nm:.2f} nm")
print(f"fs              = {fs:.6e} Hz")
print(f"duration        = {duration:.6e} s")
print(f"samples         = {n_samples}")
print(f"linewidth       = {linewidth_hz:.6e} Hz")
print(f"realizations    = {n_realizations}")

print()
print("Final-time phase variance")
print(f"Measured        = {measured_final:.6e} rad^2")
print(f"Theoretical     = {theoretical_final:.6e} rad^2")
print(f"Relative error  = {relative_error * 100:.3f} %")

plt.figure(figsize=(9,5))

plt.plot(
    t*1e9,
    measured_variance,
    label="Measured ensemble variance"
)

plt.plot(
    t*1e9,
    theoretical_variance,
    "--",
    label=r"Theoretical $2\pi\Delta\nu t$"
)

plt.xlabel("Time (ns)")
plt.ylabel("Phase variance (rad$^2$)")

plt.title("CW Laser Phase Variance: Linewidth validation")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
