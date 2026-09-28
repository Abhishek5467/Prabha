# Contributing to Prabha

Thank you for helping make photonic-electronic simulation reproducible. Discuss substantial physical-model changes in an issue before implementation. Fork the repository, create a branch and open a pull request with the problem, model assumptions, implementation and validation evidence.

## Scientific changes

Specify units, equations, analytical limits and sources. Include deterministic fixtures and seeds for stochastic runs. Preserve CSV data and figure-generation scripts. Explain whether a result is analytical, simulated or measured. Update the living BTP report and figure archive when a new experiment is validated; preserve the internship report as the historical foundation.

## Software changes

Follow `docs/site/quickstart.md`, run the original conformance runner and `python -m pytest tests -q`, and build Studio. Test browser Python after changing shared modules. For desktop changes, attach native build/smoke results. Do not commit credentials, environments, generated installers or unneeded build output.

By contributing, you agree that your original contributions are licensed under the repository's MIT license. Third-party material needs clear attribution and compatible permissions.
