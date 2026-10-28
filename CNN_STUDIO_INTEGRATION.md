# CNN integrated in Prabha Studio

Current source release: **v0.1.0-preview.4**. Both CNN interfaces expose automatic, constant-symbol and waveform execution. Use **Benchmark both modes** for repeated timing; JSON exports retain the choice. A fresh Windows source folder builds the current Studio through `RUN_PRABHA_STUDIO.bat` / `SETUP_PRABHA.bat` (Python 3.11+ and Node.js 22 LTS). The standalone demo requires only Python. Historical timing observations below retain their original workload; see `docs/site/execution.md` and `release/V0_1_PREVIEW_4.md` for current behaviour and scope.

Updated 25 October 2026.

## Open the complete application

Extract the complete archive, open its `Prabha` folder, and double-click **RUN_PRABHA_STUDIO.bat**. Python 3.11 or newer is required; the launcher uses your existing `.venv` or creates `.studio-venv`, installing missing dependencies on first launch. Keep the terminal open. The complete Studio opens at `http://127.0.0.1:8000/#cnn`; choose **ANN inference** or **Trained CNN** in the same sidebar.

Linux/macOS: `bash RUN_PRABHA_STUDIO.sh`. An occupied port can be changed with `py run_studio.py --port 8001` using the installed environment. The complete archive includes the rebuilt frontend; Node is only required when rebuilding source. The older CNN-only demo launcher is preserved.

## Update your current checkout

The included `CNN_Studio_Update` folder contains an updater and its exact payload. Extract that folder outside your current project, then run:

```bat
py apply_cnn_studio_update.py "C:\path\to\Prabha" --check
py apply_cnn_studio_update.py "C:\path\to\Prabha"
```

The updater checks original file hashes, refuses conflicting source changes, saves overwritten files in a timestamped backup inside your project, and includes the rebuilt frontend. Repeating the same update is safe. It preserves your Git repository, Python environments and unrelated project files. Then open `RUN_PRABHA_STUDIO.bat` inside your existing project. This is a local source/application update; an existing hosted page or installed desktop binary needs its normal rebuild/deploy process.

## Integrated behaviour

- Native React CNN controls and result panels, styled alongside ANN.
- The same engine module for HTTP, browser Python and desktop Python, and the same activity lock and Save bridge as ANN.
- Editable 8-by-8 digit pixels, convolution/dense weights and biases, DAC/ADC precision, ADC range and DAC tie rule.
- Current-input inference and full 360-image validation, with fresh NumPy and component-waveform computations.
- Six selectable stages: input, convolution plus bias, ReLU, pooling, flatten and logits. Per-channel maps, tensor values and numerical errors for each inspected image.
- Settings/run import, settings/run/layer JSON and prediction CSV export. Imported predictions are ignored. Exports record exact settings and the engine used.
- Tab navigation preserves CNN settings and results. Input/model/converter edits invalidate results. A failed simulation cannot export a previous run as its result.

The supplied model and numerical backend are unchanged: `8x8 -> Conv(1,4,3) -> ReLU -> MaxPool(2) -> Linear(36,10)`, 410 trained parameters. The reference profile is a 12-bit input DAC with lower-at-tie rounding, no output ADC and noise disabled. The full held-out reference is 354/360 (98.33%) for both NumPy and Prabha, with zero prediction disagreements. Edited models/profiles need fresh measurements.

## Next verification work

1. Export the reference CNN run and selected-layer inspection as a deterministic baseline.
2. Complete statistical RIN cross-validation of the laser → MZM → balanced photodetector → capacitor → ADC chain across powers, RIN levels, sample rates and independent seeds. Compare mean, variance, PSD and SNR using confidence intervals, rather than matching individual noisy waveforms.
3. Once noise transfer is validated, study DAC/ADC precision versus classification accuracy on this frozen checkpoint and split. Save the exact converter range, settings and model/data hashes with each result.
4. Build a separate latency/energy model using explicit hardware assumptions. The displayed software runtime is the simulator execution time.

This integration does not establish native Lumerical full-CNN validation, a noisy CNN accuracy claim or a hardware speedup. Those remain experiments to perform with exported data.

## Rebuild and verify source

```bat
py -m pip install -r requirements-dev.txt
npm ci --prefix frontend/studio
py scripts/build_web_assets.py
npm run build --prefix frontend/studio
py -m pytest tests -q
npm test --prefix frontend/studio
npx --prefix frontend/studio playwright install chromium
npm run test:ui --prefix frontend/studio
```

`frontend/studio/tests/ui/cnn.spec.js` covers the native CNN, all 360 held-out images, edited pixels/weights/converters, stale results, exact export/import, selected-layer inspection, desktop bridge routing and mobile/subpath layouts. The subpath layout test routes computation to the local Python API; it is not a measurement of Pyodide's numerical performance. Native installer testing and live hosting publication are separate from these checks.
