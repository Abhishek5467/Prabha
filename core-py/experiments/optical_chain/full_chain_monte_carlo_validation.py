import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import csv
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
    "Full-Chain Monte Carlo Validation "
    "=========="
)


# 1. MONTE CARLO PARAMETERS
n_trials = 200

base_seed = 1000



# 2. TIME AXIS
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


# 3. PHYSICAL PARAMETERS
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


# 4. FIXED BLOCKS
mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)


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


V_drive = np.repeat(
    V_dac_symbols,
    samples_per_symbol
)


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


# 6. CHAIN FUNCTION
def run_chain(
    include_rin=False,
    include_dark=False,
    include_shot=False,
    include_tia_noise=False,
    laser_seed=1,
    pd_seed=2,
    tia_seed=3
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


    _, E = laser.generate(
        include_rin=include_rin,
        include_linewidth=False
    )


    P_laser = laser.power(
        E
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


    # SYMBOL SAMPLING
    V_sampled = V_tia[
        sample_indices
    ]


    # ADC RANGE CHECK
    range_ok = (
        np.min(V_sampled)
        >= adc.v_min
        and
        np.max(V_sampled)
        <= adc.v_max
    )


    if not range_ok:

        return {
            "range_ok": False,
            "v_min": np.min(V_sampled),
            "v_max": np.max(V_sampled),
            "x_recovered": None
        }


    # ADC
    adc_codes = adc.convert(
        V_sampled
    )


    V_adc = adc.code_to_voltage(
        adc_codes
    )


    # RECOVER INPUT
    x_recovered = (
        1.0
        -
        2.0 * V_adc
    )


    return {
        "range_ok": True,
        "v_min": np.min(V_sampled),
        "v_max": np.max(V_sampled),
        "x_recovered": x_recovered
    }


# 7. METRIC FUNCTION
def metrics(
    x_hat,
    reference
):

    error = (
        x_hat
        -
        reference
    )


    return {
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


# 8. DETERMINISTIC BASELINE
baseline = run_chain(
    include_rin=False,
    include_dark=False,
    include_shot=False,
    include_tia_noise=False,
    laser_seed=1,
    pd_seed=2,
    tia_seed=3
)


if not baseline["range_ok"]:

    raise RuntimeError(
        "Deterministic baseline exceeds ADC range."
    )


x_baseline = baseline[
    "x_recovered"
]


baseline_metrics = metrics(
    x_baseline,
    x_symbols
)


print()

print("Deterministic Baseline")
print("----------------------------------------")

print(
    f"Maximum error : "
    f"{baseline_metrics['max']:.12e}"
)

print(
    f"RMS error     : "
    f"{baseline_metrics['rms']:.12e}"
)

print(
    f"Mean error    : "
    f"{baseline_metrics['mean']:.12e}"
)


# 9. CASE DEFINITIONS
cases = {
    "Laser RIN": {
        "include_rin": True,
        "include_dark": False,
        "include_shot": False,
        "include_tia_noise": False,
    },

    "PD dark + shot": {
        "include_rin": False,
        "include_dark": True,
        "include_shot": True,
        "include_tia_noise": False,
    },

    "TIA noise": {
        "include_rin": False,
        "include_dark": False,
        "include_shot": False,
        "include_tia_noise": True,
    },

    "FULL": {
        "include_rin": True,
        "include_dark": True,
        "include_shot": True,
        "include_tia_noise": True,
    },
}


# 10. RESULT STORAGE

results = {}

for name in cases:

    results[name] = {
        "recovery_rms": [],
        "recovery_max": [],
        "recovery_mean": [],

        "noise_rms": [],
        "noise_max": [],
        "noise_mean": [],

        "v_min": [],
        "v_max": [],
    }


range_failures = {
    name: 0
    for name in cases
}


csv_rows = []


# 11. MONTE CARLO LOOP
print()

print(
    f"Running {n_trials} Monte Carlo trials..."
)

print()


for trial in range(n_trials):

    # Independent random-number streams
    # Large offsets ensure the three physical noise mechanisms do not accidentally
    # share the same random sequence.

    laser_seed = (
        base_seed
        +
        trial
    )

    pd_seed = (
        base_seed
        +
        100_000
        +
        trial
    )

    tia_seed = (
        base_seed
        +
        200_000
        +
        trial
    )


    for name, config in cases.items():

        run = run_chain(
            include_rin=config[
                "include_rin"
            ],
            include_dark=config[
                "include_dark"
            ],
            include_shot=config[
                "include_shot"
            ],
            include_tia_noise=config[
                "include_tia_noise"
            ],
            laser_seed=laser_seed,
            pd_seed=pd_seed,
            tia_seed=tia_seed
        )


        if not run["range_ok"]:

            range_failures[name] += 1

            print(
                f"ADC range failure | "
                f"trial={trial} | "
                f"case={name} | "
                f"Vmin={run['v_min']:.6f} | "
                f"Vmax={run['v_max']:.6f}"
            )

            continue


        x_hat = run[
            "x_recovered"
        ]


        # TOTAL RECOVERY ERROR
        total = metrics(
            x_hat,
            x_symbols
        )


        # PURE STOCHASTIC DEVIATION
        # Relative to the same deterministic
        # DAC/MZM/ADC baseline.
        noise = metrics(
            x_hat,
            x_baseline
        )



        # STORE
        results[name][
            "recovery_rms"
        ].append(
            total["rms"]
        )

        results[name][
            "recovery_max"
        ].append(
            total["max"]
        )

        results[name][
            "recovery_mean"
        ].append(
            total["mean"]
        )

        results[name][
            "noise_rms"
        ].append(
            noise["rms"]
        )

        results[name][
            "noise_max"
        ].append(
            noise["max"]
        )

        results[name][
            "noise_mean"
        ].append(
            noise["mean"]
        )

        results[name][
            "v_min"
        ].append(
            run["v_min"]
        )

        results[name][
            "v_max"
        ].append(
            run["v_max"]
        )


        csv_rows.append(
            [
                trial,
                name,

                total["max"],
                total["rms"],
                total["mean"],

                noise["max"],
                noise["rms"],
                noise["mean"],

                run["v_min"],
                run["v_max"],
            ]
        )


    if (
        (trial + 1) % 20
        ==
        0
    ):

        print(
            f"Completed "
            f"{trial + 1}/{n_trials}"
        )


# 12. CONVERT TO ARRAYS
for name in results:

    for key in results[name]:

        results[name][key] = (
            np.asarray(
                results[name][key]
            )
        )


# 13. SUMMARY FUNCTION
def summarize(
    values
):

    n = len(values)

    mean = np.mean(
        values
    )

    std = np.std(
        values,
        ddof=1
    )

    sem = (
        std
        /
        np.sqrt(n)
    )

    ci95 = (
        1.96
        *
        sem
    )


    return {
        "n": n,
        "mean": mean,
        "std": std,
        "min": np.min(
            values
        ),
        "max": np.max(
            values
        ),
        "ci95": ci95,
        "p05": np.percentile(
            values,
            5
        ),
        "p50": np.percentile(
            values,
            50
        ),
        "p95": np.percentile(
            values,
            95
        )
    }


# 14. PRINT RECOVERY-ERROR STATISTICS
print()

print(
    "Monte Carlo Recovery RMS Statistics"
)

print(
    "-" * 108
)

print(
    "Case                 "
    "Mean RMS         "
    "Std RMS          "
    "95% CI(mean)     "
    "5th percentile   "
    "Median           "
    "95th percentile"
)

print(
    "-" * 108
)


recovery_summaries = {}

noise_summaries = {}


for name in cases:

    recovery_summary = summarize(
        results[name][
            "recovery_rms"
        ]
    )

    noise_summary = summarize(
        results[name][
            "noise_rms"
        ]
    )


    recovery_summaries[
        name
    ] = recovery_summary

    noise_summaries[
        name
    ] = noise_summary


    print(
        f"{name:<20s}"
        f"{recovery_summary['mean']:.9e}   "
        f"{recovery_summary['std']:.9e}   "
        f"{recovery_summary['ci95']:.9e}   "
        f"{recovery_summary['p05']:.9e}   "
        f"{recovery_summary['p50']:.9e}   "
        f"{recovery_summary['p95']:.9e}"
    )


# 15. STOCHASTIC DEVIATION STATISTICS
print()

print(
    "Noise-Induced RMS Deviation "
    "from Deterministic Baseline"
)

print(
    "-" * 95
)

print(
    "Case                 "
    "Mean RMS         "
    "Std RMS          "
    "Minimum          "
    "Maximum"
)

print(
    "-" * 95
)


for name in cases:

    s = noise_summaries[
        name
    ]


    print(
        f"{name:<20s}"
        f"{s['mean']:.9e}   "
        f"{s['std']:.9e}   "
        f"{s['min']:.9e}   "
        f"{s['max']:.9e}"
    )


# 16. ADC RANGE ROBUSTNESS
print()

print(
    "ADC Range Robustness"
)

print(
    "----------------------------------------"
)


for name in cases:

    print(
        f"{name:<20s}: "
        f"{range_failures[name]} "
        f"failures / {n_trials}"
    )


# 17. FULL-CHAIN CONFIDENCE INTERVAL
full_summary = recovery_summaries[
    "FULL"
]


print()

print(
    "Full-Chain RMS Estimate"
)

print(
    "----------------------------------------"
)

print(
    f"Mean RMS error          : "
    f"{full_summary['mean']:.12e}"
)

print(
    f"Standard deviation      : "
    f"{full_summary['std']:.12e}"
)

print(
    f"95% CI half-width       : "
    f"{full_summary['ci95']:.12e}"
)

print(
    f"95% CI for mean         : "
    f"["
    f"{full_summary['mean'] - full_summary['ci95']:.12e}, "
    f"{full_summary['mean'] + full_summary['ci95']:.12e}"
    f"]"
)


# 18. SAVE CSV
with open(
    "full_chain_monte_carlo.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(
        f
    )


    writer.writerow(
        [
            "trial",
            "case",

            "recovery_max_error",
            "recovery_rms_error",
            "recovery_mean_error",

            "noise_max_deviation",
            "noise_rms_deviation",
            "noise_mean_deviation",

            "receiver_min_voltage_V",
            "receiver_max_voltage_V",
        ]
    )


    writer.writerows(
        csv_rows
    )


# 19. PLOT:
# RMS RECOVERY ERROR DISTRIBUTION
plot_data = [
    results[name][
        "recovery_rms"
    ]
    for name in cases
]


plt.figure(
    figsize=(9, 5)
)

plt.boxplot(
    plot_data,
    labels=list(
        cases.keys()
    ),
    showmeans=True
)

plt.ylabel(
    "RMS recovery error"
)

plt.title(
    "Monte Carlo Distribution of "
    "End-to-End Recovery Error"
)

plt.grid(
    True,
    axis="y"
)

plt.tight_layout()

plt.savefig(
    "full_chain_monte_carlo_rms_boxplot.png",
    dpi=300
)

plt.close()


# 20. PLOT:
# PURE NOISE CONTRIBUTION
noise_plot_data = [
    results[name][
        "noise_rms"
    ]
    for name in cases
]


plt.figure(
    figsize=(9, 5)
)

plt.boxplot(
    noise_plot_data,
    labels=list(
        cases.keys()
    ),
    showmeans=True
)

plt.ylabel(
    "RMS deviation from quantized baseline"
)

plt.title(
    "Monte Carlo Noise Contribution "
    "Beyond Quantization"
)

plt.grid(
    True,
    axis="y"
)

plt.tight_layout()

plt.savefig(
    "full_chain_monte_carlo_noise_boxplot.png",
    dpi=300
)

plt.close()


# 21. PLOT:
# FULL-CHAIN HISTOGRAM
plt.figure(
    figsize=(8, 5)
)

plt.hist(
    results[
        "FULL"
    ][
        "recovery_rms"
    ],
    bins=25,
    density=True
)

plt.axvline(
    full_summary[
        "mean"
    ],
    linestyle="--",
    label="Mean"
)

plt.xlabel(
    "Full-chain RMS recovery error"
)

plt.ylabel(
    "Probability density"
)

plt.title(
    "Distribution of Full-Chain "
    "RMS Recovery Error"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "full_chain_monte_carlo_histogram.png",
    dpi=300
)

plt.close()


# 22. PLOT:
# CONVERGENCE OF MEAN FULL-CHAIN RMS
full_values = results[
    "FULL"
][
    "recovery_rms"
]


running_mean = (
    np.cumsum(
        full_values
    )
    /
    np.arange(
        1,
        len(full_values) + 1
    )
)


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    np.arange(
        1,
        len(running_mean) + 1
    ),
    running_mean
)

plt.axhline(
    full_summary[
        "mean"
    ],
    linestyle="--",
    label="Final mean"
)

plt.xlabel(
    "Number of Monte Carlo trials"
)

plt.ylabel(
    "Running mean RMS error"
)

plt.title(
    "Convergence of Full-Chain "
    "Monte Carlo Estimate"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "full_chain_monte_carlo_convergence.png",
    dpi=300
)

plt.close()


# 23. VALIDATION CONDITIONS
all_range_pass = all(
    range_failures[name]
    ==
    0

    for name in cases
)


full_finite_pass = np.all(
    np.isfinite(
        results[
            "FULL"
        ][
            "recovery_rms"
        ]
    )
)


# Relative statistical precision of the estimated full-chain mean RMS error.
relative_ci = (
    full_summary[
        "ci95"
    ]
    /
    full_summary[
        "mean"
    ]
)


convergence_pass = (
    relative_ci
    <
    0.05
)


print()

print(
    "Validation"
)

print(
    "----------------------------------------"
)

print(
    "No ADC range failures     : "
    f"{'PASS' if all_range_pass else 'FAIL'}"
)

print(
    "Finite full-chain metrics : "
    f"{'PASS' if full_finite_pass else 'FAIL'}"
)

print(
    "Mean RMS statistically "
    "resolved : "
    f"{'PASS' if convergence_pass else 'FAIL'}"
)

print(
    f"Relative 95% CI           : "
    f"{100 * relative_ci:.6f} %"
)


assert all_range_pass
assert full_finite_pass
assert convergence_pass


print()

print(
    "PASS: Full-chain Monte Carlo "
    "validation completed."
)

print()

print(
    "Saved:"
)

print(
    "  full_chain_monte_carlo.csv"
)

print(
    "  full_chain_monte_carlo_rms_boxplot.png"
)

print(
    "  full_chain_monte_carlo_noise_boxplot.png"
)

print(
    "  full_chain_monte_carlo_histogram.png"
)

print(
    "  full_chain_monte_carlo_convergence.png"
)