from pathlib import Path
import sys

Root = Path(__file__).resolve().parents[2]
sys.path.append(str(Root))

import numpy as np

from prabha.blocks.adc import ADC


print("========== ADC Boundary Validation ==========")

adc = ADC(
    resolution_bits=3,
    v_min=0.0,
    v_max=1.0
)

print()
print("Parameters")
print("----------------------------------------")
print(f"Resolution          : {adc.resolution_bits} bits")
print(f"Number of codes     : {adc.n_codes}")
print(f"Voltage range       : {adc.v_min:.6f} → {adc.v_max:.6f} V")
print(f"LSB                 : {adc.lsb:.9f} V")


print()
print("1. Exact Boundaries")
print("----------------------------------------")

code_min = adc.convert(adc.v_min)
code_max = adc.convert(adc.v_max)

print(
    f"{adc.v_min:.12f} V → Code {code_min}"
)

print(
    f"{adc.v_max:.12f} V → Code {code_max}"
)

assert code_min == 0
assert code_max == adc.n_codes - 1

print("PASS")


print()
print("2. Just Inside Boundaries")
print("----------------------------------------")

eps = 1e-12

low_inside = adc.v_min + eps
high_inside = adc.v_max - eps

code_low = adc.convert(low_inside)
code_high = adc.convert(high_inside)

print(
    f"{low_inside:.12f} V → Code {code_low}"
)

print(
    f"{high_inside:.12f} V → Code {code_high}"
)

assert code_low == 0
assert code_high == adc.n_codes - 1

print("PASS")


print()
print("3. Outside Boundaries")
print("----------------------------------------")

try:
    adc.convert(adc.v_min - eps)
    raise AssertionError("Below-range voltage was not rejected.")
except ValueError:
    print(
        f"{adc.v_min - eps:.12f} V → correctly rejected"
    )

try:
    adc.convert(adc.v_max + eps)
    raise AssertionError("Above-range voltage was not rejected.")
except ValueError:
    print(
        f"{adc.v_max + eps:.12f} V → correctly rejected"
    )

print("PASS")


print()
print("4. Midpoints Between ADC Levels")
print("----------------------------------------")

for code in range(adc.n_codes - 1):

    v1 = adc.code_to_voltage(code)
    v2 = adc.code_to_voltage(code + 1)

    midpoint = (v1 + v2) / 2.0

    selected_code = adc.convert(midpoint)

    print(
        f"Between Code {code} and {code + 1}"
        f" → midpoint {midpoint:.12f} V"
        f" → selected Code {selected_code}"
    )


print()
print("5. Code Range Verification")
print("----------------------------------------")

test_voltages = np.linspace(
    adc.v_min,
    adc.v_max,
    10001
)

codes = adc.convert(test_voltages)

print(f"Minimum code        : {np.min(codes)}")
print(f"Maximum code        : {np.max(codes)}")

assert np.min(codes) == 0
assert np.max(codes) == adc.n_codes - 1

print("All codes remain within valid ADC range.")
print("PASS")


print()
print("========== Validation Complete ==========")