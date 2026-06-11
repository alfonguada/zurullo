#!/usr/bin/env python3
"""
Descarga fotos de jugadores desde TheSportsDB y las guarda en static/players/.

Uso:
  python fetch_player_images.py           # solo jugadores sin imagen
  python fetch_player_images.py --all     # re-descarga todos
  python fetch_player_images.py --test    # prueba con 10 jugadores

Tiempo estimado: ~8-10 min para los 534 jugadores completos.
"""
import os
import sys
import time
import unicodedata
import requests

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PLAYERS_DIR = os.path.join(BASE_DIR, 'static', 'players')
os.makedirs(PLAYERS_DIR, exist_ok=True)

API_BASE = 'https://www.thesportsdb.com/api/v1/json/3'
HEADERS  = {'User-Agent': 'ZurulloWC/2.0 (+https://github.com/alfonguada/zurullo)'}
DELAY    = 0.9   # segundos entre llamadas a la API


def strip_accents(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def search_image_url(name):
    """Busca en TheSportsDB. Devuelve URL de imagen o None."""
    attempts = [name, strip_accents(name)]
    for attempt in attempts:
        try:
            r = requests.get(
                f'{API_BASE}/searchplayers.php',
                params={'p': attempt},
                headers=HEADERS,
                timeout=12
            )
            if r.status_code != 200:
                continue
            players = r.json().get('player') or []
            # Preferir jugador de fútbol
            for p in players:
                sport = (p.get('strSport') or '').lower()
                thumb = p.get('strThumb') or p.get('strCutout') or ''
                if sport in ('soccer', 'football', '') and thumb:
                    return thumb
            # Si no, primer resultado con thumb
            for p in players:
                if p.get('strThumb'):
                    return p['strThumb']
        except Exception as e:
            print(f'      API error: {e}')
        time.sleep(DELAY)
    return None


def download_image(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if r.status_code == 200:
            content = r.content
            if len(content) > 1500:   # descartar placeholders vacíos (<1.5KB)
                with open(filepath, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f'      Download error: {e}')
    return False


def main():
    force_all = '--all'  in sys.argv
    test_mode = '--test' in sys.argv

    from app import app, db
    from models import Player

    with app.app_context():
        query = Player.query.filter_by(card_type='player')
        if test_mode:
            players = query.limit(10).all()
        elif not force_all:
            players = query.filter(
                db.or_(Player.image == None, Player.image == '')
            ).all()
        else:
            players = query.all()

        total = len(players)
        print(f'\n{"TEST" if test_mode else "ALL" if force_all else "PENDING"} mode — {total} jugadores\n')

        ok = skip = fail = 0

        for i, player in enumerate(players, 1):
            filepath = os.path.join(PLAYERS_DIR, f'{player.id}.jpg')

            # Archivo ya existe (y no forzamos re-descarga)
            if os.path.exists(filepath) and not force_all:
                if not player.image:
                    player.image = f'{player.id}.jpg'
                skip += 1
                print(f'[{i:3}/{total}] SKIP  {player.name}')
                continue

            print(f'[{i:3}/{total}] {player.name:<30}', end=' ', flush=True)

            img_url = search_image_url(player.name)
            if img_url:
                if download_image(img_url, filepath):
                    player.image = f'{player.id}.jpg'
                    size_kb = os.path.getsize(filepath) // 1024
                    ok += 1
                    print(f'OK  ({size_kb}KB)')
                else:
                    fail += 1
                    print('FAIL  (descarga)')
            else:
                fail += 1
                print('FAIL  (no encontrado)')

            time.sleep(DELAY)

            if i % 25 == 0:
                db.session.commit()
                pct = i / total * 100
                print(f'\n  ··· {i}/{total} ({pct:.0f}%) — guardado ···\n')

        db.session.commit()
        print(f'\n{"─"*50}')
        print(f'  OK:       {ok}')
        print(f'  Saltados: {skip}')
        print(f'  Sin foto: {fail}')
        print(f'  TOTAL:    {total}')
        print(f'  Carpeta:  {PLAYERS_DIR}')
        print(f'{"─"*50}\n')


if __name__ == '__main__':
    main()
