import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from prabha.blocks.cw_laser import CWLaser
from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC


print(
    "========== "
    "Full Noisy Calibrated Electro-Optical Chain "
    "=========="
)


# 1. GLOBAL PARAMETERS
fs = 160e9

symbol_duration = 1e-9

samples_per_symbol = int(
    round(
        fs * symbol_duration
    )
)

n_symbols = 101

x_symbols = np.linspace(
    -0.95,
    0.95,
    n_symbols
)

n_samples = (
    n_symbols
    *
    samples_per_symbol
)

duration = (
    n_samples
    /
    fs
)



# 2. DEVICE PARAMETERS

P0_mW = 1.0

rin_db_hz = -150.0

V_pi = 1.0

phi_bias = np.pi / 2.0

responsivity = 1.0

dark_current_A = 5e-9

R_f = 1000.0

tia_bandwidth_Hz = 10e9

tia_noise_density = 1e-12

dac_bits = 8

adc_bits = 8


# 3. CONVERTERS
dac = DAC(
    bits=dac_bits,
    V_min=-0.5,
    V_max=0.5
)

adc = ADC(
    resolution_bits=adc_bits,
    v_min=0.0,
    v_max=1.0
)


# 4. MZM
mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)


# 5. INVERSE-MZM ENCODING
T_target_symbols = (
    0.5
    -
    0.5 * x_symbols
)


V_ideal_symbols = (
    (2.0 * V_pi / np.pi)
    *
    (
        np.arccos(
            np.sqrt(
                T_target_symbols
            )
        )
        -
        phi_bias / 2.0
    )
)


dac_codes, V_dac_symbols = (
    dac.quantize(
        V_ideal_symbols
    )
)


# Hold each DAC voltage for one symbol period.

V_drive = np.repeat(
    V_dac_symbols,
    samples_per_symbol
)


# 6. HELPER FUNCTION
def run_chain(
    include_rin=False,
    include_dark=False,
    include_shot=False,
    include_tia_noise=False,
    laser_seed=11,
    pd_seed=12,
    tia_seed=13
):


    # LASER
    
    laser = CWLaser(
        P0_mW=P0_mW,
        wavelength_nm=1550.0,
        fs=fs,
        duration=duration,
        rin_db_hz=rin_db_hz,
        linewidth_hz=0.0,
        seed=laser_seed
    )


    t, E = laser.generate(
        include_rin=include_rin,
        include_linewidth=False
    )


    P_laser = laser.power(
        E
    )


    if len(P_laser) != n_samples:

        raise RuntimeError(
            "Laser sample count does not "
            "match electrical waveform."
        )


    # MZM

    P_mzm = mzm.modulate(
        P_laser,
        V_drive
    )


    # PHOTODETECTOR
    pd = Photodetector(
        responsivity_A_per_W=responsivity,
        dark_current_A=dark_current_A,
        seed=pd_seed
    )


    I_pd = pd.detect_white_shot(
        P_mzm,
        fs=fs,
        include_dark_current=include_dark,
        include_shot_noise=include_shot
    )



    # TIA
    tia = TIA(
        R_f=R_f,
        bandwidth_Hz=tia_bandwidth_Hz,
        noise_current_density_A_per_sqrtHz=(
            tia_noise_density
            if include_tia_noise
            else 0.0
        ),
        seed=tia_seed
    )


    V_tia = tia.amplify(
        I_pd,
        fs=fs,
        include_noise=include_tia_noise
    )


    # SAMPLE NEAR END OF EACH SYMBOL
    sample_indices = (
        np.arange(
            1,
            n_symbols + 1
        )
        *
        samples_per_symbol
        -
        1
    )


    V_sampled = V_tia[
        sample_indices
    ]


    # ADC RANGE
    range_pass = (
        np.min(V_sampled)
        >= adc.v_min
        and
        np.max(V_sampled)
        <= adc.v_max
    )


    if not range_pass:

        print()

        print(
            "ADC RANGE FAILURE"
        )

        print(
            f"Minimum receiver voltage : "
            f"{np.min(V_sampled):.9f} V"
        )

        print(
            f"Maximum receiver voltage : "
            f"{np.max(V_sampled):.9f} V"
        )

        raise RuntimeError(
            "Receiver exceeded ADC range. "
            "Do not clip silently."
        )


    # ADC
    adc_codes = adc.convert(
        V_sampled
    )


    V_adc = adc.code_to_voltage(
        adc_codes
    )


    # RECOVER x
    x_recovered = (
        1.0
        -
        2.0 * V_adc
    )


    return {
        "P_laser": P_laser,
        "P_mzm": P_mzm,
        "I_pd": I_pd,
        "V_tia": V_tia,
        "V_sampled": V_sampled,
        "V_adc": V_adc,
        "adc_codes": adc_codes,
        "x_recovered": x_recovered,
    }


# 7. RUN DIFFERENT PHYSICAL CASES
print()

print(
    "Running baseline..."
)

baseline = run_chain(
    include_rin=False,
    include_dark=False,
    include_shot=False,
    include_tia_noise=False
)


print(
    "Running laser-RIN case..."
)

rin_only = run_chain(
    include_rin=True,
    include_dark=False,
    include_shot=False,
    include_tia_noise=False
)


print(
    "Running detector-noise case..."
)

pd_only = run_chain(
    include_rin=False,
    include_dark=True,
    include_shot=True,
    include_tia_noise=False
)


print(
    "Running TIA-noise case..."
)

tia_only = run_chain(
    include_rin=False,
    include_dark=False,
    include_shot=False,
    include_tia_noise=True
)


print(
    "Running FULL noisy chain..."
)

full = run_chain(
    include_rin=True,
    include_dark=True,
    include_shot=True,
    include_tia_noise=True
)


# 8. ERROR FUNCTION
def error_metrics(
    x_hat
):

    error = (
        x_hat
        -
        x_symbols
    )

    return {
        "error": error,

        "max": np.max(
            np.abs(error)
        ),

        "rms": np.sqrt(
            np.mean(
                error ** 2
            )
        ),

        "mean": np.mean(
            error
        )
    }


# 9. METRICS
metrics = {
    "Baseline":
        error_metrics(
            baseline[
                "x_recovered"
            ]
        ),

    "Laser RIN":
        error_metrics(
            rin_only[
                "x_recovered"
            ]
        ),

    "PD dark + shot":
        error_metrics(
            pd_only[
                "x_recovered"
            ]
        ),

    "TIA noise":
        error_metrics(
            tia_only[
                "x_recovered"
            ]
        ),

    "FULL":
        error_metrics(
            full[
                "x_recovered"
            ]
        )
}


# 10. PRINT SYSTEM PARAMETERS
print()

print(
    "System Parameters"
)

print(
    "----------------------------------------"
)

print(
    f"Sampling frequency       : "
    f"{fs / 1e9:.6f} GHz"
)

print(
    f"Symbol duration          : "
    f"{symbol_duration * 1e9:.6f} ns"
)

print(
    f"Samples per symbol       : "
    f"{samples_per_symbol}"
)

print(
    f"Input symbols            : "
    f"{n_symbols}"
)

print(
    f"Input range              : "
    f"{x_symbols[0]:.3f} "
    f"to "
    f"{x_symbols[-1]:.3f}"
)

print(
    f"Laser power              : "
    f"{P0_mW:.6f} mW"
)

print(
    f"Laser RIN                : "
    f"{rin_db_hz:.3f} dB/Hz"
)

print(
    f"Dark current             : "
    f"{dark_current_A * 1e9:.6f} nA"
)

print(
    f"TIA bandwidth            : "
    f"{tia_bandwidth_Hz / 1e9:.6f} GHz"
)

print(
    f"TIA noise density        : "
    f"{tia_noise_density:.6e} "
    f"A/sqrt(Hz)"
)

print(
    f"DAC / ADC                : "
    f"{dac_bits} / {adc_bits} bits"
)


# 11. PRINT ERROR TABLE
print()

print(
    "End-to-End Recovery Error"
)

print(
    "-" * 78
)

print(
    "Case                 "
    "Maximum error       "
    "RMS error           "
    "Mean error"
)

print(
    "-" * 78
)


for name, m in metrics.items():

    print(
        f"{name:<20s}"
        f"{m['max']:.9e}   "
        f"{m['rms']:.9e}   "
        f"{m['mean']:.9e}"
    )


# 12. INCREMENTAL FULL-CHAIN DEGRADATION
delta_full = (
    full["x_recovered"]
    -
    baseline["x_recovered"]
)


delta_full_rms = np.sqrt(
    np.mean(
        delta_full ** 2
    )
)


delta_full_max = np.max(
    np.abs(
        delta_full
    )
)


print()

print(
    "Noise-Induced Deviation from "
    "Quantized Baseline"
)

print(
    "----------------------------------------"
)

print(
    f"Maximum deviation : "
    f"{delta_full_max:.12e}"
)

print(
    f"RMS deviation     : "
    f"{delta_full_rms:.12e}"
)


# 13. ADC RANGE MARGIN
V_full = full[
    "V_sampled"
]


print()

print(
    "Receiver Voltage Range"
)

print(
    "----------------------------------------"
)

print(
    f"Minimum sampled voltage : "
    f"{np.min(V_full):.9f} V"
)

print(
    f"Maximum sampled voltage : "
    f"{np.max(V_full):.9f} V"
)

print(
    f"Lower ADC margin        : "
    f"{np.min(V_full) - adc.v_min:.9f} V"
)

print(
    f"Upper ADC margin        : "
    f"{adc.v_max - np.max(V_full):.9f} V"
)


# 14. VALIDATION

finite_pass = np.all(
    np.isfinite(
        full[
            "x_recovered"
        ]
    )
)

adc_range_pass = (
    np.min(V_full) >= adc.v_min
    and
    np.max(V_full) <= adc.v_max
)

baseline_pass = (
    metrics[
        "Baseline"
    ][
        "max"
    ]
    <
    0.012
)


print()

print(
    "Validation"
)

print(
    "----------------------------------------"
)

print(
    "Finite recovered output : "
    f"{'PASS' if finite_pass else 'FAIL'}"
)

print(
    "ADC range               : "
    f"{'PASS' if adc_range_pass else 'FAIL'}"
)

print(
    "Quantized baseline      : "
    f"{'PASS' if baseline_pass else 'FAIL'}"
)


assert finite_pass
assert adc_range_pass
assert baseline_pass



# 15. RECOVERY PLOT

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    x_symbols,
    x_symbols,
    label="Ideal"
)

plt.plot(
    x_symbols,
    baseline[
        "x_recovered"
    ],
    label="Quantized baseline"
)

plt.plot(
    x_symbols,
    full[
        "x_recovered"
    ],
    marker=".",
    markersize=3,
    label="Full noisy chain"
)

plt.xlabel(
    "Original normalized input x"
)

plt.ylabel(
    "Recovered normalized input"
)

plt.title(
    "Full Noisy Calibrated "
    "End-to-End Recovery"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "full_noisy_chain_recovery.png",
    dpi=300
)

plt.close()


# 16. ERROR COMPARISON

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    x_symbols,
    metrics[
        "Baseline"
    ][
        "error"
    ],
    label="Baseline"
)

plt.plot(
    x_symbols,
    metrics[
        "Laser RIN"
    ][
        "error"
    ],
    label="Laser RIN"
)

plt.plot(
    x_symbols,
    metrics[
        "PD dark + shot"
    ][
        "error"
    ],
    label="PD dark + shot"
)

plt.plot(
    x_symbols,
    metrics[
        "TIA noise"
    ][
        "error"
    ],
    label="TIA noise"
)

plt.plot(
    x_symbols,
    metrics[
        "FULL"
    ][
        "error"
    ],
    linewidth=2,
    label="FULL"
)

plt.xlabel(
    "Normalized input x"
)

plt.ylabel(
    "Recovery error"
)

plt.title(
    "Error Contributions in the "
    "Full Electro-Optical Chain"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "full_noisy_chain_error_contributions.png",
    dpi=300
)

plt.close()


# 17. RMS ERROR BAR GRAPH
names = list(
    metrics.keys()
)

rms_values = [
    metrics[name]["rms"]
    for name in names
]


plt.figure(
    figsize=(8, 5)
)

plt.bar(
    names,
    rms_values
)

plt.ylabel(
    "RMS recovery error"
)

plt.title(
    "End-to-End Error by "
    "Enabled Nonideality"
)

plt.xticks(
    rotation=15
)

plt.grid(
    True,
    axis="y"
)

plt.tight_layout()

plt.savefig(
    "full_noisy_chain_rms_comparison.png",
    dpi=300
)

plt.close()


print()

print(
    "PASS: Full noisy calibrated "
    "electro-optical chain completed."
)

print()

print(
    "Saved:"
)

print(
    "  full_noisy_chain_recovery.png"
)

print(
    "  full_noisy_chain_error_contributions.png"
)

print(
    "  full_noisy_chain_rms_comparison.png"
)