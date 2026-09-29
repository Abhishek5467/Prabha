# Quick start

Use Python 3.11 or 3.12 and Node.js 22 LTS. From the repository root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
python frontend/web/server.py
```

Open `http://127.0.0.1:8000`. The same server provides the frontend and `/api/execute`.

On Windows, you can use `.\.venv\Scripts\python.exe` instead of activating the environment and `npm.cmd` instead of `npm`. See `UPDATE_FRONTEND.md` in the source package for the complete PowerShell commands.

## Frontend development

Keep the Python server running and, in another terminal, run `npm run dev --prefix frontend/studio`. Vite proxies `/api` to port 8000. Rebuild browser assets after changing Python modules or documentation.

## Static web mode

After building, run `python -m http.server 8080 --directory frontend/studio/dist` and open port 8080. On the first simulation, the browser downloads Pyodide and its NumPy/JSON Schema dependencies. Inputs stay in the browser in this mode. An internet connection to jsDelivr is required for the initial runtime download; offline browser operation is not promised.

The static page must be served through HTTP(S), not opened as a `file://` document.
