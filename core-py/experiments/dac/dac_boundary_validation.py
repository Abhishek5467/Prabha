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
    V_max=V_max
)

eps = 1e-12

print("========== DAC Boundary Validation ==========")
print()

print("Parameters")
print("----------------------------------------")
print(f"Resolution          : {bits} bits")
print(f"Number of codes     : {dac.n_codes}")
print(f"Voltage range       : {V_min:.6f} → {V_max:.6f} V")
print(f"LSB                 : {dac.lsb:.9f} V")
print()

boundary_voltages = np.array([
    V_min,
    V_max
])

codes, voltages = dac.quantize(boundary_voltages)

print("1. Exact Boundaries")
print("----------------------------------------")

for v, code, v_actual in zip(
    boundary_voltages,
    codes,
    voltages
):
    print(
        f"{v:.12f} V"
        f" → Code {code}"
        f" → {v_actual:.12f} V"
    )

assert codes[0] == 0
assert codes[1] == dac.max_code

assert np.isclose(voltages[0], V_min)
assert np.isclose(voltages[1], V_max)

print("PASS")
print()

inside_voltages = np.array([
    V_min + eps,
    V_max - eps
])

codes, voltages = dac.quantize(inside_voltages)

print("2. Just Inside Boundaries")
print("----------------------------------------")

for v, code, v_actual in zip(
    inside_voltages,
    codes,
    voltages
):
    print(
        f"{v:.12f} V"
        f" → Code {code}"
        f" → {v_actual:.12f} V"
    )

assert codes[0] == 0
assert codes[1] == dac.max_code

print("PASS")
print()

print("3. Outside Boundaries")
print("----------------------------------------")

outside_voltages = [
    V_min - eps,
    V_max + eps
]

for voltage in outside_voltages:
    try:
        dac.quantize(voltage)
        print(
            f"{voltage:.12f} V → ERROR: "
            f"accepted invalid voltage"
        )
        raise AssertionError(
            "DAC accepted voltage outside range."
        )

    except ValueError:
        print(
            f"{voltage:.12f} V → correctly rejected"
        )

print("PASS")
print()

print("4. Midpoints Between DAC Levels")
print("----------------------------------------")

for code in range(dac.max_code):
    v1 = dac.code_to_voltage(code)
    v2 = dac.code_to_voltage(code + 1)

    midpoint = (v1 + v2) / 2.0

    quantized_code = dac.voltage_to_code(midpoint)

    print(
        f"Between Code {code} and {code + 1}"
        f" → midpoint {midpoint:.12f} V"
        f" → selected Code {quantized_code}"
    )

print()

print("5. Code Range Verification")
print("----------------------------------------")

codes = np.arange(dac.n_codes)
voltages = dac.code_to_voltage(codes)
recovered_codes = dac.voltage_to_code(voltages)

assert np.array_equal(codes, recovered_codes)

print(f"Minimum code        : {np.min(recovered_codes)}")
print(f"Maximum code        : {np.max(recovered_codes)}")
print("All codes recovered exactly.")
print("PASS")
print()

print("========== Validation Complete ==========")