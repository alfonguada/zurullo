#!/usr/bin/env python3
"""
Busca URLs de fotos en TheSportsDB y las guarda en la BD.
NO descarga nada — el navegador carga las imágenes directamente.

Uso:
  python fetch_player_images.py           # solo jugadores sin imagen
  python fetch_player_images.py --all     # re-procesa todos
  python fetch_player_images.py --test    # prueba con 10 jugadores
"""
import os
import sys
import time
import unicodedata
import requests

API_BASE = 'https://www.thesportsdb.com/api/v1/json/3'
HEADERS  = {'User-Agent': 'ZurulloWC/2.0'}
DELAY    = 0.8


def strip_accents(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def find_image_url(name):
    """Devuelve URL de foto del jugador o None."""
    for search_name in [name, strip_accents(name)]:
        try:
            r = requests.get(
                f'{API_BASE}/searchplayers.php',
                params={'p': search_name},
                headers=HEADERS,
                timeout=12
            )
            if r.status_code != 200:
                continue
            players = r.json().get('player') or []
            for p in players:
                sport = (p.get('strSport') or '').lower()
                url = p.get('strThumb') or p.get('strCutout') or ''
                if url and sport in ('soccer', 'football', ''):
                    return url
            # primer resultado aunque no sea fútbol
            for p in players:
                if p.get('strThumb'):
                    return p['strThumb']
        except Exception as e:
            print(f'      API error: {e}')
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
        print(f'\n{mode} — {total} jugadores\n')

        ok = skip = fail = 0

        for i, player in enumerate(players, 1):
            # Ya tiene URL almacenada
            if player.image and player.image.startswith('http') and not force_all:
                skip += 1
                print(f'[{i:3}/{total}] SKIP  {player.name}')
                continue

            print(f'[{i:3}/{total}] {player.name:<32}', end=' ', flush=True)

            url = find_image_url(player.name)
            if url:
                player.image = url
                ok += 1
                print(f'OK')
            else:
                fail += 1
                print('FAIL (no encontrado)')

            time.sleep(DELAY)

            if i % 25 == 0:
                db.session.commit()
                print(f'\n  ··· {i}/{total} ({i/total*100:.0f}%) guardado ···\n')

        db.session.commit()
        print(f'\n{"─"*45}')
        print(f'  OK:        {ok}')
        print(f'  Saltados:  {skip}')
        print(f'  Sin foto:  {fail}')
        print(f'  TOTAL:     {total}')
        print(f'{"─"*45}\n')
        print('Las URLs quedan guardadas en la BD.')
        print('El navegador carga las imágenes directamente — sin descargas.')


if __name__ == '__main__':
    main()
