"""
prabha.compound — normative compound-block flattening from spec/validation-rules.md.

1. Replace each compound instance with its subnetlist, namespacing internal ids
   as "<parent>/<child>".
2. Re-route external connections touching exposed ports via boundary_map.
3. Recurse until only primitives remain (C5 guarantees termination).
"""
from __future__ import annotations
import copy
from typing import Dict


def flatten(netlist: dict, registry) -> dict:
    blocks = [dict(b) for b in netlist["blocks"]]
    conns = [copy.deepcopy(c) for c in netlist["connections"]]

    while True:
        comp = next((b for b in blocks
                     if b["ref"] in registry and registry.get(b["ref"])["block_type"] == "compound"),
                    None)
        if comp is None:
            break
        defn = registry.get(comp["ref"])
        ns = comp["id"]
        sub = defn["subnetlist"]
        bmap: Dict[str, list] = defn["boundary_map"]

        # 1. inline internal blocks, namespaced; compound-level param overrides
        #    do not propagate (params belong to definitions) — v0.1 semantics.
        blocks.remove(comp)
        for ib in sub["blocks"]:
            nb = dict(ib)
            nb["id"] = f"{ns}/{ib['id']}"
            blocks.append(nb)

        # internal connections, namespaced
        for ic in sub["connections"]:
            conns.append({"from": [f"{ns}/{ic['from'][0]}", ic["from"][1]],
                          "to":   [f"{ns}/{ic['to'][0]}",   ic["to"][1]]})

        # 2. re-route external connections touching the compound's exposed ports
        for c in conns:
            if c["from"][0] == ns:                      # compound output feeding out
                ii, ip = bmap[c["from"][1]]
                c["from"] = [f"{ns}/{ii}", ip]
            if c["to"][0] == ns:                        # something feeding compound input
                ii, ip = bmap[c["to"][1]]
                c["to"] = [f"{ns}/{ii}", ip]

    return {"blocks": blocks, "connections": conns}