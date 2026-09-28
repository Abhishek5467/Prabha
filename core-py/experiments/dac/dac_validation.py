import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.dac import DAC

bits = 3

V_min = 0.0
V_max = 1.0

dac = DAC(
    bits=bits,
    V_min=V_min,
    V_max=V_max,
)

n_codes = 2 ** bits

max_code = n_codes - 1

lsb_theory = (
    (V_max - V_min)
    / max_code
)

codes = np.arange(
    0,
    n_codes
)

voltages = dac.code_to_voltage(codes)

expected = (
    V_min
    + codes * lsb_theory
)

error = np.abs(
    voltages - expected
)

max_error = np.max(error)

print("========== DAC Validation ==========")

print()
print("Parameters")
print("----------------------------------------")

print(f"Resolution          : {bits} bits")
print(f"Number of codes     : {n_codes}")
print(f"Voltage range       : {V_min:.6f} → {V_max:.6f} V")
print(f"LSB                 : {lsb_theory:.9f} V")

print()
print("Code → Voltage")
print("----------------------------------------")

for code, voltage, exp in zip(
    codes,
    voltages,
    expected
):
    print(
        f"Code {code:2d}"
        f" → {voltage:.9f} V"
        f" → expected {exp:.9f} V"
    )

print()
print("Validation")
print("----------------------------------------")

print(
    f"Maximum error       : "
    f"{max_error:.6e} V"
)
