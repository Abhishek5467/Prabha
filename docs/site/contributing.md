# Contributing

Open an issue explaining the physical model or user problem. Keep changes reviewable and include reproduction instructions. The repository's `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md` describe the workflow.

For a new primitive: define units and assumptions, add schema/contract coverage where applicable, implement a deterministic reference, validate analytical limits, then add noise and uncertainty tests. Preserve source data and plot scripts. Do not silently relax tolerances to make a test pass.

For UI work: reuse `prabha.product.dispatch`, check error states and keyboard access, and verify both HTTP and static-browser transports. Keep numerical calculations out of frontend presentation code.

Run `python -m pytest tests -q`, the original conformance runner and the frontend build before opening a PR. Desktop changes need native OS checks.

Original project code is offered under the MIT license. Third-party dependencies retain their own licenses. Cite Prabha and the underlying physical models in academic work.
