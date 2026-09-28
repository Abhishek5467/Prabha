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

voltages_ideal = np.array([
    0.00,
    0.05,
    0.10,
    0.20,
    0.37,
    0.50,
    0.63,
    0.90,
    1.00
])

codes, voltages_actual = dac.quantize(voltages_ideal)

errors = voltages_actual - voltages_ideal

print("========== DAC Quantization Validation ==========")
print()

print("Parameters")
print("----------------------------------------")
print(f"Resolution          : {bits} bits")
print(f"Number of codes     : {dac.n_codes}")
print(f"Voltage range       : {V_min:.6f} → {V_max:.6f} V")
print(f"LSB                 : {dac.lsb:.9f} V")
print()

print("Ideal Voltage → Code → DAC Voltage")
print("----------------------------------------")

for v_ideal, code, v_actual, error in zip(
    voltages_ideal,
    codes,
    voltages_actual,
    errors
):
    print(
        f"{v_ideal:.6f} V"
        f" → Code {code:2d}"
        f" → {v_actual:.9f} V"
        f" → error {error:+.9f} V"
    )

print()

print("Validation")
print("----------------------------------------")
print(f"Maximum absolute error : {np.max(np.abs(errors)):.9f} V")
print(f"RMS quantization error : {np.sqrt(np.mean(errors**2)):.9f} V")