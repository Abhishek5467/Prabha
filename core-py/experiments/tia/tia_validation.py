import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.tia import TIA


print("========== TIA Validation ==========")

R_f = 1000.0

tia = TIA(R_f=R_f)

currents_mA = np.array([
    0.0,
    0.1,
    0.5,
    1.0,
    2.0,
    5.0,
])


print()
print("Parameters")
print("----------------------------------------")
print(f"Transimpedance gain : {R_f:.6f} Ohm")


print()
print("Current → Voltage")
print("----------------------------------------")

max_error = 0.0

for I_mA in currents_mA:

    I_A = I_mA * 1e-3

    V_out = tia.amplify(I_A)

    expected = I_A * R_f

    error = abs(V_out - expected)

    max_error = max(max_error, error)

    print(
        f"I = {I_mA:.3f} mA"
        f" → V_out = {V_out:.9f} V"
        f" → expected = {expected:.9f} V"
    )


print()
print("Validation")
print("----------------------------------------")
print(f"Maximum error : {max_error:.6e} V")

if np.isclose(max_error, 0.0):
    print("PASS")
else:
    print("FAIL")