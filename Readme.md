# प्रभा Prabha

**Prabha** is a photonic-electronic circuit and neural-inference simulator. It connects explicit source, modulator, detector, converter and accumulation models to a small ANN and a trained digit CNN. The Python engine evaluates the neural models; the C++ engine retains the original typed-graph conformance tests.

**v0.1.0-preview.4** adds selectable automatic/constant-symbol/waveform execution, a separate repeated benchmark, mode-preserving exports, a precise cross-correlation convention and verified asset caching. It retains the recorded model, data, historical results and sampled noise path. See [execution and mathematical scope](docs/site/execution.md) and [next steps](docs/site/next-steps.md).

[Open Studio](https://abhishek5467.github.io/Prabha/) · [Documentation](https://abhishek5467.github.io/Prabha/docs/) · [Forum](https://prabhacommunity5701.flarum.cloud/) · [Discord](https://discord.gg/RUdRMHBFp)

**Windows:** keep your existing Git-connected `Prabha` folder and apply the in-place updater there. Then double-click `RUN_PRABHA_STUDIO.bat`. For a first checkout, extract the source into `Prabha` and use the same launcher. Its first launch calls `SETUP_PRABHA.bat` to create an isolated environment and build the current Studio. Python 3.11+ and Node.js 22 LTS with npm are required. The lighter `RUN_CNN_DEMO.bat` works without Node and exposes the same execution selector. No checkpoint retraining is required.

Keep the original archive and native INTERCONNECT evidence separately. This source package excludes virtual environments, dependencies, duplicate backups and compiled outputs.

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

The batch uses seed 12345, fixed weights and 12-bit converters. It measures numerical agreement, not classification accuracy. ANN noise, transformer inference, physical hardware throughput and energy are not established. The original typed PEMAN and later standalone ANN have different converter/activation order. See [model scope](docs/site/model-scope.md).

Install the development dependencies before running the test commands:

```bash
python -m pip install -r requirements-dev.txt
python core-py/tests/run_conformance.py
python -m pytest tests -q
```

The current regression suite includes all 200 archived ANN outputs, all 360 frozen CNN outputs, malformed inputs, graph allocation limits, execution-mode equivalence and HTTP behaviour. See release/V0_1_PREVIEW_4.md for the actual check counts. Frontend unit and browser checks cover import/export, stale results, worker recovery, native bridge routing and repository subpath hosting. Desktop installers still require native build and acceptance checks; see [the release record](release/V0_1_PREVIEW_2.md).

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

Install `requirements-dev.txt` when running tests or desktop builds. Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). Original project code is MIT licensed; dependencies retain their own licenses. The release audit records outstanding publication and installer checks.

## Editable trained CNN

The **Trained CNN** now uses native React controls inside the same Studio as ANN, with the shared Python engine, activity lock, import/export and desktop Save bridge. It preserves settings and results when you switch between ANN and CNN. Edit an 8 x 8 image, convolution/dense weights and biases, DAC/ADC precision and ADC range; compare NumPy and Prabha; inspect all six stages and export their exact tensors. Changes clear previous results.

After the setup build, double-click **RUN_PRABHA_STUDIO.bat** on Windows, or run `bash RUN_PRABHA_STUDIO.sh` on Linux/macOS. This opens the complete application at `http://127.0.0.1:8000/#cnn`; ANN remains in the sidebar. Python 3.11+ is required; dependencies are installed on first launch. A source-only checkout needs the normal web build above first. The older `RUN_CNN_DEMO.bat` remains available for the standalone demo. See [CNN_STUDIO_INTEGRATION.md](CNN_STUDIO_INTEGRATION.md).

The reference checkpoint gets 354/360 (98.33%) with zero prediction disagreements. Select automatic, constant-symbol or waveform execution; the workspace measures the chosen physical path and the NumPy reference. Edited models/converters require fresh results. Noise, native full-CNN dynamics and hardware performance remain separate validation work.
