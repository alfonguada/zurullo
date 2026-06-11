#!/usr/bin/env python3
"""
Actualiza banderas, renombra equipos en inglés a español
y limpia placeholders de ESPN (TBD / Group X Winner...).
"""
from app import app, db
from models import Team, Match, Prediction

# Nombre en BD -> emoji bandera
FLAGS = {
    # UEFA
    'Alemania': '\U0001f1e9\U0001f1ea',
    'España': '\U0001f1ea\U0001f1f8',
    'Francia': '\U0001f1eb\U0001f1f7',
    'Inglaterra': '\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f',
    'Países Bajos': '\U0001f1f3\U0001f1f1',
    'Portugal': '\U0001f1f5\U0001f1f9',
    'Italia': '\U0001f1ee\U0001f1f9',
    'Bélgica': '\U0001f1e7\U0001f1ea',
    'Croacia': '\U0001f1ed\U0001f1f7',
    'Suiza': '\U0001f1e8\U0001f1ed',
    'Serbia': '\U0001f1f7\U0001f1f8',
    'Austria': '\U0001f1e6\U0001f1f9',
    'Escocia': '\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f',
    'Turquía': '\U0001f1f9\U0001f1f7',
    'Hungría': '\U0001f1ed\U0001f1fa',
    'Dinamarca': '\U0001f1e9\U0001f1f0',
    'Albania': '\U0001f1e6\U0001f1f1',
    'Eslovenia': '\U0001f1f8\U0001f1ee',
    'Rumanía': '\U0001f1f7\U0001f1f4',
    'Grecia': '\U0001f1ec\U0001f1f7',
    'Chequia': '\U0001f1e8\U0001f1ff',
    'Bosnia-Herzegovina': '\U0001f1e7\U0001f1e6',
    'Suecia': '\U0001f1f8\U0001f1ea',
    'Noruega': '\U0001f1f3\U0001f1f4',
    'Gales': '\U0001f3f4\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f',
    'Ucrania': '\U0001f1fa\U0001f1e6',
    'Polonia': '\U0001f1f5\U0001f1f1',
    'Eslovaquia': '\U0001f1f8\U0001f1f0',
    'Georgia': '\U0001f1ec\U0001f1ea',
    # CONMEBOL
    'Brasil': '\U0001f1e7\U0001f1f7',
    'Argentina': '\U0001f1e6\U0001f1f7',
    'Colombia': '\U0001f1e8\U0001f1f4',
    'Uruguay': '\U0001f1fa\U0001f1fe',
    'Ecuador': '\U0001f1ea\U0001f1e8',
    'Paraguay': '\U0001f1f5\U0001f1fe',
    'Venezuela': '\U0001f1fb\U0001f1ea',
    'Bolivia': '\U0001f1e7\U0001f1f4',
    'Chile': '\U0001f1e8\U0001f1f1',
    # CONCACAF
    'México': '\U0001f1f2\U0001f1fd',
    'Estados Unidos': '\U0001f1fa\U0001f1f8',
    'Canadá': '\U0001f1e8\U0001f1e6',
    'Panamá': '\U0001f1f5\U0001f1e6',
    'Costa Rica': '\U0001f1e8\U0001f1f7',
    'Honduras': '\U0001f1ed\U0001f1f3',
    'Jamaica': '\U0001f1ef\U0001f1f2',
    'El Salvador': '\U0001f1f8\U0001f1fb',
    'Haiti': '\U0001f1ed\U0001f1f9',
    'Curaçao': '\U0001f1e8\U0001f1fc',
    # CAF
    'Marruecos': '\U0001f1f2\U0001f1e6',
    'Nigeria': '\U0001f1f3\U0001f1ec',
    'Senegal': '\U0001f1f8\U0001f1f3',
    'Camerún': '\U0001f1e8\U0001f1f2',
    'Egipto': '\U0001f1ea\U0001f1ec',
    'Ghana': '\U0001f1ec\U0001f1ed',
    'Costa de Marfil': '\U0001f1e8\U0001f1ee',
    'Sudáfrica': '\U0001f1ff\U0001f1e6',
    'R.D. Congo': '\U0001f1e8\U0001f1e9',
    'Argelia': '\U0001f1e9\U0001f1ff',
    'Túnez': '\U0001f1f9\U0001f1f3',
    'Cabo Verde': '\U0001f1e8\U0001f1fb',
    'Mali': '\U0001f1f2\U0001f1f1',
    'Togo': '\U0001f1f9\U0001f1ec',
    'Mozambique': '\U0001f1f2\U0001f1ff',
    # AFC
    'Japón': '\U0001f1ef\U0001f1f5',
    'Corea del Sur': '\U0001f1f0\U0001f1f7',
    'Arabia Saudí': '\U0001f1f8\U0001f1e6',
    'Irán': '\U0001f1ee\U0001f1f7',
    'Australia': '\U0001f1e6\U0001f1fa',
    'Iraq': '\U0001f1ee\U0001f1f6',
    'Uzbekistán': '\U0001f1fa\U0001f1ff',
    'Jordania': '\U0001f1ef\U0001f1f4',
    'Qatar': '\U0001f1f6\U0001f1e6',
    # OFC
    'Nueva Zelanda': '\U0001f1f3\U0001f1ff',
}

# Renombrar equipos inglés -> español
RENAME = {
    'Sweden':     'Suecia',
    'Norway':     'Noruega',
    'Cape Verde': 'Cabo Verde',
    'Curaçao':    'Curaçao',
}

# Palabras que identifican equipos placeholder de ESPN
PLACEHOLDER_KEYWORDS = [
    'winner', 'loser', 'place', 'group', 'runner', 'best',
    'round of', 'semifinal', 'quarterfinal', 'third',
]


def is_placeholder(name):
    low = name.lower()
    return any(kw in low for kw in PLACEHOLDER_KEYWORDS)


def run():
    renamed = flagged = deleted = 0

    teams = Team.query.all()
    for t in teams:
        # Borrar placeholders y sus partidos
        if is_placeholder(t.name):
            matches = Match.query.filter(
                db.or_(Match.team1_id == t.id, Match.team2_id == t.id)
            ).all()
            for m in matches:
                Prediction.query.filter_by(match_id=m.id).delete()
                db.session.delete(m)
            db.session.delete(t)
            deleted += 1
            print(f'  DEL placeholder: {t.name}')
            continue

        # Renombrar
        if t.name in RENAME:
            old = t.name
            t.name = RENAME[t.name]
            print(f'  REN {old} -> {t.name}')
            renamed += 1

        # Poner bandera
        flag = FLAGS.get(t.name)
        if flag and t.flag_emoji != flag:
            t.flag_emoji = flag
            flagged += 1

    db.session.commit()
    print(f'\nBanderas actualizadas: {flagged}')
    print(f'Equipos renombrados:   {renamed}')
    print(f'Placeholders borrados: {deleted}')
    print(f'Total equipos:         {Team.query.count()}')
    print(f'Total partidos:        {Match.query.count()}')


if __name__ == '__main__':
    print('Actualizando banderas y limpiando placeholders...')
    with app.app_context():
        run()
    print('Hecho.')
