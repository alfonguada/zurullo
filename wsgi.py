"""
Punto de entrada WSGI para PythonAnywhere.
El dashboard de PA debe apuntar a este archivo.
"""
import sys
import os

# Ruta absoluta al proyecto
APP_DIR = '/home/alfon8guada/zurullo'

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

os.chdir(APP_DIR)

from app import app as application  # noqa: E402

# Inicializar BD si es la primera vez
with application.app_context():
    from models import db, TournamentSettings, Team
    db.create_all()
    if not TournamentSettings.query.first():
        db.session.add(TournamentSettings())
        db.session.commit()
