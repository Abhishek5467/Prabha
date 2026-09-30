# Prabha 0.1.0-preview.2 release record

Prepared 29 September 2026 against GitHub main commit `fe6c2087f6c8e09f983c216948e70522902cab80` (Connect Prabha community forum).

## Scope

This is a product and documentation update before CNN work. The Python model formulas, reference coefficients, original experiments and saved figures/datasets are preserved. The shared dispatcher version changes to identify the new interface release.

Implemented:

- A getting-started workspace, reference result context, workspace bookmarks and forum/Discord navigation.
- Validation of empty inputs/network dimensions, clearing results after edits and disabled controls during runs.
- Complete run JSON with request/result/version/engine/timestamp, ANN settings import/export, component exports and batch CSV metadata.
- Browser worker failure recovery and HTTP error handling.
- Native Save-dialog commands and HTTPS link opening; desktop JS routing covered independently from OS installation.
- Four native packaging jobs (Windows x64, Linux x64, Intel Mac, Apple Silicon), sidecar protocol checks and artifact hashes/source manifest.
- Updated setup, Studio, export/API, community, troubleshooting, Pages and desktop documentation.

## Verification

- Python product regression: **16 passed**, including all 200 archived ANN outputs.
- Original conformance fixtures: **Python 14/14; C++17 14/14**.
- Frontend unit checks: **6 passed** (settings/import validation, CSV metadata, worker crash recovery and API reconnection).
- Chromium end-to-end checks: **4 passed**, using the real local Python API; includes exports/import, stale results, components, native bridge routing, mobile layout and a `/Prabha/` static path.
- Static Pyodide run under `/Prabha/`: reproduced **7.8644e-5 RMS, 1.7828e-4 maximum error, 0/100 ordering mismatches**. Browser graph execution returned 14 probes. No page JavaScript errors.
- Strict MkDocs and production Vite builds passed. Desktop and 390px mobile screenshots reviewed for layout.
- Fresh Linux PyInstaller sidecar passed the reference batch, bundled graph-asset check, invalid-input check and malformed-JSON check from a separate temporary working directory. This verifies the Python bundle, not a Tauri installer.

The static runtime check used the environment's configured network proxy and a certificate exception confined to the local QA browser. The product contains no proxy settings or certificate bypass.

Browser native-bridge tests stub the OS commands while using actual Python computation. They check routing and payloads, not real native dialogs or an installer.

## Native release gate

The authoring environment has no Rust/Tauri system toolchain. The updated Rust wrapper and native workflow must be compiled on the native runners after the source is pushed. No installers are supplied as verified downloads.

| Target | CI build | Clean-machine install / offline run / exports | Tester and artifact hash |
|---|---|---|---|
| Windows x64 | Pending | Pending | — |
| Linux x64 | Pending | Pending | — |
| macOS Intel | Pending | Pending | — |
| macOS Apple Silicon | Pending | Pending | — |

Use `docs/site/desktop.md` for the checks. Record actual results and SHA-256 hashes before publication. The desktop bundle version remains 0.1.0; the Studio and Python engine report 0.1.0-preview.2.

## Publication

This work changes the local source folder. It does not push commits, run remote workflows, deploy Pages, publish releases or send community messages. The owner applies/reviews the folder update, pushes, then starts new **Publish web preview** and **Desktop packages** runs as needed.

Current addresses:

- Studio: https://abhishek5467.github.io/Prabha/
- Docs: https://abhishek5467.github.io/Prabha/docs/
- Forum: https://prabhacommunity5701.flarum.cloud/
- Discord: https://discord.gg/RUdRMHBFp

The older `RELEASE_AUDIT.md` is a historical record of the first archive restoration, including its then-pending community setup. Its old Discourse/setup notes do not describe today's community.
