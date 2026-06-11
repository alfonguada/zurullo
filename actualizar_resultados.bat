@echo off
title Zurullo WC - Actualizando partidos
echo.
echo  ================================================
echo    ZURULLO WC - Importar / Actualizar partidos
echo  ================================================
echo.
echo  Descargando calendario y resultados de ESPN...
echo.
cd /d "%~dp0"
python fetch_schedule.py --recalc
echo.
echo  Listo. Cierra esta ventana.
pause
