# v0.1.0-preview.4 — 28 October 2026

This source release exposes the evaluated constant-symbol calculation as an explicit option and keeps the sampled waveform path. It removes redundant repeated inference, batches compatible MACs and pooling, verifies cached model/data bytes, and removes environments, build products and duplicate backups from the distribution. The uploaded original archive remains the provenance source.

## Behaviour and limits

- The CNN workspace defaults to `auto`. Choose `symbol` for deterministic constant symbols or `waveform` for the original sampled calculation. Standalone `PhysicalMAC` keeps its historical waveform default.
- Requested traces use waveforms. Explicit symbol execution rejects RIN, shot noise or linewidth settings. This is a reduction of the configured memoryless/ideal-integrator model; filtering, leakage, settling and native reset are separate work.
- Both user interfaces retain the choice in settings/run exports. Ordinary comparison is a single forward calculation per method. The separate benchmark randomizes method order and retains raw observations.
- Real neural `conv2d` is cross-correlation with an unflipped kernel, matching the inspected PyTorch/TensorFlow/Keras definitions. The asymmetric-kernel regression distinguishes it from true spatial convolution. Optional framework runtimes were not executed.
- The frozen checkpoint, disjoint 1149/288/360 split and all original results remain intact. Nine exact original source files are retained under `validation/snapshots/cnn_recorded/` so the historical source hashes remain verifiable.

## Completed verification

| Check | Result |
|---|---|
| Python regression | 133 passed |
| NumPy 1.26.4 compatibility subset | 88 passed |
| Frontend JavaScript unit tests | 11 passed |
| Browser workflows | 13 passed |
| Original Python graph conformance | 14/14 |
| Original GCC C++17 graph conformance | 14/14 |
| Frozen data/model/source audit | Passed, all 360 outputs preserved |
| Python F-class lint | Passed |
| MkDocs strict + Vite production build | Passed |

Tests ran on Linux x86-64, Python 3.12.14, NumPy 2.3.5 (and a separate NumPy 1.26.4 subset), one requested BLAS/OpenMP thread. Browser tests used Playwright 1.63.0 with a compatible Chromium 141 headless shell after the default browser download failed. They cover mode selection, actual backend counters, exports/imports, repeated benchmarking, stale results and ANN/CNN workflows. A bridge fixture checks desktop routing; it is not a built native desktop installer. Windows BAT files and INTERCONNECT were not executed here. Existing native Windows evidence is archived evidence, not a new run of this release.

## Timings must retain their workloads

The current five-block, one-warmup, 360-image release check has median waveform 11.512997321 s, symbol 0.032735914 s and NumPy 0.005292220 s. The waveform/symbol ratio is 351.6932; maximum logit difference is 2.1316282073e-14 with zero prediction changes. This descriptive Linux check was not an isolated idle-host campaign; all observations and environment fields are included. NumPy remains faster than the physical model in this comparison. Five blocks do not support a strong portable speed claim.

Historical 7.346/7.878 s waveform observations and the separate controlled three-request 315.98x cleanup remain archived, unchanged. The 736.68x INTERCONNECT result applies to a 49-setting scalar waveform workload on the author's Windows computer, with its original timing boundaries and 95% interval [699.26,808.08]. It is not a measured native CNN or chip speed. Do not multiply the ratios.

The fresh stationary RIN campaign remains complete: 23/23 unchanged checks pass, 2048 native and 4096 frozen-model trials, endpoint variance ratio 1.053187 and pointwise 90% interval [0.988915,1.119627]. Wider noise grids and noisy ANN/CNN validation remain separate. Historical zero/missing captures are retained in their original ledger.

## Citation and next work

The internship report is cited as Abhishek Singh, *Silicon Photonic Microring Resonators: FDTD Simulations, Coupling Optimization, Quality-Factor Analysis, and Cascaded Filter Architectures*, version 1.1, Zenodo, 18 June 2026, DOI 10.5281/zenodo.20744970. It is an author-deposited technical report, not peer reviewed. The Zenodo record is not presented as peer review or validation of later neural software.

Next: run the new benchmark on the author's Windows computer; validate native input/weight changes and capacitor reset; expand the fixed RIN operating-point grid; then validate noisy networks and account for converters, control, memory and hardware timing/energy. See `docs/site/next-steps.md`.
