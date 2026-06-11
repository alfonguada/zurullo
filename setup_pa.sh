#!/bin/bash
# ================================================
#  SETUP PYTHONANYWHERE — Zurullo World Cup 2026
#  Ejecutar desde la consola Bash de PythonAnywhere
# ================================================

set -e
APP_DIR="/home/alfon8guada/zurullo"
VENV_DIR="/home/alfon8guada/.virtualenvs/zurullo"

echo "=== 1. Clonando / actualizando repositorio ==="
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR" && git pull
else
    git clone https://github.com/alfonguada/zurullo.git "$APP_DIR"
    cd "$APP_DIR"
fi

echo "=== 2. Creando entorno virtual ==="
if [ ! -d "$VENV_DIR" ]; then
    python3.10 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "=== 3. Instalando dependencias ==="
pip install --upgrade pip -q
pip install -r "$APP_DIR/requirements.txt" -q

echo "=== 4. Descargando banderas y configurando BD ==="
cd "$APP_DIR"
python download_flags.py

echo "=== 5. Importando partidos desde ESPN ==="
python fetch_schedule.py

echo ""
echo "================================================"
echo "  SETUP COMPLETADO"
echo "  Ahora configura el Web App en el dashboard:"
echo "  - Source code:     $APP_DIR"
echo "  - Working dir:     $APP_DIR"
echo "  - Virtualenv:      $VENV_DIR"
echo "  - WSGI file:       $APP_DIR/wsgi.py"
echo "  - Static URL /static/ -> $APP_DIR/static/"
echo "================================================"
