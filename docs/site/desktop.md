# Desktop builds

The source includes a Tauri application, bundled documentation and a native Python sidecar. **Installers remain candidates until built and checked on their target OS.** Windows, macOS and Linux installation testing is still pending.

## Create candidates on GitHub

After pushing the updated source:

1. Open **Actions → Desktop packages → Run workflow** on the updated branch.
2. Wait for all four jobs. Each builds Python natively, runs protocol/reference-batch checks, then creates an installer.
3. Download the workflow artifacts.
4. Keep `manifest.json` and `SHA256SUMS.txt` with each installer. They identify the source commit, Studio version, platform and file hashes.
5. Complete the checks below before attaching candidates to a GitHub release.

The workflow does not publish a release. Artifact retention is 14 days; download candidates you intend to keep. See [GitHub's runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

| Candidate | Native runner | Package |
|---|---|---|
| Windows x64 | Windows 2022 | NSIS (.exe) |
| Linux x64 | Ubuntu 22.04 | Debian and AppImage |
| macOS Intel | macOS 15 Intel | DMG |
| macOS Apple Silicon | macOS 15 arm64 | DMG |

The packaging version is 0.1.0; Studio and the engine report 0.1.0-preview.3. The manifest distinguishes preview builds. Windows ARM and Linux ARM are not in this matrix.

## Build on your computer

Install Python 3.11/3.12, Node.js 22, Rust stable and the [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) for the target OS. Python and Rust must have the same native architecture.

From the repository root:

```bash
python -m pip install -r requirements-dev.txt
npm ci --prefix frontend/studio
python scripts/build_web_assets.py
npm run build --prefix frontend/studio
npm ci --prefix desktop
python scripts/build_sidecar.py
npm run build --prefix desktop
```

On Windows use the virtual environment's Python and `npm.cmd`, as in [quick start](quickstart.md). Installers appear under `desktop/src-tauri/target/release/bundle/`.

The sidecar builder rejects a target triple different from the Rust host and mismatched Python/Rust architectures. Build natively on each target; copying or renaming a binary does not change its architecture.

The wrapper adds Save dialogs and opens HTTPS community/project links in the default browser. Bundled docs have a **Back to Prabha Studio** link. Core ANN, neuron and component computation uses bundled Python, without a runtime CDN. The legacy designer's plot ZIP export still loads JSZip from its existing CDN.

## Installation checks

For each candidate record OS version, architecture, artifact hash, source commit, tester/date and these results:

- Install and launch without a separate Python installation.
- Disconnect the network. Run inference, the reference batch, neuron trace and both component experiments.
- Confirm RMS 7.8644118e-5, maximum error 1.7828381e-4 and 0/100 ordering mismatches.
- Export JSON and CSV through Save dialogs; verify content and cancellation. Import ANN settings and rerun.
- Open bundled docs and return. Enlarge an archive figure and save it.
- Reconnect and open the forum/Discord in the system browser.
- Close, reopen and uninstall; record any failures.

Record results in `release/V0_1_PREVIEW_2.md`. A sidecar test or successful installer build alone does not establish GUI/install compatibility.

Trusted Windows signing and macOS Developer ID/notarization are separate release tasks. Unsigned candidates may trigger OS prompts. Review [Tauri distribution guidance](https://v2.tauri.app/distribute/) before public distribution.
