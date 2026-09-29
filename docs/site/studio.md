# Studio guide

## ANN inference

1. Enter four normalized inputs between 0 and 1.
2. Keep both converters at 12 bits to reproduce the archived reference.
3. Select **Run inference**. Inspect hidden/output values and analytical differences.
4. Select **Validate 100 inputs** to reproduce seed 12345 and download the batch CSV.
5. Expand network parameters to edit weights and biases. These runs are exploratory.

The architecture is fixed at four inputs, three sigmoid hidden neurons and two sigmoid outputs. Weights are limited to [−1, 1], biases to [−10, 10], and converter precision to 3–16 bits. Reset inputs restores the reference input, while **Restore reference network** restores coefficients.

## Single neuron

The reference neuron uses weights [0.8, −0.6, 0.4, −0.9] and bias 0.2. Its trace exposes signed optical products, balanced current, capacitor voltage, gain/bias, behavioural sigmoid and ADC readout.

## Component lab and archive

The live lab provides MZM transfer and laser power/noise experiments. The archive presents saved detector, receiver, converter, link, perceptron and ANN results. Archived figures do not change when Studio controls change.

## System designer

The preserved node editor runs the original typed PEMAN model. Its kernels and activation/ADC order differ from the later standalone ANN path. Use the [model scope](model-scope.md) page to compare them. Export `.prabha` files for reproducibility.
