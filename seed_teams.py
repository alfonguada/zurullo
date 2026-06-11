from models import db, Team

TEAMS = [
    # UEFA
    ('Alemania', '🇩🇪'), ('España', '🇪🇸'), ('Francia', '🇫🇷'), ('Inglaterra', '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    ('Países Bajos', '🇳🇱'), ('Portugal', '🇵🇹'), ('Italia', '🇮🇹'), ('Bélgica', '🇧🇪'),
    ('Croacia', '🇭🇷'), ('Suiza', '🇨🇭'), ('Serbia', '🇷🇸'), ('Austria', '🇦🇹'),
    ('Escocia', '🏴󠁧󠁢󠁳󠁣󠁴󠁿'), ('Turquía', '🇹🇷'), ('Hungría', '🇭🇺'), ('Dinamarca', '🇩🇰'),
    ('Albania', '🇦🇱'), ('Eslovenia', '🇸🇮'), ('Rumanía', '🇷🇴'), ('Grecia', '🇬🇷'),
    # CONMEBOL
    ('Brasil', '🇧🇷'), ('Argentina', '🇦🇷'), ('Colombia', '🇨🇴'), ('Uruguay', '🇺🇾'),
    ('Ecuador', '🇪🇨'), ('Paraguay', '🇵🇾'), ('Venezuela', '🇻🇪'), ('Bolivia', '🇧🇴'),
    # CONCACAF
    ('México', '🇲🇽'), ('Estados Unidos', '🇺🇸'), ('Canadá', '🇨🇦'), ('Panamá', '🇵🇦'),
    ('Costa Rica', '🇨🇷'), ('Honduras', '🇭🇳'), ('Jamaica', '🇯🇲'), ('El Salvador', '🇸🇻'),
    # CAF
    ('Marruecos', '🇲🇦'), ('Nigeria', '🇳🇬'), ('Senegal', '🇸🇳'), ('Camerún', '🇨🇲'),
    ('Egipto', '🇪🇬'), ('Ghana', '🇬🇭'), ("Costa de Marfil", '🇨🇮'), ('Sudáfrica', '🇿🇦'),
    ('R.D. Congo', '🇨🇩'), ('Argelia', '🇩🇿'),
    # AFC
    ('Japón', '🇯🇵'), ('Corea del Sur', '🇰🇷'), ('Arabia Saudí', '🇸🇦'), ('Irán', '🇮🇷'),
    ('Australia', '🇦🇺'), ('Iraq', '🇮🇶'), ('Uzbekistán', '🇺🇿'), ('Jordania', '🇯🇴'),
    # OFC
    ('Nueva Zelanda', '🇳🇿'),
]

WORST_TEAMS = {
    'R.D. Congo', 'Bolivia', 'Jamaica', 'Honduras', 'El Salvador',
    'Nueva Zelanda', 'Uzbekistán', 'Iraq', 'Sudáfrica', 'Venezuela',
    'Panamá', 'Costa Rica', 'Argelia', 'Jordania',
}


def seed():
    if Team.query.count() > 0:
        print('Los equipos ya están cargados.')
        return
    for name, flag in TEAMS:
        t = Team(name=name, flag_emoji=flag, is_worst=(name in WORST_TEAMS))
        db.session.add(t)
    db.session.commit()
    print(f'{len(TEAMS)} equipos anadidos OK.')


if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        seed()
