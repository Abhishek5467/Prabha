import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import csv
import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC


print(
    "========== "
    "DAC-ADC End-to-End Resolution Matrix "
    "=========="
)


P0_W = 1e-3

V_pi = 1.0
phi_bias = np.pi / 2.0

responsivity = 1.0
R_f = 1000.0

dac_v_min = -0.5
dac_v_max = 0.5

adc_v_min = 0.0
adc_v_max = 1.0

bit_depths = [
    3,
    4,
    6,
    8,
    10,
    12,
]

N = 10001


mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)

pd = Photodetector(
    responsivity_A_per_W=responsivity
)

tia = TIA(
    R_f=R_f
)


x = np.linspace(
    -1.0,
    1.0,
    N
)


T_target = (0.5-0.5*x)


V_ideal = ((2.0 * V_pi / np.pi)*(np.arccos(np.sqrt(T_target))-phi_bias/2.0))


n_bits = len(bit_depths)

max_error_matrix = np.zeros(
    (n_bits, n_bits)
)

rms_error_matrix = np.zeros(
    (n_bits, n_bits)
)

mean_error_matrix = np.zeros(
    (n_bits, n_bits)
)

dac_voltage_rms_matrix = np.zeros(
    (n_bits, n_bits)
)

adc_voltage_rms_matrix = np.zeros(
    (n_bits, n_bits)
)


rows = []


for i, dac_bits in enumerate(bit_depths):
    dac = DAC(
        bits=dac_bits,
        V_min=dac_v_min,
        V_max=dac_v_max
    )

    dac_code, V_dac = dac.quantize(
        V_ideal
    )

    dac_error = (
        V_dac
        -
        V_ideal
    )

    dac_rms = np.sqrt(
        np.mean(
            dac_error ** 2
        )
    )

    # MZM
    P_in = np.full_like(
        x,
        P0_W
    )

    P_mzm = mzm.modulate(
        P_in,
        V_dac
    )

    # PHOTODETECTOR
    I_pd = pd.detect(P_mzm)

    # TIA
    V_tia = tia.amplify(I_pd)
    
    # --------------------------------------------------------
    # ADC LOOP
    # --------------------------------------------------------

    for j, adc_bits in enumerate(bit_depths):

        adc = ADC(
            resolution_bits=adc_bits,
            v_min=adc_v_min,
            v_max=adc_v_max
        )


        # ADC
        adc_code = adc.convert(
            V_tia
        )

        V_adc = adc.code_to_voltage(
            adc_code
        )


        # RECOVER NORMALIZED INPUT
        T_recovered = V_adc

        x_recovered = (
            1.0
            -
            2.0 * T_recovered
        )
        
        
        # ERROR
        x_error = (
            x_recovered
            -
            x
        )

        adc_error = (
            V_adc
            -
            V_tia
        )


        max_error = np.max(
            np.abs(x_error)
        )

        rms_error = np.sqrt(
            np.mean(
                x_error ** 2
            )
        )

        mean_error = np.mean(
            x_error
        )

        adc_rms = np.sqrt(
            np.mean(
                adc_error ** 2
            )
        )


        # STORE
        max_error_matrix[i, j] = (
            max_error
        )

        rms_error_matrix[i, j] = (
            rms_error
        )

        mean_error_matrix[i, j] = (
            mean_error
        )

        dac_voltage_rms_matrix[i, j] = (
            dac_rms
        )

        adc_voltage_rms_matrix[i, j] = (
            adc_rms
        )
        
        rows.append(
            [
                dac_bits,
                adc_bits,
                dac.lsb,
                adc.lsb,
                dac_rms,
                adc_rms,
                max_error,
                rms_error,
                mean_error,
            ]
        )


        print(
            f"DAC {dac_bits:2d} bit | "
            f"ADC {adc_bits:2d} bit | "
            f"Max error = "
            f"{max_error:.9e} | "
            f"RMS = "
            f"{rms_error:.9e}"
        )
        
print()

print("Maximum |x_hat - x| Matrix")

print(
    "Rows = DAC bits, "
    "Columns = ADC bits"
)

print("-" * 95)

print(
    "DAC\\ADC",
    end=""
)

for b in bit_depths:

    print(
        f"{b:>14d}",
        end=""
    )

print()


for i, dac_bits in enumerate(bit_depths):

    print(
        f"{dac_bits:>7d}",
        end=""
    )

    for j in range(n_bits):

        print(
            f"{max_error_matrix[i,j]:14.6e}",
            end=""
        )

    print()
    

print()

print("RMS Recovery Error Matrix")

print(
    "Rows = DAC bits, "
    "Columns = ADC bits"
)

print("-" * 95)

print(
    "DAC\\ADC",
    end=""
)

for b in bit_depths:

    print(
        f"{b:>14d}",
        end=""
    )

print()


for i, dac_bits in enumerate(bit_depths):

    print(
        f"{dac_bits:>7d}",
        end=""
    )

    for j in range(n_bits):

        print(
            f"{rms_error_matrix[i,j]:14.6e}",
            end=""
        )

    print()
    

print()

print(
    "Matched DAC/ADC Resolution"
)

print("-" * 70)

print(
    "Bits      "
    "Max Error          "
    "RMS Error          "
    "Mean Error"
)

print("-" * 70)


for i, bits in enumerate(bit_depths):

    print(
        f"{bits:4d}      "
        f"{max_error_matrix[i,i]:.10e}   "
        f"{rms_error_matrix[i,i]:.10e}   "
        f"{mean_error_matrix[i,i]:.10e}"
    )
    
best_index = np.unravel_index(
    np.argmin(rms_error_matrix),
    rms_error_matrix.shape
)

best_dac = bit_depths[
    best_index[0]
]

best_adc = bit_depths[
    best_index[1]
]

best_rms = rms_error_matrix[
    best_index
]

best_max = max_error_matrix[
    best_index
]


print()

print("Best Configuration")

print("-" * 40)

print(f"DAC bits  : {best_dac}")

print(f"ADC bits  : {best_adc}")

print(f"RMS error : {best_rms:.12e}")

print(f"Max error : {best_max:.12e}")

csv_name = ("dac_adc_resolution_matrix.csv")

with open(
    csv_name,
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "dac_bits",
            "adc_bits",
            "dac_lsb_V",
            "adc_lsb_V",
            "dac_rms_voltage_error_V",
            "adc_rms_voltage_error_V",
            "max_recovery_error",
            "rms_recovery_error",
            "mean_recovery_error",
        ]
    )

    writer.writerows(rows)
    
plt.figure(
    figsize=(8, 6)
)

im = plt.imshow(
    max_error_matrix,
    origin="lower",
    aspect="auto"
)

plt.xticks(
    np.arange(n_bits),
    bit_depths
)

plt.yticks(
    np.arange(n_bits),
    bit_depths
)

plt.xlabel("ADC resolution (bits)")

plt.ylabel("DAC resolution (bits)")

plt.title("Maximum End-to-End Recovery Error")

plt.colorbar(
    im,
    label="Maximum |x_hat - x|"
)

for i in range(n_bits):

    for j in range(n_bits):

        plt.text(
            j,
            i,
            f"{max_error_matrix[i,j]:.3e}",
            ha="center",
            va="center",
            fontsize=7
        )


plt.tight_layout()

plt.savefig(
    "dac_adc_max_error_heatmap.png",
    dpi=300
)

plt.close()


plt.figure(
    figsize=(8, 6)
)

im = plt.imshow(
    rms_error_matrix,
    origin="lower",
    aspect="auto"
)

plt.xticks(
    np.arange(n_bits),
    bit_depths
)

plt.yticks(
    np.arange(n_bits),
    bit_depths
)

plt.xlabel("ADC resolution (bits)")

plt.ylabel("DAC resolution (bits)")

plt.title("RMS End-to-End Recovery Error")

plt.colorbar(
    im,
    label="RMS recovery error"
)

for i in range(n_bits):

    for j in range(n_bits):

        plt.text(
            j,
            i,
            f"{rms_error_matrix[i,j]:.3e}",
            ha="center",
            va="center",
            fontsize=7
        )
        
plt.tight_layout()

plt.savefig(
    "dac_adc_rms_error_heatmap.png",
    dpi=300
)

plt.close()


diagonal_max = np.array(
    [
        max_error_matrix[i, i]
        for i in range(n_bits)
    ]
)

diagonal_rms = np.array(
    [
        rms_error_matrix[i, i]
        for i in range(n_bits)
    ]
)


plt.figure(figsize=(8, 5))

plt.semilogy(
    bit_depths,
    diagonal_max,
    marker="o",
    label="Maximum error"
)

plt.semilogy(
    bit_depths,
    diagonal_rms,
    marker="s",
    label="RMS error"
)

plt.xlabel("Matched DAC/ADC resolution (bits)")

plt.ylabel("End-to-end recovery error")

plt.title("Recovery Error vs Converter Resolution")

plt.grid(
    True,
    which="both"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "dac_adc_matched_resolution.png",
    dpi=300
)

plt.close()



diagonal_rms_decreasing = np.all(
    np.diff(
        diagonal_rms
    ) < 0
)

diagonal_max_decreasing = np.all(
    np.diff(
        diagonal_max
    ) < 0
)


print()

print("Validation")

print("-" * 50)

print(
    "Matched RMS error decreases "
    f": "
    f"{'PASS' if diagonal_rms_decreasing else 'FAIL'}"
)

print(
    "Matched maximum error decreases "
    f": "
    f"{'PASS' if diagonal_max_decreasing else 'FAIL'}"
)


assert diagonal_rms_decreasing
assert diagonal_max_decreasing


print()


print(
    "PASS: Joint DAC-ADC resolution "
    "sweep completed."
)

print()

print("Saved:")

print("  dac_adc_resolution_matrix.csv")

print("  dac_adc_max_error_heatmap.png")

print("  dac_adc_rms_error_heatmap.png")

print("  dac_adc_matched_resolution.png")
