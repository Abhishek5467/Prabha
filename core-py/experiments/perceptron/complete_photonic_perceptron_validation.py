import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))


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
    "Complete Photonic-Electronic Perceptron "
    "Validation "
    "=========="
)



# 1. PERCEPTRON
x = np.array(
    [
        0.9,
        0.3,
        0.7,
        0.5
    ],
    dtype=float
)


w = np.array(
    [
        0.8,
        -0.6,
        0.4,
        -0.9
    ],
    dtype=float
)


bias = 0.2


# 2. ANALYTICAL REFERENCE
ideal_products = (
    x
    *
    w
)


ideal_mac = np.sum(
    ideal_products
)


ideal_pre_activation = (
    ideal_mac
    +
    bias
)


ideal_output = (
    1.0
    /
    (
        1.0
        +
        np.exp(
            -ideal_pre_activation
        )
    )
)


print()

print(
    "Analytical Reference"
)

print(
    "----------------------------------------"
)

print(
    f"Ideal products       : "
    f"{ideal_products}"
)

print(
    f"Ideal MAC            : "
    f"{ideal_mac:.12f}"
)

print(
    f"Ideal pre-activation : "
    f"{ideal_pre_activation:.12f}"
)

print(
    f"Ideal sigmoid output : "
    f"{ideal_output:.12f}"
)


# 3. PHYSICAL PARAMETERS
P0_W = 1e-3

responsivity = 1.0

V_pi = 1.0

phi_bias = np.pi / 2.0


dac_bits = 12

adc_bits = 12


integration_time_s = 1e-9

capacitance_F = 1e-12


amplifier_gain = 2.0


# 4. BLOCKS
mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)


dac = DAC(
    bits=dac_bits,
    V_min=-0.5,
    V_max=0.5
)


pd = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=0.0,
    seed=1
)


capacitor = Capacitor(
    capacitance_F=capacitance_F
)


amplifier = Amplifier(
    gain=amplifier_gain,
    offset_V=bias
)


activation = Activation(
    kind="sigmoid",
    gain=1.0,
    threshold=0.0
)


adc = ADC(
    resolution_bits=adc_bits,
    v_min=0.0,
    v_max=1.0
)


# 5. INPUT OPTICAL ENCODING
# Target MZM transmission:
# T_i = x_i
V_input_ideal = (
    (2.0 * V_pi / np.pi)
    *
    (
        np.arccos(
            np.sqrt(
                x
            )
        )
        -
        phi_bias / 2.0
    )
)


dac_codes, V_input_dac = (
    dac.quantize(
        V_input_ideal
    )
)


P_source = np.full_like(
    x,
    P0_W
)


P_encoded = mzm.modulate(
    P_source,
    V_input_dac
)


x_encoded = (
    P_encoded
    /
    P0_W
)


# 6. DIFFERENTIAL WEIGHT ENCODING
t_plus = (
    1.0
    +
    w
) / 2.0


t_minus = (
    1.0
    -
    w
) / 2.0


# 7. OPTICAL WEIGHTING
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


# 8. BALANCED PHOTODETECTION
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


# 9. CHARGE-DOMAIN ACCUMULATION
# The currents physically enter one capacitor node.
# Vc = Tint/C * sum(I_diff)
V_cap = capacitor.integrate_currents(
    I_diff,
    integration_time_s=(
        integration_time_s
    ),
    reset=True
)


# 10. EXPECTED CAPACITOR VOLTAGE
# With our chosen scaling:
# Vcap = 0.5 * MAC
V_cap_expected = (
    0.5
    *
    ideal_mac
)


# 11. ANALOG GAIN + BIAS
V_pre_activation = float(
    amplifier.amplify(
        V_cap
    )
)


# 12. NONLINEAR ACTIVATION
V_activation = float(
    activation.activate(
        V_pre_activation
    )
)


# 13. ADC READOUT
# Activation is in [0,1] for sigmoid.
adc_code = adc.convert(
    V_activation
)


V_activation_digital = float(
    adc.code_to_voltage(
        adc_code
    )
)


# 14. RECOVER CHANNEL CONTRIBUTIONS
# For diagnosis only:
# each current contribution can be mapped back to normalized xi*wi.
recovered_products = (
    I_diff
    *
    (
        2.0
        /
        (
            P0_W
            *
            responsivity
        )
    )
)


# 15. ERRORS
product_error = (
    recovered_products
    -
    ideal_products
)


capacitor_error = (
    V_cap
    -
    V_cap_expected
)


pre_activation_error = (
    V_pre_activation
    -
    ideal_pre_activation
)


activation_error = (
    V_activation
    -
    ideal_output
)


digital_activation_error = (
    V_activation_digital
    -
    ideal_output
)


# 16. PRINT CHANNEL COMPUTATION
print()

print(
    "Photonic Multiplication"
)

print(
    "-" * 100
)

print(
    "i    "
    "x_i       "
    "w_i       "
    "Ideal product     "
    "Recovered product"
)

print(
    "-" * 100
)


for i in range(
    len(x)
):

    print(
        f"{i:1d}    "
        f"{x[i]: .6f}   "
        f"{w[i]: .6f}   "
        f"{ideal_products[i]: .9f}       "
        f"{recovered_products[i]: .9f}"
    )


# 17. PRINT CURRENT DOMAIN
print()

print(
    "Balanced Photodetector Currents"
)

print(
    "-" * 90
)

print(
    "i    "
    "I_plus[A]        "
    "I_minus[A]       "
    "I_diff[A]"
)

print(
    "-" * 90
)


for i in range(
    len(x)
):

    print(
        f"{i:1d}    "
        f"{I_plus[i]: .9e}   "
        f"{I_minus[i]: .9e}   "
        f"{I_diff[i]: .9e}"
    )


# 18. PRINT ACCUMULATION
print()

print(
    "Charge-Domain Accumulation"
)

print(
    "----------------------------------------"
)

print(
    f"Integration time      : "
    f"{integration_time_s:.12e} s"
)

print(
    f"Capacitance           : "
    f"{capacitance_F:.12e} F"
)

print(
    f"Capacitor voltage     : "
    f"{V_cap:.12f} V"
)

print(
    f"Expected capacitor V  : "
    f"{V_cap_expected:.12f} V"
)

print(
    f"Capacitor error       : "
    f"{capacitor_error:.12e} V"
)


# 19. PRINT AMPLIFIER + BIAS
print()

print(
    "Analog Gain + Bias"
)

print(
    "----------------------------------------"
)

print(
    f"Amplifier gain        : "
    f"{amplifier_gain:.6f}"
)

print(
    f"Bias                  : "
    f"{bias:.12f} V"
)

print(
    f"Pre-activation        : "
    f"{V_pre_activation:.12f}"
)

print(
    f"Ideal pre-activation  : "
    f"{ideal_pre_activation:.12f}"
)

print(
    f"Pre-activation error  : "
    f"{pre_activation_error:.12e}"
)


# 20. PRINT ACTIVATION
print()

print(
    "Nonlinear Activation"
)

print(
    "----------------------------------------"
)

print(
    f"Activation type       : "
    f"{activation.kind}"
)

print(
    f"Analog activation     : "
    f"{V_activation:.12f}"
)

print(
    f"Ideal sigmoid         : "
    f"{ideal_output:.12f}"
)

print(
    f"Analog activation err : "
    f"{activation_error:.12e}"
)


# 21. PRINT ADC
print()

print(
    "ADC Readout"
)

print(
    "----------------------------------------"
)

print(
    f"ADC resolution        : "
    f"{adc_bits} bits"
)

print(
    f"ADC code              : "
    f"{int(adc_code)}"
)

print(
    f"Digital activation    : "
    f"{V_activation_digital:.12f}"
)

print(
    f"Digital output error  : "
    f"{digital_activation_error:.12e}"
)


# 22. ERROR SUMMARY
print()

print(
    "Error Summary"
)

print(
    "----------------------------------------"
)

print(
    f"Max product error     : "
    f"{np.max(np.abs(product_error)):.12e}"
)

print(
    f"Capacitor error       : "
    f"{capacitor_error:.12e}"
)

print(
    f"Pre-activation error  : "
    f"{pre_activation_error:.12e}"
)

print(
    f"Activation error      : "
    f"{activation_error:.12e}"
)

print(
    f"Digital output error  : "
    f"{digital_activation_error:.12e}"
)


# 23. VALIDATION
weight_identity_pass = np.allclose(
    t_plus
    -
    t_minus,
    w,
    atol=1e-15
)


product_pass = (
    np.max(
        np.abs(
            product_error
        )
    )
    <
    5e-4
)


capacitor_pass = (
    abs(
        capacitor_error
    )
    <
    5e-4
)


pre_activation_pass = (
    abs(
        pre_activation_error
    )
    <
    1e-3
)


activation_pass = (
    abs(
        activation_error
    )
    <
    5e-4
)


digital_pass = (
    abs(
        digital_activation_error
    )
    <
    1e-3
)


print()

print(
    "Validation"
)

print(
    "----------------------------------------"
)

print(
    "Differential weights     : "
    f"{'PASS' if weight_identity_pass else 'FAIL'}"
)

print(
    "Photonic multiplication  : "
    f"{'PASS' if product_pass else 'FAIL'}"
)

print(
    "Capacitor accumulation   : "
    f"{'PASS' if capacitor_pass else 'FAIL'}"
)

print(
    "Amplifier + bias         : "
    f"{'PASS' if pre_activation_pass else 'FAIL'}"
)

print(
    "Nonlinear activation     : "
    f"{'PASS' if activation_pass else 'FAIL'}"
)

print(
    "ADC output               : "
    f"{'PASS' if digital_pass else 'FAIL'}"
)


assert weight_identity_pass
assert product_pass
assert capacitor_pass
assert pre_activation_pass
assert activation_pass
assert digital_pass


# 24. PLOT
indices = np.arange(
    len(x)
)


plt.figure(
    figsize=(8, 5)
)


plt.bar(
    indices - 0.18,
    ideal_products,
    width=0.36,
    label="Ideal"
)


plt.bar(
    indices + 0.18,
    recovered_products,
    width=0.36,
    label="Photonic"
)


plt.axhline(
    0.0,
    linewidth=1
)


plt.xticks(
    indices,
    [
        "Channel 1",
        "Channel 2",
        "Channel 3",
        "Channel 4"
    ]
)


plt.ylabel(
    "Weighted contribution"
)


plt.title(
    "Complete Photonic Perceptron: "
    "Weighted Products"
)


plt.grid(
    True,
    axis="y"
)


plt.legend()


plt.tight_layout()


plt.savefig(
    "complete_perceptron_products.png",
    dpi=300
)


plt.close()


# 25. PIPELINE PLOT
pipeline_labels = [
    "Capacitor",
    "Pre-activation",
    "Activation",
    "ADC output"
]


pipeline_values = [
    V_cap,
    V_pre_activation,
    V_activation,
    V_activation_digital
]


plt.figure(
    figsize=(8, 5)
)


plt.plot(
    np.arange(
        len(
            pipeline_values
        )
    ),
    pipeline_values,
    marker="o"
)


plt.xticks(
    np.arange(
        len(
            pipeline_labels
        )
    ),
    pipeline_labels
)


plt.ylabel(
    "Signal value [V / normalized]"
)


plt.title(
    "Signal Evolution Through "
    "Photonic-Electronic Perceptron"
)


plt.grid(
    True
)


plt.tight_layout()


plt.savefig(
    "complete_perceptron_pipeline.png",
    dpi=300
)


plt.close()


print()

print(
    "PASS: Complete photonic-electronic "
    "perceptron validated."
)

print()

print(
    "Saved:"
)

print(
    "  complete_perceptron_products.png"
)

print(
    "  complete_perceptron_pipeline.png"
)