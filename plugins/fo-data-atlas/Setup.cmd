@echo off
setlocal
title F^&O Data Atlas - Mahmoud Elgendi
rem Prefer the local Codex runtime; recipients can also use an installed Python 3.10+.
set "ATLAS_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%ATLAS_PY%" goto bundled
where py >nul 2>nul
if not errorlevel 1 goto launcher
python "%~dp0scripts\install.py" %*
goto finished
:launcher
py -3 "%~dp0scripts\install.py" %*
goto finished
:bundled
"%ATLAS_PY%" "%~dp0scripts\install.py" %*
:finished
set "ATLAS_RESULT=%errorlevel%"
if not "%~1"=="" exit /b %ATLAS_RESULT%
echo.
pause
exit /b %ATLAS_RESULT%
