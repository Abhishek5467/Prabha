import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from prabha.blocks.adc import ADC


adc = ADC(
    resolution_bits=3,
    v_min=0.0,
    v_max=1.0,
)

print("========== ADC Validation ==========\n")

print("Parameters")
print("----------------------------------------")
print(f"Resolution          : {adc.resolution_bits} bits")
print(f"Number of codes     : {adc.n_codes}")
print(
    f"Voltage range       : "
    f"{adc.v_min:.6f} → {adc.v_max:.6f} V"
)
print(f"LSB                 : {adc.lsb:.9f} V")

print("\nVoltage → Code")
print("----------------------------------------")

voltages = np.array([
    0.0,
    adc.lsb,
    2 * adc.lsb,
    3 * adc.lsb,
    4 * adc.lsb,
    5 * adc.lsb,
    6 * adc.lsb,
    1.0,
])

expected_codes = np.arange(adc.n_codes)

codes = adc.convert(voltages)

for V, code, expected in zip(
    voltages,
    codes,
    expected_codes,
):
    print(
        f"{V:.9f} V → "
        f"Code {code:2d} → "
        f"expected {expected:2d}"
    )

max_error = np.max(
    np.abs(codes - expected_codes)
)

print("\nValidation")
print("----------------------------------------")
print(
    f"Maximum code error : "
    f"{max_error:.6e}"
)

if max_error == 0:
    print("PASS")
else:
    print("FAIL")