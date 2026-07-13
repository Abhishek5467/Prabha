"""
Reference conformance runner (spec/conformance/README.md 'Runner contract').
Exit 0 iff every fixture passes. core-cpp implements this same loop.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import numpy as np
from prabha import SpecSchemas, BlockRegistry, System, RunContext, ValidationError

ROOT = Path(__file__).resolve().parent.parent.parent
schemas = SpecSchemas(ROOT/"spec/schema")

def fresh_registry():
    reg = BlockRegistry(schemas)
    reg.load_dir(ROOT/"spec/blocks")
    for p in sorted((ROOT/"blocks-lib").glob("*.json")):
        reg.load_file(p)
    return reg

def sample(results, spec):
    sig = results[spec["instance"]][spec["port"]]
    return float(np.asarray(sig.data).reshape(-1 if sig.kind != "optical" else (len(sig.channels), -1))[spec["sample"]]) \
        if sig.kind != "optical" else float(sig.data[0, spec["sample"]])

def run_golden(fx, reg):
    ctx = fx["context"]; fails = []
    if fx["expect"]["exact"]:
        res = System(fx["design"], reg, RunContext(ctx["duration"], noise=False,
                                                   seed=ctx.get("seed", 0))).run()
        for e in fx["expect"]["exact"]:
            got = sample(res, e)
            if abs(got - e["value"]) > e["atol"]:
                fails.append(f"exact {e['instance']}.{e['port']}: got {got!r} want {e['value']!r} ±{e['atol']}")
    for st in fx["expect"]["stats"]:
        vals = []
        for s in st["seeds"]:
            res = System(fx["design"], reg, RunContext(ctx["duration"], noise=True, seed=s)).run()
            vals.append(sample(res, st))
        v = np.array(vals)
        if abs(v.mean() - st["mean"]) > st["mean_atol"]:
            fails.append(f"stats mean {v.mean():.5f} want {st['mean']}±{st['mean_atol']}")
        if v.std() > st["std_max"]:
            fails.append(f"stats std {v.std():.5f} > max {st['std_max']}")
    return fails

def run_validation(fx, reg):
    want = sorted((v["rule"], v["severity"]) for v in fx["expect_violations"])
    got, warns = [], []
    try:
        sysm = System(fx["design"], reg, RunContext(fx["context"]["duration"], noise=False))
        warns = sorted({(v.rule, v.severity) for v in sysm.warnings})
        sysm.run()   # runtime rules (R11) fire here, not at construction
    except ValidationError as e:
        got = sorted({(v.rule, v.severity) for v in e.violations})
    fails = [] if got == want else [f"violations got {got} want {want}"]
    if "expect_warnings" in fx:
        wwant = sorted((v["rule"], v["severity"]) for v in fx["expect_warnings"])
        if warns != wwant:
            fails.append(f"warnings got {warns} want {wwant}")
    return fails

def main():
    total = failed = 0
    for kind, runner in (("golden", run_golden), ("validation", run_validation)):
        for p in sorted((ROOT/"spec/conformance"/kind).glob("*.json")):
            total += 1
            fx = json.load(open(p))
            fails = runner(fx, fresh_registry())
            status = "PASS" if not fails else "FAIL"
            if fails: failed += 1
            print(f"[{kind:10}] {fx['name']:28} {status}")
            for f in fails: print(f"    - {f}")
    print(f"\n{total-failed}/{total} fixtures pass")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()