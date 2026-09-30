# Studio guide

## Workspaces

**Get started** introduces the current prototype, reference result and community. Bookmark individual workspaces with `#ann`, `#neuron`, `#components` or `#evidence` at the end of the Studio URL.

### ANN inference

Enter four normalized inputs between 0 and 1, choose DAC/ADC precision from 3 to 16 bits, then select **Run inference**. Empty or out-of-range fields are rejected before the model runs. Controls are disabled during a run.

The architecture is fixed: four inputs, three sigmoid hidden neurons and two sigmoid outputs. Expand **Network weights and biases** to edit the JSON. Weights lie in [−1, 1]; biases lie in [−10, 10]. A badge distinguishes the reference coefficients with 12-bit converters from exploratory configurations.

**Validate 100 inputs** samples with seed 12345 using the current coefficients and converter settings. It ignores the four single-run input sliders. It measures numerical agreement against the analytical reference, not classification accuracy.

Changing settings clears previous ANN and neuron results, including the batch plot. **Reset inputs** changes only the four inputs. **Restore reference network** changes only the coefficients. **Reset reference** restores inputs, network and both converter settings.

### Save and repeat an experiment

- **Export settings** saves the ANN inputs, network and converter precision without running Python.
- **Import ANN JSON** accepts an exported settings file, inference run or standard 100-input/seed-12345 batch run. Importing a batch restores the network and converters, with default single-run inputs. Imported results are discarded; run the model again to compute new results.
- **Export inference JSON**, **Export neuron JSON**, **Export experiment JSON** and **Export batch JSON** include the exact request, computed result, Studio/engine versions, engine mode and UTC timestamp.
- **Export CSV** saves batch rows with seed, precision and engine columns. Keep its JSON companion: CSV does not contain the full network.

ANN imports are limited to 256 KB. Old result-only exports have no settings and cannot be imported reliably. The versioned file formats are documented under [API and export formats](api.md).

In a browser, exports use the browser's download folder/settings. Desktop builds use a native **Save** dialog. Cancelling the dialog does not save a file. Sessions are held in memory: export before reloading or leaving the Studio for documentation or the designer.

### Single neuron

The neuron uses fixed weights [0.8, −0.6, 0.4, −0.9] and bias 0.2. ANN coefficient edits do not change this neuron. Inputs and converter precision are shared with the ANN workspace.

The trace shows signed products, balanced current, capacitor voltage, pre-activation, behavioural sigmoid, ADC code and digital output. The JSON also records the fixed weights and bias.

### Component lab

The live lab provides MZM transfer and seeded laser power/noise experiments. Changing a lab parameter clears its old plot. Export JSON to retain the controls, sampled curve and summary.

The laser uses 160 GHz sampling, 10 ns duration, 1 MHz linewidth and seed 1. RIN density is bounded to −180 through −140 dB/Hz for this preview. The separate archive includes additional detector, receiver and converter experiments.

### Validation archive

Browse 25 original figures and four CSV datasets. Select a figure to enlarge it; press **Escape** or **Close** to return. Filters group the archived experiments. These are saved evidence, not plots regenerated from current Studio controls.

### System designer

The preserved node editor uses the original typed PEMAN engine. Its kernels and activation/ADC order differ from the later standalone ANN. Read [model scope](model-scope.md) before comparing them. Export `.prabha` files from the designer to preserve its graph.

## Engine modes

| Status | Where the model runs |
|---|---|
| Browser Python | Pyodide worker in your browser, for static hosting |
| Python API | Native Python behind the local FastAPI server |
| Desktop Python | Bundled native Python sidecar |

The first run selects the available engine. Browser initialization and requests have a two-minute limit; worker failures clear pending requests so another run can restart Python. See [troubleshooting](troubleshooting.md).
