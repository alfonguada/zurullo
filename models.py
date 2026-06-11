from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    coins_spent  = db.Column(db.Integer, default=0)

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
    def total_points(self):
        return self.match_points + self.bonus_points + self.worst_points

    @property
    def coins(self):
        return max(0, self.total_points - (self.coins_spent or 0))

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
