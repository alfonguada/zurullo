#!/bin/bash
# Otorga N puntos de bonus a todos los usuarios y genera los sobres correspondientes.
# Uso:
#   ./grant_points.sh          → 100 puntos (por defecto)
#   ./grant_points.sh 50       → 50 puntos

PUNTOS=${1:-100}

cd "$(dirname "$0")"

python3 - "$PUNTOS" <<'PYEOF'
import sys
from app import app, db
from models import User, BonusPrediction
from app import grant_milestone_packs

PUNTOS = int(sys.argv[1])

with app.app_context():
    users = User.query.all()
    if not users:
        print("No hay usuarios registrados.")
        sys.exit(0)

    print(f"\nOtorgando {PUNTOS} puntos a {len(users)} usuario(s)...\n")

    for user in users:
        antes = user.total_points

        bp = BonusPrediction.query.filter_by(user_id=user.id).first()
        if not bp:
            bp = BonusPrediction(user_id=user.id)
            db.session.add(bp)
            db.session.flush()

        bp.scorer_points = (bp.scorer_points or 0) + PUNTOS
        db.session.flush()

        despues = user.total_points
        print(f"  {user.name:<20} {antes:>4} pts  →  {despues:>4} pts  (+{PUNTOS})")

    db.session.commit()

    # Generar sobres por hitos de 25 pts
    print("\nGenerando sobres por hitos...")
    for user in users:
        antes_packs = user.packs.filter_by(opened=False).count()
        grant_milestone_packs(user)
    db.session.commit()

    for user in users:
        pendientes = user.packs.filter_by(opened=False).count()
        print(f"  {user.name:<20} {pendientes} sobre(s) pendiente(s)")

    print(f"\nListo.")
PYEOF
