@echo off
setlocal
cd /d "%~dp0"
set "PRABHA_BOOT=py -3"
where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 goto python_missing
  set "PRABHA_BOOT=python"
)
where npm >nul 2>&1
if errorlevel 1 goto node_missing
if not exist ".studio-venv\Scripts\python.exe" (
  %PRABHA_BOOT% -m venv .studio-venv
  if errorlevel 1 goto failed
)
set "PRABHA_PY=%CD%\.studio-venv\Scripts\python.exe"
"%PRABHA_PY%" -m pip install -r requirements-web.txt
if errorlevel 1 goto failed
call npm ci --prefix frontend/studio
if errorlevel 1 goto failed
"%PRABHA_PY%" scripts/build_web_assets.py
if errorlevel 1 goto failed
call npm run build --prefix frontend/studio
if errorlevel 1 goto failed
echo Prabha setup complete. Start RUN_PRABHA_STUDIO.bat.
exit /b 0
:python_missing
echo Install Python 3.11 or newer with the Windows py launcher, then run this file again.
exit /b 1
:node_missing
echo Install Node.js 22 LTS with npm, then run this file again.
exit /b 1
:failed
echo Setup stopped. Read the error above before retrying.
exit /b 1
