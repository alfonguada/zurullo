#!/usr/bin/env python3
"""
Busca URLs de fotos en TheSportsDB y las guarda en la BD.
Maneja rate limiting con reintentos y pausas automáticas.

Uso:
  python fetch_player_images.py           # solo jugadores sin imagen
  python fetch_player_images.py --all     # re-procesa todos
  python fetch_player_images.py --test    # prueba con 10 jugadores

Tiempo estimado: ~25-30 min para 524 jugadores (2s delay + pausas).
Puedes pararlo y relanzar — los ya procesados se saltan automáticamente.
"""
import os
import sys
import time
import unicodedata
import requests

API_BASE     = 'https://www.thesportsdb.com/api/v1/json/3'
HEADERS      = {'User-Agent': 'ZurulloWC/2.0'}
DELAY        = 2.0   # segundos entre peticiones normales
PAUSE_EVERY  = 20    # pausa larga cada N jugadores procesados
PAUSE_LONG   = 35    # segundos de pausa larga
FAIL_RETRY   = 3     # reintentos al detectar posible rate limit
FAIL_SLEEP   = 12    # espera entre reintentos


def strip_accents(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def api_search(name):
    """Llama a la API y devuelve lista de jugadores o None en error."""
    try:
        r = requests.get(
            f'{API_BASE}/searchplayers.php',
            params={'p': name},
            headers=HEADERS,
            timeout=14
        )
        if r.status_code == 429:
            return None  # rate limit explícito
        if r.status_code == 200:
            return r.json().get('player') or []
    except Exception as e:
        print(f'  err={e}', end=' ')
    return None


def find_image_url(name):
    """
    Busca la URL de foto con reintentos y pausa anti-rate-limit.
    Prueba nombre original y sin tildes.
    """
    # Cartas ultra: "Messi ✦ BALÓN DE ORO" → buscar solo "Messi"
    if '✦' in name:
        name = name.split('✦')[0].strip()

    candidates = [name, strip_accents(name)]
    # También probar solo apellido para jugadores difíciles
    parts = name.split()
    if len(parts) >= 2:
        candidates.append(parts[-1])        # solo apellido
        candidates.append(strip_accents(parts[-1]))

    seen = []
    for search_name in candidates:
        if search_name in seen:
            continue
        seen.append(search_name)

        for attempt in range(FAIL_RETRY):
            players = api_search(search_name)

            if players is None:
                # Rate limit detectado — esperar y reintentar
                wait = FAIL_SLEEP * (attempt + 1)
                print(f'\n  ⚠ rate limit (intento {attempt+1}), esperando {wait}s...', end='')
                time.sleep(wait)
                continue

            if len(players) == 0 and attempt == 0:
                # Respuesta vacía — podría ser RL; un reintento suave
                time.sleep(4)
                continue

            # Buscar jugador de fútbol primero
            for p in players:
                sport = (p.get('strSport') or '').lower()
                url   = p.get('strThumb') or p.get('strCutout') or ''
                if url and sport in ('soccer', 'football', ''):
                    return url
            # Cualquier resultado con thumb
            for p in players:
                if p.get('strThumb'):
                    return p['strThumb']

            break  # búsqueda OK pero sin resultado → probar siguiente candidato

        time.sleep(DELAY)

    return None


def main():
    force_all = '--all'  in sys.argv
    test_mode = '--test' in sys.argv

    from app import app, db
    from models import Player

    with app.app_context():
        q = Player.query.filter_by(card_type='player')

        if test_mode:
            players = q.limit(10).all()
        elif not force_all:
            players = q.filter(
                db.or_(Player.image == None, Player.image == '')
            ).all()
        else:
            players = q.all()

        total = len(players)
        mode  = 'TEST' if test_mode else ('ALL' if force_all else 'PENDING')
        print(f'\n{mode} — {total} jugadores (delay={DELAY}s, pausa/{PAUSE_EVERY})\n')

        ok = skip = fail = 0
        processed = 0   # contador para las pausas largas

        for i, player in enumerate(players, 1):
            # Ya tiene URL → saltar
            if player.image and player.image.startswith('http') and not force_all:
                skip += 1
                print(f'[{i:3}/{total}] SKIP  {player.name}')
                continue

            print(f'[{i:3}/{total}] {player.name:<32}', end=' ', flush=True)

            url = find_image_url(player.name)
            if url:
                player.image = url
                ok += 1
                print('OK')
            else:
                fail += 1
                print('FAIL')

            processed += 1

            # Pausa larga cada PAUSE_EVERY jugadores procesados
            if processed % PAUSE_EVERY == 0:
                db.session.commit()
                print(f'\n  ··· {i}/{total} ({i/total*100:.0f}%) — pausa {PAUSE_LONG}s anti-rate-limit ···\n')
                time.sleep(PAUSE_LONG)
            else:
                time.sleep(DELAY)

        db.session.commit()

        print(f'\n{"─"*45}')
        print(f'  OK:        {ok}')
        print(f'  Saltados:  {skip}')
        print(f'  Sin foto:  {fail}')
        print(f'  TOTAL:     {total}')
        print(f'{"─"*45}')
        print('\nURLs guardadas. Recarga la web app para ver las fotos.')


if __name__ == '__main__':
    main()
