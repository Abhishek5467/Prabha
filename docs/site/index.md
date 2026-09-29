# Prabha

Prabha is an open-source, specification-first simulator for photonic and electronic computation. PEMAN is its first neuron demonstrator. The v0.1 preview connects validated component experiments, a complete perceptron and a fixed 4–3–2 ANN to an interactive Studio.

[Open Studio](../) · <a href="../prabha-source.zip">Download preview source</a> · [Run locally](quickstart.md) · [Join the community](community.md)

## What works today

- ANN inference with editable inputs, converter resolutions and network coefficients.
- A stage-by-stage physical neuron trace and a reproducible 100-input batch check.
- Live MZM and laser experiments; 25 archived plots and four original CSV datasets.
- The existing typed graph designer, schema validation and Python conformance engine.
- Browser Python for static hosting, native FastAPI for local/server use, and a Tauri desktop build scaffold.

The baseline batch has RMS error **7.8644118 × 10⁻⁵**, maximum absolute error **1.7828381 × 10⁻⁴** and **0/100 output-ordering mismatches** against its analytical reference. These are numerical agreement results for one small fixed-weight network, not task accuracy or hardware benchmarks.

See [scope](model-scope.md) before interpreting results. CNN primitives and LLM evaluation are future work.
