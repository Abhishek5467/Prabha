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
