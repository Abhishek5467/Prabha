# Designer component integration — 30 September 2026

Release **0.1.0-preview.3**, model revision **components-1**. Baseline: supplied `Prabha(2).zip`, SHA-256 `d8b831c31c848c3bdb58f795f66db9d8f68e9df0842819eaaef834502378c983`.

## What changed

The Designer previously called simplified PEMAN kernels. It now defaults to 19 current definitions whose adapters reuse the existing Python CW laser, MZM, detector, TIA, DAC, ADC, capacitor, amplifier and activation classes. Supporting blocks expose signal sources, inverse encoding, signed weights, ideal attenuation, splitting and balanced subtraction. The compact MAC has an equivalent expanded example.

All established controls are exposed: RIN and linewidth, detector shot/dark current, receiver bandwidth/input noise, MZM bias/half-wave voltage/loss, converter precision/ranges, capacitor initial state/leakage, amplifier bias/rails and activation gain/threshold. Global noise only gates stochastic terms. Model help distinguishes implemented effects from ideal assumptions.

Current ADC code and voltage are separate outputs. The reference uses activation before ADC, matching B22. Projects save layout and settings; run exports save the request and reported results. Old graph IDs remain available and are not silently migrated. The known MZM docstring bias factor was corrected to match its existing implementation. Invalid negative-power RIN realizations now raise a clear error rather than yielding NaN. The ANN calibration and archived experimental data are unchanged.

## Integration evidence

| Gate | Observed result |
|---|---|
| Python product + model integration suite | **43 passed** (16 existing + 27 current integration cases) |
| B22 correspondence | Compact and expanded reference final output **0.6388278388278388**, integer ADC code **2616** |
| Component tests | Multiple precisions and edge inputs; noisy compact/expanded parity; seed replay; phase/power distinction; TIA class correspondence; leakage/rails/threshold; shot variance; range/size errors and code/voltage round-trip |
| Original Python/C++ conformance | **14/14 each**; coverage is the legacy fixtures |
| Frontend unit checks | **6 passed** |
| Chromium end-to-end suite | **7 passed**, real Python API; Designer settings/exports/imports/errors/noise scope/legacy plus existing Studio checks |
| Static `/Prabha/` browser runtime | Actual **Browser Python / Pyodide** ran all four new examples, forwarded validation details, and reproduced the reference ANN batch; no page JavaScript errors |
| ANN archive regression | RMS **7.864411795585e-5**, max **1.782838135357e-4**, **0/100** ordering mismatches; all 200 archived outputs compared |
| Build | Strict MkDocs + production Vite succeeded |
| Standalone Python bundle | Fresh Linux PyInstaller bundle passed from an unrelated working directory: metadata, original graph, all four component examples, reference ANN batch, invalid request and malformed JSON |

The static browser check used this environment's configured network proxy and a certificate exception limited to the QA browser. No proxy configuration or certificate bypass is in the product. Screenshots of the reference graph and parameter Inspector were reviewed. The Designer uses local font fallbacks and loads its optional plot-ZIP helper asynchronously, so an unavailable font/ZIP CDN does not block the model interface.

## Interpretation for the BTP record

This is a **software integration milestone**, not a new physical-validation claim. The Designer now exposes the component models already established by the experiments. Its four sequential 1 ns symbols reproduce the final charge of the B22 parallel-current reference with leakage disabled. Equal final values do not establish equal latency or hardware architecture. This record can be cited in the living BTP development log; it does not revise the historical internship experiments.

The fixed ANN baseline remains noiseless. No noisy ANN accuracy, energy, fabricated device, CNN or LLM/LMM result is established here. Ideal weights, behavioral activation, power-only MZM transfer and other scope limits remain documented in `docs/site/model-scope.md`.

## Remaining native release gate

A Python bundle is not a verified native GUI installer. Rust/Tauri compilation and clean-machine Windows/Linux/macOS installation, GUI, offline behavior and export checks must run on their intended native targets. The current environment does not have the Rust/Tauri toolchain, so no native installer is represented as tested. The existing desktop workflow builds these targets after the owner pushes.

No remote repository changes, Pages deployment, release publication or community messages were performed.
