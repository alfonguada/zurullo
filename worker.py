"""
Always-on worker para PythonAnywhere Developer.
Configura en: Tasks > Always-on tasks > command:
  /home/alfon8guada/.virtualenvs/zurullo/bin/python /home/alfon8guada/zurullo/worker.py

Intervalo adaptativo:
  - Partido en curso (sin resultado, empezado hace < 3h): cada 60 segundos
  - Sin partido activo:                                   cada 5 minutos
"""
import sys
import os
import time
import logging
from datetime import datetime, timedelta

APP_DIR = '/home/alfon8guada/zurullo'
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# Log a archivo + stdout para verlo en PA
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(message)s',
    datefmt='%d/%m %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(APP_DIR, 'worker.log')),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('worker')

from app import app, recalc_match, recalc_worst_teams
from models import db, Match, TournamentSettings
from fetch_schedule import import_matches

INTERVAL_IDLE   = 300   # 5 min sin partidos
INTERVAL_ACTIVE = 60    # 1 min con partido en curso
ACTIVE_WINDOW   = 180   # minutos tras el kickoff para considerar el partido "activo"


def has_active_match():
    """True si hay algún partido que debería estar en juego ahora mismo."""
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=ACTIVE_WINDOW)
    with app.app_context():
        return Match.query.filter(
            Match.match_date >= cutoff,
            Match.match_date <= now,
            Match.goals1.is_(None)
        ).count() > 0


def sync():
    now = datetime.utcnow()
    with app.app_context():
        # Garantizar que la BD está inicializada
        db.create_all()
        if not TournamentSettings.query.first():
            db.session.add(TournamentSettings())
            db.session.commit()

        added, updated, _ = import_matches(
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            recalc=True
        )

        # Guardar timestamp del último sync en BD
        settings = TournamentSettings.query.first()
        if settings:
            settings.last_sync = now
            db.session.commit()

        return added, updated


def main():
    log.info('╔══════════════════════════════════════╗')
    log.info('║  Zurullo WC Worker arrancado          ║')
    log.info('╚══════════════════════════════════════╝')

    consecutive_errors = 0

    while True:
        try:
            added, updated = sync()
            consecutive_errors = 0

            if added or updated:
                log.info(f'SYNC OK — nuevos partidos:{added}  resultados actualizados:{updated}')

        except Exception as e:
            consecutive_errors += 1
            log.error(f'Error ({consecutive_errors}): {e}')
            # Si falla 5 veces seguidas, esperar más antes de reintentar
            if consecutive_errors >= 5:
                log.error('Demasiados errores. Esperando 10 minutos.')
                time.sleep(600)
                consecutive_errors = 0
                continue

        sleep = INTERVAL_ACTIVE if has_active_match() else INTERVAL_IDLE
        log.debug(f'Siguiente sync en {sleep}s')
        time.sleep(sleep)


if __name__ == '__main__':
    main()
