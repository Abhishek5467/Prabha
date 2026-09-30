# Apply the complete Designer model update — preview.3

This update is based on the supplied **Prabha(2).zip** (SHA-256 `d8b831c31c848c3bdb58f795f66db9d8f68e9df0842819eaaef834502378c983`). It includes the earlier preview.2 frontend/community improvements and the current component integration. There is no prerequisite patch to apply first.

## 1. Extract the update outside your project

Extract `Prabha_Designer_Complete_Update.zip`, then open the extracted `Prabha-Designer-preview3` folder. It contains `START_HERE.md`, `FILE_BY_FILE.md`, `ALL_FILE_CODE.md`, `updated-files`, `apply_update.py` and a manifest. Your existing project remains the destination.

`updated-files` contains **complete files**, not code fragments. If copying manually, the relative path inside it is the exact destination beneath your Prabha root. For example:

| Package file | Destination in your project | What to do |
|---|---|---|
| `updated-files/frontend/web/index.html` | `Prabha/frontend/web/index.html` | Replace the entire file |
| `updated-files/core-py/prabha/blocks/component_kernels.py` | `Prabha/core-py/prabha/blocks/component_kernels.py` | Create this new file |
| `updated-files/spec/blocks/model_mzm.json` | `Prabha/spec/blocks/model_mzm.json` | Create this new definition |
| `updated-files/spec/examples/neuron.json` | `Prabha/spec/examples/neuron.json` | Create the folder and example file |
| `updated-files/docs/site/designer.md` | `Prabha/docs/site/designer.md` | Create the model guide |

`FILE_BY_FILE.md` lists **every** destination and whether to create, replace or synchronize it. `ALL_FILE_CODE.md` contains the complete text of each supplied file, with its path directly above its code block. Copy file contents only, excluding Markdown fences. No individual-line search or pasted snippet is required.

Do not put an `updated-files` folder inside your project. Do not delete the project or copy over its Git history or virtual environment.

## 2. Apply automatically, with backup

Open **Windows Command Prompt** in the extracted update folder. Run this read-only check:

```bat
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha" --check
```

If it passes, apply:

```bat
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
```

The script checks every file before writing, recognizes the uploaded baseline and the already-applied preview.2 versions, and skips files already current. It prints a backup folder beside your project and preserves unrelated files. If you have other local edits, it stops before copying and lists the conflicting paths; merge those deliberately using the supplied full files. Keep the backup until you finish reviewing.

The script performs no Git commands, installs, builds, network calls, commits, pushes or deployments. A failed write restores files already touched. Applying the same update twice is safe.

If the `py` launcher is unavailable, replace it with the full path to your installed Python executable. The updater itself needs only Python's standard library.

## 3. Build the frontend and generated Python bundle

Use your existing Python 3.11/3.12 environment and the project's Node setup (Node 22.12+ in the 22.x series). In Command Prompt:

```bat
cd /d "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci --prefix frontend/studio
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe frontend/web/server.py
```

If `.venv` is missing, create it first with `py -3.12 -m venv .venv`. PowerShell users should use `Set-Location` instead of `cd /d`; the explicit Python and `npm.cmd` commands also work there.

Open [Studio locally](http://127.0.0.1:8000), then **Component designer**. You can also open [the direct local Designer](http://127.0.0.1:8000/designer).

**Always run `build_web_assets.py` before the Vite build.** It generates `frontend/studio/public/designer.html`, `prabha-python.zip`, docs and the downloadable source archive. Editing source without rebuilding this bundle leaves old Python running on Pages. Do not paste edits into `dist`, generated `public/designer.html` or inside `prabha-python.zip`.

## 4. Check the result

- Studio reports **0.1.0-preview.3**; Designer header says **Component models · preview.3**.
- Default palette contains **19 current definitions**. Legacy blocks are behind **Show legacy blocks**.
- Default component neuron: noise off, duration **4 ns**, seed **1**. Run; `adc.code` final is **2616** and `adc.voltage` final is **0.6388278388278388**.
- Expanded component chain produces the same final value and exposes every MAC stage separately.
- Select the MZM, MAC, laser, detector, TIA, capacitor, amplifier or activation block. The Inspector displays its full model parameters and assumptions.
- Try the noisy receiver and leakage/rails examples. Changing seed reproduces a different noise realization; changing it back reproduces the original. Deterministic nonlinearities are independent of the global noise switch.
- Save a Designer project, reopen it and verify its settings. Export a run JSON for its request/result record. Plain `.prabha` export remains the original netlist format.
- In the ANN workspace run **Validate 100 inputs**: RMS **7.8644e-5**, max **1.7828e-4**, ordering mismatches **0/100**.

See `docs/site/designer.md` for all block defaults/equations and `release/DESIGNER_INTEGRATION_2026_09_30.md` for actual verification.

## 5. Push and refresh Pages yourself

Stop the local server with Ctrl+C when finished. Review `git status` and `git diff --stat`; commit the intended source changes and push through your normal GitHub workflow. Include the new `model_*.json`, example JSONs, Python adapter, tests and documentation. The workflow builds generated assets; dependencies and build directories remain excluded.

For the new commit, confirm **Validate prototype** passes, then start a **new Publish web preview** workflow run on that branch. Re-running an old deployment uses its old commit. Refresh the live site and verify preview.3. The current Pages route uses browser Python and requires no additional AWS backend for these operations.

Existing forum and Discord addresses are preserved. This update does not change your domain or hosting configuration.

## Desktop and scope

The same current Python models are included by the desktop sidecar builder. A Linux Python bundle was exercised during this update; native Windows/macOS/Linux Tauri installers still require their native CI build and installation checks. Use `docs/site/desktop.md` for those gates; no preverified installers are included.

This package completes the integration of the models implemented in the supplied ZIP. It does not invent additional noise/device physics or promise that future releases will never need corrections. The new model revision is `components-1`. Legacy IDs remain to preserve old saved designs. New current-model operations run through Python; C++ is still the legacy conformance engine.

## Optional clean source copy

The handoff also includes `Prabha-preview3-full-source.zip`, a clean complete source snapshot without environments, Git history, dependencies or generated builds. Use it for review or a separate fresh folder. For your existing Git repository, prefer the guarded updater so your repository identity and unrelated work are preserved.
