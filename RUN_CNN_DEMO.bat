@echo off
setlocal
cd /d "%~dp0"
set "OPENBLAS_NUM_THREADS=1"
set "OMP_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
if exist ".venv\Scripts\python.exe" (
  set "CNN_PY=%CD%\.venv\Scripts\python.exe"
) else (
  if not exist ".cnn-venv\Scripts\python.exe" (
    py -3 -m venv .cnn-venv
    if errorlevel 1 goto failed
  )
  set "CNN_PY=%CD%\.cnn-venv\Scripts\python.exe"
)
"%CNN_PY%" -c "import numpy,jsonschema" >nul 2>&1
if errorlevel 1 (
  "%CNN_PY%" -m pip install -r requirements-cnn-demo.txt
  if errorlevel 1 goto failed
)
"%CNN_PY%" run_cnn_demo.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo CNN demo could not start. Read the error above. Python 3 is required.
pause
exit /b 1
