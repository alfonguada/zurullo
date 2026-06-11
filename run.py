from app import app, db
from models import TournamentSettings, Team
from seed_teams import seed

with app.app_context():
    db.create_all()
    if not TournamentSettings.query.first():
        db.session.add(TournamentSettings())
        db.session.commit()
    if Team.query.count() == 0:
        seed()

print("=" * 50)
print("  ZURULLO WORLD CUP 2026")
print("  http://localhost:5000")
print("  El primer usuario que se registre sera ADMIN")
print("=" * 50)
app.run(debug=True, host='0.0.0.0', port=5000)
