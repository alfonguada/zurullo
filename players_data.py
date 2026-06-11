"""
Catálogo de cromos del Zurullo World Cup 2026.
Formato: (nombre, equipo_en_bd, posición, rareza, emoji)
Rarezas: common · rare · epic · legendary
"""

PLAYERS = [
    # ── LEGENDARIOS ──────────────────────────────────────────────────────────
    ('Kylian Mbappé',       'Francia',        'DEL', 'legendary', '⚡'),
    ('Lionel Messi',        'Argentina',      'DEL', 'legendary', '🐐'),
    ('Cristiano Ronaldo',   'Portugal',       'DEL', 'legendary', '🔴'),
    ('Vinicius Jr.',        'Brasil',         'EXT', 'legendary', '🌟'),
    ('Erling Haaland',      'Noruega',        'DEL', 'legendary', '💥'),
    ('Lamine Yamal',        'España',         'EXT', 'legendary', '✨'),

    # ── ÉPICOS ───────────────────────────────────────────────────────────────
    ('Jude Bellingham',     'Inglaterra',     'MED', 'epic', '🎯'),
    ('Pedri',               'España',         'MED', 'epic', '🎪'),
    ('Rodrygo',             'Brasil',         'EXT', 'epic', '🚀'),
    ('Jamal Musiala',       'Alemania',       'MED', 'epic', '🪄'),
    ('Florian Wirtz',       'Alemania',       'MED', 'epic', '⚗️'),
    ('Bukayo Saka',         'Inglaterra',     'EXT', 'epic', '🔥'),
    ('Gavi',                'España',         'MED', 'epic', '💫'),
    ('Nico Williams',       'España',         'EXT', 'epic', '🏃'),
    ('Antoine Griezmann',   'Francia',        'DEL', 'epic', '🎭'),
    ('Rafael Leão',         'Portugal',       'EXT', 'epic', '💨'),
    ('Khvicha Kvaratskhelia','Georgia',       'EXT', 'epic', '🌀'),
    ('Julián Álvarez',      'Argentina',      'DEL', 'epic', '🦁'),
    ('Lautaro Martínez',    'Argentina',      'DEL', 'epic', '⚙️'),
    ('Endrick',             'Brasil',         'DEL', 'epic', '🆕'),
    ('Takefusa Kubo',       'Japón',          'EXT', 'epic', '🌸'),
    ('Xavi Simons',         'Países Bajos',   'MED', 'epic', '🎶'),
    ('Goncalo Ramos',       'Portugal',       'DEL', 'epic', '🎯'),

    # ── RAROS ────────────────────────────────────────────────────────────────
    ('Rodri',               'España',         'MED', 'rare', '🧠'),
    ('Álvaro Morata',       'España',         'DEL', 'rare', '💪'),
    ('Dani Carvajal',       'España',         'DEF', 'rare', '🛡️'),
    ('Aymeric Laporte',     'España',         'DEF', 'rare', '🏔️'),
    ('Unai Simón',          'España',         'POR', 'rare', '🧤'),
    ('Ousmane Dembélé',     'Francia',        'EXT', 'rare', '🎨'),
    ('Marcus Thuram',       'Francia',        'DEL', 'rare', '🦅'),
    ('Aurelien Tchouaméni', 'Francia',        'MED', 'rare', '🎵'),
    ('Harry Kane',          'Inglaterra',     'DEL', 'rare', '👑'),
    ('Phil Foden',          'Inglaterra',     'EXT', 'rare', '🌈'),
    ('Declan Rice',         'Inglaterra',     'MED', 'rare', '⛰️'),
    ('Trent Alexander-Arnold','Inglaterra',   'DEF', 'rare', '📐'),
    ('Joshua Kimmich',      'Alemania',       'MED', 'rare', '🔬'),
    ('Thomas Müller',       'Alemania',       'DEL', 'rare', '🎭'),
    ('Leroy Sané',          'Alemania',       'EXT', 'rare', '💨'),
    ('Bernardo Silva',      'Portugal',       'MED', 'rare', '🎻'),
    ('Rúben Dias',          'Portugal',       'DEF', 'rare', '🗿'),
    ('João Cancelo',        'Portugal',       'DEF', 'rare', '⚡'),
    ('Virgil van Dijk',     'Países Bajos',   'DEF', 'rare', '🗼'),
    ('Frenkie de Jong',     'Países Bajos',   'MED', 'rare', '🌷'),
    ('Cody Gakpo',          'Países Bajos',   'EXT', 'rare', '🔮'),
    ('Kevin De Bruyne',     'Bélgica',        'MED', 'rare', '🎼'),
    ('Romelu Lukaku',       'Bélgica',        'DEL', 'rare', '🏋️'),
    ('Marquinhos',          'Brasil',         'DEF', 'rare', '🛡️'),
    ('Raphinha',            'Brasil',         'EXT', 'rare', '🦋'),
    ('Bruno Guimarães',     'Brasil',         'MED', 'rare', '🎯'),
    ('Enzo Fernández',      'Argentina',      'MED', 'rare', '🌊'),
    ('Rodrigo de Paul',     'Argentina',      'MED', 'rare', '🏄'),
    ('Alexis Mac Allister', 'Argentina',      'MED', 'rare', '🎪'),
    ('Heung-min Son',       'Corea del Sur',  'EXT', 'rare', '🌙'),
    ('Lee Kang-in',         'Corea del Sur',  'MED', 'rare', '⭐'),
    ('Christian Pulisic',   'Estados Unidos', 'EXT', 'rare', '🦅'),
    ('Achraf Hakimi',       'Marruecos',      'DEF', 'rare', '🌙'),
    ('Youssef En-Nesyri',   'Marruecos',      'DEL', 'rare', '🦁'),
    ('Federico Valverde',   'Uruguay',        'MED', 'rare', '💣'),
    ('Darwin Núñez',        'Uruguay',        'DEL', 'rare', '🌪️'),
    ('James Rodríguez',     'Colombia',       'MED', 'rare', '☀️'),
    ('Luis Díaz',           'Colombia',       'EXT', 'rare', '🎸'),
    ('Hirving Lozano',      'México',         'EXT', 'rare', '🌶️'),
    ('Keylor Navas',        'Costa Rica',     'POR', 'rare', '🐆'),
    ('Kaoru Mitoma',        'Japón',          'EXT', 'rare', '🌊'),
    ('Wataru Endo',         'Japón',          'MED', 'rare', '🎌'),
    ('Sandro Tonali',       'Italia',         'MED', 'rare', '🖤'),
    ('Nicolò Barella',      'Italia',         'MED', 'rare', '⚡'),
    ('Granit Xhaka',        'Suiza',          'MED', 'rare', '🏔️'),

    # ── COMUNES ──────────────────────────────────────────────────────────────
    ('Mikel Oyarzabal',     'España',         'DEL', 'common', '⚽'),
    ('Marc Cucurella',      'España',         'DEF', 'common', '💇'),
    ('Jordi Alba',          'España',         'DEF', 'common', '⚽'),
    ('William Saliba',      'Francia',        'DEF', 'common', '🏰'),
    ('Theo Hernández',      'Francia',        'DEF', 'common', '🏎️'),
    ('Kobbie Mainoo',       'Inglaterra',     'MED', 'common', '🌱'),
    ('Kai Havertz',         'Alemania',       'DEL', 'common', '🎯'),
    ('Serge Gnabry',        'Alemania',       'EXT', 'common', '⚽'),
    ('Yannick Carrasco',    'Bélgica',        'EXT', 'common', '🐦'),
    ('Gavi',                'España',         'MED', 'common', '⚽'),
    ('Fede Chiesa',         'Italia',         'EXT', 'common', '⚽'),
    ('Luka Modric',         'Croacia',        'MED', 'common', '🎩'),
    ('Ivan Perisic',        'Croacia',        'EXT', 'common', '⚽'),
    ('Aleksandar Mitrovic', 'Serbia',         'DEL', 'common', '🐻'),
    ('Dusan Vlahovic',      'Serbia',         'DEL', 'common', '🔱'),
    ('Fabian Ruiz',         'España',         'MED', 'common', '⚽'),
    ('Weston McKennie',     'Estados Unidos', 'MED', 'common', '⭐'),
    ('Giovanni Reyna',      'Estados Unidos', 'MED', 'common', '🌟'),
    ('Rodrigo Bentancur',   'Uruguay',        'MED', 'common', '⚽'),
    ('Luis Suárez',         'Uruguay',        'DEL', 'common', '🦷'),
    ('Sálim Al-Dawsari',    'Arabia Saudí',   'EXT', 'common', '🌙'),
    ('Akram Afif',          'Qatar',          'EXT', 'common', '🌴'),
    ('Noussair Mazraoui',   'Marruecos',      'DEF', 'common', '⚽'),
    ('Matteo Guendouzi',    'Francia',        'MED', 'common', '⚽'),
    ('Santiago Giménez',    'México',         'DEL', 'common', '🌵'),
    ('Edson Álvarez',       'México',         'MED', 'common', '⚽'),
    ('Matt Turner',         'Estados Unidos', 'POR', 'common', '🦅'),
    ('Ali Al-Bulayhi',      'Arabia Saudí',   'DEF', 'common', '⚽'),
    ('Remo Freuler',        'Suiza',          'MED', 'common', '⚽'),
    ('Granit Xhaka',        'Suiza',          'MED', 'common', '⚽'),
    ('Joao Felix',          'Portugal',       'DEL', 'common', '🦋'),
    ('Nuno Mendes',         'Portugal',       'DEF', 'common', '⚽'),
]

# Cartas especiales (no son jugadores)
SPECIAL_CARDS = [
    ('Golazo del Torneo',     None, 'ESPECIAL', 'epic',      '🚀'),
    ('Parada Imposible',      None, 'ESPECIAL', 'epic',      '🧤'),
    ('VAR Crisis',            None, 'ESPECIAL', 'rare',      '📺'),
    ('Larguero Maldito',      None, 'ESPECIAL', 'rare',      '😱'),
    ('Hat-Trick Histórico',   None, 'ESPECIAL', 'legendary', '🎩'),
    ('Penalti Fallado',       None, 'ESPECIAL', 'common',    '🤦'),
    ('Lesión Táctica',        None, 'ESPECIAL', 'common',    '🩹'),
    ('Expulsión Épica',       None, 'ESPECIAL', 'rare',      '🟥'),
    ('Aficionado del Año',    None, 'ESPECIAL', 'epic',      '📣'),
    ('El Milagro',            None, 'ESPECIAL', 'legendary', '✨'),
    ('Árbitro Loco',          None, 'ESPECIAL', 'common',    '🦺'),
    ('Prórroga Infinita',     None, 'ESPECIAL', 'rare',      '⏱️'),
    ('Capitán de Capitanes',  None, 'ESPECIAL', 'epic',      '🏅'),
    ('Debut Histórico',       None, 'ESPECIAL', 'rare',      '🌱'),
    ('Campeón Inesperado',    None, 'ESPECIAL', 'legendary', '🏆'),
]


def seed_players(db, Player, Team):
    if Player.query.count() > 0:
        return
    teams = {t.name: t.id for t in Team.query.all()}
    for name, team_name, pos, rarity, icon in PLAYERS:
        p = Player(
            name=name,
            team_id=teams.get(team_name),
            position=pos,
            rarity=rarity,
            icon=icon,
            card_type='player',
        )
        db.session.add(p)
    for name, _, pos, rarity, icon in SPECIAL_CARDS:
        p = Player(
            name=name,
            team_id=None,
            position=pos,
            rarity=rarity,
            icon=icon,
            card_type='special',
        )
        db.session.add(p)
    db.session.commit()
    print(f'Cromos sembrados: {Player.query.count()} cartas.')
