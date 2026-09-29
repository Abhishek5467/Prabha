# Model scope and limitations

## Two documented execution paths

| Property | Typed graph / original PEMAN | Standalone perceptron and ANN |
|---|---|---|
| Purpose | Spec conformance and composable signal graph | Later component-based numerical validation |
| Signal treatment | Sampled time-domain arrays | Per-channel behavioural transfer and integration |
| Reference resolution | 8-bit ADC in the original fixture | 12-bit DAC and ADC |
| Nonlinearity/readout | ADC before digital sigmoid | Behavioural sigmoid before ADC |
| Noise | Seeded noise in supported primitive kernels | Disabled in the ANN baseline |
| Conformance coverage | 14 shared Python/C++ fixtures | Python CSV regression and frontend/API checks |

Do not compare the two outputs as if they were the same physical pipeline. The C++ conformance engine does not implement the later standalone ANN frontend operation.

## Physical assumptions

The reference ANN uses a 1 mW CW source, ideal MZM inverse encoding (Vπ=1 V, quadrature bias), balanced signed transmissions, 1 A/W responsivity, 1 pF capacitance, 1 ns integration and gain 2. The sigmoid is an abstract behavioural electronic function. Weights are ideal normalized transmissions, not calibrated fabricated weight banks.

Converter quantization is included. Laser noise, shot/dark noise, TIA bandwidth/noise, calibration drift, weight setting cost, parasitics, thermal effects and inter-layer timing are not propagated through this ANN validation. Separate noisy-link experiments do not establish noisy ANN accuracy.

## What the result establishes

For one fixed network and 100 sampled inputs, the physical behavioural path closely matches the analytical sigmoid network. Zero ordering mismatches is not dataset classification accuracy. No throughput, energy, area, fabricated-chip or LLM performance claim follows from this result.

The source includes some placeholders (including CNN and temporal systems) and an empty linewidth sweep file. Their presence is not evidence of implementation.
