@echo off
setlocal
if "%~1"=="" (
  echo arg1 ThroneDir is required
  exit /b 1
)
if "%~2"=="" (
  echo arg2 Python is required
  exit /b 1
)
set "LOG=%~3"
if "%LOG%"=="" set "LOG=%~1\config\autostart-flags.log"
"%~2" "%~dp0ensure_autostart_flags.py" --throne-dir "%~1" > "%LOG%" 2>&1
exit /b %ERRORLEVEL%
