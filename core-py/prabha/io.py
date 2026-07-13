"""
prabha.io — design file I/O.

Today: load a top-level .prabha design (netlist document) with schema validation.
Future home of HDF5 results persistence (not yet designed).
"""
from __future__ import annotations
import json
from pathlib import Path

from .block import SpecSchemas


def load_design(path: Path, schemas: SpecSchemas) -> dict:
    """Load a top-level .prabha design (a netlist document) with structural validation."""
    with open(path) as f:
        doc = json.load(f)
    schemas.check_netlist(doc, str(path))
    return doc