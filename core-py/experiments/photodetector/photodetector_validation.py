import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.photodetector import Photodetector

responsivity = 1.0       

P_mW = np.array([
    0.0,
    0.1,
    0.5,
    1.0,
    2.0,
    5.0,
])


P_W = P_mW * 1e-3


pd = Photodetector(
    responsivity_A_per_W=responsivity
)


I_A = pd.detect(P_W)

I_mA = I_A * 1e3



I_expected_A = responsivity * P_W


error = np.abs(I_A - I_expected_A)

max_error = np.max(error)


print("========== Photodetector Validation ==========")

print(f"Responsivity : {responsivity:.6f} A/W")
print()

for p, i, expected in zip(
    P_mW,
    I_mA,
    I_expected_A * 1e3
):
    print(
        f"P = {p:.3f} mW"
        f" -> I = {i:.6f} mA"
        f" -> expected = {expected:.6f} mA"
    )

print()
print(f"Maximum error : {max_error:.6e} A")