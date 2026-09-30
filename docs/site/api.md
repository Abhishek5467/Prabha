# API

`GET /api/health` returns version and native engine status. `POST /api/execute` accepts JSON. Successful responses have `{"ok":true,"result":...}`; validation failures have `{"ok":false,"error":"..."}` and HTTP 422. Malformed or oversized JSON returns HTTP 400.

```json
{"action":"infer","inputs":[0.9,0.3,0.7,0.5],"dac_bits":12,"adc_bits":12}
```

| Action | Additional fields | Result |
|---|---|---|
| `meta` | none | Version, defaults and operations |
| `infer` | `inputs`, optional `network`, converter bits | Layer outputs, neuron traces and errors |
| `batch` | `count` (1–256), `seed`, optional input matrix | Per-sample rows and aggregate errors |
| `neuron` | `inputs`, `weights`, `bias`, converter bits | Complete single-neuron trace |
| `component` | `kind`: `mzm` or `laser`, documented controls | Curve and summary |
| `blocks` | none | Original graph block definitions |
| `example` | none | Reference PEMAN design |
| `graph` | `design`, `duration`, `noise`, `seed` | Decimated probes and warnings |

The graph preview caps designs at 64 instances, 256 connections and 20,000 samples per source. The API body limit is 1 MB. These are preview resource limits, not a multi-tenant service guarantee. Put public native API deployments behind rate limits and monitoring. Static browser mode needs no public Python server.

`GET /api/blocks` and `POST /api/run` remain available for the original editor. The browser and desktop call the same operations without HTTP. No request can select a Python module or submit executable code.

## Studio export formats

Studio saves a complete run as `prabha.run.v1`. Fields are `studio_version`, `engine_version`, `engine` (execution mode), `created_at` (UTC), `request` and `result`. The `request` is the exact JSON dispatcher payload, including coefficients and precision; `result` contains the computed values. The export wrapper is not itself an API request.

To replay from Python:

```python
import json
from pathlib import Path
import httpx

record = json.loads(Path('prabha-infer.json').read_text(encoding='utf-8'))
response = httpx.post('http://127.0.0.1:8000/api/execute', json=record['request'], timeout=120)
response.raise_for_status()
print(response.json())
```

Install development dependencies for this example's `httpx` client. Run the local API first.

ANN settings use `prabha.ann-settings.v1`, with `studio_version` and `settings`. The settings object contains four `inputs`, `dac_bits`, `adc_bits` and `network` (`w1`, `b1`, `w2`, `b2`). Studio accepts only supported fields and validates their dimensions/ranges. It never uses imported results as computed evidence.

The batch CSV has 16 columns: sample, four inputs, two ideal outputs, two physical outputs, two errors, seed, DAC bits, ADC bits, engine version and engine mode. Keep the batch JSON for the full network. These export schemas are versioned separately from the model and retain the preview's fixed architecture.


## Current Designer models

`{"action":"example","name":"neuron"}` returns a Designer document with `design`, `settings` (duration in ns), `positions` and `model_revision`. Other names: `expanded`, `receiver`, `nonlinear`. Omitting `name` preserves the original legacy netlist response.

Run a current example with `action: "graph"`, its `design`, `duration: settings.duration_ns * 1e-9`, `noise` and `seed`. Graph responses include `model_revision`, `version`, `settings`, `model_profiles`, warnings and probes. Each probe has `sample_indices` and `unit`; optical probes also have `phase_rad`. At most 1,200 plotted points are returned, with `last` computed from the complete signal. New `model_*` definitions are returned by `blocks` alongside the historical definitions.
