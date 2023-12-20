@echo off
setlocal enabledelayedexpansion

REM Get the current script directory
for %%I in ("%~dp0.") do set "script_dir=%%~fI"

REM Change the current directory to the script directory
cd /d "%script_dir%"

REM Execute pip3 install -r requirements.txt
pip3 install -r requirements.txt

REM Restore the previous directory
cd /d "%~dp0"

endlocal