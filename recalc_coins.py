"""
Recalcula puntos de todos los partidos jugados y muestra las monedas
resultantes de cada usuario con el nuevo sistema (25 por resultado, 50 por exacto).

Las monedas son un valor CALCULADO (no se guarda en la BD): con solo subir el
codigo nuevo y recargar la web ya quedan corregidas. Este script sirve para
forzar el recalculo de puntos y verificar el resultado.

Uso en una consola Bash de PythonAnywhere (con el virtualenv activado):

    cd ~/zurullo        # o la ruta de tu proyecto
    git pull
    python recalc_coins.py

Luego pulsa "Reload" en la pestana Web de PythonAnywhere.
"""
from app import app, db, recalc_match, recalc_worst_teams
from models import User, Match

with app.app_context():
    # Recalcular puntos de todos los partidos con resultado
    played = Match.query.filter(Match.goals1.isnot(None)).all()
    for m in played:
        recalc_match(m)
    db.session.commit()
    recalc_worst_teams()

    print("=" * 60)
    print(f"  Partidos recalculados: {len(played)}")
    print("=" * 60)
    print(f"  {'Usuario':<22}{'Puntos':>8}{'Monedas':>10}{'Gastado':>10}")
    print("-" * 60)
    for u in sorted(User.query.all(), key=lambda x: x.coins, reverse=True):
        print(f"  {u.name:<22}{u.total_points:>8}{u.coins:>10}{u.coins_spent or 0:>10}")
    print("=" * 60)
    print("  Listo. Recarga la web en PythonAnywhere para ver los cambios.")
