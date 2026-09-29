# Architecture

Prabha keeps the numerical implementation in Python and exposes one JSON dispatcher to three clients.

| Layer | Source | Responsibility |
|---|---|---|
| Model contract | `spec/` | Five schemas, 18 validation rules, 11 primitives and 14 fixtures |
| Typed reference engine | `core-py/prabha/` | Registry, graph checks, compound flattening, signals and kernels |
| C++ engine | `core-cpp/` | Original contract conformance |
| Reusable inference | `core-py/prabha/systems/` | Complete neuron and fixed 4–3–2 ANN |
| JSON interface | `core-py/prabha/product.py` | Bounded operations and structured results |
| Web transport | `frontend/web/server.py` | FastAPI HTTP interface |
| Browser transport | `frontend/studio/public/python-worker.js` | Pyodide worker running the same Python source |
| Studio | `frontend/studio/src/` | React inputs, computation traces, charts and exports |
| Desktop | `desktop/src-tauri/` | Tauri shell invoking a bundled Python sidecar |

The browser bundle is rebuilt from the same Python modules used by FastAPI. It is not a JavaScript approximation of the ANN. The desktop sidecar is built with PyInstaller on each target OS; shipping a prebuilt Python environment avoids asking desktop users to install Python separately.

The original 48 experiment files remain the experiment record. Forty-seven have content; the linewidth sweep is a placeholder. Archived data are copied, not regenerated, by the frontend build.
