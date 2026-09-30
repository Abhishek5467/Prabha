# Prabha preview.3: clarity and academic review update

Apply this after the complete preview.3 updater that you already ran. It changes labels/help and documentation without changing the component equations or ANN baseline.

## Changes

- Generic source nodes show x, w or transmission roles based on connected current-model consumers. Their normalized controls are explicitly dimensionless. Actual electrical voltages still use volts; exported signal kinds remain compatible.
- Optical phase is enabled only for optical probes, with its power/phase meaning explained.
- Results identify current or legacy model profiles correctly.
- A fresh digital source uses valid integer codes (0,1024,2048,4095).
- The full mathematical/user guide is added to the documentation website, with native MathML equations that do not require an external rendering CDN.
- Source descriptions, browser regression checks and documentation navigation are updated.

## Apply

Extract the new review ZIP outside your repository. Open Command Prompt in `Prabha-Clarity-Update`:

```bat
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha" --check
py apply_update.py "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
```

The script requires the preview.3 versions of modified files, backs up all replacements and verifies them. Already-current files are skipped. Conflicting local edits stop the entire update before writing; use the complete `updated-files` versions for a deliberate merge. No Git commands or deployment are run by the updater.

## Build and push

```bat
cd /d "C:\Users\samay\OneDrive\Documents\Research_Works\Prabha"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci --prefix frontend/studio
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe frontend/web/server.py
```

Open http://127.0.0.1:8000/designer and run the default neuron. Expect ADC code **2616**, readout **0.6388278388278388**, distinct x/w labels and phase disabled for the ADC probe. The noisy receiver's laser probe should permit phase selection. Open the new **User manual and mathematics** page in Documentation.

Stop the server with Ctrl+C. Review the changed and staged paths before committing:

```bat
git status
git diff --stat
git remote -v
git branch --show-current
git add .
git diff --cached --stat
git commit -m "Clarify Designer signals and document the model mathematics"
git push
```

If Git says the branch has no upstream, use `git push -u origin YOUR_BRANCH`, substituting the printed branch name. Keep unrelated changes out of the commit. Do not force-push to solve a rejected update.

In GitHub Actions, check **Validate prototype** on the new commit, then start a **new Publish web preview** run on that branch. Re-running an old deployment uses its old commit. Existing Pages/community addresses remain unchanged. No AWS backend is needed for the current browser-Python mode.

## Editing the manual

`docs/manual/Prabha_User_Manual.md` is the editable study source. Its final catalogue is generated from the block JSON definitions. `docs/site/user-manual.md` is generated HTML/MathML checked into the repository. Ordinary web builds need no new dependency. To revise the guide later, install Pandoc and run `python scripts/build_manual.py`, then rebuild the web assets and frontend.

The academic PDFs, editable LaTeX and PPTX with speaker notes are supplied separately in the review package. They are review drafts. Check author/mentor attribution, declarations, release identifiers and venue formatting before submitting. The LLM paper remains a research proposal; its hypotheses are not completed benchmark results.
