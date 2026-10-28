# CNN operators and execution modes

## Cross-correlation is the CNN convention

Prabha's `conv2d` computes a real-valued cross-correlation: each image patch and learned kernel use the same spatial order. It flattens both, evaluates their dot product with the reusable linear physical MAC, then adds the bias. The mathematical name `cross_correlate2d` is also available as an alias.

Mathematical convolution rotates a two-dimensional kernel by 180 degrees before that dot product. For input `[[0,1,2],[3,4,5],[6,7,8]]` and kernel `[[0,1],[2,3]]`, Prabha returns `[[19,25],[37,43]]`. The rotated-kernel operation returns `[[5,11],[23,29]]`.

Both conventions can express the same family of learned real filters because spatial rotation is a one-to-one reparameterization of all kernel coefficients. A fixed checkpoint still depends on its convention. Keep its orientation when transferring weights between matching CNN implementations. Transpose channel axes where necessary; channel transposition does not imply spatial reversal.

PyTorch explicitly calls its Conv2d operation cross-correlation. TensorFlow's conv2d formula uses input and kernel indices in the same order. Keras delegates its TensorFlow and PyTorch backends to those operations. Sources:

- [PyTorch Conv2d](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html)
- [TensorFlow conv2d](https://www.tensorflow.org/api_docs/python/tf/nn/conv2d)
- [Keras Conv2D](https://keras.io/api/layers/convolution_layers/convolution2d/)
- [Keras 3.15.1 TensorFlow backend](https://github.com/keras-team/keras/blob/v3.15.1/keras/src/backend/tensorflow/nn.py)
- [Keras 3.15.1 PyTorch backend](https://github.com/keras-team/keras/blob/v3.15.1/keras/src/backend/torch/nn.py)

## Select an execution mode

The CNN UI offers Automatic, Fast constant-symbol and Sampled waveform. The same choice is available through `PhysicalMAC(config, execution='auto')` and the JSON request field `execution`. The standalone MAC keeps its historical `waveform` default; the CNN workspace defaults to `auto`.

| Mode | Calculation | Scope |
|---|---|---|
| `auto` | Constant-symbol execution when deterministic; otherwise sampled waveforms | Normal CNN inference uses this default |
| `symbol` | Integrate one constant current per symbol over its duration | Explicit noise or linewidth settings are rejected |
| `waveform` | Evaluate every configured time sample | Retains the sampled calculation and noise streams |

For constant current over S samples, the configured ideal capacitor endpoint is the same whether the program sums S repeated samples or multiplies that current by S. Fast execution retains input DAC, inverse MZM encoding, extinction, complementary weights, detection, capacitor/gain calibration, signed-input passes, reset tiles and optional per-pass ADC conversion. ADC boundary cases use the sampled reduction order. A requested `dot(..., record=True)` uses the waveform path to return actual sampled traces.

This reduction does not approximate arbitrary filtering, leakage, settling or switching: those effects are absent from this configured MAC. Full transient device models require separate validation. Bias, ReLU, pooling, layout changes, scale recovery and argmax remain software operations. The convolution and dense operators reuse a linear MAC and do not insert the complete neuron's sigmoid.

## Measure the current code

Ordinary inference evaluates each path once and reuses its first-image tensors for inspection. It does not run hidden timing repetitions. Use **Benchmark both modes** for an explicit repeated measurement or run:

```bat
python benchmark_execution.py --count 360 --blocks 5 --warmups 1
```

The benchmark keeps the frozen data and weights, randomizes NumPy/waveform/symbol order inside each block, checks waveform/symbol output agreement, and exports all observations plus environment and model identifiers. Loading, backend construction, validation, accuracy gates and export are outside the forward timers. It writes a new results directory and never retrains the checkpoint.

`equivalent_waveform_samples` describes the sampled workload represented by the calculation. `materialized_waveform_samples` counts samples actually evaluated on the waveform path, including any ADC-boundary fallback. Do not call the equivalent count a measured hardware throughput.

The archived 736.68x result compares a deterministic **scalar waveform** workload with INTERCONNECT on the same Windows computer. It is independent of the CNN waveform/symbol cleanup. Neither ratio measures photonic chip speed, and the ratios must not be multiplied.

## Internship source

Abhishek Singh, *Silicon Photonic Microring Resonators: FDTD Simulations, Coupling Optimization, Quality-Factor Analysis, and Cascaded Filter Architectures*, version 1.1, Zenodo, 18 June 2026. [DOI: 10.5281/zenodo.20744970](https://doi.org/10.5281/zenodo.20744970).

This is the author's openly deposited technical report, identified here as not peer reviewed. Repository publication and a DOI establish a citable record; they are not presented as independent peer review or as validation of the later Prabha neural simulator.
