import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from prabha.blocks.photodetector import Photodetector


print(
    "========== "
    "Photodetector Dark-Current Validation "
    "=========="
)



# PARAMETERS

responsivity = 1.0

dark_current_A = 5e-9


pd = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=dark_current_A
)


# TEST POWERS

P_mW = np.array([
    0.0,
    0.1,
    0.5,
    1.0,
    2.0,
    5.0
])

P_W = (
    P_mW
    *
    1e-3
)


# DETECT

I_out = pd.detect(
    P_W,
    include_dark_current=True,
    include_shot_noise=False
)


# THEORY

I_expected = (
    responsivity
    *
    P_W
    +
    dark_current_A
)


error = (
    I_out
    -
    I_expected
)


max_error = np.max(
    np.abs(error)
)


# OUTPUT
print()

print(
    f"Responsivity : "
    f"{responsivity:.6f} A/W"
)

print(
    f"Dark current : "
    f"{dark_current_A:.6e} A"
)

print()

print(
    "P[mW]      Expected I[A]       "
    "Measured I[A]       Error[A]"
)

print("-" * 70)


for p, expected, measured, err in zip(
    P_mW,
    I_expected,
    I_out,
    error
):

    print(
        f"{p:6.3f}   "
        f"{expected: .12e}   "
        f"{measured: .12e}   "
        f"{err: .3e}"
    )


print()

print(
    f"Maximum error : "
    f"{max_error:.12e} A"
)


assert max_error < 1e-15


print()

print(
    "PASS: Photodetector dark-current "
    "model validated."
)