"""
Punto de entrada WSGI para PythonAnywhere.
"""
import sys
import os

APP_DIR = '/home/alfon8guada/zurullo'
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from app import app as application
from models import db, TournamentSettings


def run_migrations():
    """Aplica columnas nuevas que db.create_all() no añade a tablas existentes."""
    migrations = [
        "ALTER TABLE teams ADD COLUMN flag_img VARCHAR(50) DEFAULT ''",
        "ALTER TABLE tournament_settings ADD COLUMN last_sync DATETIME",
    ]
    with db.engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(db.text(sql))
                conn.commit()
            except Exception:
                pass  # La columna ya existe


with application.app_context():
    db.create_all()
    run_migrations()
    if not TournamentSettings.query.first():
        db.session.add(TournamentSettings())
        db.session.commit()
