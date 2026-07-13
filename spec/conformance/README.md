# Prabha Conformance Suite — v0.1.0

Language-neutral fixtures that ANY engine claiming to implement the Prabha spec
must reproduce. core-py generated these expected values; core-cpp (and every
future engine) is tested against the same files with an equivalent runner.

## Layout

    conformance/
      golden/       end-to-end simulation cases with expected numeric outputs
      validation/   designs with deliberate errors + the expected violations

Every fixture is self-contained JSON: the design is EMBEDDED (no external file
references), so a fixture never breaks because a sibling file moved. Block
definitions are the one external dependency: fixtures list required definition
ids under "requires"; the runner loads spec/blocks/ + blocks-lib/ first.

## Golden fixture format

    {
      "name": "...", "requires": ["laser_cw", ...],
      "context": { "duration": 4e-10, "noise": false, "seed": 0 },
      "design": { <netlist> },
      "expect": {
        "exact":  [ { "instance": "amp", "port": "out", "sample": -1,
                      "value": 0.57, "atol": 1e-9 } ],
        "stats":  [ { "instance": "act", "port": "z", "sample": -1,
                      "seeds": [0,1,...,19], "noise": true,
                      "mean": 0.6388, "mean_atol": 0.005, "std_max": 0.01 } ]
      }
    }

**Comparison policy (normative):**
- `exact` entries run ONCE with the fixture's context (noise MUST be false) and
  compare |sim - value| <= atol. Deterministic math must agree across languages
  to ~1e-9 (accumulated float ordering differences; NOT bit-exact).
- `stats` entries re-run the design once per listed seed with noise on, collect
  the sampled value, and compare mean within mean_atol and std <= std_max.
  Rationale: noise RNG streams CANNOT match across languages; only the
  STATISTICS of noise are portable. This split is the whole reason the suite
  distinguishes exact from stats.

## Validation fixture format

    {
      "name": "...", "requires": [...],
      "context": { "duration": 4e-10, "noise": false },
      "design": { <netlist with a deliberate error> },
      "expect_violations": [ { "rule": "R5", "severity": "error" }, ... ]
    }

**Comparison policy (normative):** the engine's violation list, reduced to the
multiset of (rule, severity) pairs, must EQUAL the fixture's multiset —
order-insensitive, no missing, no extra. `where` fields are informative in
v0.1.0 (human debugging) and not compared; a future minor version may tighten
this once both engines exist.

Validation fixtures with zero expected errors are EXECUTED (`run()`), not just
constructed: runtime rules (R11 fs-match) fire during execution. A fixture may
also declare `"expect_warnings": [{rule, severity}, ...]`; if present, the
engine's warning multiset must match it exactly (this is how R9 is tested).
R6 (domain-match) has no fixture yet: it becomes testable when the first
frequency-domain block exists — tracked as a known coverage gap.

## Runner contract

A conforming runner: loads spec/schema (Phase 0), loads spec/blocks + blocks-lib,
then for each fixture builds the system and applies the policy above. Exit code
0 iff every fixture passes. Reference runner: core-py/tests/run_conformance.py.