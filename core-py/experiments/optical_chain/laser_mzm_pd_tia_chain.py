import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA


print("========== Laser → MZM → Photodetector → TIA ==========")


P0_mW = 1.0
wavelength_nm = 1550.0

V = 0.1
V_pi = 1.0
phi_bias = np.pi / 2

responsivity = 1.0       
R_f = 1000.0             


laser = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=wavelength_nm,
    fs=1e9,
    duration=1e-9,
    rin_db_hz=-150.0,
    linewidth_hz=0.0,
    seed=1,
)

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
    insertion_loss_dB=0.0,
)

pd = Photodetector(
    responsivity_A_per_W=responsivity,
)

tia = TIA(
    R_f=R_f,
)


t, E_laser = laser.generate(
    include_rin=False,
    include_linewidth=False,
)

P_laser = laser.power(E_laser)

mean_laser_power = np.mean(P_laser)


P_mzm = mzm.modulate(
    P_laser,
    V,
)

mean_mzm_power = np.mean(P_mzm)

T = mzm.transfer(V)

expected_mzm_power = P0_mW * 1e-3 * T


I_pd = pd.detect(P_mzm)

mean_current = np.mean(I_pd)

expected_current = expected_mzm_power * responsivity


V_tia = tia.amplify(I_pd)

mean_tia_voltage = np.mean(V_tia)

expected_tia_voltage = expected_current * R_f


power_error = np.max(
    np.abs(P_mzm - expected_mzm_power)
)

current_error = np.max(
    np.abs(I_pd - expected_current)
)

voltage_error = np.max(
    np.abs(V_tia - expected_tia_voltage)
)


print()
print("System parameters")
print("----------------------------------------")
print(f"Laser power             : {P0_mW:.6f} mW")
print(f"Laser wavelength        : {wavelength_nm:.1f} nm")
print(f"MZM voltage             : {V:.6f} V")
print(f"MZM V_pi                : {V_pi:.6f} V")
print(f"MZM bias phase          : {phi_bias:.6f} rad")
print(f"MZM transmission        : {T:.6f}")
print(f"Photodetector response  : {responsivity:.6f} A/W")
print(f"TIA transimpedance      : {R_f:.6f} Ohm")


print()
print("Laser")
print("----------------------------------------")
print(f"Mean laser power        : {mean_laser_power * 1e3:.6f} mW")


print()
print("MZM")
print("----------------------------------------")
print(f"Mean MZM output         : {mean_mzm_power * 1e3:.6f} mW")
print(f"Expected MZM output     : {expected_mzm_power * 1e3:.6f} mW")


print()
print("Photodetector")
print("----------------------------------------")
print(f"Mean photocurrent       : {mean_current * 1e3:.6f} mA")
print(f"Expected photocurrent   : {expected_current * 1e3:.6f} mA")


print()
print("TIA")
print("----------------------------------------")
print(f"Mean TIA output         : {mean_tia_voltage:.6f} V")
print(f"Expected TIA output     : {expected_tia_voltage:.6f} V")


print()
print("Validation")
print("----------------------------------------")
print(f"Maximum power error     : {power_error:.6e} W")
print(f"Maximum current error   : {current_error:.6e} A")
print(f"Maximum voltage error   : {voltage_error:.6e} V")


all_correct = (
    np.isclose(power_error, 0.0)
    and np.isclose(current_error, 0.0)
    and np.isclose(voltage_error, 0.0)
)

print()

if all_correct:
    print("PASS: Complete optical receiver chain validated.")
else:
    print("FAIL: Optical receiver chain validation failed.")

print()