@echo off
set "PATH=C:\Program Files\Git\cmd;C:\Program Files\Git\bin;%PATH%"
cd /d "%~dp0"

echo [DAMAGOCHI] Pushing to GitHub...
"C:\Program Files\Git\cmd\git.exe" branch -M main
"C:\Program Files\Git\cmd\git.exe" push -u origin main

echo.
pause
