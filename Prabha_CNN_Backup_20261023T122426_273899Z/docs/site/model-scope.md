# Model scope and limitations

## Three explicit paths

| Property | Current Designer (`model_*`) | Legacy PEMAN | Standalone ANN |
|---|---|---|---|
| Purpose | Compose the established component models | Preserve original graphs and conformance fixtures | Fixed 4–3–2 regression network |
| Signal treatment | Sampled time arrays, explicit integration | Original sampled kernels | Per-channel behavioral computation |
| Readout | Analog activation before ADC in reference example | ADC before digital activation in fixture | Analog sigmoid before ADC |
| Noise | Configurable laser, detector and TIA sources | Original laser/PD noise rules | Disabled in archived baseline |
| Nonlinear/deterministic effects | MZM transfer, DAC/ADC quantization, optional leakage/rails, activation | Original simplified kernels | Reference MZM/converter/activation chain |
| Execution | Python API, browser Pyodide, Python desktop sidecar | Python and limited C++ fixture engine | Python shared dispatcher |

Current Designer adapters call the **same Python component classes** as the standalone experiments. The compact MAC and expanded chain expose that computation in a graph. Historical IDs remain unchanged so old files preserve their semantics. C++ has **not** been extended to run the new `model_*` kernels or standalone ANN operations; its conformance result applies to the original fixtures.

## Reference correspondence

The B22 neuron uses 1 mW optical power, inverse MZM encoding (Vπ=1 V, differential bias π/2), 12-bit DAC, balanced ideal signed transmissions, 1 A/W responsivity, 1 pF capacitance, gain 2, bias 0.2, sigmoid and 12-bit ADC.

The Designer reference sends four sequential symbols held for 1 ns each (16 samples/symbol at 16 GHz). With leakage off, the final charge equals B22's sum of four parallel currents each integrated for 1 ns. The final voltage/output agrees. **This is a numerical final-value correspondence, not a claim of equal circuit latency, bandwidth or parallel architecture.** Changing integration time, leakage, weights, gain or noise changes the modeled experiment.

## Physical assumptions

MZM is a power-transfer model; the Designer preserves incident envelope phase but does not model chirp, coherent arm field signs or interferometric phase-to-intensity conversion. Laser phase diffusion therefore appears in the optical phase probe without changing a direct-detection power trace when RIN is disabled. Zero optical amplitude has no meaningful phase.

Weights are ideal normalized transmissions, not calibrated fabricated weight banks. The activation is a behavioral transfer on a normalized voltage scale, not a transistor implementation. TIA uses the established backward-Euler first-order filter; its initial output equals the first input times gain, and its discrete response depends on sample rate.

Photodetector shot noise uses the one-sided white-sample convention `variance = 2 q Imean fs/2`. TIA input noise density is an explicit user parameter, applied before filtering. No separate load thermal noise is silently added. Dark current and deterministic nonidealities remain active when global noise is off. RIN is a linearized Gaussian power perturbation; negative-power realizations are rejected instead of propagating NaNs.

Converter jitter, DNL/INL, kT/C reset noise, drift, parasitics, fabrication effects, weight-setting energy and a calibrated device-level activation are outside these models. The scope and parameter help for every block are in the [Designer guide](designer.md).

## What is validated

Archived ANN regression remains: RMS error **7.864411795585e-5**, maximum error **1.782838135357e-4**, **0/100** output-order mismatches. This is one fixed network and sampled input set; it does not establish dataset classification accuracy, noisy ANN accuracy, throughput, energy, area or fabricated-chip performance.

Designer integration checks establish correspondence to the existing models and correct controls/transport. They are not new physical measurements. CNN and temporal placeholders remain outside this release; there is no validated LLM/LMM accelerator implementation here.
