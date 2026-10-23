#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
if [ -x .venv/bin/python ]; then CNN_PY=.venv/bin/python; else
  if [ ! -x .cnn-venv/bin/python ]; then python3 -m venv .cnn-venv; fi
  CNN_PY=.cnn-venv/bin/python
fi
if ! "$CNN_PY" -c 'import numpy,jsonschema' >/dev/null 2>&1; then
  "$CNN_PY" -m pip install -r requirements-cnn-demo.txt
fi
exec "$CNN_PY" run_cnn_demo.py
