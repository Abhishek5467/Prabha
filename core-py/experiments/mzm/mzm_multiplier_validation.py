import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.mzm import MachZehnderModulator as MZM

P0_mW=1.0
V_pi=1.0
bias_phase=np.pi/2

V_scale = 0.10

x=np.linspace(-1.0,1.0,201)

V = V_scale*x

mzm = MZM(V_pi=V_pi, phi_bias=bias_phase,)

T = mzm.transfer(V)

P_out = P0_mW*T

center = len(x)//2

slope = np.polyfit(V,P_out,1)[0]
intercept = np.polyfit(V,P_out,1)[1]

P_linear = slope*V+intercept

error = P_out - P_linear

max_error = np.max(np.abs(error))
rms_error = np.sqrt(np.mean(error**2))

relative_error=(max_error/P0_mW)*100.0

print()
print("+++++ MZM PHOTONIC MULTIPLIER VALIDATION +++++")

print()
print(f"Input power = {P0_mW:.6f} mW")
print(f"V_pi = {V_pi:.6f} V")
print(f"Bias phase = {bias_phase:.6f} rad")
print(f"Input range = [{x.min():.2f}, {x.max():.2f}]")
print(f"Voltage range = [{V.min():.3f}, {V.max():.3f}] V")

print()
print("MZM response")

print(f"Slope = {slope:.6e} mW/V")
print(f"Intercept = {intercept:.6e} mW")

print()
print("Linearity error")

print(f"Maximum error = {max_error:.6e} mW")
print(f"RMS error = {rms_error:.6e} mW")
print(f"Relative max error = {relative_error:.6f} %")

print()
print("++++ SAMPLE INPUTS ++++")

sample_x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])

sample_V = V_scale*sample_x
sample_T = mzm.transfer(sample_V)
sample_P = P0_mW*sample_T

for xi, vi, ti, pi in zip(
    sample_x,
    sample_V,
    sample_T,
    sample_P,
):
    
    print(
        f"x = {xi:.2f} | "
        f"V = {vi: .4f} V | "
        f"T = {ti:.6f} | "
        f"P_out = {pi:.6f} mW"
    )
    
plt.figure(figsize=(9,5))

plt.plot(x,P_out,label="MZM optical output",)

plt.plot(x,P_linear,"--",label="Linear approximation",)

plt.xlabel("Normalized input x")
plt.ylabel("Output optical power (mW)")
plt.title("MZM-Based Photonic Input Encoding")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))

plt.plot(x,P_out,)

plt.xlabel("Normalized input x")
plt.ylabel("Output optical power (mW)")
plt.title("Photonic Encoding: x -> MZM -> Optical Power")

plt.grid()

plt.tight_layout()
plt.show()