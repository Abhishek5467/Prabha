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
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC
from prabha.blocks.capacitor import Capacitor
from prabha.blocks.amplifier import Amplifier
from prabha.blocks.activation import Activation


print(
    "========== "
    "Photonic-Electronic ANN Batch Validation "
    "=========="
)


# 1. NETWORK
W1 = np.array(
    [
        [0.8, -0.6, 0.4, -0.9],
        [-0.3, 0.7, 0.5, 0.2],
        [0.6, 0.1, -0.8, 0.7],
    ],
    dtype=float
)

b1 = np.array(
    [
        0.2,
        -0.1,
        0.05
    ],
    dtype=float
)

W2 = np.array(
    [
        [0.7, -0.5, 0.6],
        [-0.4, 0.9, -0.7],
    ],
    dtype=float
)

b2 = np.array(
    [
        0.1,
        -0.05
    ],
    dtype=float
)


# 2. PHYSICAL PARAMETERS
P0_W = 1e-3

responsivity = 1.0

V_pi = 1.0

phi_bias = np.pi / 2.0

dac_bits = 12

adc_bits = 12

integration_time_s = 1e-9

capacitance_F = 1e-12

amplifier_gain = 2.0


# 3. SHARED COMPONENTS
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

activation = Activation(
    kind="sigmoid",
    gain=1.0,
    threshold=0.0
)


# 4. MATHEMATICAL SIGMOID
def sigmoid(z):

    z = np.asarray(
        z,
        dtype=float
    )

    return (
        1.0
        /
        (
            1.0
            +
            np.exp(-z)
        )
    )


# 5. PHYSICAL NEURON
def physical_neuron(
    inputs,
    weights,
    bias
):

    inputs = np.asarray(
        inputs,
        dtype=float
    )

    weights = np.asarray(
        weights,
        dtype=float
    )


    if len(inputs) != len(weights):

        raise ValueError(
            "Input/weight dimension mismatch."
        )


    if (
        np.any(inputs < 0.0)
        or
        np.any(inputs > 1.0)
    ):

        raise ValueError(
            "Inputs must lie in [0,1]."
        )


    if (
        np.any(weights < -1.0)
        or
        np.any(weights > 1.0)
    ):

        raise ValueError(
            "Weights must lie in [-1,1]."
        )


    # INPUT -> INVERSE MZM

    V_ideal = (
        (2.0 * V_pi / np.pi)
        *
        (
            np.arccos(
                np.sqrt(inputs)
            )
            -
            phi_bias / 2.0
        )
    )


    _, V_dac = dac.quantize(
        V_ideal
    )


    # OPTICAL ENCODING
    P_source = np.full_like(
        inputs,
        P0_W
    )


    P_encoded = mzm.modulate(
        P_source,
        V_dac
    )



    # DIFFERENTIAL SIGNED WEIGHTS
    t_plus = (
        1.0 + weights
    ) / 2.0

    t_minus = (
        1.0 - weights
    ) / 2.0


    P_plus = (
        0.5
        *
        P_encoded
        *
        t_plus
    )

    P_minus = (
        0.5
        *
        P_encoded
        *
        t_minus
    )


    # BALANCED PHOTODETECTION
    pd = Photodetector(
        responsivity_A_per_W=responsivity,
        dark_current_A=0.0,
        seed=1
    )


    I_plus = pd.detect(
        P_plus,
        include_dark_current=False,
        include_shot_noise=False
    )

    I_minus = pd.detect(
        P_minus,
        include_dark_current=False,
        include_shot_noise=False
    )


    I_diff = (
        I_plus
        -
        I_minus
    )


    # CAPACITIVE ACCUMULATION

    capacitor = Capacitor(
        capacitance_F=capacitance_F
    )


    V_cap = capacitor.integrate_currents(
        I_diff,
        integration_time_s=integration_time_s,
        reset=True
    )


    # GAIN + BIAS

    amplifier = Amplifier(
        gain=amplifier_gain,
        offset_V=bias
    )


    pre_activation = float(
        amplifier.amplify(
            V_cap
        )
    )


    # ACTIVATION

    analog_activation = float(
        activation.activate(
            pre_activation
        )
    )


    # ADC

    if not (
        adc.v_min
        <=
        analog_activation
        <=
        adc.v_max
    ):

        raise RuntimeError(
            "Activation exceeded ADC range."
        )


    code = adc.convert(
        analog_activation
    )


    output = float(
        adc.code_to_voltage(
            code
        )
    )


    return output


# 6. PHYSICAL ANN

def physical_ann(x):

    hidden = []


    for j in range(
        W1.shape[0]
    ):

        hidden.append(
            physical_neuron(
                x,
                W1[j],
                b1[j]
            )
        )


    hidden = np.asarray(
        hidden
    )


    output = []


    for j in range(
        W2.shape[0]
    ):

        output.append(
            physical_neuron(
                hidden,
                W2[j],
                b2[j]
            )
        )


    return (
        hidden,
        np.asarray(output)
    )


# 7. IDEAL ANN
def ideal_ann(x):

    hidden_pre = (
        W1 @ x
        +
        b1
    )

    hidden = sigmoid(
        hidden_pre
    )


    output_pre = (
        W2 @ hidden
        +
        b2
    )

    output = sigmoid(
        output_pre
    )


    return (
        hidden,
        output
    )



# 8. GENERATE TEST INPUTS
# These are not training examples.
# They sample the valid operating region.
N = 100

rng = np.random.default_rng(
    12345
)


X = rng.uniform(
    low=0.05,
    high=0.95,
    size=(N, 4)
)


# Include the original validated point explicitly.

X[0] = np.array(
    [
        0.9,
        0.3,
        0.7,
        0.5
    ]
)


# 9. STORAGE
ideal_hidden_all = []

physical_hidden_all = []

ideal_output_all = []

physical_output_all = []


# 10. BATCH RUN
print()

print(
    f"Running {N} input vectors..."
)


for i in range(N):

    x = X[i]


    h_ideal, y_ideal = ideal_ann(
        x
    )


    h_phys, y_phys = physical_ann(
        x
    )


    ideal_hidden_all.append(
        h_ideal
    )

    physical_hidden_all.append(
        h_phys
    )

    ideal_output_all.append(
        y_ideal
    )

    physical_output_all.append(
        y_phys
    )


    if (
        (i + 1) % 10
        ==
        0
    ):

        print(
            f"Completed {i+1}/{N}"
        )


# 11. CONVERT
ideal_hidden_all = np.asarray(
    ideal_hidden_all
)

physical_hidden_all = np.asarray(
    physical_hidden_all
)

ideal_output_all = np.asarray(
    ideal_output_all
)

physical_output_all = np.asarray(
    physical_output_all
)


# 12. ERRORS
hidden_error = (
    physical_hidden_all
    -
    ideal_hidden_all
)


output_error = (
    physical_output_all
    -
    ideal_output_all
)


hidden_abs = np.abs(
    hidden_error
)

output_abs = np.abs(
    output_error
)


hidden_max = np.max(
    hidden_abs
)

hidden_rms = np.sqrt(
    np.mean(
        hidden_error ** 2
    )
)


output_max = np.max(
    output_abs
)

output_rms = np.sqrt(
    np.mean(
        output_error ** 2
    )
)


output_mean_error = np.mean(
    output_error
)


# 13. PER-OUTPUT ERROR
per_output_rms = np.sqrt(
    np.mean(
        output_error ** 2,
        axis=0
    )
)


per_output_max = np.max(
    output_abs,
    axis=0
)


# 14. WORST SAMPLE
sample_max_error = np.max(
    output_abs,
    axis=1
)


worst_index = int(
    np.argmax(
        sample_max_error
    )
)


# 15. OUTPUT ORDER / DECISION STABILITY
# Not classification accuracy.
# This checks whether physical quantization changes
# which output neuron is larger.
ideal_winner = np.argmax(
    ideal_output_all,
    axis=1
)


physical_winner = np.argmax(
    physical_output_all,
    axis=1
)


winner_mismatch = np.sum(
    ideal_winner
    !=
    physical_winner
)


ideal_margin = np.abs(
    ideal_output_all[:, 0]
    -
    ideal_output_all[:, 1]
)


minimum_margin = np.min(
    ideal_margin
)


# 16. PRINT RESULTS
print()

print(
    "Batch Validation Summary"
)

print(
    "----------------------------------------"
)

print(
    f"Samples                : "
    f"{N}"
)

print(
    f"Hidden maximum error   : "
    f"{hidden_max:.12e}"
)

print(
    f"Hidden RMS error       : "
    f"{hidden_rms:.12e}"
)

print(
    f"Output maximum error   : "
    f"{output_max:.12e}"
)

print(
    f"Output RMS error       : "
    f"{output_rms:.12e}"
)

print(
    f"Output mean error      : "
    f"{output_mean_error:.12e}"
)


print()

print(
    "Per-Output Statistics"
)

print(
    "----------------------------------------"
)


for j in range(
    W2.shape[0]
):

    print(
        f"Output {j+1}: "
        f"RMS={per_output_rms[j]:.12e}, "
        f"MAX={per_output_max[j]:.12e}"
    )


print()

print(
    "Worst-Case Input"
)

print(
    "----------------------------------------"
)

print(
    f"Index                  : "
    f"{worst_index}"
)

print(
    f"Input                  : "
    f"{X[worst_index]}"
)

print(
    f"Ideal output           : "
    f"{ideal_output_all[worst_index]}"
)

print(
    f"Physical output        : "
    f"{physical_output_all[worst_index]}"
)

print(
    f"Maximum sample error   : "
    f"{sample_max_error[worst_index]:.12e}"
)


print()

print(
    "Output Ordering"
)

print(
    "----------------------------------------"
)

print(
    f"Winner mismatches      : "
    f"{winner_mismatch}/{N}"
)

print(
    f"Minimum ideal margin   : "
    f"{minimum_margin:.12e}"
)


# 17. SAVE CSV
with open(
    "ann_batch_validation.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(
        f
    )


    writer.writerow(
        [
            "sample",
            "x1",
            "x2",
            "x3",
            "x4",
            "ideal_y1",
            "ideal_y2",
            "physical_y1",
            "physical_y2",
            "error_y1",
            "error_y2",
        ]
    )


    for i in range(N):

        writer.writerow(
            [
                i,
                *X[i],
                *ideal_output_all[i],
                *physical_output_all[i],
                *output_error[i],
            ]
        )


# 18. SCATTER: IDEAL VS PHYSICAL
plt.figure(
    figsize=(7, 6)
)


plt.scatter(
    ideal_output_all[:, 0],
    physical_output_all[:, 0],
    label="Output 1"
)


plt.scatter(
    ideal_output_all[:, 1],
    physical_output_all[:, 1],
    label="Output 2"
)


all_values = np.concatenate(
    [
        ideal_output_all.ravel(),
        physical_output_all.ravel()
    ]
)


lo = np.min(
    all_values
)

hi = np.max(
    all_values
)


plt.plot(
    [lo, hi],
    [lo, hi],
    linestyle="--",
    label="Ideal y = x"
)


plt.xlabel(
    "Ideal ANN output"
)

plt.ylabel(
    "Photonic ANN output"
)

plt.title(
    "Batch ANN Validation: "
    "Ideal vs Photonic"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "ann_batch_ideal_vs_physical.png",
    dpi=300
)

plt.close()



# 19. ERROR HISTOGRAM
plt.figure(
    figsize=(8, 5)
)


plt.hist(
    output_error.ravel(),
    bins=30
)


plt.xlabel(
    "Physical - ideal output error"
)

plt.ylabel(
    "Count"
)

plt.title(
    "Distribution of ANN Output Error"
)

plt.grid(
    True
)

plt.tight_layout()

plt.savefig(
    "ann_batch_error_histogram.png",
    dpi=300
)

plt.close()


# 20. ERROR BY SAMPLE
plt.figure(
    figsize=(9, 5)
)


plt.plot(
    output_abs[:, 0],
    label="Output 1"
)


plt.plot(
    output_abs[:, 1],
    label="Output 2"
)


plt.xlabel(
    "Input sample index"
)

plt.ylabel(
    "Absolute output error"
)

plt.title(
    "ANN Batch Error Across Input Space"
)

plt.grid(
    True
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "ann_batch_error_by_sample.png",
    dpi=300
)

plt.close()


# 21. VALIDATION

finite_pass = (
    np.all(
        np.isfinite(
            physical_output_all
        )
    )
)


range_pass = (
    np.all(
        physical_output_all >= 0.0
    )
    and
    np.all(
        physical_output_all <= 1.0
    )
)


# Conservative limits relative to the
# single-input result.

hidden_pass = (
    hidden_max
    <
    5e-4
)


output_pass = (
    output_max
    <
    5e-4
)


rms_pass = (
    output_rms
    <
    2e-4
)


print()

print(
    "Validation"
)

print(
    "----------------------------------------"
)

print(
    "Finite outputs          : "
    f"{'PASS' if finite_pass else 'FAIL'}"
)

print(
    "Signal range            : "
    f"{'PASS' if range_pass else 'FAIL'}"
)

print(
    "Hidden-layer accuracy   : "
    f"{'PASS' if hidden_pass else 'FAIL'}"
)

print(
    "Output maximum error    : "
    f"{'PASS' if output_pass else 'FAIL'}"
)

print(
    "Output RMS error        : "
    f"{'PASS' if rms_pass else 'FAIL'}"
)


assert finite_pass
assert range_pass
assert hidden_pass
assert output_pass
assert rms_pass


print()

print(
    "PASS: Photonic ANN batch "
    "validation completed."
)

print()

print(
    "Saved:"
)

print(
    "  ann_batch_validation.csv"
)

print(
    "  ann_batch_ideal_vs_physical.png"
)

print(
    "  ann_batch_error_histogram.png"
)

print(
    "  ann_batch_error_by_sample.png"
)