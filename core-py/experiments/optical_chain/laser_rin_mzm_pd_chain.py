import numpy as np
import sys
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.photodetector import Photodetector
from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator

P0_mW = 1.0

fs = 160e9
duration = 10e-9

wavelength_nm = 1550.0

rin_db_hz = -150.0

V_pi = 1.0
phi_bias = np.pi / 2
V = 0.1

responsivity = 1.0 
seed=1

laser=CWLaser(
    P0_mW=P0_mW,
    wavelength_nm=wavelength_nm,
    fs=fs,
    duration=duration,
    rin_db_hz=rin_db_hz,
    linewidth_hz=0.0,
    seed=seed,
)

t,E = laser.generate(include_linewidth=False, include_rin=True)

P_in=np.abs(E)**2

mzm=MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias,
    insertion_loss_dB=0.0,
)

P_out=mzm.modulate(
    P_in,
    V
)

T=mzm.transfer(V)

pd=Photodetector(responsivity_A_per_W=responsivity)

I_ph = pd.detect(P_out)

rin_linear=10**(rin_db_hz/10.0)

bandwidth=fs/2.0

sigma_P_in_theory=(
    P0_mW*1e-3*np.sqrt(rin_linear*bandwidth)
)

sigma_P_out_theory=(T*sigma_P_in_theory)

sigma_I_theory=(responsivity*sigma_P_out_theory)

mean_P_in=np.mean(P_in)
std_P_in=np.std(P_in)

mean_P_out=np.mean(P_out)
std_P_out=np.std(P_out)

mean_I=np.mean(I_ph)
std_I=np.std(I_ph)

relative_rms_in = std_P_in / mean_P_in
relative_rms_out = std_P_out / mean_P_out
relative_rms_I = std_I / mean_I


input_noise_error=abs(std_P_in-sigma_P_in_theory)
output_noise_error=abs(std_P_out-sigma_P_out_theory)
current_noise_error=abs(std_I-sigma_I_theory)

print("========== Laser RIN → MZM → Photodetector ==========")

print()
print("Parameters")
print("----------------------------------------")
print(f"Laser power             : {P0_mW:.6f} mW")
print(f"RIN                     : {rin_db_hz:.2f} dB/Hz")
print(f"Sampling frequency      : {fs/1e9:.1f} GHz")
print(f"Duration                : {duration*1e9:.1f} ns")
print(f"MZM voltage             : {V:.6f} V")
print(f"MZM transmission        : {T:.6f}")
print(f"Responsivity            : {responsivity:.6f} A/W")
print()

print("Optical input")
print("----------------------------------------")
print(
    f"Mean power              : "
    f"{mean_P_in*1e3:.6f} mW"
)
print(
    f"Measured RMS noise      : "
    f"{std_P_in*1e3:.6f} mW"
)
print(
    f"Theoretical RMS noise   : "
    f"{sigma_P_in_theory*1e3:.6f} mW"
)
print(
    f"Relative RMS            : "
    f"{relative_rms_in*100:.6f} %"
)
print()

print("MZM output")
print("----------------------------------------")
print(
    f"Mean power              : "
    f"{mean_P_out*1e3:.6f} mW"
)
print(
    f"Measured RMS noise      : "
    f"{std_P_out*1e3:.6f} mW"
)
print(
    f"Theoretical RMS noise   : "
    f"{sigma_P_out_theory*1e3:.6f} mW"
)
print(
    f"Relative RMS            : "
    f"{relative_rms_out*100:.6f} %"
)
print()

print("Photodetector output")
print("----------------------------------------")
print(
    f"Mean photocurrent       : "
    f"{mean_I*1e3:.6f} mA"
)
print(
    f"Measured RMS noise      : "
    f"{std_I*1e3:.6f} mA"
)
print(
    f"Theoretical RMS noise   : "
    f"{sigma_I_theory*1e3:.6f} mA"
)
print(
    f"Relative RMS            : "
    f"{relative_rms_I*100:.6f} %"
)
print()

print("Validation")
print("----------------------------------------")
print(
    f"Input noise error       : "
    f"{input_noise_error:.6e} W"
)
print(
    f"MZM noise error         : "
    f"{output_noise_error:.6e} W"
)
print(
    f"Detector noise error    : "
    f"{current_noise_error:.6e} A"
)

print()
print(
    "Relative RMS difference "
    "(input → MZM): "
    f"{abs(relative_rms_in-relative_rms_out)*100:.6e} %"
)

print(
    "Relative RMS difference "
    "(MZM → detector): "
    f"{abs(relative_rms_out-relative_rms_I)*100:.6e} %"
)

plt.figure()

plt.plot(
    t * 1e9,
    P_in * 1e3,
    label="Laser Output"
)

plt.plot(
    t * 1e9,
    P_out * 1e3,
    label="MZM Output"
)

plt.xlabel("Time [ns]")
plt.ylabel("Optical Power [mW]")
plt.title("RIN Propagation: Laser → MZM")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

plt.figure()

plt.plot(
    t * 1e9,
    I_ph * 1e3
)

plt.xlabel("Time [ns]")
plt.ylabel("Photocurrent [mA]")
plt.title("RIN at Photodetector Output")

plt.grid(True)
plt.tight_layout()

plt.show()