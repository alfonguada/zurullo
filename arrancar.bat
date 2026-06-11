@echo off
title Zurullo World Cup 2026
echo.
echo  ================================================
echo    ZURULLO WORLD CUP 2026
echo  ================================================
echo.
echo  Arrancando servidor...
echo  Abre tu navegador en: http://localhost:5000
echo.
echo  Para parar el servidor: cierra esta ventana
echo  ================================================
echo.
cd /d "%~dp0"
python run.py
pause
