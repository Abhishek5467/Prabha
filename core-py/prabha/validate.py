"""
prabha.validate — implements spec/validation-rules.md v0.1.0.

Every violation is a machine-readable Violation(rule, severity, where, message).
Rule IDs here MUST match the spec exactly; the conformance suite compares them
across engines. validate_netlist() returns ALL violations, never just the first.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

FANOUT_ALLOWED = {"voltage", "digital"}          # R10 policy
FANOUT_FORBIDDEN = {"optical", "current"}


@dataclass
class Violation:
    rule: str
    severity: str          # "error" | "warning"
    where: dict
    message: str

    def key(self):         # order-insensitive comparison for conformance
        return (self.rule, self.severity, tuple(sorted(self.where.items())))


def _ports(defn: dict, side: str) -> Dict[str, dict]:
    return {p["name"]: p for p in defn["ports"][side]}


def _param_schema(defn: dict) -> Dict[str, dict]:
    return {p["name"]: p for p in defn["params"]}


# ----------------------------------------------------------------------
# Phases 1-3 on a netlist (top-level design or a compound's subnetlist)
# ----------------------------------------------------------------------
def validate_netlist(netlist: dict, registry, *,
                     boundary_inputs=None, boundary_outputs=None) -> List[Violation]:
    """boundary_inputs/outputs: set of (instance, port) satisfied by a compound
    boundary (C6: treated as driven / consumed)."""
    V: List[Violation] = []
    boundary_inputs = boundary_inputs or set()
    boundary_outputs = boundary_outputs or set()
    blocks = netlist["blocks"]
    conns = netlist["connections"]

    # R2 unique instance ids
    seen = set()
    for b in blocks:
        if b["id"] in seen:
            V.append(Violation("R2", "error", {"instance": b["id"]},
                               f"duplicate instance id {b['id']!r}"))
        seen.add(b["id"])

    # R1 refs resolve
    inst: Dict[str, dict] = {}
    for b in blocks:
        if b["ref"] not in registry:
            V.append(Violation("R1", "error", {"instance": b["id"]},
                               f"unknown block definition {b['ref']!r}"))
        else:
            inst[b["id"]] = registry.get(b["ref"])

    # R4 params
    for b in blocks:
        if b["id"] not in inst:
            continue
        pschema = _param_schema(inst[b["id"]])
        for k, v in (b.get("params") or {}).items():
            if k not in pschema:
                V.append(Violation("R4", "error", {"instance": b["id"], "param": k},
                                   f"unknown param {k!r}"))
                continue
            ps = pschema[k]
            t = ps["type"]
            ok_type = (t == "number" and isinstance(v, (int, float)) and not isinstance(v, bool)) \
                or (t == "string" and isinstance(v, str)) \
                or (t == "boolean" and isinstance(v, bool)) \
                or (t == "enum" and isinstance(v, str))
            if not ok_type:
                V.append(Violation("R4", "error", {"instance": b["id"], "param": k},
                                   f"param {k!r} type mismatch (expected {t})"))
                continue
            if t == "number":
                if "min" in ps and v < ps["min"] or "max" in ps and v > ps["max"]:
                    V.append(Violation("R4", "error", {"instance": b["id"], "param": k},
                                       f"param {k!r}={v} outside [{ps.get('min','-inf')},{ps.get('max','inf')}]"))
            if t == "enum" and v not in ps["options"]:
                V.append(Violation("R4", "error", {"instance": b["id"], "param": k},
                                   f"param {k!r}={v!r} not in options {ps['options']}"))

    # R3 endpoints exist & direction; collect resolved connections
    resolved = []   # (ci, from_inst, from_port(dict), to_inst, to_port(dict))
    for ci, c in enumerate(conns):
        fi, fp = c["from"]; ti, tp = c["to"]
        bad = False
        if fi not in inst:
            V.append(Violation("R3", "error", {"connection": ci},
                               f"'from' instance {fi!r} unknown")); bad = True
        elif fp not in _ports(inst[fi], "outputs"):
            V.append(Violation("R3", "error", {"connection": ci, "instance": fi, "port": fp},
                               f"{fp!r} is not an output of {fi!r}")); bad = True
        if ti not in inst:
            V.append(Violation("R3", "error", {"connection": ci},
                               f"'to' instance {ti!r} unknown")); bad = True
        elif tp not in _ports(inst[ti], "inputs"):
            V.append(Violation("R3", "error", {"connection": ci, "instance": ti, "port": tp},
                               f"{tp!r} is not an input of {ti!r}")); bad = True
        if not bad:
            resolved.append((ci, fi, _ports(inst[fi], "outputs")[fp],
                                 ti, _ports(inst[ti], "inputs")[tp]))

    # R5 kind-match, R6 domain-match
    for ci, fi, fport, ti, tport in resolved:
        if fport["kind"] != tport["kind"]:
            V.append(Violation("R5", "error", {"connection": ci},
                f"kind mismatch: {fi}.{fport['name']}({fport['kind']}) -> {ti}.{tport['name']}({tport['kind']})"))
        fdom = fport.get("domain", "time"); tdom = tport.get("domain", "time")
        if fdom != tdom:
            V.append(Violation("R6", "error", {"connection": ci},
                f"domain mismatch: {fdom} -> {tdom}"))

    # R7 one driver per input (boundary counts as a driver via C4, checked there)
    targets: Dict[tuple, int] = {}
    for ci, fi, fport, ti, tport in resolved:
        targets[(ti, tport["name"])] = targets.get((ti, tport["name"]), 0) + 1
    for (ti, tp), cnt in targets.items():
        if cnt > 1:
            V.append(Violation("R7", "error", {"instance": ti, "port": tp},
                               f"input {ti}.{tp} has {cnt} drivers"))

    # R8 required inputs connected
    for b in blocks:
        if b["id"] not in inst:
            continue
        for p in inst[b["id"]]["ports"]["inputs"]:
            if p.get("optional", False):
                continue
            if (b["id"], p["name"]) not in targets and (b["id"], p["name"]) not in boundary_inputs:
                V.append(Violation("R8", "error", {"instance": b["id"], "port": p["name"]},
                                   f"required input {b['id']}.{p['name']} unconnected"))

    # R9 unused outputs (warning) & R10 fan-out policy
    fanout: Dict[tuple, int] = {}
    for ci, fi, fport, ti, tport in resolved:
        fanout[(fi, fport["name"])] = fanout.get((fi, fport["name"]), 0) + 1
    for b in blocks:
        if b["id"] not in inst:
            continue
        for p in inst[b["id"]]["ports"]["outputs"]:
            k = (b["id"], p["name"])
            n = fanout.get(k, 0)
            if n == 0 and k not in boundary_outputs:
                V.append(Violation("R9", "warning", {"instance": b["id"], "port": p["name"]},
                                   f"output {b['id']}.{p['name']} unused"))
            if n > 1 and p["kind"] in FANOUT_FORBIDDEN:
                V.append(Violation("R10", "error", {"instance": b["id"], "port": p["name"]},
                    f"{p['kind']} output fan-out ({n}) — insert an explicit splitter/divider block"))

    # R12 cycle detection (Kahn); R11 fs-match is runtime (per-signal fs known then)
    ids = [b["id"] for b in blocks]
    deps = {i: set() for i in ids}
    for ci, fi, fport, ti, tport in resolved:
        deps[ti].add(fi)
    order, ready = [], [i for i in ids if not deps[i]]
    seen2 = set(ready)
    while ready:
        n0 = ready.pop()
        order.append(n0)
        for m in ids:
            if n0 in deps[m]:
                deps[m].discard(n0)
                if not deps[m] and m not in seen2:
                    ready.append(m); seen2.add(m)
    if len(order) != len(ids):
        cyc = [i for i in ids if i not in order]
        V.append(Violation("R12", "error", {"instances": ",".join(sorted(cyc))},
                           "feedback loops not yet supported (cycle detected)"))
    return V


# ----------------------------------------------------------------------
# Phase 4 — compound definition rules (C1-C6), at library load
# ----------------------------------------------------------------------
def validate_compound_def(defn: dict, registry) -> List[Violation]:
    V: List[Violation] = []
    bid = defn["id"]
    sub = defn["subnetlist"]; bmap = defn["boundary_map"]
    exposed_in = _ports(defn, "inputs"); exposed_out = _ports(defn, "outputs")

    # C1 bijection between exposed ports and map keys
    want = set(exposed_in) | set(exposed_out)
    got = set(bmap)
    for missing in sorted(want - got):
        V.append(Violation("C1", "error", {"block": bid, "port": missing},
                           f"exposed port {missing!r} missing from boundary_map"))
    for extra in sorted(got - want):
        V.append(Violation("C1", "error", {"block": bid, "port": extra},
                           f"boundary_map key {extra!r} is not an exposed port"))

    inst = {b["id"]: b for b in sub["blocks"]}
    bin_set, bout_set = set(), set()
    for pname, (ii, ip) in bmap.items():
        # C2 internal target exists
        if ii not in inst or inst[ii]["ref"] not in registry:
            V.append(Violation("C2", "error", {"block": bid, "port": pname},
                               f"boundary target instance {ii!r} unknown"))
            continue
        idef = registry.get(inst[ii]["ref"])
        iin, iout = _ports(idef, "inputs"), _ports(idef, "outputs")
        if pname in exposed_in:
            if ip not in iin:
                V.append(Violation("C3", "error", {"block": bid, "port": pname},
                                   f"exposed input must map to an internal INPUT; {ii}.{ip} is not"))
                continue
            tgt = iin[ip]; src = exposed_in[pname]; bin_set.add((ii, ip))
        else:
            if ip not in iout:
                V.append(Violation("C3", "error", {"block": bid, "port": pname},
                                   f"exposed output must map to an internal OUTPUT; {ii}.{ip} is not"))
                continue
            tgt = iout[ip]; src = exposed_out[pname]; bout_set.add((ii, ip))
        if src["kind"] != tgt["kind"] or src.get("domain", "time") != tgt.get("domain", "time"):
            V.append(Violation("C3", "error", {"block": bid, "port": pname},
                               f"boundary kind/domain mismatch on {pname!r}"))

    # C4 boundary-mapped internal input must not also have an internal driver
    for c in sub["connections"]:
        ti, tp = c["to"]
        if (ti, tp) in bin_set:
            V.append(Violation("C4", "error", {"block": bid, "instance": ti, "port": tp},
                               f"internal input {ti}.{tp} is boundary-mapped AND internally driven"))

    # C6 subnetlist satisfies R1-R12 with boundary ports satisfied
    V.extend(validate_netlist(sub, registry,
                              boundary_inputs=bin_set, boundary_outputs=bout_set))
    return V


def check_definition_cycles(registry) -> List[Violation]:
    """C5: no compound block may (transitively) instantiate itself."""
    V: List[Violation] = []
    def deps_of(bid):
        d = registry.get(bid)
        if d["block_type"] != "compound":
            return []
        return [b["ref"] for b in d["subnetlist"]["blocks"] if b["ref"] in registry]
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {bid: WHITE for bid in registry.defs}
    def dfs(bid, path):
        color[bid] = GRAY
        for dep in deps_of(bid):
            if color.get(dep) == GRAY:
                V.append(Violation("C5", "error", {"block": dep},
                                   f"recursive compound definition: {' -> '.join(path + [dep])}"))
            elif color.get(dep) == WHITE:
                dfs(dep, path + [dep])
        color[bid] = BLACK
    for bid in list(registry.defs):
        if color[bid] == WHITE:
            dfs(bid, [bid])
    return V
