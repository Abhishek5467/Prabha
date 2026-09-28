import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

C = 299_792_458.0

P0_mW = 1.0
wavelength_nm = 1550.0

fs = 160e9
duration = 10e-9

linewidth_hz = 1e6
phase0 = 0.0

seed = 1


P0 = P0_mW * 1e-3
wavelength = wavelength_nm * 1e-9

f0 = C / wavelength

Ts = 1.0 / fs

n_samples = int(fs * duration)

t = np.arange(n_samples) * Ts

sigma_phi = np.sqrt(2.0*np.pi*linewidth_hz*Ts)

rng = np.random.default_rng(seed=seed)

delta_phi = rng.normal(loc=0.0, scale=sigma_phi, size=n_samples)

phase = phase0 + np.cumsum(delta_phi)


E = np.sqrt(P0)*np.exp(1j*phase)

P = np.abs(E)**2

phase_variance = np.var(phase)

power_mean = np.mean(P)
power_std = np.std(P)

print("========== CW LASER LINEWIDTH TEST ==========")

print(f"P0              = {P0:.6e} W")
print(f"wavelength      = {wavelength:.6e} m")
print(f"f0              = {f0:.6e} Hz")

print(f"fs              = {fs:.6e} Hz")
print(f"Ts              = {Ts:.6e} s")
print(f"duration        = {duration:.6e} s")
print(f"samples         = {n_samples}")

print(f"linewidth       = {linewidth_hz:.6e} Hz")

print(f"sigma_phi       = {sigma_phi:.6e} rad")

print()
print(f"Mean power      = {power_mean:.12e} W")
print(f"Std power       = {power_std:.12e} W")
print(f"Phase variance  = {phase_variance:.6e} rad^2")


theoritical_variance = (
    2.0*np.pi*linewidth_hz*duration
)

print(
    f"Theoretical phase variance = {theoritical_variance:.6e} rad^2"
)

plt.figure()

plt.plot(
    t*1e9,
    phase
)

plt.xlabel("Time (ns)")
plt.ylabel("Phase (rad)")
plt.title("CW Laser Phase vs Time")

plt.grid()

plt.show()