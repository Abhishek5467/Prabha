# Final CNN handoff - 15 October 2026

Launch `RUN_CNN_DEMO.bat` on Windows. The minimal demo runs from source without Node, Lumerical, PyTorch or a GPU. Model/data files are bundled; the first launch may install NumPy and JSON-schema dependencies. Studio's Trained CNN workspace uses the same Python dispatcher.

Implemented: editable 8 x 8 images/pixel painting, all 410 weights and biases, input DAC and optional MAC-output ADC precision/range/rounding, strict settings validation, settings/run-file import, settings/run/CSV/layer exports, and six-stage per-image tensor inspection. Edited controls clear stale results. Imported results are never treated as fresh computations. The architecture is fixed, not an arbitrary CNN graph editor.

Reference: 1-to-4 valid 3x3 convolution, ReLU, 2x2 max pool, flatten 36 and linear 36-to-10. The supplied split is 1149/288/360 from the 8x8 digits dataset. The checkpoint selects epoch 155 by validation loss. Both NumPy and Prabha classify 354/360 correctly (98.33%) with zero prediction disagreements. These figures apply to the supplied checkpoint and converter profile, not edited settings.

Noise stays disabled in this workspace. The default output ADC is off, while the new controls can enable it. The reference uses 12-bit lower-at-tie input conversion and 100 dB extinction. Software preprocessing, inverse scaling, bias, ReLU and pooling are explicit. There is no validated native full-CNN run, noisy-CNN accuracy claim or measured physical hardware speedup. The separate native scalar-noise ledger remains 68 passing checks and one inconclusive RIN endpoint check; the zero-valued trial is not removed.

Run `py verify_cnn_snapshot.py` for the frozen model/data/source/results audit. The full project suite passes 97 Python tests; frontend tests pass 10 checks. Real Chromium tests exercise held-out inference, edited settings, import/export, selected-image inspection and the Studio iframe bridge. Numerical control experiments and audit files are under `results/cnn_workspace/`.

The BTP report revision 4.6 includes the completed workspace, measured converter effects, reproducibility and software-runtime limits. Its independent native evidence and earlier simulator images remain preserved. The matching LaTeX source ZIP contains its figures and numerical summaries.

To continue later, use this source ZIP and the final report. Do not infer that UI completion resolves the outstanding native/noise/hardware experiments. Rebuild Studio and the native sidecar before expecting an already installed desktop executable to contain these source changes.
