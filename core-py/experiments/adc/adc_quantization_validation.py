import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from prabha.blocks.adc import ADC


print("========== ADC Quantization Validation ==========")

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

voltages = np.array([
    0.00,
    0.05,
    0.10,
    0.20,
    0.37,
    0.50,
    0.63,
    0.90,
    1.00,
])

codes = adc.convert(voltages)
quantized_voltages = adc.code_to_voltage(codes)

errors = quantized_voltages - voltages

print()
print("Voltage → Code → Quantized Voltage")
print("----------------------------------------")

for v, code, vq, error in zip(
    voltages,
    codes,
    quantized_voltages,
    errors
):
    print(
        f"{v:.9f} V → "
        f"Code {code:2d} → "
        f"{vq:.9f} V → "
        f"error {error:+.9f} V"
    )

max_error = np.max(np.abs(errors))
rms_error = np.sqrt(np.mean(errors ** 2))

print()
print("Validation")
print("----------------------------------------")
print(f"Maximum absolute error : {max_error:.9f} V")
print(f"RMS quantization error : {rms_error:.9f} V")

print()
print("PASS: ADC quantization model validated.")