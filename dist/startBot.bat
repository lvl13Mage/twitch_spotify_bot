@echo off
setlocal enabledelayedexpansion

REM Get the current script directory
for %%I in ("%~dp0.") do set "script_dir=%%~fI"

REM Change the current directory to the script directory
cd /d "%script_dir%"

REM Execute python3 main.py
spotifyBot.exe --config config.json %*

REM Restore the previous directory
cd /d "%~dp0"

endlocal