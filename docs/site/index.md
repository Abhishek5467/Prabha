# Prabha

Prabha is an open-source, specification-first simulator for photonic and electronic computation. PEMAN is its first neuron demonstrator. The v0.1 preview connects validated component experiments, a complete perceptron and a fixed 4–3–2 ANN to an interactive Studio.

<a href="../">Open Studio</a> · <a href="../prabha-source.zip">Download preview source</a> · [Run locally](quickstart.md) · [Join the community](community.md)

## What works today

- ANN inference with editable inputs, converter resolutions and network coefficients; importable settings and complete run JSON exports.
- A stage-by-stage physical neuron trace and a reproducible 100-input batch check.
- Live MZM and laser experiments; 25 archived plots and four original CSV datasets.
- The current component Designer with 19 definitions, explicit legacy compatibility, schema validation and Python execution.
- Browser Python for static hosting, native FastAPI for local use, and a four-target Tauri packaging workflow with native exports.
- A public community forum and Discord chat, linked from Studio and documentation.

The baseline batch has RMS error **7.8644118 × 10⁻⁵**, maximum absolute error **1.7828381 × 10⁻⁴** and **0/100 output-ordering mismatches** against its analytical reference. These are numerical agreement results for one small fixed-weight network, not task accuracy or hardware benchmarks.

See [scope](model-scope.md) before interpreting results. CNN primitives and LLM evaluation are future work.

## Understand the model

Read the [extended user manual and mathematical reference](user-manual.md) for the worked B22 calculation, signal units, phase/noise interpretation, ANN protocol, professor questions and GitHub publishing steps.
