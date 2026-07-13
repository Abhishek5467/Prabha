"""
prabha.engine — execution: resolve kernels, schedule topologically, stream signals.

Pipeline per spec: schema-validate (registry) -> validate defs (C1-C6, load time)
-> flatten -> validate flattened (R1-R12) -> run. R11 (fs-match) is enforced here
at runtime because per-signal fs is only known when signals exist.
"""
from __future__ import annotations
from typing import Callable, Dict, List, Optional

from .signal import Signal
from .validate import validate_netlist, validate_compound_def, check_definition_cycles, Violation
from .compound import flatten

KERNELS: Dict[str, type] = {}          # implementation name -> Kernel class


def kernel(name: str):
    """Decorator registering a primitive compute kernel by its 'implementation' tag."""
    def deco(cls):
        KERNELS[name] = cls
        return cls
    return deco


class Kernel:
    """Base primitive kernel. Subclasses implement process(inputs) -> {port: Signal}.

    self.seed is deterministic per (run seed, instance id): CRC32(instance_id) + run seed
    + the block's own 'seed' param if it has one. CRC32 is used because it is
    identically defined in every language (portable to core-cpp)."""
    def __init__(self, params: dict, ctx: "RunContext", instance_id: str = ""):
        import zlib
        self.p = params
        self.ctx = ctx
        self.instance_id = instance_id
        self.seed = (zlib.crc32(instance_id.encode()) + ctx.seed
                     + int(params.get("seed", 0))) & 0xFFFFFFFF

    def process(self, inputs: Dict[str, Optional[Signal]]) -> Dict[str, Signal]:
        raise NotImplementedError


class RunContext:
    """Global run settings: duration and noise toggle. fs is per-signal (spec),
    set by source blocks; duration defines how many samples sources emit."""
    def __init__(self, duration: float, noise: bool = True, seed: int = 0):
        self.duration = duration
        self.noise = noise
        self.seed = seed


class ValidationError(Exception):
    def __init__(self, violations: List[Violation]):
        self.violations = violations
        msgs = "; ".join(f"[{v.rule}] {v.message}" for v in violations)
        super().__init__(f"design has errors: {msgs}")


class System:
    def __init__(self, design: dict, registry, ctx: RunContext):
        self.registry = registry
        self.ctx = ctx

        # Phase 4 at load: every compound definition + C5 definition cycles
        vio: List[Violation] = list(check_definition_cycles(registry))
        for bid, defn in registry.defs.items():
            if defn["block_type"] == "compound":
                vio += validate_compound_def(defn, registry)

        # flatten, then Phases 1-3 on flattened graph
        self.flat = flatten(design, registry)
        vio += validate_netlist(self.flat, registry)

        self.warnings = [v for v in vio if v.severity == "warning"]
        errors = [v for v in vio if v.severity == "error"]
        if errors:
            raise ValidationError(errors)

        # resolve kernels
        self.kernels: Dict[str, Kernel] = {}
        self.defs: Dict[str, dict] = {}
        for b in self.flat["blocks"]:
            defn = registry.get(b["ref"])
            self.defs[b["id"]] = defn
            impl = defn["implementation"]
            if impl not in KERNELS:
                raise KeyError(f"no kernel registered for implementation {impl!r}")
            # merge params: definition defaults <- instance overrides
            params = {p["name"]: p["default"] for p in defn["params"]}
            params.update(b.get("params") or {})
            self.kernels[b["id"]] = KERNELS[impl](params, ctx, b["id"])

    def _topo(self) -> List[str]:
        ids = [b["id"] for b in self.flat["blocks"]]
        deps = {i: set() for i in ids}
        for c in self.flat["connections"]:
            deps[c["to"][0]].add(c["from"][0])
        order, ready = [], sorted([i for i in ids if not deps[i]])
        seen = set(ready)
        while ready:
            n = ready.pop(0)
            order.append(n)
            for m in ids:
                if n in deps[m]:
                    deps[m].discard(n)
                    if not deps[m] and m not in seen:
                        ready.append(m); seen.add(m)
        return order

    def run(self) -> Dict[str, Dict[str, Signal]]:
        buf: Dict[tuple, Signal] = {}
        results: Dict[str, Dict[str, Signal]] = {}
        for nid in self._topo():
            inputs: Dict[str, Optional[Signal]] = {}
            for c in self.flat["connections"]:
                if c["to"][0] == nid:
                    inputs[c["to"][1]] = buf[tuple(c["from"])]
            # R11 runtime: all time-domain inputs share fs
            fss = {s.fs for s in inputs.values() if s is not None and s.domain == "time"}
            if len(fss) > 1:
                raise ValidationError([Violation("R11", "error", {"instance": nid},
                    f"fs mismatch at {nid}: {sorted(fss)}")])
            out = self.kernels[nid].process(inputs)
            results[nid] = out
            for pname, sig in out.items():
                buf[(nid, pname)] = sig
        return results