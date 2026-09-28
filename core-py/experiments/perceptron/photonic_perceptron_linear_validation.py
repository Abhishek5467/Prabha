import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from prabha.blocks.mzm import MachZehnderModulator
from prabha.blocks.photodetector import Photodetector
from prabha.blocks.tia import TIA
from prabha.blocks.dac import DAC
from prabha.blocks.adc import ADC


print(
    "========== "
    "Photonic-Electronic Perceptron "
    "Linear-Core Validation "
    "=========="
)


# 1. PERCEPTRON DEFINITION
x = np.array([
    0.9,
    0.3,
    0.7,
    0.5
], dtype=float)


w = np.array([
    0.8,
    -0.6,
    0.4,
    -0.9
], dtype=float)


bias = 0.2


# 2. ANALYTICAL REFERENCE
ideal_contributions = (
    x * w
)

ideal_mac = np.sum(
    ideal_contributions
)

ideal_pre_activation = (
    ideal_mac
    +
    bias
)


print()

print("Analytical Reference")
print("----------------------------------------")

print(
    f"x = {x}"
)

print(
    f"w = {w}"
)

print(
    f"Bias = {bias:.9f}"
)

print(
    f"Ideal MAC = "
    f"{ideal_mac:.12f}"
)

print(
    f"Ideal pre-activation = "
    f"{ideal_pre_activation:.12f}"
)


# 3. PHYSICAL PARAMETERS
P0_W = 1e-3

V_pi = 1.0

phi_bias = np.pi / 2.0

responsivity = 1.0

R_f = 1000.0

electronic_gain = 2.0

dac_bits = 12

adc_bits = 12

fs = 160e9



# 4. COMPONENTS
mzm = MachZehnderModulator(
    V_pi=V_pi,
    phi_bias=phi_bias
)


pd = Photodetector(
    responsivity_A_per_W=responsivity,
    dark_current_A=0.0,
    seed=1
)


tia = TIA(
    R_f=R_f
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



# 5. INPUT ENCODING
# Desired:
# T_x = x
# Since all current reference inputs are in [0,1].
T_input_target = x.copy()


# 6. INVERSE-MZM VOLTAGE
V_input_ideal = (
    (2.0 * V_pi / np.pi)
    *
    (
        np.arccos(
            np.sqrt(
                T_input_target
            )
        )
        -
        phi_bias / 2.0
    )
)


# 7. DAC QUANTIZATION
dac_codes, V_input_dac = (
    dac.quantize(
        V_input_ideal
    )
)


# 8. INPUT MZM

P_input = np.full_like(
    x,
    P0_W
)


P_encoded = mzm.modulate(
    P_input,
    V_input_dac
)


T_input_actual = (
    P_encoded
    /
    P0_W
)


# 9. DIFFERENTIAL SIGNED-WEIGHT REPRESENTATION

# t_plus  = (1 + w)/2
# t_minus = (1 - w)/2
# so:
# t_plus - t_minus = w
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


# 10. 50:50 OPTICAL SPLIT + WEIGHTING
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


# 11. BALANCED PHOTODETECTION
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


# 12. ELECTRICAL ACCUMULATION
# Sum all differential branch currents.
I_sum = np.sum(
    I_diff
)


# 13. TIA
# Use a single-element electrical signal so we remain
# compatible with the current TIA API.
V_raw_array = tia.amplify(
    np.array([
        I_sum
    ]),
    fs=fs,
    include_noise=False
)


V_raw = float(
    V_raw_array[0]
)


# 14. ELECTRONIC CALIBRATION GAIN
#
# With:
#
# P0 = 1 mW
# R  = 1 A/W
# Rf = 1000 Ohm
#
# V_raw = 0.5 * sum(x_i w_i)
#
# therefore gain 2 recovers the mathematical MAC.

V_mac = (
    electronic_gain
    *
    V_raw
)


# 15. BIAS ADDITION

V_pre_activation = (
    V_mac
    +
    bias
)


# 16. ADC
if (
    V_pre_activation
    <
    adc.v_min
    or
    V_pre_activation
    >
    adc.v_max
):

    raise RuntimeError(
        "Perceptron pre-activation "
        "is outside ADC range."
    )


adc_code = adc.convert(
    V_pre_activation
)


V_pre_digital = float(
    adc.code_to_voltage(
        adc_code
    )
)


# 17. RECOVER PER-CHANNEL CONTRIBUTIONS
#
# After TIA + gain calibration:
#
# contribution_i
#
# should approximately equal
#
# x_i * w_i
V_channel_raw = (
    R_f
    *
    I_diff
)


recovered_contributions = (
    electronic_gain
    *
    V_channel_raw
)



# 18. ERRORS
input_transmission_error = (
    T_input_actual
    -
    x
)


contribution_error = (
    recovered_contributions
    -
    ideal_contributions
)


mac_error = (
    V_mac
    -
    ideal_mac
)


pre_activation_analog_error = (
    V_pre_activation
    -
    ideal_pre_activation
)


pre_activation_digital_error = (
    V_pre_digital
    -
    ideal_pre_activation
)


# 19. PRINT INPUT ENCODING
print()

print("Input Optical Encoding")
print("-" * 94)

print(
    "i    x_i       "
    "V_ideal[V]    "
    "DAC code    "
    "V_DAC[V]      "
    "T_actual"
)

print("-" * 94)


for i in range(len(x)):

    print(
        f"{i:1d}    "
        f"{x[i]: .6f}   "
        f"{V_input_ideal[i]: .9f}   "
        f"{dac_codes[i]:5d}      "
        f"{V_input_dac[i]: .9f}   "
        f"{T_input_actual[i]: .9f}"
    )


# 20. PRINT DIFFERENTIAL WEIGHTING
print()

print("Differential Weight Encoding")
print("-" * 88)

print(
    "i    w_i       "
    "t_plus      "
    "t_minus     "
    "t_plus - t_minus"
)

print("-" * 88)


for i in range(len(w)):

    print(
        f"{i:1d}    "
        f"{w[i]: .6f}   "
        f"{t_plus[i]: .9f}   "
        f"{t_minus[i]: .9f}   "
        f"{t_plus[i] - t_minus[i]: .9f}"
    )



# 21. PRINT CHANNEL RESULTS
print()

print("Per-Channel Multiplication")
print("-" * 105)

print(
    "i    "
    "x_i*w_i ideal    "
    "I_plus[A]        "
    "I_minus[A]       "
    "I_diff[A]        "
    "Recovered contribution"
)

print("-" * 105)


for i in range(len(x)):

    print(
        f"{i:1d}    "
        f"{ideal_contributions[i]: .9f}       "
        f"{I_plus[i]: .9e}   "
        f"{I_minus[i]: .9e}   "
        f"{I_diff[i]: .9e}   "
        f"{recovered_contributions[i]: .9f}"
    )


# 22. PRINT ACCUMULATION
print()

print("Electrical Accumulation")
print("----------------------------------------")

print(
    f"Summed differential current : "
    f"{I_sum:.12e} A"
)

print(
    f"Raw TIA voltage             : "
    f"{V_raw:.12f} V"
)

print(
    f"Electronic gain             : "
    f"{electronic_gain:.6f}"
)

print(
    f"Recovered MAC voltage       : "
    f"{V_mac:.12f} V"
)

print(
    f"Ideal MAC                   : "
    f"{ideal_mac:.12f}"
)


# 23. PRINT BIAS / ADC

print()

print("Bias and ADC")
print("----------------------------------------")

print(
    f"Bias                        : "
    f"{bias:.12f}"
)

print(
    f"Analog pre-activation       : "
    f"{V_pre_activation:.12f}"
)

print(
    f"Ideal pre-activation        : "
    f"{ideal_pre_activation:.12f}"
)

print(
    f"ADC code                    : "
    f"{int(adc_code)}"
)

print(
    f"ADC reconstructed voltage   : "
    f"{V_pre_digital:.12f}"
)


# 24. ERROR SUMMARY
print()

print("Error Summary")
print("----------------------------------------")

print(
    f"Maximum input T error       : "
    f"{np.max(np.abs(input_transmission_error)):.12e}"
)

print(
    f"Maximum contribution error  : "
    f"{np.max(np.abs(contribution_error)):.12e}"
)

print(
    f"Analog MAC error            : "
    f"{mac_error:.12e}"
)

print(
    f"Analog pre-activation error : "
    f"{pre_activation_analog_error:.12e}"
)

print(
    f"Digital pre-activation error: "
    f"{pre_activation_digital_error:.12e}"
)


# 25. REFERENCE SIGMOID
#
# IMPORTANT:
#
# This is only a mathematical reference.
# It is NOT yet claimed as the validated hardware activation.
sigmoid_reference = (
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


sigmoid_from_adc = (
    1.0
    /
    (
        1.0
        +
        np.exp(
            -V_pre_digital
        )
    )
)


print()

print("Activation Reference")
print("----------------------------------------")

print(
    f"Ideal sigmoid reference     : "
    f"{sigmoid_reference:.12f}"
)

print(
    f"Sigmoid from ADC value      : "
    f"{sigmoid_from_adc:.12f}"
)

print()

print(
    "NOTE: sigmoid is only a mathematical "
    "reference in this experiment."
)


# 26. VALIDATION CONDITIONS
weight_identity_pass = np.allclose(
    t_plus
    -
    t_minus,
    w,
    atol=1e-15
)


sign_pass = np.all(
    np.sign(
        recovered_contributions
    )
    ==
    np.sign(
        ideal_contributions
    )
)


contribution_pass = (
    np.max(
        np.abs(
            contribution_error
        )
    )
    <
    5e-4
)


mac_pass = (
    abs(
        mac_error
    )
    <
    1e-3
)


pre_activation_pass = (
    abs(
        pre_activation_digital_error
    )
    <
    1e-3
)


print()

print("Validation")
print("----------------------------------------")

print(
    "Differential weight identity : "
    f"{'PASS' if weight_identity_pass else 'FAIL'}"
)

print(
    "Signed multiplication        : "
    f"{'PASS' if sign_pass else 'FAIL'}"
)

print(
    "Per-channel contributions    : "
    f"{'PASS' if contribution_pass else 'FAIL'}"
)

print(
    "Photonic MAC recovery        : "
    f"{'PASS' if mac_pass else 'FAIL'}"
)

print(
    "Biased pre-activation        : "
    f"{'PASS' if pre_activation_pass else 'FAIL'}"
)


assert weight_identity_pass
assert sign_pass
assert contribution_pass
assert mac_pass
assert pre_activation_pass


print()

print(
    "PASS: Photonic-electronic "
    "perceptron linear core validated."
)