import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import numpy as np
import matplotlib.pyplot as plt


from prabha.blocks.mzm import (
    MachZehnderModulator
)

from prabha.blocks.photodetector import (
    Photodetector
)

from prabha.blocks.dac import (
    DAC
)

from prabha.blocks.adc import (
    ADC
)

from prabha.blocks.capacitor import (
    Capacitor
)

from prabha.blocks.amplifier import (
    Amplifier
)

from prabha.blocks.activation import (
    Activation
)


print(
    "========== "
    "Photonic-Electronic ANN "
    "4 -> 3 -> 2 Validation "
    "=========="
)

# 1. Input Vector

x = np.array([0.9,0.3,0.7,0.5], dtype=float)

# 2. Hidden Layer
# Shape:
# 3 neurons
# 4 inputs per neuron

W1 = np.array([[0.8,-0.6,0.4,-0.9],[-0.3,0.7,0.5,0.2],[0.6,0.1,-0.8,0.7],], dtype=float)

b1 = np.array([0.2, -0.1, 0.05],dtype=float)


# 3. Output Layer
# Shape:
# 2 neurons
# 3 inputs per neuron

W2 = np.array([[0.7,-0.5,0.6],[-0.4,0.9,-0.7]],dtype=float)

b2 = np.array([0.1,-0.05],dtype=float)


# 4. Physical Parameters

P0_W = 1e-3

responsivity = 1.0

V_pi = 1.0

phi_bias = np.pi / 2.0

dac_bits = 12

adc_bits = 12

integration_time_s = 1e-9

capacitance_F = 1e-12

amplifier_gain = 2.0


# 5. Shared Blocks

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

# Sigmoid Reference

def sigmoid(z):
    
    z = np.asarray(z,dtype=float)
    
    return (1.0/(1.0+np.exp(-z)))

# 7. Physical Neuron
# This function performs the entire validated perceptron.
# No np.dot() is used for the physical neuron computation.

def physical_neuron(inputs, weights, bias, neuron_name=""):
    
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
            "Input and weight dimensions do not match."
        )


    if np.any(inputs < 0.0) or np.any(inputs > 1.0):

        raise ValueError(
            "Physical input encoding requires "
            "inputs in [0,1]."
        )


    if np.any(weights < -1.0) or np.any(weights > 1.0):

        raise ValueError(
            "Differential weights must lie in [-1,1]."
        )
        
    # Input Inverse-MZM Encoding
    
    V_ideal = ((2.0*V_pi/np.pi)*(np.arccos(np.sqrt(inputs))-phi_bias/2.0))
    
    dac_codes, V_dac = (dac.quantize(V_ideal))
    
    # Optical Inputs
    
    P_source = np.full_like(inputs, P0_W)

    P_encoded = mzm.modulate(P_source, V_dac)
    
    encoded_inputs = (P_encoded/P0_W)
    
    
    # Differential Weight Representation
    
    t_plus = (1.0+weights)/2.0
    t_minus = (1.0-weights)/2.0
    
    # Optical Split + Weighting
    
    P_plus = (0.5*P_encoded*t_plus)
    P_minus = (0.5*P_encoded*t_minus)
    
    # Balanced Photodetection
    
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
    
    # Capacitive Accumulation
    
    capacitor = Capacitor(capacitance_F=capacitance_F)
    
    V_cap = capacitor.integrate_currents(I_diff,integration_time_s=integration_time_s,reset=True)
    
    
    # Analog Gain + Bias
    
    amplifier = Amplifier(gain=amplifier_gain,offset_V=bias)
    
    pre_activation = float(amplifier.amplify(V_cap))
    
    
    # Nonlinear Activation
    
    analog_activation = float(activation.activate(pre_activation))
    
    
    # ADC
    
    if (
        analog_activation
        <
        adc.v_min
        or
        analog_activation
        >
        adc.v_max
    ):

        raise RuntimeError(
            f"{neuron_name}: activation "
            "outside ADC range."
        )


    adc_code = adc.convert(
        analog_activation
    )


    digital_activation = float(
        adc.code_to_voltage(
            adc_code
        )
    )
    
    
    # Diagnostic Product Recovery
    
    recovered_products=(I_diff*(2.0/(P0_W*responsivity)))
    
    return {
        "inputs": inputs,

        "weights": weights,

        "encoded_inputs": encoded_inputs,

        "dac_codes": dac_codes,

        "recovered_products": (
            recovered_products
        ),

        "I_diff": I_diff,

        "V_cap": V_cap,

        "pre_activation": (
            pre_activation
        ),

        "analog_activation": (
            analog_activation
        ),

        "adc_code": int(
            adc_code
        ),

        "output": (
            digital_activation
        ),
    }
    

# 8. Ideal ANN Reference

ideal_hidden_pre = (W1@x+b1)

ideal_hidden = sigmoid(ideal_hidden_pre)

ideal_output_pre = (W2@ideal_hidden+b2)

ideal_output = sigmoid(ideal_output_pre)


print()

print(
    "Ideal ANN Reference"
)

print(
    "----------------------------------------"
)

print(
    f"Input             : "
    f"{x}"
)

print(
    f"Hidden pre-act    : "
    f"{ideal_hidden_pre}"
)

print(
    f"Hidden activation : "
    f"{ideal_hidden}"
)

print(
    f"Output pre-act    : "
    f"{ideal_output_pre}"
)

print(
    f"Output activation : "
    f"{ideal_output}"
)


# 9. Physical Hidden Layer

print()

print(
    "Running physical hidden layer..."
)


hidden_results = []

hidden_physical = []


for j in range(
    W1.shape[0]
):

    result = physical_neuron(
        inputs=x,
        weights=W1[j],
        bias=b1[j],
        neuron_name=(
            f"Hidden neuron {j+1}"
        )
    )


    hidden_results.append(
        result
    )


    hidden_physical.append(
        result["output"]
    )


hidden_physical = np.asarray(
    hidden_physical
)


# 10. Physical Output Layer
# The next physical layer receives the actual digitized
# outputs of the previous layer.

print(
    "Running physical output layer..."
)


output_results = []

output_physical = []


for j in range(
    W2.shape[0]
):

    result = physical_neuron(
        inputs=hidden_physical,
        weights=W2[j],
        bias=b2[j],
        neuron_name=(
            f"Output neuron {j+1}"
        )
    )


    output_results.append(
        result
    )


    output_physical.append(
        result["output"]
    )


output_physical = np.asarray(
    output_physical
)


# 11. STAGE-MATCHED REFERENCE
# This reference uses the physical hidden outputs as the
# second-layer input, but ideal mathematical output neurons.
# It lets us separate:
# hidden-layer error from
# output-neuron implementation error.


stage_matched_output_pre = (
    W2
    @
    hidden_physical
    +
    b2
)


stage_matched_output = sigmoid(
    stage_matched_output_pre
)


# 12. Errors

hidden_error = (
    hidden_physical
    -
    ideal_hidden
)


output_total_error = (
    output_physical
    -
    ideal_output
)


output_local_error = (
    output_physical
    -
    stage_matched_output
)


hidden_max_error = np.max(
    np.abs(
        hidden_error
    )
)


output_max_error = np.max(
    np.abs(
        output_total_error
    )
)


output_local_max_error = np.max(
    np.abs(
        output_local_error
    )
)


# 13. PRINT HIDDEN LAYER

print()

print(
    "Hidden Layer Results"
)

print(
    "-" * 100
)

print(
    "Neuron   "
    "Ideal pre-act   "
    "Physical pre-act   "
    "Ideal activation   "
    "Physical output"
)

print(
    "-" * 100
)


for j in range(
    len(hidden_results)
):

    result = hidden_results[j]

    print(
        f"H{j+1:<7d}"
        f"{ideal_hidden_pre[j]: .9f}       "
        f"{result['pre_activation']: .9f}         "
        f"{ideal_hidden[j]: .9f}         "
        f"{hidden_physical[j]: .9f}"
    )
    
    
# 14. PRINT HIDDEN PRODUCT DETAILS

for j in range(
    len(hidden_results)
):

    result = hidden_results[j]

    ideal_products = (
        x
        *
        W1[j]
    )


    print()

    print(
        f"Hidden Neuron {j+1} Products"
    )

    print(
        "----------------------------------------"
    )

    print(
        f"Ideal     : "
        f"{ideal_products}"
    )

    print(
        f"Recovered : "
        f"{result['recovered_products']}"
    )

    print(
        f"Capacitor : "
        f"{result['V_cap']:.12f} V"
    )
    
    print(
        f"ADC code  : "
        f"{result['adc_code']}"
    )
    
    
# 15. Print Output Layer

print()

print(
    "Output Layer Results"
)

print(
    "-" * 110
)

print(
    "Neuron   "
    "Ideal pre-act   "
    "Physical pre-act   "
    "Ideal output      "
    "Physical output"
)

print(
    "-" * 110
)


for j in range(
    len(output_results)
):

    result = output_results[j]

    print(
        f"O{j+1:<7d}"
        f"{ideal_output_pre[j]: .9f}       "
        f"{result['pre_activation']: .9f}         "
        f"{ideal_output[j]: .9f}       "
        f"{output_physical[j]: .9f}"
    )
    

# 16. Final ANN Comparison

print()

print(
    "Final ANN Comparison"
)

print(
    "----------------------------------------"
)

print(
    f"Ideal hidden layer    : "
    f"{ideal_hidden}"
)

print(
    f"Physical hidden layer : "
    f"{hidden_physical}"
)

print()

print(
    f"Ideal ANN output      : "
    f"{ideal_output}"
)

print(
    f"Physical ANN output   : "
    f"{output_physical}"
)

print()

print(
    f"Hidden max error      : "
    f"{hidden_max_error:.12e}"
)

print(
    f"Output max error      : "
    f"{output_max_error:.12e}"
)

print(
    f"Output local error    : "
    f"{output_local_max_error:.12e}"
)


# 17. NETWORK-LEVEL RMS ERROR

hidden_rms_error = np.sqrt(
    np.mean(
        hidden_error ** 2
    )
)


output_rms_error = np.sqrt(
    np.mean(
        output_total_error ** 2
    )
)


print()

print(
    "Network Error Metrics"
)

print(
    "----------------------------------------"
)

print(
    f"Hidden RMS error      : "
    f"{hidden_rms_error:.12e}"
)

print(
    f"Output RMS error      : "
    f"{output_rms_error:.12e}"
)

# 18. VALIDATION CONDITIONS

hidden_pass = (
    hidden_max_error
    <
    1e-3
)


output_pass = (
    output_max_error
    <
    2e-3
)


local_output_pass = (
    output_local_max_error
    <
    1e-3
)


dimension_pass = (
    len(hidden_physical)
    ==
    3

    and

    len(output_physical)
    ==
    2
)


range_pass = (
    np.all(
        hidden_physical >= 0.0
    )

    and

    np.all(
        hidden_physical <= 1.0
    )

    and

    np.all(
        output_physical >= 0.0
    )

    and

    np.all(
        output_physical <= 1.0
    )
)


print()

print(
    "Validation"
)

print(
    "----------------------------------------"
)

print(
    "Network dimensions       : "
    f"{'PASS' if dimension_pass else 'FAIL'}"
)

print(
    "Hidden-layer neurons     : "
    f"{'PASS' if hidden_pass else 'FAIL'}"
)

print(
    "Output-layer neurons     : "
    f"{'PASS' if output_pass else 'FAIL'}"
)

print(
    "Output local accuracy    : "
    f"{'PASS' if local_output_pass else 'FAIL'}"
)

print(
    "Signal range propagation : "
    f"{'PASS' if range_pass else 'FAIL'}"
)


assert dimension_pass
assert hidden_pass
assert output_pass
assert local_output_pass
assert range_pass


# 19. HIDDEN LAYER PLOT

indices = np.arange(3)

width = 0.35


plt.figure(
    figsize=(8, 5)
)


plt.bar(
    indices - width / 2,
    ideal_hidden,
    width,
    label="Ideal"
)


plt.bar(
    indices + width / 2,
    hidden_physical,
    width,
    label="Photonic"
)


plt.xticks(
    indices,
    [
        "Hidden 1",
        "Hidden 2",
        "Hidden 3"
    ]
)


plt.ylabel(
    "Activation"
)

plt.title(
    "ANN Hidden Layer: "
    "Ideal vs Photonic"
)


plt.grid(
    True,
    axis="y"
)


plt.legend()


plt.tight_layout()


plt.savefig(
    "ann_hidden_layer_comparison.png",
    dpi=300
)


plt.close()


# 20. OUTPUT LAYER PLOT

indices = np.arange(
    2
)


plt.figure(
    figsize=(8, 5)
)


plt.bar(
    indices - width / 2,
    ideal_output,
    width,
    label="Ideal"
)


plt.bar(
    indices + width / 2,
    output_physical,
    width,
    label="Photonic"
)


plt.xticks(
    indices,
    [
        "Output 1",
        "Output 2"
    ]
)


plt.ylabel(
    "Activation"
)


plt.title(
    "ANN Output Layer: "
    "Ideal vs Photonic"
)


plt.grid(
    True,
    axis="y"
)


plt.legend()


plt.tight_layout()


plt.savefig(
    "ann_output_layer_comparison.png",
    dpi=300
)


plt.close()


# 21. NETWORK PIPELINE PLOT

plt.figure(
    figsize=(8, 5)
)


for j in range(
    3
):

    plt.scatter(
        1,
        hidden_physical[j],
        s=80
    )


for j in range(
    2
):

    plt.scatter(
        2,
        output_physical[j],
        s=80
    )


plt.xticks(
    [
        0,
        1,
        2
    ],
    [
        "Input",
        "Hidden",
        "Output"
    ]
)


plt.xlim(
    -0.3,
    2.3
)


plt.ylabel(
    "Normalized activation"
)


plt.title(
    "Physical Signal Propagation "
    "Through 4-3-2 ANN"
)


plt.grid(
    True
)


plt.tight_layout()


plt.savefig(
    "ann_signal_propagation.png",
    dpi=300
)


plt.close()


print()

print(
    "PASS: 4 -> 3 -> 2 "
    "photonic-electronic ANN validated."
)

print()

print(
    "Saved:"
)

print(
    "  ann_hidden_layer_comparison.png"
)

print(
    "  ann_output_layer_comparison.png"
)

print(
    "  ann_signal_propagation.png"
)