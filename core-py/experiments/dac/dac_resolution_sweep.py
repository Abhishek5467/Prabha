import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.dac import DAC
from prabha.blocks.mzm import MachZehnderModulator

P_in_mW = 1.0

V_pi = 1.0
phi_bias = np.pi / 2

V_min = -0.5
V_max = 0.5

bit_values = [3, 4, 6, 8, 10, 12]

x = np.linspace(-1.0, 1.0, 10001)


mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)


T_target = 0.5 - 0.5 * x

theta = np.arccos(np.sqrt(T_target))

V_ideal = (
    2.0 * V_pi / np.pi
    * (theta - phi_bias / 2.0)
)

T_ideal = mzm.transfer(V_ideal)

P_ideal = P_in_mW * T_ideal


results = []

print("========== DAC RESOLUTION SWEEP ==========")
print()

print("Parameters")
print("----------------------------------------")
print(f"Input optical power : {P_in_mW:.6f} mW")
print(f"MZM V_pi            : {V_pi:.6f} V")
print(f"MZM bias            : {phi_bias:.6f} rad")
print(f"DAC voltage range   : {V_min:.6f} → {V_max:.6f} V")
print(f"Input samples       : {len(x)}")
print()

print(
    "Bits   Codes    LSB [V]       "
    "Max V err [V]   RMS V err [V]   "
    "Max T err       RMS T err       "
    "Max P err [mW]  RMS P err [mW]"
)

print("-" * 125)


for bits in bit_values:

    dac = DAC(
        bits=bits,
        V_min=V_min,
        V_max=V_max
    )

    codes, V_actual = dac.quantize(V_ideal)

    T_actual = mzm.transfer(V_actual)

    P_actual = P_in_mW * T_actual

    voltage_error = V_actual - V_ideal
    transmission_error = T_actual - T_ideal
    power_error = P_actual - P_ideal

    max_v_error = np.max(np.abs(voltage_error))
    rms_v_error = np.sqrt(
        np.mean(voltage_error ** 2)
    )

    max_t_error = np.max(
        np.abs(transmission_error)
    )

    rms_t_error = np.sqrt(
        np.mean(transmission_error ** 2)
    )

    max_p_error = np.max(
        np.abs(power_error)
    )

    rms_p_error = np.sqrt(
        np.mean(power_error ** 2)
    )

    results.append({
        "bits": bits,
        "codes": dac.n_codes,
        "lsb": dac.lsb,
        "max_v_error": max_v_error,
        "rms_v_error": rms_v_error,
        "max_t_error": max_t_error,
        "rms_t_error": rms_t_error,
        "max_p_error": max_p_error,
        "rms_p_error": rms_p_error,
    })

    print(
        f"{bits:4d}   "
        f"{dac.n_codes:5d}   "
        f"{dac.lsb:.9e}   "
        f"{max_v_error:.9e}   "
        f"{rms_v_error:.9e}   "
        f"{max_t_error:.9e}   "
        f"{rms_t_error:.9e}   "
        f"{max_p_error:.9e}   "
        f"{rms_p_error:.9e}"
    )



print()
print("Validation")
print("----------------------------------------")

lsbs = np.array([r["lsb"] for r in results])
rms_voltage = np.array(
    [r["rms_v_error"] for r in results]
)
rms_transmission = np.array(
    [r["rms_t_error"] for r in results]
)
rms_power = np.array(
    [r["rms_p_error"] for r in results]
)

assert np.all(np.diff(lsbs) < 0)
assert np.all(np.diff(rms_voltage) < 0)
assert np.all(np.diff(rms_transmission) < 0)
assert np.all(np.diff(rms_power) < 0)

print("LSB decreases with resolution       : PASS")
print("Voltage quantization error decreases: PASS")
print("MZM transmission error decreases    : PASS")
print("Optical power error decreases       : PASS")

print()
print("========== Sweep Complete ==========")