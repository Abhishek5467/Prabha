# प्रभा Prabha

**Prabha** (प्रभा, Sanskrit for *radiance*) is an indigenous photonic-electronic
system simulator in the spirit of Lumerical INTERCONNECT — spec-first,
dual-engine, and built to grow toward full photonic-EDA capability.

Open photonic-electronic simulation, from typed device models to a validated small ANN.

**v0.1.0-preview.3** connects the existing experiments to a React/Vite Studio, shared Python interface, documentation and desktop packaging. This cumulative update adds a 19-block component Designer, MZM nonlinearity, converter quantization, TIA noise/bandwidth, capacitor leakage, amplifier saturation and activation thresholds, alongside guided onboarding, reproducible exports/imports, connected communities and native packaging workflows. PEMAN remains the first neuron demonstrator; Prabha is the broader simulator.

[Open Studio](https://abhishek5467.github.io/Prabha/) · [Documentation](https://abhishek5467.github.io/Prabha/docs/) · [Forum](https://prabhacommunity5701.flarum.cloud/) · [Discord](https://discord.gg/RUdRMHBFp)

**Updating your existing folder?** Start with [UPDATE_DESIGNER.md](UPDATE_DESIGNER.md) for Windows commands, folder merging, the community address setting, and your GitHub push/Pages workflow.

## Try the prototype locally

Requires Python 3.11/3.12 and Node.js 22 LTS.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
python frontend/web/server.py
```

Open http://127.0.0.1:8000. For a static deployment, serve `frontend/studio/dist`; the browser downloads Pyodide and executes the same Python models. The first static-mode run requires internet access. See [deployment](docs/site/deployment.md).

## Included

- Four-input, three-hidden-neuron, two-output ANN inference with editable inputs, coefficients and converter resolutions.
- Full neuron traces, reproducible 100-input validation, complete run JSON/CSV exports and ANN settings import.
- Live MZM and CW laser experiments; 25 archived figures and 4 datasets.
- Original graph designer and typed Python engine.
- MkDocs documentation and community contribution files.
- Tauri desktop source with native Save dialogs, sidecar checks, hashes and separate Windows/Linux/Intel Mac/Apple Silicon build jobs.

## Evidence and boundaries

| Check | Result |
|---|---|
| Original shared fixtures | Python 14/14; GCC C++ 14/14 |
| ANN output RMS error | 7.864411795585 × 10⁻⁵ |
| ANN maximum absolute error | 1.782838135357 × 10⁻⁴ |
| Output-ordering mismatch | 0/100 |

The batch uses seed 12345, fixed weights and 12-bit converters. It measures numerical agreement, not classification accuracy. ANN noise, transformer inference, measured throughput and energy are not established. The original typed PEMAN and later standalone ANN have different converter/activation order. See [model scope](docs/site/model-scope.md).

Install the development dependencies before running the test commands:

```bash
python -m pip install -r requirements-dev.txt
python core-py/tests/run_conformance.py
python -m pytest tests -q
```

The 16 product checks include all 200 archived ANN outputs, malformed inputs, graph allocation limits and HTTP behaviour. Frontend unit and browser checks cover import/export, stale results, worker recovery, native bridge routing and repository subpath hosting. Desktop installers still require native build and acceptance checks; see [the release record](release/V0_1_PREVIEW_2.md).

```bash
npm test --prefix frontend/studio
npx --prefix frontend/studio playwright install chromium
npm run test:ui --prefix frontend/studio
```

Build web assets and the frontend before UI tests. They start local servers on ports 8000 and 8081.

## Source map

| Folder | Purpose |
|---|---|
| `spec/`, `blocks-lib/` | Original schemas, rules, fixtures and compound library |
| `core-py/prabha/` | Python models, graph engine and shared operations |
| `core-py/experiments/` | Original experiment record |
| `core-cpp/` | Original C++17 conformance engine |
| `frontend/studio/` | New Studio UI and browser Python transport |
| `frontend/web/` | FastAPI server and original designer |
| `desktop/`, `scripts/` | Desktop wrapper and reproducible asset/sidecar builders |
| `docs/site/` | Documentation and community website source |
| `tests/`, `release/` | Regression checks and release audit |

Install `requirements-dev.txt` when running tests or desktop builds. Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). Original project code is MIT licensed; dependencies retain their own licenses. The release audit records outstanding publication and installer checks. CNN is the next scientific milestone after the ANN prototype freeze.
