import sys, json, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import numpy as np
from prabha import (SpecSchemas, BlockRegistry, load_design, System, RunContext,
                    ValidationError, validate_netlist, flatten)

ROOT = Path(__file__).parent.parent.parent
schemas = SpecSchemas(ROOT/"spec/schema")
reg = BlockRegistry(schemas)
reg.load_dir(ROOT/"spec/blocks")
reg.load_file(ROOT/"blocks-lib/photonic_mac.json")
design = load_design(ROOT/"peman.prabha", schemas)

# ---------- GOLDEN CASE: PEMAN via compound block ----------
x=[0.9,0.3,0.7,0.5]; w=[0.8,-0.6,0.4,-0.9]; theta=0.2
N=len(x); rate=10e9; dur=N/rate
sysm = System(design, reg, RunContext(duration=dur, noise=True, seed=3))
res = sysm.run()
pre = res["amp"]["out"].data[-1]
z   = res["act"]["z"].data[-1]
sxw = float(np.dot(x,w)); z_true = 1/(1+np.exp(-(sxw+theta)))
print(f"flattened blocks: {len(sysm.flat['blocks'])} (compound inlined)")
print(f"namespaced ids sample: {[b['id'] for b in sysm.flat['blocks'] if '/' in b['id']][:3]}")
print(f"pre-act sim {pre:.4f}  target {sxw+theta:.4f}")
print(f"z sim {z:.4f}  analytic {z_true:.4f}  |err| {abs(z-z_true):.2e}")
assert abs(pre-(sxw+theta)) < 0.05 and abs(z-z_true) < 0.01, "GOLDEN CASE FAILED"
print("GOLDEN CASE PASS\n")

# ---------- VIOLATION CASES: each rule fires with its ID ----------
def rules_of(d):
    try:
        System(d, reg, RunContext(duration=dur, noise=False))
        return set()
    except ValidationError as e:
        return {v.rule for v in e.violations}

def mutate(fn):
    d = copy.deepcopy(design); fn(d); return d

cases = [
 ("R1 unknown ref",        mutate(lambda d: d["blocks"][3].update(ref="nonexistent")), "R1"),
 ("R2 duplicate id",       mutate(lambda d: d["blocks"].append({"id":"laser","ref":"laser_cw"})), "R2"),
 ("R3 bad port",           mutate(lambda d: d["connections"][0]["from"].__setitem__(1,"nope")), "R3"),
 ("R4 param out of range", mutate(lambda d: d["blocks"][0]["params"].update(P0=1e6)), "R4"),
 ("R5 kind mismatch",      mutate(lambda d: d["connections"].__setitem__(1,
                              {"from":["laser","out"],"to":["cap","I"]})), "R5"),
 ("R7 two drivers",        mutate(lambda d: d["connections"].append(
                              {"from":["w","lower"],"to":["mac","x"]})), "R7"),
 ("R8 required unconnected", mutate(lambda d: d["connections"].pop(0)), "R8"),
 ("R10 optical fan-out",   mutate(lambda d: d["connections"].append(
                              {"from":["laser","out"],"to":["mac","light"]}) or
                              d["connections"].pop(0)), None),  # replaced below
 ("R12 cycle",             mutate(lambda d: (d["blocks"].append({"id":"g","ref":"bias_gain"}),
                              d["connections"].append({"from":["amp","out"],"to":["g","in"]}),
                              d["connections"].__setitem__(6,{"from":["g","out"],"to":["adc","in"]}),
                              d["connections"].append({"from":["g","out"],"to":["amp","in"]}))), "R12"),
]
# R10 needs a real fan-out: laser feeds mac.light twice isn't possible (R7 catches),
# so wire laser.out to a second mod's optical input alongside mac
d10 = copy.deepcopy(design)
d10["blocks"].append({"id":"m2","ref":"intensity_mod"})
d10["connections"].append({"from":["laser","out"],"to":["m2","in"]})
d10["connections"].append({"from":["x","out"],"to":["m2","drive"]})  # x now drives 2 (voltage fanout OK)
allpass=True
for name, d, want in cases:
    if want is None: continue
    got = rules_of(d)
    ok = want in got
    if not ok: allpass=False
    print(f"{name:28} want {want:4} got {sorted(got)}  {'PASS' if ok else '*** FAIL ***'}")
got10 = rules_of(d10)
ok10 = "R10" in got10
print(f"{'R10 optical fan-out':28} want R10  got {sorted(got10)}  {'PASS' if ok10 else '*** FAIL ***'}")
if not ok10: allpass=False

# voltage fan-out must be LEGAL (drive two modulator inputs) — build minimal legal case
dv = copy.deepcopy(design)
dv["blocks"].append({"id":"g2","ref":"bias_gain"})
dv["connections"].append({"from":["cap","Vc"],"to":["g2","in"]})   # Vc fans out to amp and g2
try:
    System(dv, reg, RunContext(duration=dur, noise=False))
    print(f"{'voltage fan-out legal':28} PASS")
except ValidationError as e:
    print(f"{'voltage fan-out legal':28} *** FAIL *** {[v.rule for v in e.violations]}")
    allpass=False

print("\nALL VALIDATION TESTS PASS" if allpass else "\nSOME FAILED")