"""Exercise the bundled JSON protocol without relying on a system Python import."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

binary = str(Path(sys.argv[1]).resolve())

def invoke(payload, cwd, raw=False):
    completed = subprocess.run([binary, payload if raw else json.dumps(payload)],
                               cwd=cwd, capture_output=True, text=True, timeout=120, check=True)
    return json.loads(completed.stdout)

with tempfile.TemporaryDirectory(prefix="prabha-smoke-") as directory:
    meta = invoke({"action": "meta"}, directory)
    assert meta["ok"] and meta["result"]["version"] == "0.1.0-preview.3", meta
    batch = invoke({"action": "batch", "count": 100, "seed": 12345}, directory)
    assert batch["ok"], batch
    assert abs(batch["result"]["rms_error"] - 7.864411795585e-5) < 1e-12
    assert abs(batch["result"]["max_error"] - 1.782838135357e-4) < 1e-12
    assert batch["result"]["winner_mismatches"] == 0
    example = invoke({"action": "example"}, directory)
    graph = invoke({"action": "graph", "design": example["result"], "noise": False}, directory)
    assert graph["ok"] and graph["result"]["probes"], graph
    for name in ['neuron', 'expanded', 'receiver', 'nonlinear']:
        doc = invoke({'action': 'example', 'name': name}, directory)['result']
        settings = doc['settings']
        result = invoke({'action':'graph','design':doc['design'],
                         'duration':settings['duration_ns']*1e-9,
                         'noise':settings['noise'],'seed':settings['seed']}, directory)
        assert result['ok'], result
        if name in {'neuron','expanded'}:
            assert abs(result['result']['probes']['adc']['voltage']['last']-0.6388278388278388)<1e-14
    assert not invoke({"action": "infer", "inputs": [9, 0, 0, 0]}, directory)["ok"]
    assert not invoke("{broken json", directory, raw=True)["ok"]
print("Sidecar passed: reference batch, bundled graph assets, invalid inputs and malformed JSON.")
