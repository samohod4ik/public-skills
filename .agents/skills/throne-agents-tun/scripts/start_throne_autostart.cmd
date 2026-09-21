@echo off
setlocal
set "DIR=%~1"
set "PY=%~2"
if "%DIR%"=="" set "DIR=%THRONE_DIR%"
if "%PY%"=="" set "PY=%THRONE_PYTHON%"
if "%DIR%"=="" (
  echo THRONE_DIR / arg1 is required
  exit /b 1
)
if not exist "%DIR%\Throne.exe" (
  echo Missing "%DIR%\Throne.exe"
  exit /b 1
)
if "%PY%"=="" set "PY=python"
"%PY%" "%~dp0ensure_autostart_flags.py" --throne-dir "%DIR%"
if errorlevel 1 echo writer failed; starting Throne.exe anyway
start "" "%DIR%\Throne.exe"
exit /b 0
