@echo off
setlocal
cd /d "%~dp0"
set "OPENBLAS_NUM_THREADS=1"
set "OMP_NUM_THREADS=1"
set "MKL_NUM_THREADS=1"
if exist ".venv\Scripts\python.exe" (
  set "STUDIO_PY=%CD%\.venv\Scripts\python.exe"
) else (
  if not exist ".studio-venv\Scripts\python.exe" (
    py -3 -m venv .studio-venv
    if errorlevel 1 goto failed
  )
  set "STUDIO_PY=%CD%\.studio-venv\Scripts\python.exe"
)
"%STUDIO_PY%" -c "import numpy,jsonschema,fastapi,uvicorn" >nul 2>&1
if errorlevel 1 (
  "%STUDIO_PY%" -m pip install -r requirements.txt
  if errorlevel 1 goto failed
)
"%STUDIO_PY%" run_studio.py %*
if errorlevel 1 goto failed
exit /b 0
:failed
echo Prabha Studio could not start. Read the error above. Python 3.11 or newer is required.
pause
exit /b 1
