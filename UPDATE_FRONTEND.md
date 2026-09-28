# Update your local Prabha folder

This package is the editable source for the v0.1 frontend, shared Python model, documentation and desktop scaffold. It is based on the supplied Prabha archive. You control the GitHub push and deployment.

## 1. Apply the folder update

1. Make a backup of your current local Prabha folder, especially changes made since you supplied the archive.
2. Extract `Prabha_v0.1_Source.zip` somewhere outside that folder.
3. Open the extracted `Prabha-v0.1` folder. Copy its **contents** into your existing Prabha repository, merging matching folders and replacing the supplied files after reviewing local changes. Do not create an extra `Prabha-v0.1` folder inside your repository.
4. Keep your existing Git metadata and any unrelated work. The ZIP contains no `.git` directory and does not delete files.
5. Open a terminal in the repository root: the folder containing `Readme.md`, `requirements-web.txt`, `core-py` and `frontend`.

If you only have the older GitHub checkout, use the complete package: the ANN model and research assets in the uploaded archive are newer than that checkout. Copying only a React file is insufficient.

## 2. Run on Windows

Install Python 3.12 (or 3.11), Node.js 22.12 or later in the 22.x series, and Git if you do not already have them. Open a new PowerShell terminal after installation.

Check:

```powershell
py -3.12 --version
node --version
npm.cmd --version
```

From your Prabha root, run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
npm.cmd ci --prefix frontend/studio
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe frontend/web/server.py
```

Open **http://127.0.0.1:8000**. Keep the terminal running. Stop the server with Ctrl+C.

These commands use the environment's Python directly, so PowerShell activation is unnecessary. `npm.cmd` also avoids PowerShell's `npm.ps1` execution-policy issue. If Python 3.11 is installed instead, use `py -3.11` for the first command. If the Python launcher is absent but `python --version` reports a supported version, use `python -m venv .venv`.

For later runs, only the final server command is needed. After changing frontend code, run the Vite build again. After changing Python modules, documentation or archived assets, run `build_web_assets.py` and then the Vite build again.

## 3. Run on Linux or macOS

With Python 3.11/3.12 and Node.js 22.12+ installed:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-web.txt
npm ci --prefix frontend/studio
.venv/bin/python scripts/build_web_assets.py
npm run build --prefix frontend/studio
.venv/bin/python frontend/web/server.py
```

On Linux, install your distribution's matching Python venv package if creating the environment reports that `ensurepip` is unavailable.

## 4. Check the frontend

- Run the default ANN input and inspect the analytical and physical outputs.
- Select **Validate 100 inputs** with the reference weights and 12-bit converters. Expect RMS `7.8644e-5`, maximum error `1.7828e-4`, and `0/100` ordering mismatches.
- Open Single neuron, Component lab, Validation archive, System designer and Documentation.
- The Community link opens the local guide until you configure a real community address.

To edit React with live reload, keep the Python server running and use a second terminal:

```powershell
npm.cmd run dev --prefix frontend/studio
```

Open http://localhost:5173. The production preview remains at port 8000.

## 5. Connect the free community when it exists

Create the community through https://www.discourse.org/free and choose an available address. Then edit this public configuration file:

`frontend/studio/public/community.json`

Its initial content is:

```json
{
  "url": ""
}
```

Replace the empty string with the actual HTTPS address Discourse gives you. Do not invent a URL or put passwords/API keys in this file. The Studio Community link and documentation Join link read the same setting. An empty or invalid address keeps the guide available and hides the Join link.

Run the frontend build again to copy the changed configuration into `dist`. Creating or editing this file does not create a Discourse account or community. Posts and member accounts are stored by Discourse, separately from your source repository.

## 6. Review and push to GitHub

From your existing repository, review the changes and remote first:

```bash
git status
git diff --stat
git remote -v
git switch -c prabha-frontend-v01
git add .
git diff --cached --stat
git commit -m "Add Prabha Studio, documentation and community configuration"
git push -u origin prabha-frontend-v01
```

Use a different branch name if that branch already exists. Confirm `origin` is your intended Prabha repository. Open a pull request on GitHub, inspect the validation workflow, and merge when ready. If your folder is not a Git checkout, clone your repository first and copy the package contents into that clone.

Generated builds, Python environments, npm dependencies, credentials and local environment files are excluded by `.gitignore`. The source package also excludes those files.

## 7. Publish with your free GitHub Pages address

Once the reviewed changes are on your default branch:

1. Open the repository's **Settings → Pages** and select **GitHub Actions** as the build/deployment source.
2. Open **Actions → Publish web preview → Run workflow** and select your updated default branch.
3. Wait for the workflow to succeed and use its returned deployment URL. For the existing repository, the usual project address is `https://abhishek5467.github.io/Prabha/`.

The workflow builds the Studio and documentation together. It is manually triggered; pushing code alone does not deploy it. The browser runs the Python model with Pyodide, so this deployment does not require an AWS Python server. The first browser simulation requires an internet connection to download the runtime.

## Files you will usually edit

| Project-relative path | Purpose |
|---|---|
| `frontend/studio/src/main.jsx` | Studio views and interactions |
| `frontend/studio/src/style.css` | Studio visual styling |
| `frontend/studio/public/community.json` | Community address |
| `docs/site/` | Documentation content |
| `mkdocs.yml` | Documentation navigation and build configuration |
| `core-py/prabha/product.py` | Shared operation dispatcher |
| `core-py/prabha/systems/` | Reusable neuron and ANN model |
| `frontend/web/server.py` | Local Python API/server |
| `.github/workflows/pages.yml` | Manual GitHub Pages deployment |

The original graph editor is preserved under `frontend/web/index.html`. The new Studio is built from `frontend/studio`; starting the server without that build will not show the new frontend. Full desktop installers and CNN work are separate later steps.
