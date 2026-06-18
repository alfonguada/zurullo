from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Monedas que otorga cada porra según los puntos conseguidos.
# 25 por acertar el resultado (1/X/2), 50 por el marcador exacto. En partidos
# dobles los puntos se duplican (2 y 6), por lo que las monedas también: 50 y 100.
COINS_BY_POINTS = {1: 25, 2: 50, 3: 50, 6: 100}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_emoji = db.Column(db.String(10), default='👾')
    avatar_bg = db.Column(db.String(20), default='#ff0066')
    is_admin = db.Column(db.Boolean, default=False)
    onboarding_done = db.Column(db.Boolean, default=False)
    tutorial_seen   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    coins_spent    = db.Column(db.Integer, default=0)
    bet_winnings   = db.Column(db.Integer, default=0)  # monedas ganadas en apuestas
    gift_coins     = db.Column(db.Integer, default=0)  # monedas regaladas por el admin
    gift_alert     = db.Column(db.Integer, default=0)  # regalo pendiente de avisar (una vez)
    pending_notice = db.Column(db.Text, default=None)  # aviso admin pendiente de leer

    predictions  = db.relationship('Prediction', back_populates='user', lazy='dynamic')
    bonus        = db.relationship('BonusPrediction', back_populates='user', uselist=False)
    extra_bonus  = db.relationship('ExtraBonusPrediction', back_populates='user', uselist=False)
    worst_team   = db.relationship('WorstTeamAssignment', back_populates='user', uselist=False)
    cards        = db.relationship('UserCard', back_populates='user', lazy='dynamic')
    packs        = db.relationship('UserPack', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def name(self):
        return self.display_name or self.username

    @property
    def match_points(self):
        result = db.session.query(db.func.sum(Prediction.points_earned)).filter(
            Prediction.user_id == self.id,
            Prediction.points_earned.isnot(None)
        ).scalar()
        return result or 0

    @property
    def bonus_points(self):
        pts = 0
        if self.bonus:
            pts += (self.bonus.champion_points or 0) + (self.bonus.runner_up_points or 0) + (self.bonus.scorer_points or 0)
        if self.extra_bonus:
            pts += self.extra_bonus.total_pts
        return pts

    @property
    def worst_points(self):
        return self.worst_team.points_earned if self.worst_team else 0

    @property
    def worst_coins(self):
        """50 monedas por cada gol a favor de tu peor selección, 25 por cada en contra."""
        if not self.worst_team:
            return 0
        gf = self.worst_team.goals_for or 0
        ga = self.worst_team.goals_against or 0
        return gf * 50 + ga * 25

    @property
    def total_points(self):
        return self.match_points + self.bonus_points + self.worst_points

    @property
    def coins_earned(self):
        """Monedas ganadas en porras: 25 por resultado, 50 por exacto (x2 en dobles)."""
        rows = db.session.query(Prediction.points_earned).filter(
            Prediction.user_id == self.id,
            Prediction.points_earned.isnot(None)
        ).all()
        return sum(COINS_BY_POINTS.get(pts, 0) for (pts,) in rows)

    @property
    def coins(self):
        return max(0, self.coins_earned + self.worst_coins + (self.bet_winnings or 0)
                   + (self.gift_coins or 0) - (self.coins_spent or 0))

    @property
    def exact_scores(self):
        return Prediction.query.filter(
            Prediction.user_id == self.id,
            Prediction.points_earned.in_([3, 6])
        ).count()


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    flag_emoji = db.Column(db.String(10), default='🏳️')
    flag_img = db.Column(db.String(50), default='')
    group_letter = db.Column(db.String(1))
    is_worst = db.Column(db.Boolean, default=False)
    is_spain_group = db.Column(db.Boolean, default=False)


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(30), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    stadium = db.Column(db.String(100), default='')
    city = db.Column(db.String(100), default='')
    goals1 = db.Column(db.Integer)
    goals2 = db.Column(db.Integer)
    is_locked = db.Column(db.Boolean, default=False)
    double_points = db.Column(db.Boolean, default=False)
    is_daily_bonus = db.Column(db.Boolean, default=False)
    match_number = db.Column(db.Integer, default=0)
    total_corners = db.Column(db.Integer)  # córners totales (entrada manual del admin)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])
    predictions = db.relationship('Prediction', back_populates='match', lazy='dynamic')

    @property
    def any_double(self):
        return self.double_points or self.is_daily_bonus

    @property
    def result_entered(self):
        return self.goals1 is not None and self.goals2 is not None

    @property
    def display_phase(self):
        phases = {
            'group': 'Fase de Grupos', 'r16': 'Octavos de Final',
            'qf': 'Cuartos de Final', 'sf': 'Semifinales', 'final': 'FINAL',
        }
        return phases.get(self.phase, self.phase)


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    goals1 = db.Column(db.Integer)
    goals2 = db.Column(db.Integer)
    points_earned = db.Column(db.Integer)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user  = db.relationship('User', back_populates='predictions')
    match = db.relationship('Match', back_populates='predictions')

    __table_args__ = (db.UniqueConstraint('user_id', 'match_id'),)


class BonusPrediction(db.Model):
    __tablename__ = 'bonus_predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    champion_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    runner_up_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    top_scorer_name = db.Column(db.String(100), default='')
    champion_points = db.Column(db.Integer, default=0)
    runner_up_points = db.Column(db.Integer, default=0)
    scorer_points = db.Column(db.Integer, default=0)

    user       = db.relationship('User', back_populates='bonus')
    champion   = db.relationship('Team', foreign_keys=[champion_id])
    runner_up  = db.relationship('Team', foreign_keys=[runner_up_id])


class ExtraBonusPrediction(db.Model):
    """Bonus extra: equipo más goleador, más tarjetas, caballo negro."""
    __tablename__ = 'extra_bonus'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    most_goals_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))
    most_cards_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))
    dark_horse_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))
    most_goals_pts = db.Column(db.Integer, default=0)
    most_cards_pts = db.Column(db.Integer, default=0)
    dark_horse_pts = db.Column(db.Integer, default=0)

    user            = db.relationship('User', back_populates='extra_bonus')
    most_goals_team = db.relationship('Team', foreign_keys=[most_goals_id])
    most_cards_team = db.relationship('Team', foreign_keys=[most_cards_id])
    dark_horse_team = db.relationship('Team', foreign_keys=[dark_horse_id])

    @property
    def total_pts(self):
        return (self.most_goals_pts or 0) + (self.most_cards_pts or 0) + (self.dark_horse_pts or 0)


class WorstTeamAssignment(db.Model):
    __tablename__ = 'worst_team_assignments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)

    user = db.relationship('User', back_populates='worst_team')
    team = db.relationship('Team')


class TournamentSettings(db.Model):
    __tablename__ = 'tournament_settings'
    id = db.Column(db.Integer, primary_key=True)
    bonus_locked   = db.Column(db.Boolean, default=False)
    champion_id    = db.Column(db.Integer, db.ForeignKey('teams.id'))
    runner_up_id   = db.Column(db.Integer, db.ForeignKey('teams.id'))
    top_scorer_name= db.Column(db.String(100), default='')
    prize_pool     = db.Column(db.Float, default=0.0)
    last_sync      = db.Column(db.DateTime)
    # Extra bonus winners
    most_goals_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))
    most_cards_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))
    dark_horse_id  = db.Column(db.Integer, db.ForeignKey('teams.id'))

    champion_team    = db.relationship('Team', foreign_keys=[champion_id])
    runner_up_team   = db.relationship('Team', foreign_keys=[runner_up_id])
    most_goals_team  = db.relationship('Team', foreign_keys=[most_goals_id])
    most_cards_team  = db.relationship('Team', foreign_keys=[most_cards_id])
    dark_horse_team  = db.relationship('Team', foreign_keys=[dark_horse_id])


class Player(db.Model):
    __tablename__ = 'players'
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    team_id   = db.Column(db.Integer, db.ForeignKey('teams.id'))
    position  = db.Column(db.String(20), default='')
    rarity    = db.Column(db.String(20), nullable=False)   # common · rare · epic · legendary
    icon      = db.Column(db.String(10), default='⚽')
    card_type = db.Column(db.String(20), default='player') # player · special
    image     = db.Column(db.String(100), default='')

    team = db.relationship('Team', foreign_keys=[team_id])


class UserCard(db.Model):
    __tablename__ = 'user_cards'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player_id       = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    obtained_at     = db.Column(db.DateTime, default=datetime.utcnow)
    duplicate_count = db.Column(db.Integer, default=0)

    user   = db.relationship('User', back_populates='cards')
    player = db.relationship('Player')

    __table_args__ = (db.UniqueConstraint('user_id', 'player_id'),)


class UserPack(db.Model):
    __tablename__ = 'user_packs'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    opened     = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at  = db.Column(db.DateTime)
    pack_type  = db.Column(db.String(20), default='standard')
    source     = db.Column(db.String(100), default='')  # previene dobles entregas

    user = db.relationship('User', back_populates='packs')


class Bet(db.Model):
    """Apuesta de un usuario en un mercado de un partido."""
    __tablename__ = 'bets'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id      = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    market        = db.Column(db.String(20), nullable=False)  # '1x2' | 'goals25' | 'btts'
    outcome       = db.Column(db.String(10), nullable=False)  # '1'|'X'|'2'|'over'|'under'|'yes'|'no'
    amount        = db.Column(db.Integer, nullable=False)     # monedas apostadas
    odds          = db.Column(db.Float,   nullable=False)     # cuota al apostar
    potential_win = db.Column(db.Integer, nullable=False)     # ganancia potencial (amount*odds)
    result        = db.Column(db.String(10))                  # None=pendiente 'won' 'lost' 'void'
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at    = db.Column(db.DateTime)

    user  = db.relationship('User',  backref=db.backref('bets', lazy='dynamic'))
    match = db.relationship('Match', backref=db.backref('bets', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('user_id', 'match_id', 'market',
                                          name='uq_bet_user_match_market'),)

    @property
    def market_label(self):
        return MARKET_LABELS.get(self.market, self.market)

    @property
    def outcome_label(self):
        return OUTCOME_LABELS.get(self.outcome, self.outcome)


# Etiquetas compartidas para mercados/resultados (apuestas y combinadas)
MARKET_LABELS = {
    '1x2': 'Ganador', 'goals25': '+2.5 Goles', 'btts': 'Ambos Marcan',
    'goals15': '+1.5 Goles', 'goals35': '+3.5 Goles', 'oddeven': 'Par / Impar',
    'corners': 'Córners',
}
OUTCOME_LABELS = {
    '1': '1 (local)', 'X': 'Empate', '2': '2 (visitante)',
    'over': 'Más de 2.5', 'under': 'Menos de 2.5', 'yes': 'Sí', 'no': 'No',
    'o15': 'Más de 1.5', 'u15': 'Menos de 1.5',
    'o35': 'Más de 3.5', 'u35': 'Menos de 3.5',
    'odd': 'Impar', 'even': 'Par',
    'c0_7': '≤7 córners', 'c8': '8 córners', 'c9': '9 córners', 'c10': '10 córners',
    'c11': '11 córners', 'c12': '12 córners', 'c13': '13 córners', 'c14p': '14+ córners',
}


class Parlay(db.Model):
    """Apuesta combinada: varias selecciones con una sola apuesta. Gana si aciertan todas."""
    __tablename__ = 'parlays'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount        = db.Column(db.Integer, nullable=False)   # monedas apostadas (una sola)
    total_odds    = db.Column(db.Float,   nullable=False)   # producto de las cuotas
    potential_win = db.Column(db.Integer, nullable=False)   # amount * total_odds
    result        = db.Column(db.String(10))                # None=pendiente 'won' 'lost'
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at    = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('parlays', lazy='dynamic'))
    legs = db.relationship('ParlayLeg', back_populates='parlay',
                           cascade='all, delete-orphan', lazy='select')

    @property
    def leg_count(self):
        return len(self.legs)

    @property
    def cancellable(self):
        """Se puede cancelar si ningún partido de la combinada ha empezado."""
        return self.result is None and all(
            (not leg.match.is_locked) and leg.match.goals1 is None for leg in self.legs
        )


class ParlayLeg(db.Model):
    """Cada selección de una combinada."""
    __tablename__ = 'parlay_legs'
    id         = db.Column(db.Integer, primary_key=True)
    parlay_id  = db.Column(db.Integer, db.ForeignKey('parlays.id'), nullable=False)
    match_id   = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    market     = db.Column(db.String(20), nullable=False)
    outcome    = db.Column(db.String(10), nullable=False)
    odds       = db.Column(db.Float, nullable=False)
    result     = db.Column(db.String(10))  # None=pendiente 'won' 'lost'

    parlay = db.relationship('Parlay', back_populates='legs')
    match  = db.relationship('Match')

    @property
    def market_label(self):
        return MARKET_LABELS.get(self.market, self.market)

    @property
    def outcome_label(self):
        return OUTCOME_LABELS.get(self.outcome, self.outcome)
