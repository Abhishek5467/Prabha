# Validation and reproducibility

## Reproduce the checks

```bash
python core-py/tests/run_conformance.py
python -m pytest tests -q
# Native C++ fixture runner (GCC/Clang):
g++ -std=c++17 -O2 -Icore-cpp/include -Icore-cpp/third_party core-cpp/src/main_conformance.cpp -o prabha-conformance
./prabha-conformance .
```

The original CMake build is also preserved. The Python suite compares all 200 ANN output values with `core-py/ann_batch_validation.csv`, rather than checking only rounded headline metrics.

| Evidence | Result | Scope |
|---|---|---|
| Shared conformance | 14/14 Python and GCC fixtures | Original typed engine |
| Complete perceptron | output 0.638827838828; absolute error 6.46637e−5 | One deterministic input |
| ANN single input | RMS 6.28219e−5; max 7.58422e−5 | Fixed 4–3–2 network |
| ANN batch | RMS 7.864411795585e−5; max 1.782838135357e−4 | 100 inputs, seed 12345 |
| Output ordering | 0/100 mismatches | Same ANN batch; not classification accuracy |
| Noisy optical link | mean RMS 0.006367976495 | Stored full-noise case, 200 seeds |

The link CSV contains four cases × 200 seeds = 800 rows. The ANN batch does not use that noise model. The archived BTP report is the detailed historical record; the source data and scripts are the executable evidence.

When reporting new physics experiments, preserve the script, configuration, random seeds, CSV, plots and scope statement together. Update the living BTP report and figure archive when new results are validated.
