import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector


P0_mW = 1.0

fs = 160e9
duration = 1e-9

wavelength_nm = 1550.0

V_pi = 1.0
phi_bias = np.pi / 2
V = 0.1

responsivity = 1.0

laser = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=wavelength_nm,
    fs=fs,
    duration=duration,
    rin_db_hz=-150.0,
    linewidth_hz=0.0,
    seed=1,
)

t, E = laser.generate(
    include_rin=False,
    include_linewidth=False,
)

P_laser = np.abs(E)**2

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
    insertion_loss_dB=0.0,
)

P_mzm = mzm.modulate(
    P_laser,
    V,
)

pd = Photodetector(responsivity_A_per_W=responsivity)

I_ph = pd.detect(P_mzm)

T_expected = np.cos(
    np.pi*V/(2*V_pi)+phi_bias/2.0
)**2

P_expected=(P0_mW*1e-3*T_expected)

I_expected=(responsivity*P_expected)

max_power_error = np.max(np.abs(P_mzm-P_expected))

max_current_error = np.max(np.abs(I_ph-I_expected))

print("========== Laser → MZM → Photodetector ==========")

print(f"Laser power             : {P0_mW:.6f} mW")
print(f"Laser wavelength        : {wavelength_nm:.1f} nm")
print(f"MZM voltage             : {V:.6f} V")
print(f"MZM transmission        : {T_expected:.6f}")
print(f"Photodetector response  : {responsivity:.6f} A/W")

print()

print(
    f"Mean laser power        : "
    f"{np.mean(P_laser) * 1e3:.6f} mW"
)

print(
    f"Mean MZM output         : "
    f"{np.mean(P_mzm) * 1e3:.6f} mW"
)

print(
    f"Expected MZM output     : "
    f"{P_expected * 1e3:.6f} mW"
)

print()

print(
    f"Mean photocurrent       : "
    f"{np.mean(I_ph) * 1e3:.6f} mA"
)

print(
    f"Expected photocurrent   : "
    f"{I_expected * 1e3:.6f} mA"
)

print()

print(
    f"Maximum power error     : "
    f"{max_power_error:.6e} W"
)

print(
    f"Maximum current error   : "
    f"{max_current_error:.6e} A"
)


plt.figure()

plt.plot(
    t*1e12,
    P_mzm*1e3,
    label="MZM Output"
)

plt.xlabel("Time [ps]")
plt.ylabel("Optical Power [mW]")
plt.title("Laser -> MZM")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

plt.figure()

plt.plot(t*1e12, I_ph*1e3)

plt.xlabel("Time [ps]")
plt.ylabel("Photocurrent [mA]")
plt.title("Photodetector Output")

plt.grid(True)
plt.tight_layout()

plt.show()