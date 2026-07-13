"""
prabha.block — block-definition registry + Phase-0 structural (schema) validation.

Layering per spec: this module does Phase 0 (JSON-Schema structural validation)
and holds the definition registry. Relational rules live in prabha.validate.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

from jsonschema import Draft202012Validator
from referencing import Registry as RefRegistry, Resource

_SCHEMA_FILES = ["common.schema.json", "signal.schema.json", "port.schema.json",
                 "netlist.schema.json", "block.schema.json"]


class SpecSchemas:
    """Loads spec/schema/*.json once; provides validators with cross-file $refs resolved."""

    def __init__(self, schema_dir: Path):
        self.docs = {}
        for name in _SCHEMA_FILES:
            with open(schema_dir / name) as f:
                self.docs[name] = json.load(f)
        reg = RefRegistry().with_resources(
            [(d["$id"], Resource.from_contents(d)) for d in self.docs.values()])
        for d in self.docs.values():
            Draft202012Validator.check_schema(d)
        self._block_v = Draft202012Validator(self.docs["block.schema.json"], registry=reg)
        self._netlist_v = Draft202012Validator(self.docs["netlist.schema.json"], registry=reg)

    def check_block(self, doc: dict, source: str = "?"):
        errs = [e.message for e in self._block_v.iter_errors(doc)]
        if errs:
            raise ValueError(f"block definition {source} fails schema: " + "; ".join(errs))

    def check_netlist(self, doc: dict, source: str = "?"):
        errs = [e.message for e in self._netlist_v.iter_errors(doc)]
        if errs:
            raise ValueError(f"netlist {source} fails schema: " + "; ".join(errs))


class BlockRegistry:
    """Block definitions by id. Definitions come from spec/blocks/ (built-ins)
    and blocks-lib/ (compound library) — both are the same schema."""

    def __init__(self, schemas: SpecSchemas):
        self.schemas = schemas
        self.defs: Dict[str, dict] = {}

    def load_dir(self, d: Path):
        for p in sorted(Path(d).glob("*.json")) + sorted(Path(d).glob("*.prabha")):
            self.load_file(p)

    def load_file(self, p: Path):
        with open(p) as f:
            doc = json.load(f)
        self.add(doc, source=str(p))

    def add(self, doc: dict, source: str = "<inline>"):
        self.schemas.check_block(doc, source)
        bid = doc["id"]
        if bid in self.defs:
            raise ValueError(f"duplicate block definition id {bid!r} (from {source})")
        self.defs[bid] = doc

    def get(self, bid: str) -> dict:
        return self.defs[bid]

    def __contains__(self, bid: str) -> bool:
        return bid in self.defs