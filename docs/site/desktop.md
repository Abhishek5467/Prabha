# Desktop application

The Tauri scaffold targets Windows, macOS and Linux with the same Studio interface and a native Python simulation sidecar. This release provides build infrastructure; installers must pass native smoke checks before being described as supported downloads.

## Build on each target OS

Install Python 3.11/3.12, Node.js 22 LTS, Rust stable and the [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) for that OS.

```bash
python -m pip install -r requirements-dev.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
npm ci --prefix desktop
python scripts/build_sidecar.py
npm run build --prefix desktop
```

The sidecar is built for the current Rust host triple. Cross-platform installers are built on native CI runners, not cross-compiled from one OS. Use the **Desktop packages** GitHub Actions workflow; it uploads per-platform build artifacts without creating a public release automatically.

Windows signing and macOS Developer ID/notarization require credentials and may incur costs. Unsigned prototype packages may trigger operating-system trust prompts. Signing is a release task, not a prerequisite for local development. Linux CI targets AppImage and Debian packages.

## Acceptance check

On a clean machine: launch the app without Python installed, disconnect the network, run the reference ANN and 100-input validation, export a CSV, open docs, then close/reopen the application. Confirm RMS 7.8644118e−5 and no crashes. Only publish installers that pass this check.
