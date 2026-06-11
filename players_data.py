"""
Catálogo de cromos del Zurullo World Cup 2026.
Formato: (nombre, equipo_en_bd, posición, rareza, emoji)
Rarezas: common · rare · epic · legendary
Posiciones: DEL · EXT · MED · DEF · POR
"""

PLAYERS = [

    # ══════════════════════════════════════════════════════════
    # ULTRA — EDICIONES ESPECIALES (tipo Adrenalyn / Balón de Oro)
    # ══════════════════════════════════════════════════════════
    ('Messi ✦ BALÓN DE ORO',       'Argentina',    'DEL', 'ultra', '🐐'),
    ('Ronaldo ✦ UCL KING',         'Portugal',     'DEL', 'ultra', '🔴'),
    ('Mbappé ✦ CHAMPIONS',         'Francia',      'DEL', 'ultra', '⚡'),
    ('Haaland ✦ GOLDEN BOOT',      'Noruega',      'DEL', 'ultra', '💥'),
    ('Bellingham ✦ RISING STAR',   'Inglaterra',   'MED', 'ultra', '🎯'),
    ('Vinicius ✦ BALÓN DE ORO',    'Brasil',       'EXT', 'ultra', '🌟'),
    ('Yamal ✦ MEJOR JOVEN',        'España',       'EXT', 'ultra', '✨'),
    ('De Bruyne ✦ TOTY',           'Bélgica',      'MED', 'ultra', '🎼'),
    ('Pedri ✦ GOLDEN BOY',         'España',       'MED', 'ultra', '🎪'),
    ('Rodri ✦ BALÓN DE ORO',       'España',       'MED', 'ultra', '🧠'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — ESPAÑA (18)
    # ══════════════════════════════════════════════════════════
    ('Lamine Yamal',        'España', 'EXT', 'legendary', '✨'),
    ('Pedri',               'España', 'MED', 'epic',      '🎪'),
    ('Gavi',                'España', 'MED', 'epic',      '💫'),
    ('Nico Williams',       'España', 'EXT', 'epic',      '🏃'),
    ('Rodri',               'España', 'MED', 'rare',      '🧠'),
    ('Dani Olmo',           'España', 'MED', 'rare',      '🎭'),
    ('Fabián Ruiz',         'España', 'MED', 'rare',      '🎯'),
    ('Álvaro Morata',       'España', 'DEL', 'rare',      '💪'),
    ('Ferran Torres',       'España', 'EXT', 'rare',      '🔥'),
    ('Dani Carvajal',       'España', 'DEF', 'rare',      '🛡️'),
    ('Aymeric Laporte',     'España', 'DEF', 'rare',      '🏔️'),
    ('Le Normand',          'España', 'DEF', 'rare',      '🗿'),
    ('Unai Simón',          'España', 'POR', 'rare',      '🧤'),
    ('Alejandro Grimaldo',  'España', 'DEF', 'common',    '🔋'),
    ('Mikel Merino',        'España', 'MED', 'common',    '🔧'),
    ('Mikel Oyarzabal',     'España', 'DEL', 'common',    '⚽'),
    ('Marc Cucurella',      'España', 'DEF', 'common',    '💇'),
    ('David Raya',          'España', 'POR', 'common',    '🥅'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — FRANCIA (17)
    # ══════════════════════════════════════════════════════════
    ('Kylian Mbappé',       'Francia', 'DEL', 'legendary', '⚡'),
    ('Antoine Griezmann',   'Francia', 'DEL', 'epic',      '🎭'),
    ('Eduardo Camavinga',   'Francia', 'MED', 'rare',      '🌱'),
    ('Ousmane Dembélé',     'Francia', 'EXT', 'rare',      '🎨'),
    ('Marcus Thuram',       'Francia', 'DEL', 'rare',      '🦅'),
    ('Aurélien Tchouaméni', 'Francia', 'MED', 'rare',      '🎵'),
    ('William Saliba',      'Francia', 'DEF', 'rare',      '🏰'),
    ('Théo Hernández',      'Francia', 'DEF', 'rare',      '🏎️'),
    ('Jules Koundé',        'Francia', 'DEF', 'rare',      '🔐'),
    ('Mike Maignan',        'Francia', 'POR', 'rare',      '🧤'),
    ('Bradley Barcola',     'Francia', 'EXT', 'rare',      '🌟'),
    ('Youssouf Fofana',     'Francia', 'MED', 'common',    '⚽'),
    ('Randal Kolo Muani',   'Francia', 'DEL', 'common',    '🏹'),
    ('Matteo Guendouzi',    'Francia', 'MED', 'common',    '⚽'),
    ('Dayot Upamecano',     'Francia', 'DEF', 'common',    '🧱'),
    ('Jonathan Clauss',     'Francia', 'DEF', 'common',    '⚽'),
    ('Warren Zaïre-Emery',  'Francia', 'MED', 'common',    '🆕'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — BRASIL (17)
    # ══════════════════════════════════════════════════════════
    ('Vinicius Jr.',        'Brasil', 'EXT', 'legendary', '🌟'),
    ('Rodrygo',             'Brasil', 'EXT', 'epic',      '🚀'),
    ('Endrick',             'Brasil', 'DEL', 'epic',      '🆕'),
    ('Savinho',             'Brasil', 'EXT', 'rare',      '🏃'),
    ('Raphinha',            'Brasil', 'EXT', 'rare',      '🦋'),
    ('Bruno Guimarães',     'Brasil', 'MED', 'rare',      '🎯'),
    ('Lucas Paquetá',       'Brasil', 'MED', 'rare',      '🎶'),
    ('Marquinhos',          'Brasil', 'DEF', 'rare',      '🛡️'),
    ('Éder Militão',        'Brasil', 'DEF', 'rare',      '⚔️'),
    ('Alisson',             'Brasil', 'POR', 'rare',      '🧤'),
    ('Gabriel Martinelli',  'Brasil', 'EXT', 'rare',      '🔥'),
    ('Matheus Cunha',       'Brasil', 'DEL', 'rare',      '🐆'),
    ('Danilo',              'Brasil', 'DEF', 'common',    '⚽'),
    ('Casemiro',            'Brasil', 'MED', 'common',    '🦁'),
    ('Gabriel Magalhães',   'Brasil', 'DEF', 'common',    '⚽'),
    ('Gerson',              'Brasil', 'MED', 'common',    '⚽'),
    ('Andreas Pereira',     'Brasil', 'MED', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — ARGENTINA (17)
    # ══════════════════════════════════════════════════════════
    ('Lionel Messi',        'Argentina', 'DEL', 'legendary', '🐐'),
    ('Julián Álvarez',      'Argentina', 'DEL', 'epic',      '🦁'),
    ('Lautaro Martínez',    'Argentina', 'DEL', 'epic',      '⚙️'),
    ('Enzo Fernández',      'Argentina', 'MED', 'rare',      '🌊'),
    ('Alexis Mac Allister', 'Argentina', 'MED', 'rare',      '🎪'),
    ('Rodrigo de Paul',     'Argentina', 'MED', 'rare',      '🏄'),
    ('Paulo Dybala',        'Argentina', 'DEL', 'rare',      '🌹'),
    ('Ángel Di María',      'Argentina', 'EXT', 'rare',      '👻'),
    ('Cristian Romero',     'Argentina', 'DEF', 'rare',      '🪖'),
    ('Lisandro Martínez',   'Argentina', 'DEF', 'rare',      '🔒'),
    ('Emiliano Martínez',   'Argentina', 'POR', 'rare',      '🧤'),
    ('Nicolás González',    'Argentina', 'EXT', 'common',    '🌪️'),
    ('Nahuel Molina',       'Argentina', 'DEF', 'common',    '⚡'),
    ('Nicolás Otamendi',    'Argentina', 'DEF', 'common',    '🏔️'),
    ('Marcos Acuña',        'Argentina', 'DEF', 'common',    '⚽'),
    ('Germán Pezzella',     'Argentina', 'DEF', 'common',    '⚽'),
    ('Leandro Paredes',     'Argentina', 'MED', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — INGLATERRA (17)
    # ══════════════════════════════════════════════════════════
    ('Jude Bellingham',     'Inglaterra', 'MED', 'legendary', '🎯'),
    ('Bukayo Saka',         'Inglaterra', 'EXT', 'epic',      '🔥'),
    ('Cole Palmer',         'Inglaterra', 'MED', 'epic',      '🎨'),
    ('Phil Foden',          'Inglaterra', 'EXT', 'rare',      '🌈'),
    ('Harry Kane',          'Inglaterra', 'DEL', 'rare',      '👑'),
    ('Declan Rice',         'Inglaterra', 'MED', 'rare',      '⛰️'),
    ('Kobbie Mainoo',       'Inglaterra', 'MED', 'rare',      '🌱'),
    ('Trent Alexander-Arnold','Inglaterra','DEF','rare',      '📐'),
    ('Jordan Pickford',     'Inglaterra', 'POR', 'rare',      '🧤'),
    ('Marc Guehi',          'Inglaterra', 'DEF', 'common',    '🛡️'),
    ('John Stones',         'Inglaterra', 'DEF', 'common',    '🪨'),
    ('Ezri Konsa',          'Inglaterra', 'DEF', 'common',    '⚽'),
    ('Luke Shaw',           'Inglaterra', 'DEF', 'common',    '⚽'),
    ('Marcus Rashford',     'Inglaterra', 'EXT', 'common',    '⚡'),
    ('Ollie Watkins',       'Inglaterra', 'DEL', 'common',    '⚽'),
    ('Morgan Gibbs-White',  'Inglaterra', 'MED', 'common',    '⚽'),
    ('Conor Gallagher',     'Inglaterra', 'MED', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — ALEMANIA (17)
    # ══════════════════════════════════════════════════════════
    ('Jamal Musiala',       'Alemania', 'MED', 'legendary', '🪄'),
    ('Florian Wirtz',       'Alemania', 'MED', 'epic',      '⚗️'),
    ('Joshua Kimmich',      'Alemania', 'MED', 'rare',      '🔬'),
    ('Ilkay Gündogan',      'Alemania', 'MED', 'rare',      '🧩'),
    ('Kai Havertz',         'Alemania', 'DEL', 'rare',      '🎯'),
    ('Leroy Sané',          'Alemania', 'EXT', 'rare',      '💨'),
    ('Antonio Rüdiger',     'Alemania', 'DEF', 'rare',      '🦍'),
    ('Manuel Neuer',        'Alemania', 'POR', 'rare',      '🧤'),
    ('Deniz Undav',         'Alemania', 'DEL', 'rare',      '🏹'),
    ('Jonathan Tah',        'Alemania', 'DEF', 'common',    '🏛️'),
    ('Nico Schlotterbeck',  'Alemania', 'DEF', 'common',    '⚽'),
    ('David Raum',          'Alemania', 'DEF', 'common',    '⚽'),
    ('Pascal Groß',         'Alemania', 'MED', 'common',    '⚽'),
    ('Serge Gnabry',        'Alemania', 'EXT', 'common',    '⚽'),
    ('Maximilian Mittelstädt','Alemania','DEF','common',    '⚽'),
    ('Chris Führich',       'Alemania', 'EXT', 'common',    '⚽'),
    ('Alexander Nübel',     'Alemania', 'POR', 'common',    '🥅'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — PORTUGAL (17)
    # ══════════════════════════════════════════════════════════
    ('Cristiano Ronaldo',   'Portugal', 'DEL', 'legendary', '🔴'),
    ('Bruno Fernandes',     'Portugal', 'MED', 'epic',      '🎭'),
    ('Rafael Leão',         'Portugal', 'EXT', 'epic',      '💨'),
    ('Gonçalo Ramos',       'Portugal', 'DEL', 'epic',      '🎯'),
    ('Bernardo Silva',      'Portugal', 'MED', 'rare',      '🎻'),
    ('Vitinha',             'Portugal', 'MED', 'rare',      '🌊'),
    ('Pedro Neto',          'Portugal', 'EXT', 'rare',      '🚀'),
    ('João Félix',          'Portugal', 'DEL', 'rare',      '🦋'),
    ('Rúben Dias',          'Portugal', 'DEF', 'rare',      '🗿'),
    ('João Cancelo',        'Portugal', 'DEF', 'rare',      '⚡'),
    ('Nuno Mendes',         'Portugal', 'DEF', 'rare',      '⚽'),
    ('Diogo Costa',         'Portugal', 'POR', 'rare',      '🧤'),
    ('Diogo Dalot',         'Portugal', 'DEF', 'common',    '⚽'),
    ('Rúben Neves',         'Portugal', 'MED', 'common',    '⚙️'),
    ('Francisco Conceição', 'Portugal', 'EXT', 'common',    '⚽'),
    ('António Silva',       'Portugal', 'DEF', 'common',    '🏗️'),
    ('Palhinha',            'Portugal', 'MED', 'common',    '🔒'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — PAÍSES BAJOS (16)
    # ══════════════════════════════════════════════════════════
    ('Xavi Simons',         'Países Bajos', 'MED', 'epic',   '🎶'),
    ('Virgil van Dijk',     'Países Bajos', 'DEF', 'epic',   '🗼'),
    ('Cody Gakpo',          'Países Bajos', 'EXT', 'rare',   '🔮'),
    ('Frenkie de Jong',     'Países Bajos', 'MED', 'rare',   '🌷'),
    ('Tijjani Reijnders',   'Países Bajos', 'MED', 'rare',   '🎯'),
    ('Jeremie Frimpong',    'Países Bajos', 'DEF', 'rare',   '⚡'),
    ('Denzel Dumfries',     'Países Bajos', 'DEF', 'rare',   '🚂'),
    ('Brian Brobbey',       'Países Bajos', 'DEL', 'rare',   '💪'),
    ('Bart Verbruggen',     'Países Bajos', 'POR', 'rare',   '🧤'),
    ('Nathan Aké',          'Países Bajos', 'DEF', 'common', '⚽'),
    ('Stefan de Vrij',      'Países Bajos', 'DEF', 'common', '🧱'),
    ('Wout Weghorst',       'Países Bajos', 'DEL', 'common', '🦣'),
    ('Donyell Malen',       'Países Bajos', 'EXT', 'common', '🏹'),
    ('Georginio Wijnaldum', 'Países Bajos', 'MED', 'common', '⚽'),
    ('Joey Veerman',        'Países Bajos', 'MED', 'common', '⚽'),
    ('Justin Bijlow',       'Países Bajos', 'POR', 'common', '🥅'),

    # ══════════════════════════════════════════════════════════
    # TIER 1 — ITALIA (16)
    # ══════════════════════════════════════════════════════════
    ('Nicolò Barella',      'Italia', 'MED', 'epic',   '⚡'),
    ('Davide Frattesi',     'Italia', 'MED', 'rare',   '🎯'),
    ('Sandro Tonali',       'Italia', 'MED', 'rare',   '🖤'),
    ('Giacomo Raspadori',   'Italia', 'DEL', 'rare',   '🌿'),
    ('Federico Dimarco',    'Italia', 'DEF', 'rare',   '🏹'),
    ('Alessandro Bastoni',  'Italia', 'DEF', 'rare',   '🧱'),
    ('Gianluca Scamacca',   'Italia', 'DEL', 'rare',   '💪'),
    ('Gianluigi Donnarumma','Italia', 'POR', 'rare',   '🧤'),
    ('Giovanni Di Lorenzo', 'Italia', 'DEF', 'rare',   '⚽'),
    ('Federico Chiesa',     'Italia', 'EXT', 'rare',   '⚽'),
    ('Lorenzo Pellegrini',  'Italia', 'MED', 'common', '⚽'),
    ('Mattia Zaccagni',     'Italia', 'EXT', 'common', '⚽'),
    ('Manuel Locatelli',    'Italia', 'MED', 'common', '⚙️'),
    ('Matteo Darmian',      'Italia', 'DEF', 'common', '⚽'),
    ('Matteo Retegui',      'Italia', 'DEL', 'common', '🇮🇹'),
    ('Bryan Cristante',     'Italia', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — NORUEGA (13)
    # ══════════════════════════════════════════════════════════
    ('Erling Haaland',      'Noruega', 'DEL', 'legendary', '💥'),
    ('Martin Ødegaard',     'Noruega', 'MED', 'epic',      '🌊'),
    ('Alexander Sørloth',   'Noruega', 'DEL', 'rare',      '🏔️'),
    ('Sander Berge',        'Noruega', 'MED', 'rare',      '🔒'),
    ('Kristian Thorstvedt', 'Noruega', 'MED', 'rare',      '⚽'),
    ('Antonio Nusa',        'Noruega', 'EXT', 'rare',      '⭐'),
    ('Mohamed Elyounoussi', 'Noruega', 'EXT', 'common',    '⚽'),
    ('Leo Østigård',        'Noruega', 'DEF', 'common',    '⚽'),
    ('Andreas Hanche-Olsen','Noruega', 'DEF', 'common',    '⚽'),
    ('Ørjan Nyland',        'Noruega', 'POR', 'common',    '🧤'),
    ('Patrick Berg',        'Noruega', 'MED', 'common',    '⚽'),
    ('Ola Solbakken',       'Noruega', 'EXT', 'common',    '⚽'),
    ('Hugo Vetlesen',       'Noruega', 'MED', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — URUGUAY (13)
    # ══════════════════════════════════════════════════════════
    ('Federico Valverde',   'Uruguay', 'MED', 'legendary', '💣'),
    ('Darwin Núñez',        'Uruguay', 'DEL', 'epic',      '🌪️'),
    ('Ronald Araújo',       'Uruguay', 'DEF', 'rare',      '🛡️'),
    ('Rodrigo Bentancur',   'Uruguay', 'MED', 'rare',      '🎯'),
    ('Luis Suárez',         'Uruguay', 'DEL', 'rare',      '🦷'),
    ('José María Giménez',  'Uruguay', 'DEF', 'rare',      '🪖'),
    ('Sergio Rochet',       'Uruguay', 'POR', 'rare',      '🧤'),
    ('Mathías Olivera',     'Uruguay', 'DEF', 'common',    '⚽'),
    ('Facundo Pellistri',   'Uruguay', 'EXT', 'common',    '⚡'),
    ('Maximiliano Araújo',  'Uruguay', 'EXT', 'common',    '⚽'),
    ('Matías Vecino',       'Uruguay', 'MED', 'common',    '⚽'),
    ('Agustín Canobbio',    'Uruguay', 'EXT', 'common',    '⚽'),
    ('Sebastián Cáceres',   'Uruguay', 'DEF', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — COLOMBIA (13)
    # ══════════════════════════════════════════════════════════
    ('Luis Díaz',           'Colombia', 'EXT', 'epic',   '🎸'),
    ('James Rodríguez',     'Colombia', 'MED', 'epic',   '☀️'),
    ('Richard Ríos',        'Colombia', 'MED', 'rare',   '🌿'),
    ('Juan Cuadrado',       'Colombia', 'EXT', 'rare',   '⚽'),
    ('Rafael Santos Borré', 'Colombia', 'DEL', 'rare',   '🏹'),
    ('Jhon Lucumí',         'Colombia', 'DEF', 'rare',   '⚽'),
    ('Jhon Arias',          'Colombia', 'EXT', 'rare',   '⚽'),
    ('Jhon Córdoba',        'Colombia', 'DEL', 'common', '⚽'),
    ('Yerson Mosquera',     'Colombia', 'DEF', 'common', '🛡️'),
    ('David Ospina',        'Colombia', 'POR', 'common', '🧤'),
    ('Jefferson Lerma',     'Colombia', 'MED', 'common', '⚽'),
    ('Sebastián Villa',     'Colombia', 'EXT', 'common', '⚽'),
    ('Óscar Estupiñán',     'Colombia', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — JAPÓN (13)
    # ══════════════════════════════════════════════════════════
    ('Takefusa Kubo',       'Japón', 'EXT', 'epic',   '🌸'),
    ('Kaoru Mitoma',        'Japón', 'EXT', 'rare',   '🌊'),
    ('Wataru Endo',         'Japón', 'MED', 'rare',   '🎌'),
    ('Daichi Kamada',       'Japón', 'MED', 'rare',   '🗾'),
    ('Ritsu Doan',          'Japón', 'MED', 'rare',   '🌙'),
    ('Ayase Ueda',          'Japón', 'DEL', 'rare',   '🎯'),
    ('Hidemasa Morita',     'Japón', 'MED', 'common', '⚽'),
    ('Hiroki Ito',          'Japón', 'DEF', 'common', '🛡️'),
    ('Ko Itakura',          'Japón', 'DEF', 'common', '⚽'),
    ('Shuichi Gonda',       'Japón', 'POR', 'common', '🧤'),
    ('Junya Ito',           'Japón', 'EXT', 'common', '⚽'),
    ('Mao Hosoya',          'Japón', 'DEL', 'common', '⚽'),
    ('Takehiro Tomiyasu',   'Japón', 'DEF', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — MARRUECOS (13)
    # ══════════════════════════════════════════════════════════
    ('Achraf Hakimi',       'Marruecos', 'DEF', 'epic',   '🌙'),
    ('Hakim Ziyech',        'Marruecos', 'EXT', 'rare',   '🔮'),
    ('Youssef En-Nesyri',   'Marruecos', 'DEL', 'rare',   '🦁'),
    ('Sofyan Amrabat',      'Marruecos', 'MED', 'rare',   '🔒'),
    ('Noussair Mazraoui',   'Marruecos', 'DEF', 'rare',   '🔐'),
    ('Abde Ezzalzouli',     'Marruecos', 'EXT', 'rare',   '🌿'),
    ('Bono',                'Marruecos', 'POR', 'rare',   '🧤'),
    ('Azzedine Ounahi',     'Marruecos', 'MED', 'common', '🌟'),
    ('Selim Amallah',       'Marruecos', 'MED', 'common', '⚽'),
    ('Romain Saïss',        'Marruecos', 'DEF', 'common', '⚽'),
    ('Yahia Attiyat Allah', 'Marruecos', 'DEF', 'common', '⚽'),
    ('Munir El-Kajoui',     'Marruecos', 'POR', 'common', '🥅'),
    ('Amine Harit',         'Marruecos', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — ESTADOS UNIDOS (13)
    # ══════════════════════════════════════════════════════════
    ('Christian Pulisic',   'Estados Unidos', 'EXT', 'epic',   '🦅'),
    ('Gio Reyna',           'Estados Unidos', 'MED', 'rare',   '🌟'),
    ('Weston McKennie',     'Estados Unidos', 'MED', 'rare',   '⭐'),
    ('Tyler Adams',         'Estados Unidos', 'MED', 'rare',   '🎯'),
    ('Yunus Musah',         'Estados Unidos', 'MED', 'rare',   '🌊'),
    ('Folarin Balogun',     'Estados Unidos', 'DEL', 'rare',   '🏹'),
    ('Tim Weah',            'Estados Unidos', 'EXT', 'common', '⚽'),
    ('Antonee Robinson',    'Estados Unidos', 'DEF', 'common', '⚡'),
    ('Sergiño Dest',        'Estados Unidos', 'DEF', 'common', '⚽'),
    ('Matt Turner',         'Estados Unidos', 'POR', 'common', '🧤'),
    ('Ricardo Pepi',        'Estados Unidos', 'DEL', 'common', '🏄'),
    ('Joe Scally',          'Estados Unidos', 'DEF', 'common', '⚽'),
    ('Brendan Aaronson',    'Estados Unidos', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — MÉXICO (13)
    # ══════════════════════════════════════════════════════════
    ('Santiago Giménez',    'México', 'DEL', 'epic',   '🌵'),
    ('Hirving Lozano',      'México', 'EXT', 'rare',   '🌶️'),
    ('Edson Álvarez',       'México', 'MED', 'rare',   '⚽'),
    ('Raúl Jiménez',        'México', 'DEL', 'rare',   '🐺'),
    ('Guillermo Ochoa',     'México', 'POR', 'rare',   '🧤'),
    ('Orbelín Pineda',      'México', 'MED', 'rare',   '⚽'),
    ('Alexis Vega',         'México', 'EXT', 'common', '⚽'),
    ('Roberto Alvarado',    'México', 'MED', 'common', '⚽'),
    ('Johan Vásquez',       'México', 'DEF', 'common', '🛡️'),
    ('Jesús Gallardo',      'México', 'DEF', 'common', '⚽'),
    ('Diego Lainez',        'México', 'EXT', 'common', '⚽'),
    ('César Montes',        'México', 'DEF', 'common', '⚽'),
    ('Andrés Guardado',     'México', 'MED', 'common', '🎖️'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — BÉLGICA (11)
    # ══════════════════════════════════════════════════════════
    ('Kevin De Bruyne',     'Bélgica', 'MED', 'legendary', '🎼'),
    ('Lois Openda',         'Bélgica', 'DEL', 'epic',      '💫'),
    ('Romelu Lukaku',       'Bélgica', 'DEL', 'rare',      '🏋️'),
    ('Amadou Onana',        'Bélgica', 'MED', 'rare',      '🏔️'),
    ('Charles De Ketelaere','Bélgica', 'MED', 'rare',      '🌹'),
    ('Yannick Carrasco',    'Bélgica', 'EXT', 'rare',      '🐦'),
    ('Thibaut Courtois',    'Bélgica', 'POR', 'rare',      '🧤'),
    ('Timothy Castagne',    'Bélgica', 'DEF', 'common',    '⚽'),
    ('Jan Vertonghen',      'Bélgica', 'DEF', 'common',    '🏛️'),
    ('Leandro Trossard',    'Bélgica', 'EXT', 'common',    '⚽'),
    ('Axel Witsel',         'Bélgica', 'MED', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 2 — GEORGIA (11)
    # ══════════════════════════════════════════════════════════
    ('Khvicha Kvaratskhelia','Georgia', 'EXT', 'legendary', '🌀'),
    ('Georges Mikautadze',  'Georgia', 'DEL', 'epic',      '🥊'),
    ('Giorgi Mamardashvili','Georgia', 'POR', 'rare',      '🧤'),
    ('Otar Kiteishvili',    'Georgia', 'MED', 'rare',      '⚽'),
    ('Giorgi Chakvetadze',  'Georgia', 'MED', 'rare',      '🎯'),
    ('Luka Lochoshvili',    'Georgia', 'DEF', 'common',    '⚽'),
    ('Giorgi Tsitaishvili', 'Georgia', 'EXT', 'common',    '⚽'),
    ('Davit Khocholava',    'Georgia', 'DEF', 'common',    '⚽'),
    ('Saba Lobzhanidze',    'Georgia', 'MED', 'common',    '⚽'),
    ('Nika Kwekweskiri',    'Georgia', 'DEF', 'common',    '⚽'),
    ('Budu Zivzivadze',     'Georgia', 'DEL', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — SUIZA (10)
    # ══════════════════════════════════════════════════════════
    ('Granit Xhaka',        'Suiza', 'MED', 'epic',   '🏔️'),
    ('Manuel Akanji',       'Suiza', 'DEF', 'rare',   '🪖'),
    ('Breel Embolo',        'Suiza', 'DEL', 'rare',   '🦁'),
    ('Fabian Rieder',       'Suiza', 'MED', 'rare',   '🎯'),
    ('Yann Sommer',         'Suiza', 'POR', 'rare',   '🧤'),
    ('Remo Freuler',        'Suiza', 'MED', 'common', '⚽'),
    ('Zeki Amdouni',        'Suiza', 'DEL', 'common', '🌟'),
    ('Silvan Widmer',       'Suiza', 'DEF', 'common', '⚽'),
    ('Kwadwo Duah',         'Suiza', 'EXT', 'common', '⚽'),
    ('Xherdan Shaqiri',     'Suiza', 'EXT', 'common', '⭐'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — CROACIA (10)
    # ══════════════════════════════════════════════════════════
    ('Luka Modrić',         'Croacia', 'MED', 'legendary', '🎩'),
    ('Joško Gvardiol',      'Croacia', 'DEF', 'epic',      '🛡️'),
    ('Mateo Kovačić',       'Croacia', 'MED', 'rare',      '🎼'),
    ('Marcelo Brozović',    'Croacia', 'MED', 'rare',      '⚙️'),
    ('Ivan Perišić',        'Croacia', 'EXT', 'rare',      '⚽'),
    ('Lovro Majer',         'Croacia', 'MED', 'common',    '🌿'),
    ('Dominik Livaković',   'Croacia', 'POR', 'common',    '🧤'),
    ('Josip Stanišić',      'Croacia', 'DEF', 'common',    '⚽'),
    ('Bruno Petković',      'Croacia', 'DEL', 'common',    '⚽'),
    ('Andrej Kramarić',     'Croacia', 'DEL', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — COREA DEL SUR (10)
    # ══════════════════════════════════════════════════════════
    ('Heung-min Son',       'Corea del Sur', 'EXT', 'legendary', '🌙'),
    ('Lee Kang-in',         'Corea del Sur', 'MED', 'epic',      '⭐'),
    ('Hwang Hee-chan',      'Corea del Sur', 'EXT', 'rare',      '🔥'),
    ('Kim Min-jae',         'Corea del Sur', 'DEF', 'rare',      '🗻'),
    ('Cho Gue-sung',        'Corea del Sur', 'DEL', 'rare',      '🏹'),
    ('Hwang In-beom',       'Corea del Sur', 'MED', 'common',    '⚽'),
    ('Kim Seung-gyu',       'Corea del Sur', 'POR', 'common',    '🧤'),
    ('Kim Jin-su',          'Corea del Sur', 'DEF', 'common',    '⚽'),
    ('Jung Woo-young',      'Corea del Sur', 'MED', 'common',    '⚽'),
    ('Oh Hyeon-gyu',        'Corea del Sur', 'DEL', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — TURQUÍA (10)
    # ══════════════════════════════════════════════════════════
    ('Hakan Çalhanoğlu',    'Turquía', 'MED', 'epic',   '🌟'),
    ('Arda Güler',          'Turquía', 'MED', 'epic',   '🌙'),
    ('Kenan Yıldız',        'Turquía', 'EXT', 'rare',   '⭐'),
    ('Ferdi Kadıoğlu',      'Turquía', 'DEF', 'rare',   '⚡'),
    ('Orkun Kökçü',         'Turquía', 'MED', 'rare',   '⚽'),
    ('Mert Günok',          'Turquía', 'POR', 'common', '🧤'),
    ('Samet Akaydın',       'Turquía', 'DEF', 'common', '🛡️'),
    ('Ozan Kabak',          'Turquía', 'DEF', 'common', '⚽'),
    ('Barış Alper Yılmaz',  'Turquía', 'EXT', 'common', '⚽'),
    ('Cenk Tosun',          'Turquía', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — SERBIA (10)
    # ══════════════════════════════════════════════════════════
    ('Dušan Vlahović',      'Serbia', 'DEL', 'epic',   '🔱'),
    ('Aleksandar Mitrović', 'Serbia', 'DEL', 'rare',   '🐻'),
    ('Sergej Milinković-Savić','Serbia','MED','rare',  '🎯'),
    ('Luka Jović',          'Serbia', 'DEL', 'rare',   '⚽'),
    ('Nikola Milenković',   'Serbia', 'DEF', 'common', '🛡️'),
    ('Predrag Rajković',    'Serbia', 'POR', 'common', '🧤'),
    ('Strahinja Pavlović',  'Serbia', 'DEF', 'common', '⚽'),
    ('Saša Lukić',          'Serbia', 'MED', 'common', '⚽'),
    ('Andrija Živković',    'Serbia', 'EXT', 'common', '⚽'),
    ('Filip Kostić',        'Serbia', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — SENEGAL (10)
    # ══════════════════════════════════════════════════════════
    ('Sadio Mané',          'Senegal', 'EXT', 'legendary', '🦁'),
    ('Nicolas Jackson',     'Senegal', 'DEL', 'epic',      '🏹'),
    ('Pape Matar Sarr',     'Senegal', 'MED', 'rare',      '🌿'),
    ('Ismaïla Sarr',        'Senegal', 'EXT', 'rare',      '🌊'),
    ('Kalidou Koulibaly',   'Senegal', 'DEF', 'rare',      '🗿'),
    ('Édouard Mendy',       'Senegal', 'POR', 'rare',      '🧤'),
    ('Idrissa Gueye',       'Senegal', 'MED', 'rare',      '⚡'),
    ('Boulaye Dia',         'Senegal', 'DEL', 'common',    '⚽'),
    ('Krepin Diatta',       'Senegal', 'EXT', 'common',    '⚽'),
    ('Formose Mendy',       'Senegal', 'DEF', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — NIGERIA (9)
    # ══════════════════════════════════════════════════════════
    ('Victor Osimhen',      'Nigeria', 'DEL', 'epic',   '⚡'),
    ('Samuel Chukwueze',    'Nigeria', 'EXT', 'rare',   '🌩️'),
    ('Wilfried Ndidi',      'Nigeria', 'MED', 'rare',   '🔒'),
    ('Alex Iwobi',          'Nigeria', 'MED', 'rare',   '🎭'),
    ('Terem Moffi',         'Nigeria', 'DEL', 'common', '🏹'),
    ('William Troost-Ekong','Nigeria', 'DEF', 'common', '🛡️'),
    ('Cyriel Dessers',      'Nigeria', 'DEL', 'common', '⚽'),
    ('Stanley Nwabali',     'Nigeria', 'POR', 'common', '🧤'),
    ('Ola Aina',            'Nigeria', 'DEF', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — ECUADOR (9)
    # ══════════════════════════════════════════════════════════
    ('Moisés Caicedo',      'Ecuador', 'MED', 'epic',   '🌎'),
    ('Enner Valencia',      'Ecuador', 'DEL', 'rare',   '⚡'),
    ('Piero Hincapié',      'Ecuador', 'DEF', 'rare',   '🛡️'),
    ('Jeremy Sarmiento',    'Ecuador', 'EXT', 'rare',   '🌊'),
    ('Gonzalo Plata',       'Ecuador', 'EXT', 'common', '⚽'),
    ('Jhegson Méndez',      'Ecuador', 'MED', 'common', '⚽'),
    ('Angelo Preciado',     'Ecuador', 'DEF', 'common', '⚽'),
    ('Alexander Domínguez', 'Ecuador', 'POR', 'common', '🧤'),
    ('Kevin Rodríguez',     'Ecuador', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — CANADÁ (9)
    # ══════════════════════════════════════════════════════════
    ('Alphonso Davies',     'Canadá', 'DEF', 'epic',   '🍁'),
    ('Jonathan David',      'Canadá', 'DEL', 'epic',   '🎯'),
    ('Stephen Eustáquio',   'Canadá', 'MED', 'rare',   '⚡'),
    ('Cyle Larin',          'Canadá', 'DEL', 'rare',   '🏒'),
    ('Ismaël Koné',         'Canadá', 'MED', 'rare',   '🌿'),
    ('Tajon Buchanan',      'Canadá', 'EXT', 'rare',   '🍂'),
    ('Maxime Crépeau',      'Canadá', 'POR', 'common', '🧤'),
    ('Liam Millar',         'Canadá', 'EXT', 'common', '⚽'),
    ('Samuel Piette',       'Canadá', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — DINAMARCA (9)
    # ══════════════════════════════════════════════════════════
    ('Christian Eriksen',   'Dinamarca', 'MED', 'epic',   '💙'),
    ('Rasmus Højlund',      'Dinamarca', 'DEL', 'epic',   '🌟'),
    ('Pierre-Emile Højbjerg','Dinamarca','MED', 'rare',   '⚙️'),
    ('Andreas Christensen', 'Dinamarca', 'DEF', 'rare',   '🛡️'),
    ('Kasper Schmeichel',   'Dinamarca', 'POR', 'rare',   '🧤'),
    ('Joakim Mæhle',        'Dinamarca', 'DEF', 'common', '⚽'),
    ('Simon Kjær',          'Dinamarca', 'DEF', 'common', '⚽'),
    ('Jonas Wind',          'Dinamarca', 'DEL', 'common', '⚽'),
    ('Viktor Claesson',     'Dinamarca', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 3 — AUSTRIA (9)
    # ══════════════════════════════════════════════════════════
    ('David Alaba',         'Austria', 'DEF', 'epic',   '🏔️'),
    ('Marcel Sabitzer',     'Austria', 'MED', 'rare',   '🎯'),
    ('Christoph Baumgartner','Austria', 'MED', 'rare',  '🌿'),
    ('Marko Arnautović',    'Austria', 'DEL', 'rare',   '🐉'),
    ('Florian Grillitsch',  'Austria', 'MED', 'common', '⚽'),
    ('Maximilian Wöber',    'Austria', 'DEF', 'common', '🛡️'),
    ('Stefan Posch',        'Austria', 'DEF', 'common', '⚽'),
    ('Patrick Pentz',       'Austria', 'POR', 'common', '🧤'),
    ('Michael Gregoritsch', 'Austria', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — GHANA (7)
    # ══════════════════════════════════════════════════════════
    ('Mohammed Kudus',      'Ghana', 'MED', 'epic',   '⚡'),
    ('Iñaki Williams',      'Ghana', 'EXT', 'rare',   '🏃'),
    ('Thomas Partey',       'Ghana', 'MED', 'rare',   '🔒'),
    ('Jordan Ayew',         'Ghana', 'EXT', 'common', '⚽'),
    ('Tariq Lamptey',       'Ghana', 'DEF', 'common', '⚽'),
    ('Lawrence Ati-Zigi',   'Ghana', 'POR', 'common', '🧤'),
    ('Antoine Semenyo',     'Ghana', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — CAMERÚN (7)
    # ══════════════════════════════════════════════════════════
    ('André Onana',         'Camerún', 'POR', 'epic',   '🧤'),
    ('Bryan Mbeumo',        'Camerún', 'EXT', 'epic',   '🌟'),
    ('Vincent Aboubakar',   'Camerún', 'DEL', 'rare',   '🦁'),
    ('Zambo Anguissa',      'Camerún', 'MED', 'rare',   '💪'),
    ('Karl Toko Ekambi',    'Camerún', 'EXT', 'common', '⚽'),
    ('Collins Fai',         'Camerún', 'DEF', 'common', '⚽'),
    ('Jeando Fuchs',        'Camerún', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — COSTA DE MARFIL (7)
    # ══════════════════════════════════════════════════════════
    ('Sébastien Haller',    'Costa de Marfil', 'DEL', 'epic',   '🐘'),
    ('Franck Kessié',       'Costa de Marfil', 'MED', 'rare',   '🔒'),
    ('Ibrahim Sangaré',     'Costa de Marfil', 'MED', 'rare',   '🛡️'),
    ('Simon Deli',          'Costa de Marfil', 'DEF', 'common', '⚽'),
    ('Wilfried Zaha',       'Costa de Marfil', 'EXT', 'common', '⚽'),
    ('Jean-Philippe Krasso','Costa de Marfil', 'DEL', 'common', '⚽'),
    ('Badra Sangaré',       'Costa de Marfil', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — IRÁN (7)
    # ══════════════════════════════════════════════════════════
    ('Mehdi Taremi',        'Irán', 'DEL', 'epic',   '🦅'),
    ('Sardar Azmoun',       'Irán', 'DEL', 'rare',   '🐯'),
    ('Alireza Jahanbakhsh', 'Irán', 'EXT', 'rare',   '🌙'),
    ('Ali Gholizadeh',      'Irán', 'EXT', 'common', '⚽'),
    ('Morteza Pouraliganji','Irán', 'DEF', 'common', '⚽'),
    ('Hossein Hosseini',    'Irán', 'POR', 'common', '🧤'),
    ('Ahmad Nourollahi',    'Irán', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — ARABIA SAUDÍ (7)
    # ══════════════════════════════════════════════════════════
    ('Sálim Al-Dawsari',    'Arabia Saudí', 'EXT', 'rare',   '🌙'),
    ('Saleh Al-Shehri',     'Arabia Saudí', 'DEL', 'rare',   '🏹'),
    ('Firas Al-Buraikan',   'Arabia Saudí', 'DEL', 'common', '⚽'),
    ('Mohammed Al-Burayk',  'Arabia Saudí', 'DEF', 'common', '⚽'),
    ('Abdullah Otayf',      'Arabia Saudí', 'MED', 'common', '⚽'),
    ('Mohammed Al-Owais',   'Arabia Saudí', 'POR', 'common', '🧤'),
    ('Ali Al-Bulayhi',      'Arabia Saudí', 'DEF', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — QATAR (6)
    # ══════════════════════════════════════════════════════════
    ('Akram Afif',          'Qatar', 'EXT', 'rare',   '🌴'),
    ('Almoez Ali',          'Qatar', 'DEL', 'rare',   '🦁'),
    ('Hassan Al-Haydos',    'Qatar', 'MED', 'common', '⚽'),
    ('Bassam Al-Rawi',      'Qatar', 'DEF', 'common', '⚽'),
    ('Abdelkarim Hassan',   'Qatar', 'DEF', 'common', '⚽'),
    ('Meshaal Barsham',     'Qatar', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — COSTA RICA (6)
    # ══════════════════════════════════════════════════════════
    ('Keylor Navas',        'Costa Rica', 'POR', 'rare',   '🐆'),
    ('Joel Campbell',       'Costa Rica', 'EXT', 'rare',   '🌴'),
    ('Bryan Ruiz',          'Costa Rica', 'MED', 'common', '⚽'),
    ('Celso Borges',        'Costa Rica', 'MED', 'common', '⚽'),
    ('Óscar Duarte',        'Costa Rica', 'DEF', 'common', '⚽'),
    ('Patrick Sequeira',    'Costa Rica', 'POR', 'common', '🥅'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — PANAMÁ (6)
    # ══════════════════════════════════════════════════════════
    ('Ismael Díaz',         'Panamá', 'DEL', 'rare',   '🎯'),
    ('Rolando Blackburn',   'Panamá', 'EXT', 'common', '⚽'),
    ('Aníbal Godoy',        'Panamá', 'MED', 'common', '⚽'),
    ('Fidel Escobar',       'Panamá', 'DEF', 'common', '⚽'),
    ('Luis Mejía',          'Panamá', 'POR', 'common', '🧤'),
    ('José Fajardo',        'Panamá', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — JAMAICA (6)
    # ══════════════════════════════════════════════════════════
    ('Leon Bailey',         'Jamaica', 'EXT', 'rare',   '🏝️'),
    ('Demarai Gray',        'Jamaica', 'EXT', 'rare',   '⚡'),
    ('Shamar Nicholson',    'Jamaica', 'DEL', 'common', '⚽'),
    ('Bobby Decordova-Reid','Jamaica', 'MED', 'common', '⚽'),
    ('Daniel Johnson',      'Jamaica', 'MED', 'common', '⚽'),
    ('Andre Blake',         'Jamaica', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — POLONIA (7)
    # ══════════════════════════════════════════════════════════
    ('Robert Lewandowski',  'Polonia', 'DEL', 'legendary', '🏰'),
    ('Piotr Zieliński',     'Polonia', 'MED', 'epic',      '🎯'),
    ('Artur Sobiech',       'Polonia', 'DEL', 'common',    '⚽'),
    ('Wojciech Szczęsny',   'Polonia', 'POR', 'rare',      '🧤'),
    ('Jan Bednarek',        'Polonia', 'DEF', 'common',    '🛡️'),
    ('Jakub Kiwior',        'Polonia', 'DEF', 'common',    '⚽'),
    ('Karol Świderski',     'Polonia', 'DEL', 'common',    '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — UCRANIA (7)
    # ══════════════════════════════════════════════════════════
    ('Mykhailo Mudryk',     'Ucrania', 'EXT', 'epic',   '⚡'),
    ('Artem Dovbyk',        'Ucrania', 'DEL', 'epic',   '🎯'),
    ('Oleksandr Zinchenko', 'Ucrania', 'DEF', 'rare',   '💙'),
    ('Andriy Lunin',        'Ucrania', 'POR', 'rare',   '🧤'),
    ('Ruslan Malinovskyi',  'Ucrania', 'MED', 'common', '⚽'),
    ('Roman Yaremchuk',     'Ucrania', 'DEL', 'common', '⚽'),
    ('Viktor Tsygankov',    'Ucrania', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — HUNGRÍA (6)
    # ══════════════════════════════════════════════════════════
    ('Dominik Szoboszlai',  'Hungría', 'MED', 'epic',   '🔴'),
    ('Roland Sallai',       'Hungría', 'EXT', 'rare',   '⚽'),
    ('Péter Gulácsi',       'Hungría', 'POR', 'rare',   '🧤'),
    ('Willi Orbán',         'Hungría', 'DEF', 'common', '🛡️'),
    ('Ádám Lang',           'Hungría', 'DEF', 'common', '⚽'),
    ('Martin Ádám',         'Hungría', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 4 — ESLOVAQUIA (5)
    # ══════════════════════════════════════════════════════════
    ('Milan Škriniar',      'Eslovaquia', 'DEF', 'rare',   '🛡️'),
    ('Ondrej Duda',         'Eslovaquia', 'MED', 'common', '⚽'),
    ('Martin Dúbravka',     'Eslovaquia', 'POR', 'common', '🧤'),
    ('Lukáš Haraslín',      'Eslovaquia', 'EXT', 'common', '⚽'),
    ('Ivan Schranz',        'Eslovaquia', 'EXT', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — ESLOVENIA (5)
    # ══════════════════════════════════════════════════════════
    ('Jan Oblak',           'Eslovenia', 'POR', 'epic',   '🧱'),
    ('Benjamin Šeško',      'Eslovenia', 'DEL', 'epic',   '🦌'),
    ('Jaka Bijol',          'Eslovenia', 'DEF', 'common', '⚽'),
    ('Jon Gorenc-Stanković','Eslovenia', 'MED', 'common', '⚽'),
    ('Petar Stojanović',    'Eslovenia', 'DEF', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — ALBANIA (5)
    # ══════════════════════════════════════════════════════════
    ('Armando Broja',       'Albania', 'DEL', 'rare',   '🦅'),
    ('Kristjan Asllani',    'Albania', 'MED', 'rare',   '⚽'),
    ('Berat Djimsiti',      'Albania', 'DEF', 'common', '⚽'),
    ('Etrit Berisha',       'Albania', 'POR', 'common', '🧤'),
    ('Klaus Gjasula',       'Albania', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — ESCOCIA (5)
    # ══════════════════════════════════════════════════════════
    ('Andrew Robertson',    'Escocia', 'DEF', 'rare',   '🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
    ('Scott McTominay',     'Escocia', 'MED', 'rare',   '🎯'),
    ('John McGinn',         'Escocia', 'MED', 'rare',   '⚽'),
    ('Che Adams',           'Escocia', 'DEL', 'common', '⚽'),
    ('Angus Gunn',          'Escocia', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — RUMANÍA (5)
    # ══════════════════════════════════════════════════════════
    ('Ianis Hagi',          'Rumanía', 'MED', 'rare',   '🌟'),
    ('Radu Drăgușin',       'Rumanía', 'DEF', 'rare',   '🛡️'),
    ('Nicolae Stanciu',     'Rumanía', 'MED', 'common', '⚽'),
    ('Florin Niță',         'Rumanía', 'POR', 'common', '🧤'),
    ('Denis Drăguș',        'Rumanía', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — SUECIA (5)
    # ══════════════════════════════════════════════════════════
    ('Viktor Gyökeres',     'Suecia', 'DEL', 'epic',   '🇸🇪'),
    ('Alexander Isak',      'Suecia', 'DEL', 'epic',   '🎯'),
    ('Dejan Kulusevski',    'Suecia', 'MED', 'rare',   '⚡'),
    ('Victor Nilsson Lindelöf','Suecia','DEF','common', '⚽'),
    ('Emil Forsberg',       'Suecia', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — VENEZUELA (5)
    # ══════════════════════════════════════════════════════════
    ('Yangel Herrera',      'Venezuela', 'MED', 'rare',   '🌺'),
    ('Darwin Machís',       'Venezuela', 'EXT', 'rare',   '🌪️'),
    ('Salomón Rondón',      'Venezuela', 'DEL', 'common', '⚽'),
    ('Josef Martínez',      'Venezuela', 'DEL', 'common', '⚽'),
    ('Wuilker Faríñez',     'Venezuela', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — PARAGUAY (5)
    # ══════════════════════════════════════════════════════════
    ('Miguel Almirón',      'Paraguay', 'MED', 'rare',   '🦅'),
    ('Julio Enciso',        'Paraguay', 'EXT', 'rare',   '⭐'),
    ('Gustavo Gómez',       'Paraguay', 'DEF', 'common', '⚽'),
    ('Robert Rojas',        'Paraguay', 'DEF', 'common', '⚽'),
    ('Antonio Sanabria',    'Paraguay', 'DEL', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — CHILE (5)
    # ══════════════════════════════════════════════════════════
    ('Alexis Sánchez',      'Chile', 'EXT', 'rare',   '🦊'),
    ('Ben Brereton Díaz',   'Chile', 'DEL', 'rare',   '🌮'),
    ('Darío Osorio',        'Chile', 'MED', 'rare',   '🌟'),
    ('Víctor Dávila',       'Chile', 'EXT', 'common', '⚽'),
    ('Marcelino Núñez',     'Chile', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — PERÚ (5)
    # ══════════════════════════════════════════════════════════
    ('André Carrillo',      'Perú', 'EXT', 'rare',   '🦁'),
    ('Gianluca Lapadula',   'Perú', 'DEL', 'rare',   '🇮🇹'),
    ('Renato Tapia',        'Perú', 'MED', 'common', '⚽'),
    ('Pedro Gallese',       'Perú', 'POR', 'common', '🧤'),
    ('Christian Cueva',     'Perú', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — ARGELIA (5)
    # ══════════════════════════════════════════════════════════
    ('Riyad Mahrez',        'Argelia', 'EXT', 'epic',   '🌟'),
    ('Youcef Atal',         'Argelia', 'DEF', 'rare',   '⚡'),
    ('Hichem Boudaoui',     'Argelia', 'MED', 'rare',   '⚽'),
    ('Aissa Mandi',         'Argelia', 'DEF', 'common', '⚽'),
    ('Raïs M\'Bolhi',       'Argelia', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — EGIPTO (5)
    # ══════════════════════════════════════════════════════════
    ('Mohamed Salah',       'Egipto', 'EXT', 'legendary', '🌟'),
    ('Omar Marmoush',       'Egipto', 'EXT', 'epic',      '🔥'),
    ('Mostafa Mohamed',     'Egipto', 'DEL', 'rare',      '🦅'),
    ('Mohamed Elneny',      'Egipto', 'MED', 'common',    '⚽'),
    ('Ahmed El-Shenawy',    'Egipto', 'POR', 'common',    '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — TÚNEZ (5)
    # ══════════════════════════════════════════════════════════
    ('Hannibal Mejbri',     'Túnez', 'MED', 'rare',   '⭐'),
    ('Ellyes Skhiri',       'Túnez', 'MED', 'rare',   '⚽'),
    ('Issam Jebali',        'Túnez', 'DEL', 'common', '⚽'),
    ('Montassar Talbi',     'Túnez', 'DEF', 'common', '⚽'),
    ('Aymen Dahmen',        'Túnez', 'POR', 'common', '🧤'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — MALI (4)
    # ══════════════════════════════════════════════════════════
    ('Yves Bissouma',       'Mali', 'MED', 'rare',   '🥁'),
    ('Amadou Haidara',      'Mali', 'MED', 'rare',   '🌍'),
    ('El Bilal Touré',      'Mali', 'DEL', 'rare',   '🏹'),
    ('Hamari Traoré',       'Mali', 'DEF', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — INDONESIA (4)
    # ══════════════════════════════════════════════════════════
    ('Marselino Ferdinan',  'Indonesia', 'MED', 'rare',   '🌴'),
    ('Jay Idzes',           'Indonesia', 'DEF', 'common', '⚽'),
    ('Rafael Struick',      'Indonesia', 'DEL', 'common', '⚽'),
    ('Ivar Jenner',         'Indonesia', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — NUEVA ZELANDA (4)
    # ══════════════════════════════════════════════════════════
    ('Chris Wood',          'Nueva Zelanda', 'DEL', 'rare',   '🥝'),
    ('Liberato Cacace',     'Nueva Zelanda', 'DEF', 'common', '⚽'),
    ('Clayton Lewis',       'Nueva Zelanda', 'MED', 'common', '⚽'),
    ('Joe Bell',            'Nueva Zelanda', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — UZBEKISTÁN (4)
    # ══════════════════════════════════════════════════════════
    ('Eldor Shomurodov',    'Uzbekistán', 'DEL', 'rare',   '🏹'),
    ('Abbosbek Fayzullaev', 'Uzbekistán', 'EXT', 'rare',   '⭐'),
    ('Jaloliddin Masharipov','Uzbekistán','EXT', 'common', '⚽'),
    ('Dostonbek Khamdamov', 'Uzbekistán', 'MED', 'common', '⚽'),

    # ══════════════════════════════════════════════════════════
    # TIER 5 — IRAK (4)
    # ══════════════════════════════════════════════════════════
    ('Aymen Hussein',       'Irak', 'DEL', 'rare',   '🌙'),
    ('Amjad Attwan',        'Irak', 'MED', 'common', '⚽'),
    ('Jalal Hassan',        'Irak', 'POR', 'common', '🧤'),
    ('Ali Adnan',           'Irak', 'DEF', 'common', '⚽'),
]


# ══════════════════════════════════════════════════════════════
# CARTAS ESPECIALES
# ══════════════════════════════════════════════════════════════
SPECIAL_CARDS = [
    ('Golazo del Torneo',    None, 'ESPECIAL', 'epic',      '🚀'),
    ('Parada Imposible',     None, 'ESPECIAL', 'epic',      '🧤'),
    ('VAR Crisis',           None, 'ESPECIAL', 'rare',      '📺'),
    ('Larguero Maldito',     None, 'ESPECIAL', 'rare',      '😱'),
    ('Hat-Trick Histórico',  None, 'ESPECIAL', 'legendary', '🎩'),
    ('Penalti Fallado',      None, 'ESPECIAL', 'common',    '🤦'),
    ('Lesión Táctica',       None, 'ESPECIAL', 'common',    '🩹'),
    ('Expulsión Épica',      None, 'ESPECIAL', 'rare',      '🟥'),
    ('Aficionado del Año',   None, 'ESPECIAL', 'epic',      '📣'),
    ('El Milagro',           None, 'ESPECIAL', 'legendary', '✨'),
    ('Árbitro Loco',         None, 'ESPECIAL', 'common',    '🦺'),
    ('Prórroga Infinita',    None, 'ESPECIAL', 'rare',      '⏱️'),
    ('Capitán de Capitanes', None, 'ESPECIAL', 'epic',      '🏅'),
    ('Debut Histórico',      None, 'ESPECIAL', 'rare',      '🌱'),
    ('Campeón Inesperado',   None, 'ESPECIAL', 'legendary', '🏆'),
]


def seed_players(db, Player, Team, force=False):
    """Siembra jugadores por primera vez. Con force=True re-siembra aunque ya existan."""
    if not force and Player.query.count() > 0:
        return
    teams = {t.name: t.id for t in Team.query.all()}
    for name, team_name, pos, rarity, icon in PLAYERS:
        p = Player(
            name=name,
            team_id=teams.get(team_name) if team_name else None,
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


def reseed_players(db, Player, UserCard, Team):
    """Elimina todos los cromos y UserCards y vuelve a sembrar desde cero."""
    UserCard.query.delete()
    Player.query.delete()
    db.session.commit()
    seed_players(db, Player, Team, force=True)
