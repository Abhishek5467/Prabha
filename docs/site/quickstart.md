# Quick start

## First run in the browser

1. Open [Prabha Studio](https://abhishek5467.github.io/Prabha/).
2. Select **ANN inference**. Keep the default inputs and 12-bit DAC/ADC.
3. Select **Run inference**. On static hosting, the first run downloads browser Python and its numerical packages. Keep the tab open while the engine status shows loading.
4. Inspect the analytical and physical-model outputs.
5. Select **Validate 100 inputs**. With the reference network, expect RMS error about **7.8644e-5**, maximum error **1.7828e-4**, and **0/100** output-ordering mismatches.
6. Export **batch JSON** and **CSV**. The JSON includes the network, converter precision, seed and engine version.

The batch uses 100 sampled inputs with seed 12345; it ignores the four input sliders. It uses the network and converter settings currently selected. Select **Reset reference** to restore all ANN defaults.

Static hosting requires an internet connection to jsDelivr for the initial runtime download. Computation runs in the browser; no Prabha simulation server receives your inputs. Offline browser startup is not promised. See [troubleshooting](troubleshooting.md) if loading fails.

## Run locally on Windows

Install Python 3.11 or 3.12 and Node.js 22. Open **Command Prompt** in your Prabha folder:

```bat
cd /d "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
npm.cmd ci --prefix frontend/studio
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe frontend/web/server.py
```

If Python 3.11 is installed, use `py -3.11` instead. If the virtual environment already exists, reuse it and skip its creation.

Open [localhost:8000](http://127.0.0.1:8000). The Studio now uses **Python API**. Keep the terminal open while working. Press **Ctrl+C** to stop the server.

In PowerShell, replace the first line with `Set-Location "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"`. The remaining commands work unchanged.

## Run locally on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
python frontend/web/server.py
```

Run these commands from the repository root and open port 8000.

## Develop the frontend

Keep the Python server running. In another terminal, run `npm run dev --prefix frontend/studio` (`npm.cmd` on Windows). Open port 5173. Vite proxies API requests to port 8000. Rebuild browser assets after changing Python modules or documentation.

## Check static hosting locally

```bash
python -m http.server 8080 --directory frontend/studio/dist
```

Open port 8080. There is no Python API on that port, so the Studio uses **Browser Python**. Serve the site through HTTP(S); opening its HTML as a local file will not work.

For native applications, see [desktop builds](desktop.md).
