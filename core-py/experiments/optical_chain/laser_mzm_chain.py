import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator


P0_mW = 1.0
fs = 160e9
duration = 1e-9

V_pi = 1.0
phi_bias = np.pi / 2

V = 0.1


laser = CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=1550.0,
    fs=fs,
    duration=duration,
    rin_db_hz=-150.0,
    linewidth_hz=0.0,
    seed=1,
)

t, E = laser.generate(include_rin=False, include_linewidth=False)

P_in = np.abs(E)**2

mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
    insertion_loss_dB=0.0,
)

P_out = mzm.modulate(P_in,V)

T = mzm.transfer(V)

expected_P_out = P_in*T

max_error = np.max(np.abs(P_out-expected_P_out))

print("========== Laser → MZM ==========")

print(f"Laser power          : {P0_mW:.6f} mW")
print(f"Mean input power     : {np.mean(P_in) * 1e3:.6f} mW")
print(f"MZM voltage          : {V:.6f} V")
print(f"MZM transmission     : {T:.6f}")
print(f"Mean output power    : {np.mean(P_out) * 1e3:.6f} mW")
print(f"Expected output      : {np.mean(P_in) * T * 1e3:.6f} mW")
print(f"Maximum error        : {max_error:.6e} W")

plt.figure()

plt.plot(t * 1e12, P_in * 1e3, label="Input")
plt.plot(t * 1e12, P_out * 1e3, label="MZM Output")

plt.xlabel("Time [ps]")
plt.ylabel("Optical Power [mW]")
plt.title("Laser → MZM Optical Chain")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()