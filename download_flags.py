#!/usr/bin/env python3
"""
Descarga banderas reales (PNG) de flagcdn.com y las asigna a cada equipo.
Re-ejecutar en cualquier momento es seguro (solo descarga las que faltan).
"""
import os
import requests
from app import app, db
from models import Team, Match, Prediction

FLAGS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'flags')

# Nombre en BD → código ISO 3166-1 alpha-2 (para flagcdn.com)
ISO = {
    # UEFA
    'Alemania': 'de', 'España': 'es', 'Francia': 'fr',
    'Inglaterra': 'gb-eng', 'Países Bajos': 'nl', 'Portugal': 'pt',
    'Italia': 'it', 'Bélgica': 'be', 'Croacia': 'hr', 'Suiza': 'ch',
    'Serbia': 'rs', 'Austria': 'at', 'Escocia': 'gb-sct', 'Turquía': 'tr',
    'Hungría': 'hu', 'Dinamarca': 'dk', 'Albania': 'al', 'Eslovenia': 'si',
    'Rumanía': 'ro', 'Grecia': 'gr', 'Chequia': 'cz', 'Bosnia-Herzegovina': 'ba',
    'Suecia': 'se', 'Noruega': 'no', 'Gales': 'gb-wls', 'Ucrania': 'ua',
    'Polonia': 'pl', 'Eslovaquia': 'sk', 'Georgia': 'ge',
    # CONMEBOL
    'Brasil': 'br', 'Argentina': 'ar', 'Colombia': 'co', 'Uruguay': 'uy',
    'Ecuador': 'ec', 'Paraguay': 'py', 'Venezuela': 've', 'Bolivia': 'bo', 'Chile': 'cl',
    # CONCACAF
    'México': 'mx', 'Estados Unidos': 'us', 'Canadá': 'ca', 'Panamá': 'pa',
    'Costa Rica': 'cr', 'Honduras': 'hn', 'Jamaica': 'jm', 'El Salvador': 'sv',
    'Haiti': 'ht', 'Curaçao': 'cw',
    # CAF
    'Marruecos': 'ma', 'Nigeria': 'ng', 'Senegal': 'sn', 'Camerún': 'cm',
    'Egipto': 'eg', 'Ghana': 'gh', 'Costa de Marfil': 'ci', 'Sudáfrica': 'za',
    'R.D. Congo': 'cd', 'Argelia': 'dz', 'Túnez': 'tn', 'Cabo Verde': 'cv',
    'Mali': 'ml', 'Togo': 'tg', 'Mozambique': 'mz',
    # AFC
    'Japón': 'jp', 'Corea del Sur': 'kr', 'Arabia Saudí': 'sa', 'Irán': 'ir',
    'Australia': 'au', 'Iraq': 'iq', 'Uzbekistán': 'uz', 'Jordania': 'jo', 'Qatar': 'qa',
    # OFC
    'Nueva Zelanda': 'nz',
}

# Renombrar equipos que quedaron en inglés tras la importación de ESPN
RENAME = {
    'Sweden': 'Suecia', 'Norway': 'Noruega', 'Cape Verde': 'Cabo Verde',
    'Tunisia': 'Túnez', 'Curaçao': 'Curaçao',
}

PLACEHOLDER_KEYWORDS = [
    'winner', 'loser', 'place', 'group', 'runner', 'round of',
    'semifinal', 'quarterfinal', 'third', 'best',
]


def is_placeholder(name):
    low = name.lower()
    return any(k in low for k in PLACEHOLDER_KEYWORDS)


def ensure_flag_img_column():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE teams ADD COLUMN flag_img VARCHAR(50) DEFAULT ""'))
            conn.commit()
        print('  Columna flag_img añadida a la BD.')
    except Exception:
        pass  # ya existe


def download_png(code):
    path = os.path.join(FLAGS_DIR, f'{code}.png')
    if os.path.exists(path):
        return True
    url = f'https://flagcdn.com/w40/{code}.png'
    try:
        r = requests.get(url, timeout=12, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f'    ERROR descargando {code}: {e}')
        return False


def run():
    os.makedirs(FLAGS_DIR, exist_ok=True)

    # Crear tablas si no existen y sembrar equipos
    db.create_all()
    from models import TournamentSettings
    if not TournamentSettings.query.first():
        db.session.add(TournamentSettings())
        db.session.commit()
    if Team.query.count() == 0:
        from seed_teams import seed
        seed()

    ensure_flag_img_column()

    # 1. Limpiar placeholders de ESPN
    deleted = 0
    for t in Team.query.all():
        if is_placeholder(t.name):
            for m in Match.query.filter(
                db.or_(Match.team1_id == t.id, Match.team2_id == t.id)
            ).all():
                Prediction.query.filter_by(match_id=m.id).delete()
                db.session.delete(m)
            db.session.delete(t)
            deleted += 1
            print(f'  DEL placeholder: {t.name}')
    db.session.commit()

    # 2. Renombrar equipos en inglés
    renamed = 0
    for t in Team.query.all():
        if t.name in RENAME:
            old = t.name
            t.name = RENAME[t.name]
            renamed += 1
            print(f'  REN {old} -> {t.name}')
    db.session.commit()

    # 3. Descargar banderas y actualizar BD
    ok = fail = skip = 0
    for t in Team.query.order_by(Team.name).all():
        code = ISO.get(t.name)
        if not code:
            print(f'  SIN CODIGO ISO: {t.name}')
            fail += 1
            continue
        filename = f'{code}.png'
        if t.flag_img == filename and os.path.exists(os.path.join(FLAGS_DIR, filename)):
            skip += 1
            continue
        if download_png(code):
            t.flag_img = filename
            ok += 1
            print(f'  OK  {t.name} ({code})')
        else:
            fail += 1
    db.session.commit()

    print(f'\n  Banderas descargadas:  {ok}')
    print(f'  Ya existian:           {skip}')
    print(f'  Fallidas/sin codigo:   {fail}')
    print(f'  Placeholders borrados: {deleted}')
    print(f'  Equipos renombrados:   {renamed}')
    print(f'  Total equipos en BD:   {Team.query.count()}')
    print(f'  Total partidos en BD:  {Match.query.count()}')


if __name__ == '__main__':
    print('=' * 50)
    print('  Descargando banderas desde flagcdn.com...')
    print('=' * 50)
    with app.app_context():
        run()
    print('  Hecho.')
    print('=' * 50)
