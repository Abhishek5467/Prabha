# 0.1.0-preview.3 — 30 September 2026

- Current component classes integrated into 19 Designer blocks, with 4 examples.
- Explicit laser RIN/phase, PD shot noise and TIA noise switches and run seed.
- MZM nonlinear transfer, converter quantization/ranges, capacitor leakage, amplifier rails and activation threshold/gain exposed.
- Integer ADC code and reconstructed voltage outputs separated.
- Complete project/run exports, sample-index/phase probes and stale-result protection.
- Legacy graph semantics retained; ANN regression calibration unchanged.
- See `release/DESIGNER_INTEGRATION_2026_09_30.md` for verification and scope.

# Changelog

## 0.1.0-preview.2 — 2026-09-29

- Added Get started, direct forum/Discord links and workspace bookmarks.
- Clear results when their settings change; validate empty inputs and network dimensions before running.
- Export complete run requests/results with engine/version/timestamp metadata; import ANN settings and runs.
- Added component JSON exports, batch CSV metadata and accessible figure previews.
- Recover pending requests after browser worker failures and check HTTP transport errors.
- Added native Save dialogs and system-browser handling for external links.
- Added separate Windows x64, Linux x64, Intel Mac and Apple Silicon packaging jobs, protocol smoke checks and artifact hashes.
- Updated Windows setup, Studio usage, community, Pages deployment, troubleshooting and desktop release documentation.
- Preserved numerical models and archived evidence. Native installer builds/installation checks remain pending.

## 0.1.0-preview.1 — 2026-09-28

- Restored later component, perceptron and ANN experiments from the supplied archive beyond the original M0 Git commit.
- Extracted reusable perceptron/ANN functions while preserving the archived 100-input outputs.
- Added Studio inference, traces, live component experiments, evidence gallery and downloads.
- Added shared bounded JSON operations for FastAPI, Pyodide and a native desktop sidecar.
- Preserved the original graph editor and documented its distinct numerical path.
- Added docs, community contribution templates, MIT licensing and citation metadata.
- Added web deployment and desktop build workflows.
- Added 16 product regression/transport checks; original 14-fixture Python/C++ suites remain intact.

This is a research preview. CNN, transformer inference, measured hardware calibration and signed native installer releases remain future work. No new scientific performance result is claimed by the interface migration.
