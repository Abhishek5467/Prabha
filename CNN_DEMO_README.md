# Run the trained CNN in Prabha

## Fast demonstration on Windows

1. Extract the complete source ZIP. Open its `Prabha-v0.1` folder.
2. Double-click **RUN_CNN_DEMO.bat**. Python 3.11 or newer must be installed. The first launch installs the small NumPy/JSON-schema dependencies if necessary.
3. Your browser opens `http://127.0.0.1:8765/`. Keep the terminal open.
4. Keep **Held-out digits**, start index **0** and image count **360** and click **Run live comparison**.
5. Show the two accuracies, zero prediction disagreements, and measured software runtimes. Click any prediction row to inspect its digit. **Export run JSON** saves the actual results as JSON.

The trained checkpoint and digit dataset are included. Running the demo does not download data or train the network. Node, PyTorch, a GPU and Lumerical are not required for this demonstration.

If the browser does not open, enter the URL above manually. If port 8765 is occupied, close the previous demo, or run `py run_cnn_demo.py --port 8766` using a Python environment with the demo dependencies. Stop with Ctrl+C or close its terminal.

Linux/macOS: run `bash RUN_CNN_DEMO.sh` with Python 3.11+ installed.

## Add this to your existing source folder

Use the separate **Prabha_CNN_Update.zip** if you want to preserve your current checkout and virtual environment. Extract it outside your project, then run:

```bat
py apply_cnn_update.py "C:\path\to\Prabha"
```

The updater checks that existing files match the uploaded source, backs up changed files, and refuses to overwrite conflicting local edits. Preview with `--check`. Running it again is safe. Then double-click `RUN_CNN_DEMO.bat` inside your project. You do not need the updater when using the complete source ZIP.

## What is integrated

- Studio has a **Trained CNN** workspace. It uses the shared `cnn_info`, `cnn_validate`, `cnn`, and `cnn_inspect` dispatcher actions across HTTP, browser Python and desktop transport.
- `core-py/prabha/systems/cnn.py` implements convolution, ReLU, pooling and dense operations; `mac.py` supplies the Prabha component-waveform MAC backend.
- `cnn_training.py` and `run_cnn_digits.py` provide training and reproducible evaluation; weights, splits, predictions and training history are supplied.
- `cnn_workspace.py` connects the editable fixed-architecture model to the application; `cnn_product.py` preserves earlier imports. `run_cnn_demo.py` launches the demo directly with a local Python server.
- Existing source build scripts now include CNN model/data in browser and desktop bundles. Rebuild Studio/sidecar using the project's normal build steps before using the CNN in an existing compiled application; an old installed executable cannot acquire Python changes by itself.

The complete source archive excludes virtual environments, Git history and old build binaries. The standalone demo runs directly from the supplied source.

## Edit inputs, weights and converters

- Select **Editable 8 x 8 image**. Edit the 8-by-8 pixel JSON (values 0 to 16), or click the image to paint a pixel using the brush value. Load any held-out digit by its zero-based index. A true label is optional; unlabelled inputs show predictions without an accuracy claim.
- Expand **Edit convolution/dense weights and biases**. Change any of the 410 parameters. The architecture stays fixed. **Restore trained weights only** preserves your other choices; **Restore full reference** resets the entire experiment.
- Choose DAC and MAC-output ADC precision (1 to 24 bits or Off), ADC positive/negative voltage range, and DAC tie rule. Out-of-range ADC values produce an error rather than silent clipping. ADC conversion occurs before inverse scaling and digital bias.
- **Validate settings** checks arrays, dimensions and ranges. **Export settings** saves all image/model/converter values. **Import settings / run JSON** restores settings and requires fresh inference; imported predictions are ignored.
- Run inference, then select a prediction row. Inspect normalized input, convolution with bias, ReLU, max pool, flattened features and logits. Select a feature channel, view both tensor maps and their difference, expand exact values, or export the inspection JSON.
- **Export run JSON** includes the exact settings, fresh timings, all predictions and the first-image inspection. **Export CSV** saves predictions and converter/timing metadata. Editing experiment controls clears old results so they cannot appear to belong to new settings.

## Results and what to say

The frozen network is `8x8 -> Conv(1,4,3) -> ReLU -> MaxPool(2) -> Linear(36,10)`, with **410 trained parameters**. The fixed split has 1,149 training, 288 validation and 360 test images. Both NumPy and Prabha classify **354/360 correctly (98.33%)**, with **zero prediction disagreements**. They have slightly different logits because of the physical-model input quantization.

A final browser-connected Python run on the development machine measured **7.878 s for Prabha** and **0.001683 s for vectorised NumPy** over all 360 images. Your machine and execution engine will produce different timings. Each run computes both paths again. NumPy uses the median of seven warmed runs; Prabha uses one warmed full pass. Validation, loading, warmup, layer inspection and exports are excluded. Exported JSON also includes the shared digital-operator runtime.

A same-checkpoint converter experiment got 352/360 with a 4-bit DAC and ADC off, and 340/360 with a 4-bit DAC and 8-bit ADC at the declared range. These are separate sensitivity results; the checkpoint's 354/360 applies to the reference profile.

You can say: **"The trained CNN works through Prabha: it gets 98.33% on this held-out digit set and matches the reference predictions. Its component-waveform simulation is substantially slower in software than vectorised NumPy."**

Each full Prabha inference performs 55,440 MAC calls and simulates 9,538,560 waveform samples. The slowdown is measured, with no artificial computation delay. It includes Python/operator overhead and detailed waveform modelling; it is not a measurement or prediction of physical photonic hardware speed.

Scope: this is the bundled 8x8 digits dataset, not MNIST. The split is image-stratified, not writer-disjoint. The reference profile disables noise and the output ADC; the new interface can enable the optional MAC output ADC. Noise stays disabled; it does not establish a complete noisy CNN or a native Lumerical CNN run. Bias, activation, pooling and per-MAC scaling include digital/software operations.

## Verification

The integrated source passed **97 Python tests** and **10 frontend tests** including the original application tests and all 360 frozen CNN outputs. Real Chromium tests also verified the full held-out run, edited controls, imports/exports and the Studio iframe bridge. The existing ANN smoke result remained unchanged. `verify_cnn_snapshot.py` checks model/data/source hashes and the saved split/results offline.

```bat
py -m pip install -r requirements-cnn-demo.txt
py verify_cnn_snapshot.py
py run_cnn_demo.py
```

For the full test suite, install the project's development/web requirements and run `py -m pytest`. For retraining, use `requirements-cnn-training.txt` and see `py run_cnn_digits.py --help`. The accompanying BTP report revision 4.6 documents the completed workspace and its verified scope.
