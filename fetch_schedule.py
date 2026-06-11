#!/usr/bin/env python3
"""
Importa el calendario del Mundial 2026 desde la API de ESPN.
Ejecutar: python fetch_schedule.py
Re-ejecutar en cualquier momento para actualizar resultados.
"""
import requests
from datetime import datetime, timedelta
from app import app, db
from models import Team, Match
# Nombres ESPN/inglés -> nombres en nuestra BD
TEAM_MAP = {
    'Germany': 'Alemania', 'Spain': 'España', 'France': 'Francia',
    'England': 'Inglaterra', 'Netherlands': 'Países Bajos', 'Holland': 'Países Bajos',
    'Portugal': 'Portugal', 'Italy': 'Italia', 'Belgium': 'Bélgica',
    'Croatia': 'Croacia', 'Switzerland': 'Suiza', 'Serbia': 'Serbia',
    'Austria': 'Austria', 'Scotland': 'Escocia', 'Turkey': 'Turquía',
    'Türkiye': 'Turquía', 'Hungary': 'Hungría', 'Denmark': 'Dinamarca',
    'Albania': 'Albania', 'Slovenia': 'Eslovenia', 'Romania': 'Rumanía',
    'Greece': 'Grecia', 'Brazil': 'Brasil', 'Argentina': 'Argentina',
    'Colombia': 'Colombia', 'Uruguay': 'Uruguay', 'Ecuador': 'Ecuador',
    'Paraguay': 'Paraguay', 'Venezuela': 'Venezuela', 'Bolivia': 'Bolivia',
    'Mexico': 'México', 'United States': 'Estados Unidos', 'USA': 'Estados Unidos',
    'Canada': 'Canadá', 'Panama': 'Panamá', 'Costa Rica': 'Costa Rica',
    'Honduras': 'Honduras', 'Jamaica': 'Jamaica', 'El Salvador': 'El Salvador',
    'Morocco': 'Marruecos', 'Nigeria': 'Nigeria', 'Senegal': 'Senegal',
    'Cameroon': 'Camerún', 'Egypt': 'Egipto', 'Ghana': 'Ghana',
    "Ivory Coast": "Costa de Marfil", "Côte d'Ivoire": "Costa de Marfil",
    "Cote d'Ivoire": "Costa de Marfil",
    'South Africa': 'Sudáfrica', 'DR Congo': 'R.D. Congo', 'Congo DR': 'R.D. Congo',
    'Congo, DR': 'R.D. Congo',
    'Algeria': 'Argelia', 'Japan': 'Japón', 'South Korea': 'Corea del Sur',
    'Korea Republic': 'Corea del Sur', 'Saudi Arabia': 'Arabia Saudí',
    'Iran': 'Irán', 'Australia': 'Australia', 'Iraq': 'Iraq',
    'Uzbekistan': 'Uzbekistán', 'Jordan': 'Jordania', 'New Zealand': 'Nueva Zelanda',
    'Wales': 'Gales', 'Ukraine': 'Ucrania', 'Poland': 'Polonia',
    'Czech Republic': 'Chequia', 'Czechia': 'Chequia', 'Slovakia': 'Eslovaquia',
    'Georgia': 'Georgia', 'Mali': 'Mali', 'Tunisia': 'Túnez',
    'Togo': 'Togo', 'Mozambique': 'Mozambique',
}

ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
HEADERS  = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def resolve_team(name):
    """Busca el equipo en BD, crea si no existe."""
    mapped = TEAM_MAP.get(name, name)
    team = Team.query.filter_by(name=mapped).first()
    if not team:
        # Búsqueda parcial
        team = Team.query.filter(Team.name.ilike(f'{mapped[:4]}%')).first()
    if not team:
        print(f"    [NUEVO EQUIPO] Creando: {mapped}")
        team = Team(name=mapped, flag_emoji='🏳️')
        db.session.add(team)
        db.session.flush()
    return team


def detect_phase(text):
    t = text.lower()
    if any(k in t for k in ('group', 'grupo', 'matchday')):
        return 'group'
    if any(k in t for k in ('round of 16', 'round of sixteen', 'octavo', 'last 16')):
        return 'r16'
    if 'quarter' in t:
        return 'qf'
    if 'semi' in t:
        return 'sf'
    if 'final' in t:
        return 'final'
    return 'group'


def parse_date(date_str):
    for fmt in ('%Y-%m-%dT%H:%MZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.000Z'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"No se pudo parsear la fecha: {date_str}")


def fetch_day(day):
    url = f"{ESPN_URL}?dates={day.strftime('%Y%m%d')}&limit=30"
    try:
        r = requests.get(url, timeout=12, headers=HEADERS)
        r.raise_for_status()
        return r.json().get('events', [])
    except requests.exceptions.RequestException as e:
        print(f"  Error de red {day.strftime('%d/%m')}: {e}")
        return []


def import_matches(start_date, end_date, recalc=False):
    added = updated = skipped = 0
    match_number = Match.query.count()

    day = start_date
    while day <= end_date:
        events = fetch_day(day)

        if events:
            print(f"\n  {day.strftime('%d/%m/%Y')} — {len(events)} partidos encontrados")

        for ev in events:
            try:
                name = ev.get('name', '?')
                comp = ev['competitions'][0]
                competitors = comp.get('competitors', [])
                if len(competitors) < 2:
                    continue

                # Determinar local/visitante
                home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                name1 = home['team']['displayName']
                name2 = away['team']['displayName']

                # Fecha UTC
                dt = parse_date(ev['date'])

                # Fase
                phase = 'group'
                for note in comp.get('notes', []):
                    hl = note.get('headline', '')
                    if hl:
                        phase = detect_phase(hl)
                        break
                # Fallback desde el nombre del evento
                if phase == 'group':
                    phase = detect_phase(ev.get('name', '') + ev.get('shortName', ''))

                # Venue
                venue   = comp.get('venue', {})
                city    = venue.get('address', {}).get('city', '')
                stadium = venue.get('fullName', '')

                # Estado y resultado
                status   = comp.get('status', {}).get('type', {})
                is_done  = status.get('completed', False)
                score1 = score2 = None
                if is_done:
                    try:
                        score1 = int(home.get('score', ''))
                        score2 = int(away.get('score', ''))
                    except (ValueError, TypeError):
                        is_done = False

                team1 = resolve_team(name1)
                team2 = resolve_team(name2)

                # Buscar partido existente (mismo día + mismos equipos)
                existing = Match.query.filter(
                    Match.team1_id == team1.id,
                    Match.team2_id == team2.id,
                    db.func.date(Match.match_date) == dt.date()
                ).first()

                if existing:
                    changed = False
                    if is_done and score1 is not None and existing.goals1 is None:
                        existing.goals1 = score1
                        existing.goals2 = score2
                        existing.is_locked = True
                        if recalc:
                            from app import recalc_match, recalc_worst_teams
                            recalc_match(existing)
                        changed = True
                        updated += 1
                        print(f"    UPD  {name1} {score1}-{score2} {name2}")
                    elif not existing.city and city:
                        existing.city    = city
                        existing.stadium = stadium
                        changed = True
                    if not changed:
                        skipped += 1
                else:
                    match_number += 1
                    m = Match(
                        phase=phase,
                        team1_id=team1.id,
                        team2_id=team2.id,
                        match_date=dt,
                        city=city,
                        stadium=stadium,
                        match_number=match_number,
                        goals1=score1,
                        goals2=score2,
                        is_locked=is_done,
                    )
                    db.session.add(m)
                    added += 1
                    score_str = f" [{score1}-{score2}]" if is_done else ""
                    print(f"    ADD  {name1} vs {name2}  {dt.strftime('%d/%m %H:%M')} UTC{score_str}")

            except Exception as e:
                print(f"    [SKIP] {ev.get('name', '?')}: {e}")

        db.session.commit()
        day += timedelta(days=1)

    return added, updated, skipped


def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))


if __name__ == '__main__':
    import sys
    recalc = '--recalc' in sys.argv

    # Rango completo del Mundial 2026
    START = datetime(2026, 6, 11)
    END   = datetime(2026, 7, 20)

    print("=" * 55)
    print("  ZURULLO WC — Importando partidos desde ESPN")
    print(f"  Periodo: {START.strftime('%d/%m/%Y')} — {END.strftime('%d/%m/%Y')}")
    if recalc:
        print("  Modo: recalcular puntos al actualizar resultados")
    print("=" * 55)

    with app.app_context():
        a, u, s = import_matches(START, END, recalc=recalc)
        if recalc:
            from app import recalc_worst_teams
            recalc_worst_teams()
        print("\n" + "=" * 55)
        print(f"  Añadidos:    {a}")
        print(f"  Actualizados:{u}")
        print(f"  Ignorados:   {s}")
        print(f"  Total en BD: {Match.query.count()}")
        print("=" * 55)
