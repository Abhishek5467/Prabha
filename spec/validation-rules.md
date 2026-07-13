# Prabha Semantic Validation Rules — v0.1.0

**Status:** Draft for review
**Scope:** Rules the engine's `validate()` pass enforces on a loaded design, *after* JSON-Schema
structural validation has passed and *before* simulation is allowed to run.

**Layering (do not blur):** JSON Schema guarantees a file is **well-formed**.
These rules guarantee a design is **well-connected**. They are relational — they require the
resolved graph — so they are implemented in engine code (`core-py`, `core-cpp`), never in schema.
Both engines MUST emit identical rule IDs for identical violations; the conformance suite tests this.

---

## Error reporting contract

Every violation is reported as a machine-readable record:

```
{ "rule": "<rule id>", "severity": "error" | "warning",
  "where": { "instance": "...", "port": "...", "connection": <index> },   // whichever apply
  "message": "<human-readable>" }
```

- `error`   → design MUST NOT run.
- `warning` → design may run; report is surfaced to the user (GUI highlights, CLI prints).
- `validate()` returns ALL violations found, not just the first (a designer fixing a circuit
  needs the full list, and the GUI needs every marker at once).

---

## Phase 1 — Reference resolution

| ID | Severity | Rule |
|----|----------|------|
| R1 | error | Every `blockInstance.ref` resolves to a known block definition (built-in registry or `blocks-lib/`). |
| R2 | error | Instance `id`s are unique within a netlist. |
| R3 | error | Every connection endpoint `[instance, port]` names an existing instance, and the port exists on its resolved definition: `from` MUST name an **output** port, `to` MUST name an **input** port. (Direction correctness is implied by which list the port is found in — a consequence of the separate-inputs/outputs decision.) |
| R4 | error | Every key in `blockInstance.params` names a declared param of the definition; the value matches the param's `type`; numeric values respect `min`/`max` when declared; enum values are members of `options`. |

## Phase 2 — Connection rules

| ID | Severity | Rule |
|----|----------|------|
| R5 | error | **Kind-match:** the `from` port's `kind` equals the `to` port's `kind`, exactly. No implicit conversion — a current→voltage conversion is an explicit block (e.g. TIA). |
| R6 | error | **Domain-match:** the `from` port's `domain` equals the `to` port's `domain`, exactly. (All `time` today; the rule exists so frequency-domain blocks compose safely later.) |
| R7 | error | **One driver per input:** no two connections may target the same `[instance, input port]`. |
| R8 | error | **Required inputs connected:** every input port with `optional: false` (the default) has exactly one incoming connection. `optional: true` inputs may dangle; the block's compute supplies its documented default behavior. |
| R9 | warning | **Unused output:** an output port with no outgoing connection is legal but reported, since it usually indicates a forgotten probe or wire. |
| R10 | mixed | **Fan-out policy (JUDGMENT CALL — see note):** one output feeding multiple inputs is **allowed for `voltage` and `digital`** (high-impedance sensing / logical copy), and an **error for `optical` and `current`** (must use an explicit splitter / current-divider block). |

> **R10 note (call #1):** fanning out an optical wire duplicates energy — two branches each carrying
> the full field violates power conservation; physics says "insert a splitter." Likewise a current
> fanned to two loads must divide (KCL); duplicating it is wrong. Voltage sensing and digital reads
> are non-consuming, so fan-out is physical there. Alternative if you prefer simplicity: forbid all
> fan-out and require explicit fanout blocks everywhere. I chose the physics-faithful split.

## Phase 3 — Rate & graph rules

| ID | Severity | Rule |
|----|----------|------|
| R11 | error | **fs-match:** all time-domain signals arriving at one block share the same `fs`, unless the block definition is flagged as a rate converter (`rate_converter: true` metadata — reserved, no block uses it yet). Per-signal `fs` made this rule necessary; this is where it lives. |
| R12 | error | **No cycles (for now — JUDGMENT CALL):** the flattened graph must be a DAG. Feedback loops require a time-stepped/state-space solver the engine doesn't have yet; until it does, a cycle is an error with a message saying exactly that ("feedback loops not yet supported"), not a crash. |

> **R12 note (call #2):** when the stepped solver lands, this rule relaxes to "cycles allowed if every
> loop contains at least one declared-delay element." Writing the rule this way now means the error
> message already teaches the future fix, and the rule ID survives the transition.

## Phase 4 — Compound-block rules (validated per definition, at load)

| ID | Severity | Rule |
|----|----------|------|
| C1 | error | `boundary_map` keys are **exactly** the set of the compound block's declared port names — no missing, no extra (a bijection between exposed ports and map entries). |
| C2 | error | Every `boundary_map` value `[instance, port]` names an existing instance/port **inside** `subnetlist`. |
| C3 | error | Boundary consistency: an exposed **input** maps to an internal **input** port; an exposed **output** maps to an internal **output** port; and the exposed port's `kind`/`domain` equal the internal port's `kind`/`domain`. |
| C4 | error | An internal input port targeted by the boundary map must not ALSO have an internal driver (would violate R7 after flattening). |
| C5 | error | **No recursive definitions:** a compound block must not instantiate itself, directly or transitively (cycle in the *definition* dependency graph). Detected at library load. |
| C6 | — | The `subnetlist` itself must satisfy R1–R12, with boundary-mapped internal inputs treated as driven and boundary-mapped internal outputs treated as consumed. |

## Flattening procedure (normative)

Flattening happens **after** per-definition validation (C1–C6) and **before** graph validation of
the top-level design (R1–R12 run on the flattened result):

1. Replace each compound instance with its `subnetlist`, **namespacing** internal instance ids as
   `<parent instance id>/<internal id>` (guarantees global uniqueness; preserves traceability so a
   violation inside a flattened PEMAN neuron still points at a path a human can follow).
2. Re-route: every external connection touching the compound's exposed port is rewired to the
   internal `[namespaced instance, port]` given by `boundary_map`.
3. Recurse until no compound instances remain (C5 guarantees termination).
4. Run R1–R12 on the flattened graph.

> **Call #3 — validate-then-flatten-then-revalidate:** definitions are validated once at load
> (cheap, catches library errors early, errors point at the definition), and the flattened top-level
> graph is validated per run (catches wiring errors, errors point at namespaced paths). The
> alternative — validating only the flattened graph — is simpler but produces errors like
> "neuron_1/mac_2/pd_1 kind mismatch" for a bug that lives in the library file; validating
> definitions at load reports it where it can be fixed.

## Execution order

`Phase 1 → Phase 4 (per definition, at load) → flatten → Phases 1–3 on flattened graph → run.`
Phases short-circuit: if Phase 1 has errors, later phases still run where possible (to maximize the
report) but the design cannot execute.

---

## Conformance hooks

`spec/conformance/validation/` will hold golden cases: each a `.prabha` (or block definition) plus
the expected violation list `[{rule, severity, where}]`. Both engines must reproduce the list
exactly (order-insensitive). Noiseless by construction — validation is deterministic, so exact
comparison applies.