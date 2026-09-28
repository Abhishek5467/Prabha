import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.photonic_mac import PhotonicMAC

x = np.array([0.9,0.3,0.7,0.5])
w = np.array([0.8,-0.6,0.4,-0.9])

P0_values_mW = [0.1,1.0,10.0]

expected = np.dot(x,w)

print()
print("Ideal PHOTONIC MAC Validation")
expected = np.dot(x, w)

print()
print("========== IDEAL PHOTONIC MAC VALIDATION ==========")

print()
print("Input vector:")
print(x)

print()
print("Weight vector:")
print(w)

print()
print("Expected mathematical MAC")
print(f"y = {expected:.12f}")


mac = PhotonicMAC(P0_mW=1.0)

w_plus, w_minus = mac.split_weights(w)

print()
print("Positive weights:")
print(w_plus)

print()
print("Negative weights:")
print(w_minus)

print()
print("Weight reconstruction:")
print(w_plus - w_minus)


results = []


for P0_mW in P0_values_mW:
    
    mac = PhotonicMAC(P0_mW=P0_mW)
    
    result = mac.compute(x,w)
    results.append(result)
    
    print()
    print("----------====------------")
    print("-------====---------------")
    print("------====---------------")
    print("-------====---------------")
    print("----------====------------")
    
    print()
    print("Input optical powers [mW]:")
    print(result["P_in"]*1e3)
    
    print()
    print("Positive branch P+ = "f"{result['P_plus']*1e3:.9f} mW")
    print("Negative branch P- = "f"{result['P_minus']*1e3:.9f} mW")
    print("Differential output P_diff = "f"{result['P_diff']*1e3:.9f} mW")
    
    print()
    print(f"Mathematical MAC = "f"{result['mac']:.12f}")
    print(f"Recovered MAC = "f"{result['mac_recovered']:.12f}")
    
    error = abs(result['mac_recovered']-expected)
    
    print(f"MAC error = {error:.6e}")
    
    
P0_plot = 1.0

mac = PhotonicMAC(P0_mW=P0_plot)
result=mac.compute(x,w)

indices = np.arange(len(x))

plt.figure(figsize=(10,6))

plt.bar(
    indices-0.15,
    result["P_plus_channels"]*1e3,
    width=0.3,
    label="Positive contribution",
)

plt.bar(
    indices+0.15,
    result["P_minus_channels"]*1e3,
    width=0.3,
    label="Negative contribution",
)

plt.xlabel("MAC channel i")
plt.ylabel("Optical power (mW)")
plt.title(f"Ideal Photonic MAC: Differential Contributions")

plt.xticks(indices)

plt.legend()
plt.grid(axis="y")

plt.tight_layout()
plt.show()

P0_axis = []
Pdiff_axis = []
mac_axis = []

for result in results:
    P0_axis.append(result["x"].size*0+1)

for P0_mW in P0_values_mW:
    
    mac = PhotonicMAC(P0_mW=P0_mW)
    result = mac.compute(x,w)
    
    Pdiff_axis.append(result["P_diff"]*1e3)
    
    mac_axis.append(result["mac_recovered"])
    
plt.figure(figsize=(8,5))

plt.plot(P0_values_mW, Pdiff_axis, "o-")

plt.xlabel("Laser power P0 [mW]")
plt.ylabel("Differential optical output (mW)")
plt.title("Ideal Photonic MAC Validation: Differential Output vs Laser Power")

plt.grid()

plt.tight_layout()
plt.show()

all_correct = True

for value in mac_axis:
    if not np.isclose(value, expected, rtol=1e-6):
        all_correct = False

print()
print("=== Ideal Photonic MAC Validation Summary ===")

print(f"Expected MAC: {expected:.12f}")
print(f"ALL recovered MACs = {mac_axis}")

print()
print(
    "PASS: Optical MAC reproduces mathematical MAC."
    if all_correct
    else
    "FAIL: Optical MAC does not reproduce mathematical MAC."
) 

print()