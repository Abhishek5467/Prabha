import sys
from pathlib import Path

Root = Path(__file__).resolve().parents[2]
sys.path.append(str(Root))

import numpy as np

from prabha.blocks.adc import ADC


print("========== ADC RESOLUTION SWEEP ==========")

v_min = 0.0
v_max = 1.0

# Dense voltage sweep
voltages = np.linspace(v_min, v_max, 10001)

resolutions = [3, 4, 6, 8, 10, 12]

print()
print("Parameters")
print("----------------------------------------")
print(f"Voltage range       : {v_min:.6f} → {v_max:.6f} V")
print(f"Input samples       : {len(voltages)}")

print()
print(
    "Bits   Codes    LSB [V]       "
    "Max V err [V]   RMS V err [V]"
)
print("-" * 85)

results = []

for bits in resolutions:

    adc = ADC(
        resolution_bits=bits,
        v_min=v_min,
        v_max=v_max
    )

    codes = adc.convert(voltages)

    quantized_voltages = adc.code_to_voltage(codes)

    errors = quantized_voltages - voltages

    max_error = np.max(np.abs(errors))
    rms_error = np.sqrt(np.mean(errors ** 2))

    results.append({
        "bits": bits,
        "codes": adc.n_codes,
        "lsb": adc.lsb,
        "max_error": max_error,
        "rms_error": rms_error
    })

    print(
        f"{bits:4d} "
        f"{adc.n_codes:8d} "
        f"{adc.lsb: .9e} "
        f"{max_error: .9e} "
        f"{rms_error: .9e}"
    )


print()
print("Validation")
print("----------------------------------------")

lsbs = np.array([r["lsb"] for r in results])
max_errors = np.array([r["max_error"] for r in results])
rms_errors = np.array([r["rms_error"] for r in results])

lsb_decreases = np.all(np.diff(lsbs) < 0)
max_error_decreases = np.all(np.diff(max_errors) < 0)
rms_error_decreases = np.all(np.diff(rms_errors) < 0)

print(
    f"LSB decreases with resolution       : "
    f"{'PASS' if lsb_decreases else 'FAIL'}"
)

print(
    f"Maximum quantization error decreases: "
    f"{'PASS' if max_error_decreases else 'FAIL'}"
)

print(
    f"RMS quantization error decreases    : "
    f"{'PASS' if rms_error_decreases else 'FAIL'}"
)

assert lsb_decreases
assert max_error_decreases
assert rms_error_decreases

print()
print("========== Sweep Complete ==========")