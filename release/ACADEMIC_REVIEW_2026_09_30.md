# Clarity and academic review — 30 September 2026

This revision follows the complete preview.3 update. It clarifies the interface and adds a mathematical/user manual; it does not change the scientific component equations or the fixed ANN reference.

## Implemented changes

- Infer normalized x/w/transmission source labels from connected current-model ports.
- State dimensionless control semantics while retaining compatible voltage-kind transport.
- Restrict the optical phase selector to optical probes and explain direct-detection scope.
- Display actual result model profiles; preserve components-1 implementation metadata.
- Give newly added digital sources valid integer code defaults.
- Add a complete Markdown manual, generated MathML documentation page and regeneration script.
- Extend the existing browser checks and update the model catalogue/navigation.

## Verification in this review

- Python suite: 43 tests pass; a test-client dependency deprecation warning is separate from simulation validity.
- Browser suite: 7 tests pass across Designer, Studio and deployment-path behaviour.
- Web asset build and frontend production build succeed.
- A fresh digital source drives the 12-bit DAC successfully; its final default code 4095 reconstructs 0.5 V.
- Archived ANN CSV recomputation: 100 inputs, 200 output comparisons, RMS 7.864411795584628e-05, maximum absolute error 1.7828381353568457e-04, output-order mismatches 0/100.
- Archived noisy-link CSV: 200 trials per case; full-chain mean per-trial recovery RMS 0.0063679764948395955. This is separate from the deterministic ANN.

These checks establish implementation behaviour under tested assumptions. They do not establish measured device accuracy, a trained classification score, or LLM performance. Original Python/C++ 14-fixture conformance belongs to the legacy kernel set; no full current-model C++ parity is claimed.

## Companion review documents

A 33-page mathematical/user manual, two 7-page academic working drafts and two revised 21-slide presentations with speaker notes accompany this patch. Literature positioning distinguishes implemented software/reproducibility contributions from unestablished priority or hardware-performance claims. The LLM manuscript is a position paper and proposed evaluation protocol.

Native desktop installers have not been built and installed on all three supported operating systems in this review. No Git push, public deployment or paper submission has been performed by this update. See UPDATE_CLARITY.md for the Windows rebuild and push sequence.
