#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
if [ -x .venv/bin/python ]; then STUDIO_PY=.venv/bin/python; else
  if [ ! -x .studio-venv/bin/python ]; then python3 -m venv .studio-venv; fi
  STUDIO_PY=.studio-venv/bin/python
fi
if ! "$STUDIO_PY" -c 'import numpy,jsonschema,fastapi,uvicorn' >/dev/null 2>&1; then
  "$STUDIO_PY" -m pip install -r requirements.txt
fi
exec "$STUDIO_PY" run_studio.py "$@"
