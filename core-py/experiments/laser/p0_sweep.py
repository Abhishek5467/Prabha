import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from prabha.blocks.cw_laser import CWLaser

P0_values = [0.1,1.0,10.0]

for P0_mW in P0_values:
    laser = CWLaser(P0_mW=P0_mW, wavelength_nm=1550.0,fs=160e9,duration=1e-9,phase0=0.0)

    t,E=laser.generate()

    P=laser.power(E)

    print(
        f"P0 = {P0_mW} mW | "
        f"mean = {np.mean(P)*1e3:.6f} mW | "
        f"min = {np.min(P)*1e3:.6f} mW | "
        f"max = {np.max(P)*1e3:.6f} mW"
    )

    plt.plot(t*1e12,P*1e3,label=f"P0 = {P0_mW} mW")

plt.xlabel("Time (ps)")
plt.ylabel("Power (mW)")
plt.title("Ideal CW Laser Power vs Time")

plt.legend()
plt.grid()

plt.show()
