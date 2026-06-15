from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markupsafe import Markup
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import os

import random
from models import db, User, Team, Match, Prediction, BonusPrediction, ExtraBonusPrediction, WorstTeamAssignment, TournamentSettings, Player, UserCard, UserPack, Bet, Parlay, ParlayLeg

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zurullo-wc-2026-secret')
_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zurullo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ── Migración automática de schema ────────────────────────────────────────────
# Corre en todos los puntos de entrada (WSGI, __main__, worker).
# SQLite no soporta ALTER TABLE IF NOT EXISTS, así que usamos inspect + try/except.
def _ensure_schema():
    from sqlalchemy import text, inspect as _inspect
    try:
        cols = {c['name'] for c in _inspect(db.engine).get_columns('users')}
        pending = []
        if 'bet_winnings' not in cols:
            pending.append("ALTER TABLE users ADD COLUMN bet_winnings INTEGER DEFAULT 0")
        if 'gift_coins' not in cols:
            pending.append("ALTER TABLE users ADD COLUMN gift_coins INTEGER DEFAULT 0")
        if 'gift_alert' not in cols:
            pending.append("ALTER TABLE users ADD COLUMN gift_alert INTEGER DEFAULT 0")
        mcols = {c['name'] for c in _inspect(db.engine).get_columns('matches')}
        if 'total_corners' not in mcols:
            pending.append("ALTER TABLE matches ADD COLUMN total_corners INTEGER")
        wcols = {c['name'] for c in _inspect(db.engine).get_columns('worst_team_assignments')}
        if 'goals_for' not in wcols:
            pending.append("ALTER TABLE worst_team_assignments ADD COLUMN goals_for INTEGER DEFAULT 0")
        if 'goals_against' not in wcols:
            pending.append("ALTER TABLE worst_team_assignments ADD COLUMN goals_against INTEGER DEFAULT 0")
        if 'pending_notice' not in cols:
            pending.append("ALTER TABLE users ADD COLUMN pending_notice TEXT")
        if pending:
            with db.engine.connect() as conn:
                for sql in pending:
                    conn.execute(text(sql))
                conn.commit()
    except Exception:
        pass  # tabla users aún no existe (primera ejecución)

with app.app_context():
    db.create_all()
    _ensure_schema()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Inicia sesión para continuar.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def auto_lock_started_matches():
    """Bloquea automáticamente partidos cuya hora de inicio ya pasó."""
    if not current_user.is_authenticated:
        return
    now = datetime.utcnow()
    started = Match.query.filter(
        Match.is_locked == False,
        Match.match_date <= now
    ).all()
    if started:
        for m in started:
            m.is_locked = True
        db.session.commit()


@app.template_global()
def flag(team, size='sm'):
    if not team:
        return Markup('')
    if team.flag_img:
        cls = 'flag-img-lg' if size == 'lg' else 'flag-img'
        return Markup(f'<img src="/static/flags/{team.flag_img}" class="{cls}" alt="{team.name}" loading="lazy">')
    return Markup(f'<span class="flag-emoji">{team.flag_emoji or ""}</span>')


@app.template_global()
def flagx(team):
    return flag(team, size='lg')
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# ─── CONTEXT PROCESSOR ────────────────────────────────────────────────────────

@app.context_processor
def inject_pack_count():
    ctx = {'pending_packs': 0, 'user_coins': 0, 'gift_alert': 0,
           'pending_notice': None, 'PACK_TYPES': PACK_TYPES}
    if current_user.is_authenticated:
        try:
            ctx['pending_packs'] = UserPack.query.filter_by(
                user_id=current_user.id, opened=False).count()
            ctx['user_coins'] = current_user.coins
            ctx['gift_alert'] = current_user.gift_alert or 0
            ctx['pending_notice'] = current_user.pending_notice or None
        except Exception:
            pass
    return ctx


# ─── SCORING LOGIC ────────────────────────────────────────────────────────────

def calc_points(p1, p2, r1, r2, double=False):
    if p1 is None or p2 is None:
        return 0
    mult = 2 if double else 1
    if p1 == r1 and p2 == r2:
        return 3 * mult
    pred_w = 1 if p1 > p2 else (2 if p2 > p1 else 0)
    real_w = 1 if r1 > r2 else (2 if r2 > r1 else 0)
    if pred_w == real_w:
        return 1 * mult
    return 0


def recalc_match(match):
    if not match.result_entered:
        return
    for pred in match.predictions:
        pred.points_earned = calc_points(pred.goals1, pred.goals2,
                                         match.goals1, match.goals2,
                                         match.any_double)
        if pred.points_earned in (3, 6):
            _grant_pack_no_commit(pred.user, 'standard', source=f'exact_{pred.id}')
    settle_match_bets(match)
    settle_match_parlays(match)


# ─── HELPERS: STREAKS & ACHIEVEMENTS ─────────────────────────────────────────

def compute_streak(user_id, positive=True):
    """Consecutive correct (positive=True) or wrong (False) predictions, most recent first."""
    preds = (Prediction.query.join(Match)
             .filter(Prediction.user_id == user_id,
                     Prediction.points_earned.isnot(None))
             .order_by(Match.match_date.desc()).all())
    streak = 0
    for p in preds:
        hit = (p.points_earned > 0) if positive else (p.points_earned == 0)
        if hit:
            streak += 1
        else:
            break
    return streak


def compute_achievements(user, all_users):
    ranked = sorted(all_users, key=lambda u: (u.total_points, u.exact_scores), reverse=True)
    rank = next((i + 1 for i, u in enumerate(ranked) if u.id == user.id), len(ranked))
    n = len(ranked)

    scored = Prediction.query.filter(
        Prediction.user_id == user.id, Prediction.points_earned.isnot(None)).count()
    correct = Prediction.query.filter(
        Prediction.user_id == user.id, Prediction.points_earned > 0).count()
    accuracy = (correct / scored * 100) if scored > 0 else 0

    streak_w = compute_streak(user.id, True)
    streak_l = compute_streak(user.id, False)

    A = []
    if rank == 1 and n > 1:
        A.append({'e': '👑', 'n': 'Líder Supremo',     'd': '#1 de la clasificación',       'c': 'accent'})
    if rank == n and n > 1:
        A.append({'e': '🤡', 'n': 'Gafe Oficial',       'd': 'Último en la clasificación',   'c': 'secondary'})
    if user.exact_scores >= 10:
        A.append({'e': '🧙', 'n': 'El Adivino',         'd': f'{user.exact_scores} exactos', 'c': 'primary'})
    elif user.exact_scores >= 3:
        A.append({'e': '🎯', 'n': 'Francotirador',      'd': f'{user.exact_scores} exactos', 'c': 'primary'})
    elif user.exact_scores >= 1:
        A.append({'e': '💡', 'n': 'Primer Impacto',     'd': 'Primer resultado exacto',      'c': 'blue'})
    if streak_w >= 5:
        A.append({'e': '🔥', 'n': 'En Llamas',          'd': f'{streak_w} seguidos',         'c': 'orange'})
    elif streak_w >= 3:
        A.append({'e': '⚡', 'n': 'Calentando',         'd': f'{streak_w} seguidos',         'c': 'accent'})
    if streak_l >= 5:
        A.append({'e': '🧊', 'n': 'Cubito de Hielo',    'd': f'{streak_l} fallos seguidos',  'c': 'secondary'})
    elif streak_l >= 3:
        A.append({'e': '💀', 'n': 'Racha Negra',        'd': f'{streak_l} fallos seguidos',  'c': 'secondary'})
    if accuracy >= 70 and scored >= 10:
        A.append({'e': '🦅', 'n': 'Águila Real',        'd': f'{accuracy:.0f}% acierto',     'c': 'blue'})
    if scored == 0:
        A.append({'e': '😴', 'n': '¿Estás Ahí?',        'd': 'Aún sin porras',               'c': 'muted'})
    if user.bonus and user.bonus.champion_id and user.bonus.runner_up_id and user.bonus.top_scorer_name:
        A.append({'e': '🏆', 'n': 'All-In',             'd': 'Todos los bonus rellenados',   'c': 'accent'})
    if user.worst_team and user.worst_points >= 5:
        A.append({'e': '🎪', 'n': 'Mi Equipo, Mi Vida', 'd': f'+{user.worst_points} pts con tu peor selección', 'c': 'orange'})
    if not A:
        A.append({'e': '🐣', 'n': 'Recién Llegado',     'd': 'El inicio de una leyenda',     'c': 'muted'})
    return A


def build_activity_feed():
    """Generate interesting activity items from DB."""
    items = []
    users = User.query.all()
    for user in users:
        sw = compute_streak(user.id, True)
        sl = compute_streak(user.id, False)
        if sw >= 3:
            items.append({'e': '🔥', 'text': f'{user.name} lleva {sw} aciertos seguidos',
                          'user': user, 'score': sw * 2})
        if sl >= 3:
            items.append({'e': '❄️', 'text': f'{user.name} no da ni una ({sl} fallos seguidos)',
                          'user': user, 'score': sl})
        last_exact = (Prediction.query.filter(
            Prediction.user_id == user.id, Prediction.points_earned.in_([3, 6]))
            .join(Match).order_by(Match.match_date.desc()).first())
        if last_exact and last_exact.match.result_entered:
            m = last_exact.match
            items.append({'e': '🎯',
                          'text': f'{user.name} acertó el exacto: {m.team1.name} {m.goals1}–{m.goals2} {m.team2.name}',
                          'user': user, 'score': 4})
    # Global: leader
    ranked = sorted(users, key=lambda u: u.total_points, reverse=True)
    if ranked:
        top = ranked[0]
        items.append({'e': '👑', 'text': f'{top.name} lidera con {top.total_points} puntos',
                      'user': top, 'score': 10})
        if len(ranked) > 1:
            last = ranked[-1]
            items.append({'e': '🤡', 'text': f'{last.name} cierra la tabla con {last.total_points} pts',
                          'user': last, 'score': 3})
    # Deduplicate and sort
    seen = set()
    unique = []
    for it in sorted(items, key=lambda x: x['score'], reverse=True):
        key = it['text']
        if key not in seen:
            seen.add(key)
            unique.append(it)
    return unique[:20]


def auto_assign_worst_team(user):
    """Assign a random unclaimed worst team to user. Returns team or None."""
    if WorstTeamAssignment.query.filter_by(user_id=user.id).first():
        return None
    taken = [a.team_id for a in WorstTeamAssignment.query.all()]
    available = Team.query.filter_by(is_worst=True).filter(
        ~Team.id.in_(taken) if taken else db.true()
    ).all()
    if not available:
        return None
    team = random.choice(available)
    db.session.add(WorstTeamAssignment(user_id=user.id, team_id=team.id))
    db.session.commit()
    return team


def recalc_worst_teams():
    for assignment in WorstTeamAssignment.query.all():
        team_id = assignment.team_id
        matches = Match.query.filter(
            db.or_(Match.team1_id == team_id, Match.team2_id == team_id),
            Match.goals1.isnot(None)
        ).all()
        gf = ga = 0
        for m in matches:
            if m.team1_id == team_id:
                gf += m.goals1
                ga += m.goals2
            else:
                gf += m.goals2
                ga += m.goals1
        assignment.goals_for = gf
        assignment.goals_against = ga
        assignment.points_earned = gf + (ga // 3)
    db.session.commit()


# ─── PACK CONFIGURATION ───────────────────────────────────────────────────────

PACK_TYPES = {
    'standard': {
        'name': 'Estándar',   'icon': '📦', 'cost': 25,  'cards': 5,
        'color': '#7090c8',
        'desc': '5 cartas · probabilidades base',
        'weights': {'common': 65, 'rare': 25, 'epic': 8, 'legendary': 2, 'ultra': 0},
        'guaranteed': None,
    },
    'premium': {
        'name': 'Premium',    'icon': '🎁', 'cost': 50,  'cards': 7,
        'color': '#00b4ff',
        'desc': '7 cartas · rara garantizada · posibilidad ultra',
        'weights': {'common': 44, 'rare': 34, 'epic': 16, 'legendary': 5, 'ultra': 1},
        'guaranteed': 'rare',
    },
    'elite': {
        'name': 'Élite',      'icon': '👑', 'cost': 100, 'cards': 10,
        'color': '#ffaa00',
        'desc': '10 cartas · épica garantizada · ultra posible',
        'weights': {'common': 24, 'rare': 33, 'epic': 27, 'legendary': 13, 'ultra': 3},
        'guaranteed': 'epic',
    },
}

# ─── BETTING MARKETS ──────────────────────────────────────────────────────────

BETTING_MARKETS = {
    '1x2': {
        'name': 'Ganador',
        'icon': '🏆',
        'outcomes': ['1', 'X', '2'],
        'labels': {'1': 'Local', 'X': 'Empate', '2': 'Visitante'},
        'base_probs': {'1': 0.395, 'X': 0.270, '2': 0.335},
        'margin': 1.065,
    },
    'goals25': {
        'name': '+2.5 Goles',
        'icon': '⚽',
        'outcomes': ['over', 'under'],
        'labels': {'over': 'Más de 2.5', 'under': 'Menos de 2.5'},
        'base_probs': {'over': 0.524, 'under': 0.476},
        'margin': 1.040,
    },
    'btts': {
        'name': 'Ambos Marcan',
        'icon': '🎯',
        'outcomes': ['yes', 'no'],
        'labels': {'yes': 'Sí', 'no': 'No'},
        'base_probs': {'yes': 0.524, 'under': 0.476},  # 'under' key kept for compat
        'margin': 1.040,
    },
    'goals15': {
        'name': '+1.5 Goles',
        'icon': '🥅',
        'outcomes': ['o15', 'u15'],
        'labels': {'o15': 'Más de 1.5', 'u15': 'Menos de 1.5'},
        'base_probs': {'o15': 0.74, 'u15': 0.26},
        'margin': 1.045,
    },
    'goals35': {
        'name': '+3.5 Goles',
        'icon': '💥',
        'outcomes': ['o35', 'u35'],
        'labels': {'o35': 'Más de 3.5', 'u35': 'Menos de 3.5'},
        'base_probs': {'o35': 0.33, 'u35': 0.67},
        'margin': 1.045,
    },
    'oddeven': {
        'name': 'Par / Impar',
        'icon': '🔢',
        'outcomes': ['odd', 'even'],
        'labels': {'odd': 'Impar', 'even': 'Par'},
        'base_probs': {'odd': 0.51, 'even': 0.49},
        'margin': 1.050,
    },
    'corners': {
        'name': 'Córners (total)',
        'icon': '🚩',
        'outcomes': ['c0_7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13', 'c14p'],
        'labels': {'c0_7': '≤7', 'c8': '8', 'c9': '9', 'c10': '10',
                   'c11': '11', 'c12': '12', 'c13': '13', 'c14p': '14+'},
        'base_probs': {'c0_7': 0.16, 'c8': 0.10, 'c9': 0.12, 'c10': 0.13,
                       'c11': 0.12, 'c12': 0.10, 'c13': 0.08, 'c14p': 0.19},
        'margin': 1.100,
    },
}
# Corrección clave btts
BETTING_MARKETS['btts']['base_probs'] = {'yes': 0.524, 'no': 0.476}


def calc_live_odds(match_id, market):
    """Calcula cuotas en vivo para un mercado según el dinero apostado."""
    cfg = BETTING_MARKETS[market]
    base_probs = cfg['base_probs']
    margin = cfg['margin']
    outcomes = cfg['outcomes']

    bets = Bet.query.filter_by(match_id=match_id, market=market).all()
    total_wagered = sum(b.amount for b in bets)
    wagered = {o: sum(b.amount for b in bets if b.outcome == o) for o in outcomes}

    # Probabilidad mezclada: 65% base + 35% mercado (solo si hay suficiente volumen)
    blended = {}
    for o in outcomes:
        bp = base_probs[o]
        if total_wagered >= 50:
            mp = wagered[o] / total_wagered
            blended[o] = 0.65 * bp + 0.35 * mp
        else:
            blended[o] = bp

    total_blended = sum(blended.values())
    result = {}
    for o in outcomes:
        prob = (blended[o] / total_blended) * margin
        result[o] = round(max(1.05, min(15.0, 1.0 / prob)), 2)
    return result


def _winning_outcomes(match):
    """Resultado ganador de cada mercado para un partido jugado."""
    g1, g2 = match.goals1, match.goals2
    total_goals = g1 + g2
    outcomes = {
        '1x2':    '1' if g1 > g2 else ('X' if g1 == g2 else '2'),
        'goals25': 'over' if total_goals > 2.5 else 'under',
        'goals15': 'o15' if total_goals > 1.5 else 'u15',
        'goals35': 'o35' if total_goals > 3.5 else 'u35',
        'btts':    'yes' if (g1 > 0 and g2 > 0) else 'no',
        'oddeven': 'odd' if total_goals % 2 == 1 else 'even',
    }
    # Córners: solo se liquidan cuando el admin ha introducido el total
    if match.total_corners is not None:
        c = match.total_corners
        if c <= 7:
            cw = 'c0_7'
        elif c >= 14:
            cw = 'c14p'
        else:
            cw = f'c{c}'
        outcomes['corners'] = cw
    return outcomes


def settle_match_bets(match):
    """Liquida automáticamente todas las apuestas simples de un partido."""
    if not match.result_entered:
        return
    winning_outcomes = _winning_outcomes(match)
    pending = Bet.query.filter_by(match_id=match.id, result=None).all()
    for bet in pending:
        correct = winning_outcomes.get(bet.market)
        if correct is None:
            continue
        if bet.outcome == correct:
            bet.result = 'won'
            bet.user.bet_winnings = (bet.user.bet_winnings or 0) + bet.potential_win
        else:
            bet.result = 'lost'
        bet.settled_at = datetime.utcnow()
    # No commit here — caller commits


def settle_match_parlays(match):
    """Resuelve las selecciones de combinadas de este partido y liquida las que queden completas."""
    if not match.result_entered:
        return
    winning_outcomes = _winning_outcomes(match)
    legs = ParlayLeg.query.filter_by(match_id=match.id, result=None).all()
    affected = set()
    for leg in legs:
        correct = winning_outcomes.get(leg.market)
        if correct is None:
            continue
        leg.result = 'won' if leg.outcome == correct else 'lost'
        affected.add(leg.parlay_id)
    # Reevaluar cada combinada afectada
    for pid in affected:
        parlay = Parlay.query.get(pid)
        if not parlay or parlay.result is not None:
            continue
        results = [l.result for l in parlay.legs]
        if any(r == 'lost' for r in results):
            parlay.result = 'lost'
            parlay.settled_at = datetime.utcnow()
        elif all(r == 'won' for r in results):
            parlay.result = 'won'
            parlay.settled_at = datetime.utcnow()
            parlay.user.bet_winnings = (parlay.user.bet_winnings or 0) + parlay.potential_win
        # si quedan selecciones pendientes, la combinada sigue abierta
    # No commit here — caller commits


# ─── PACK HELPERS ─────────────────────────────────────────────────────────────

_RARITY_WEIGHTS = PACK_TYPES['standard']['weights']


def _grant_pack_no_commit(user, pack_type='standard', source=''):
    """Añade un sobre a la sesión sin hacer commit. Idempotente por source."""
    if source and UserPack.query.filter_by(user_id=user.id, source=source).first():
        return None
    pack = UserPack(user_id=user.id, pack_type=pack_type, source=source)
    db.session.add(pack)
    return pack


def grant_pack(user, pack_type='standard', source=''):
    """Entrega un sobre y hace commit inmediato."""
    pack = _grant_pack_no_commit(user, pack_type, source)
    if pack:
        db.session.commit()
    return pack


def grant_milestone_packs(user):
    """Entrega sobres por cada hito de 25 puntos aún no entregado."""
    earned = user.total_points // 25
    existing = UserPack.query.filter(
        UserPack.user_id == user.id,
        UserPack.source.like('milestone_%')
    ).count()
    for i in range(existing, earned):
        _grant_pack_no_commit(user, 'standard', source=f'milestone_{i + 1}')


def draw_cards(n=5, rarity_weights=None, guaranteed=None):
    """Extrae n cartas únicas con pesos de rareza opcionales y garantía mínima."""
    if rarity_weights is None:
        rarity_weights = _RARITY_WEIGHTS
    all_players = Player.query.all()
    if not all_players:
        return []
    weights = [rarity_weights.get(p.rarity, 1) for p in all_players]
    drawn, drawn_ids, attempts = [], set(), 0
    while len(drawn) < n and len(drawn) < len(all_players) and attempts < 300:
        attempts += 1
        card = random.choices(all_players, weights=weights, k=1)[0]
        if card.id not in drawn_ids:
            drawn_ids.add(card.id)
            drawn.append(card)

    if guaranteed and drawn:
        _rarity_rank = {'ultra': 0, 'legendary': 1, 'epic': 2, 'rare': 3, 'common': 4}
        g_rank = _rarity_rank.get(guaranteed, 4)
        has_guarantee = any(_rarity_rank.get(c.rarity, 3) <= g_rank for c in drawn)
        if not has_guarantee:
            drawn_set = {c.id for c in drawn}
            eligible = [p for p in all_players
                        if _rarity_rank.get(p.rarity, 3) <= g_rank and p.id not in drawn_set]
            if eligible:
                worst_idx = max(range(len(drawn)),
                                key=lambda i: _rarity_rank.get(drawn[i].rarity, 3))
                drawn[worst_idx] = random.choice(eligible)
    return drawn


def grant_daily_packs():
    """Entrega 2 sobres estándar gratuitos a cada usuario una vez por día."""
    today = datetime.utcnow().date().isoformat()
    source = f'daily_{today}'
    users = User.query.all()
    granted = 0
    for user in users:
        for n in range(2):
            if _grant_pack_no_commit(user, 'standard', source=f'{source}_u{user.id}_n{n}'):
                granted += 1
    if granted:
        db.session.commit()
    return granted


# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_done:
            return redirect(url_for('onboarding'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        ident = request.form.get('username', '').strip()
        pw = request.form.get('password', '')
        user = User.query.filter(
            db.or_(User.username == ident, User.email == ident.lower())
        ).first()
        if user and user.check_password(pw):
            login_user(user, remember=bool(request.form.get('remember')))
            return redirect(request.args.get('next') or url_for('index'))
        flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        pw = request.form.get('password', '')
        pw2 = request.form.get('password2', '')
        if not username or not email or not pw:
            flash('Todos los campos son obligatorios.', 'error')
        elif pw != pw2:
            flash('Las contraseñas no coinciden.', 'error')
        elif len(pw) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Ese nombre de usuario ya existe.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Ese email ya está registrado.', 'error')
        else:
            is_first = User.query.filter_by(is_admin=True).count() == 0
            user = User(username=username, display_name=username, email=email, is_admin=is_first)
            user.set_password(pw)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('onboarding'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    teams = Team.query.order_by(Team.name).all()
    settings = TournamentSettings.query.first()
    if request.method == 'POST':
        step = request.form.get('step')
        if step == 'profile':
            dn = request.form.get('display_name', '').strip()
            current_user.display_name = dn or current_user.username
            current_user.avatar_emoji = request.form.get('avatar_emoji', '👾')
            current_user.avatar_bg = request.form.get('avatar_bg', '#ff0066')
            db.session.commit()
            return jsonify({'ok': True})
        elif step == 'bonus':
            if not (settings and settings.bonus_locked):
                bonus = BonusPrediction.query.filter_by(user_id=current_user.id).first()
                if not bonus:
                    bonus = BonusPrediction(user_id=current_user.id)
                    db.session.add(bonus)
                champ = request.form.get('champion_id')
                sub = request.form.get('runner_up_id')
                bonus.champion_id = int(champ) if champ else None
                bonus.runner_up_id = int(sub) if sub else None
                bonus.top_scorer_name = request.form.get('top_scorer_name', '').strip()
                db.session.commit()
            current_user.onboarding_done = True
            db.session.commit()
            # Auto-asignar peor selección aleatoria
            assigned = auto_assign_worst_team(current_user)
            team_data = None
            if assigned:
                team_data = {'name': assigned.name, 'flag_img': assigned.flag_img, 'flag_emoji': assigned.flag_emoji}
            return jsonify({'ok': True, 'redirect': url_for('dashboard'), 'worst_team': team_data})
    return render_template('onboarding.html', teams=teams, settings=settings)


@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    now = datetime.utcnow()
    upcoming = Match.query.filter(Match.goals1.is_(None), Match.match_date >= now)\
        .order_by(Match.match_date).limit(6).all()
    recent = Match.query.filter(Match.goals1.isnot(None))\
        .order_by(Match.match_date.desc()).limit(5).all()
    all_users = User.query.all()
    top5 = sorted(all_users, key=lambda u: (u.total_points, u.exact_scores), reverse=True)[:5]
    user_rank = next((i + 1 for i, u in enumerate(
        sorted(all_users, key=lambda u: (u.total_points, u.exact_scores), reverse=True)
    ) if u.id == current_user.id), 1)
    match_ids = [m.id for m in upcoming + recent]
    preds = {p.match_id: p for p in Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.match_id.in_(match_ids)
    ).all()} if match_ids else {}
    settings = TournamentSettings.query.first()
    total_users = len(all_users)
    prize_pool = settings.prize_pool if settings else 0
    return render_template('dashboard.html',
                           upcoming=upcoming, recent=recent, top5=top5,
                           user_rank=user_rank, preds=preds,
                           total_users=total_users, prize_pool=prize_pool)


@app.route('/predictions')
@login_required
def predictions():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    phase = request.args.get('phase', 'all')
    q = Match.query.order_by(Match.match_date, Match.match_number)
    if phase != 'all':
        q = q.filter(Match.phase == phase)
    matches = q.all()
    match_ids = [m.id for m in matches]
    preds = {p.match_id: p for p in Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.match_id.in_(match_ids)
    ).all()} if match_ids else {}
    by_date = defaultdict(list)
    for m in matches:
        by_date[m.match_date.strftime('%Y-%m-%d')].append(m)
    return render_template('predictions.html',
                           matches=matches, by_date=dict(by_date),
                           preds=preds, phase=phase)


@app.route('/predict/<int:match_id>', methods=['POST'])
@login_required
def predict(match_id):
    match = Match.query.get_or_404(match_id)
    if match.is_locked:
        return jsonify({'error': 'Partido bloqueado.'}), 400
    try:
        g1 = int(request.form['goals1'])
        g2 = int(request.form['goals2'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Valores inválidos.'}), 400
    if g1 < 0 or g2 < 0 or g1 > 20 or g2 > 20:
        return jsonify({'error': 'Rango inválido.'}), 400
    if match.phase != 'group' and g1 == g2:
        return jsonify({'error': 'En eliminatorias no puede haber empate.'}), 400
    pred = Prediction.query.filter_by(user_id=current_user.id, match_id=match_id).first()
    if pred:
        pred.goals1 = g1
        pred.goals2 = g2
        pred.submitted_at = datetime.utcnow()
    else:
        pred = Prediction(user_id=current_user.id, match_id=match_id, goals1=g1, goals2=g2)
        db.session.add(pred)
    if match.result_entered:
        pred.points_earned = calc_points(g1, g2, match.goals1, match.goals2, match.double_points)
    db.session.commit()
    return jsonify({'ok': True, 'g1': g1, 'g2': g2})


# ─── CASA DE APUESTAS ─────────────────────────────────────────────────────────

@app.route('/casa')
@login_required
def casa():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    now = datetime.utcnow()
    open_matches = (Match.query
                    .filter(Match.is_locked == False, Match.goals1.is_(None))
                    .order_by(Match.match_date).limit(20).all())
    locked_noresult = (Match.query
                       .filter(Match.is_locked == True, Match.goals1.is_(None))
                       .order_by(Match.match_date).all())
    recent = (Match.query
              .filter(Match.goals1.isnot(None))
              .order_by(Match.match_date.desc()).limit(6).all())

    # Cuotas base para los partidos abiertos
    odds_map = {}
    for m in open_matches:
        odds_map[m.id] = {mk: calc_live_odds(m.id, mk) for mk in BETTING_MARKETS}

    # Apuestas activas del usuario en partidos aún no liquidados
    active_bets = (Bet.query
                   .filter_by(user_id=current_user.id, result=None)
                   .join(Match)
                   .order_by(Match.match_date)
                   .all())
    # Últimas 5 apuestas liquidadas
    recent_bets = (Bet.query
                   .filter(Bet.user_id == current_user.id, Bet.result.isnot(None))
                   .order_by(Bet.settled_at.desc()).limit(5).all())

    # Combinadas activas del usuario
    active_parlays = (Parlay.query
                      .filter_by(user_id=current_user.id, result=None)
                      .order_by(Parlay.created_at.desc()).all())

    return render_template('casa.html',
        open_matches=open_matches,
        locked_noresult=locked_noresult,
        recent_results=recent,
        odds_map=odds_map,
        MARKETS=BETTING_MARKETS,
        active_bets=active_bets,
        recent_bets=recent_bets,
        active_parlays=active_parlays,
    )


MAX_PARLAY_LEGS = 10
MAX_TOTAL_ODDS  = 1000.0


@app.route('/casa/boleto', methods=['POST'])
@login_required
def place_slip():
    """Registra un boleto: 1 selección = apuesta simple, 2-10 = combinada."""
    data = request.get_json(silent=True) or {}
    legs_in = data.get('legs') or []
    try:
        amount = int(data.get('amount') or 0)
    except (TypeError, ValueError):
        amount = 0

    if not legs_in:
        return jsonify({'error': 'Selecciona al menos una apuesta.'}), 400
    if len(legs_in) > MAX_PARLAY_LEGS:
        return jsonify({'error': f'Máximo {MAX_PARLAY_LEGS} selecciones por combinada.'}), 400
    if not (10 <= amount <= 1000):
        return jsonify({'error': 'Importe entre 10 y 1.000 🪙.'}), 400
    if current_user.coins < amount:
        return jsonify({'error': f'No tienes suficientes monedas ({current_user.coins}🪙).'}), 400

    # Validar y normalizar cada selección (recalculando cuotas en el servidor)
    seen, legs = set(), []
    for lg in legs_in:
        try:
            mid = int(lg.get('match_id'))
        except (TypeError, ValueError):
            return jsonify({'error': 'Selección inválida.'}), 400
        market, outcome = lg.get('market'), lg.get('outcome')
        if market not in BETTING_MARKETS:
            return jsonify({'error': 'Mercado inválido.'}), 400
        if outcome not in BETTING_MARKETS[market]['outcomes']:
            return jsonify({'error': 'Resultado inválido.'}), 400
        if (mid, market) in seen:
            return jsonify({'error': 'No puedes repetir el mismo mercado de un partido.'}), 400
        seen.add((mid, market))
        match = Match.query.get(mid)
        if not match:
            return jsonify({'error': 'Partido no encontrado.'}), 404
        if match.is_locked or match.result_entered:
            return jsonify({'error': f'{match.team1.name}-{match.team2.name} ya no admite apuestas.'}), 400
        odds = calc_live_odds(mid, market)[outcome]
        legs.append({'match': match, 'market': market, 'outcome': outcome, 'odds': odds})

    # ── Apuesta simple ──
    if len(legs) == 1:
        lg = legs[0]
        if Bet.query.filter_by(user_id=current_user.id, match_id=lg['match'].id,
                               market=lg['market'], result=None).first():
            return jsonify({'error': 'Ya tienes una apuesta activa en ese mercado.'}), 400
        potential = int(amount * lg['odds'])
        current_user.coins_spent = (current_user.coins_spent or 0) + amount
        db.session.add(Bet(
            user_id=current_user.id, match_id=lg['match'].id,
            market=lg['market'], outcome=lg['outcome'],
            amount=amount, odds=lg['odds'], potential_win=potential,
        ))
        db.session.commit()
        return jsonify({'ok': True, 'kind': 'single', 'total_odds': lg['odds'],
                        'potential': potential, 'coins': current_user.coins})

    # ── Combinada ──
    total_odds = 1.0
    for lg in legs:
        total_odds *= lg['odds']
    total_odds = round(min(total_odds, MAX_TOTAL_ODDS), 2)
    potential = int(amount * total_odds)
    current_user.coins_spent = (current_user.coins_spent or 0) + amount
    parlay = Parlay(user_id=current_user.id, amount=amount,
                    total_odds=total_odds, potential_win=potential)
    db.session.add(parlay)
    db.session.flush()
    for lg in legs:
        db.session.add(ParlayLeg(
            parlay_id=parlay.id, match_id=lg['match'].id,
            market=lg['market'], outcome=lg['outcome'], odds=round(lg['odds'], 2),
        ))
    db.session.commit()
    return jsonify({'ok': True, 'kind': 'combo', 'legs': len(legs),
                    'total_odds': total_odds, 'potential': potential,
                    'coins': current_user.coins})


@app.route('/casa/cancelar/<int:bet_id>', methods=['POST'])
@login_required
def cancel_bet(bet_id):
    """Cancela una apuesta simple y devuelve las monedas si el partido no ha empezado."""
    bet = Bet.query.get_or_404(bet_id)
    if bet.user_id != current_user.id:
        return jsonify({'error': 'No autorizado.'}), 403
    if bet.result is not None:
        return jsonify({'error': 'Esta apuesta ya está liquidada.'}), 400
    if bet.match.is_locked or bet.match.result_entered:
        return jsonify({'error': 'El partido ya empezó, no se puede cancelar.'}), 400
    current_user.coins_spent = max(0, (current_user.coins_spent or 0) - bet.amount)
    db.session.delete(bet)
    db.session.commit()
    return jsonify({'ok': True, 'coins': current_user.coins})


@app.route('/casa/combinada/cancelar/<int:parlay_id>', methods=['POST'])
@login_required
def cancel_parlay(parlay_id):
    """Cancela una combinada y devuelve las monedas si ningún partido ha empezado."""
    parlay = Parlay.query.get_or_404(parlay_id)
    if parlay.user_id != current_user.id:
        return jsonify({'error': 'No autorizado.'}), 403
    if parlay.result is not None:
        return jsonify({'error': 'Esta combinada ya está liquidada.'}), 400
    if not parlay.cancellable:
        return jsonify({'error': 'Algún partido ya empezó, no se puede cancelar.'}), 400
    current_user.coins_spent = max(0, (current_user.coins_spent or 0) - parlay.amount)
    db.session.delete(parlay)
    db.session.commit()
    return jsonify({'ok': True, 'coins': current_user.coins})


@app.route('/api/casa/odds/<int:match_id>')
@login_required
def api_betting_odds(match_id):
    match = Match.query.get_or_404(match_id)
    if match.is_locked:
        return jsonify({'locked': True})
    odds = {mk: calc_live_odds(match_id, mk) for mk in BETTING_MARKETS}
    user_bets = {
        b.market: {'outcome': b.outcome, 'amount': b.amount,
                   'odds': b.odds, 'potential': b.potential_win}
        for b in Bet.query.filter_by(user_id=current_user.id, match_id=match_id).all()
    }
    return jsonify({'odds': odds, 'user_bets': user_bets, 'coins': current_user.coins})


@app.route('/casa/mis-apuestas')
@login_required
def mis_apuestas():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    bets = (Bet.query
            .filter_by(user_id=current_user.id)
            .join(Match).order_by(Bet.created_at.desc()).all())
    parlays = (Parlay.query
               .filter_by(user_id=current_user.id)
               .order_by(Parlay.created_at.desc()).all())
    pending = [b for b in bets if b.result is None]
    won     = [b for b in bets if b.result == 'won']
    lost    = [b for b in bets if b.result == 'lost']
    pending_parlays = [p for p in parlays if p.result is None]
    won_parlays     = [p for p in parlays if p.result == 'won']
    lost_parlays    = [p for p in parlays if p.result == 'lost']
    # KPIs combinando apuestas simples y combinadas
    all_won  = won + won_parlays
    all_lost = lost + lost_parlays
    total_wagered = sum(b.amount for b in bets) + sum(p.amount for p in parlays)
    total_won     = sum(b.potential_win for b in won) + sum(p.potential_win for p in won_parlays)
    n_total = len(bets) + len(parlays)
    roi = round((total_won - total_wagered) / total_wagered * 100, 1) if total_wagered > 0 else 0
    return render_template('mis_apuestas.html',
        bets=bets, pending=pending, won=all_won, lost=all_lost,
        parlays=parlays, pending_parlays=pending_parlays,
        n_total=n_total, total_wagered=total_wagered, total_won=total_won,
        roi=roi,
    )


@app.route('/stats')
@login_required
def stats():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))

    from collections import Counter
    from sqlalchemy import func

    all_users = User.query.all()
    users_ranked = sorted(all_users, key=lambda u: (u.total_points, u.exact_scores), reverse=True)
    played_matches = (Match.query
                      .filter(Match.goals1.isnot(None))
                      .order_by(Match.match_date).all())

    # ── Global KPIs ───────────────────────────────────────────────
    total_preds   = Prediction.query.count()
    scored_preds  = Prediction.query.filter(Prediction.points_earned.isnot(None)).count()
    correct_preds = Prediction.query.filter(Prediction.points_earned > 0).count()
    exact_preds   = Prediction.query.filter(Prediction.points_earned.in_([3, 6])).count()
    global_acc    = round(correct_preds / scored_preds * 100) if scored_preds > 0 else 0

    # ── Per-user stats ────────────────────────────────────────────
    user_stats = []
    for i, u in enumerate(users_ranked):
        u_scored  = Prediction.query.filter(
            Prediction.user_id == u.id, Prediction.points_earned.isnot(None)).count()
        u_correct = Prediction.query.filter(
            Prediction.user_id == u.id, Prediction.points_earned > 0).count()
        u_exact   = Prediction.query.filter(
            Prediction.user_id == u.id, Prediction.points_earned.in_([3, 6])).count()
        user_stats.append({
            'rank': i + 1,
            'user': u,
            'scored': u_scored,
            'correct': u_correct,
            'exact': u_exact,
            'accuracy': round(u_correct / u_scored * 100) if u_scored > 0 else 0,
            'coins_earned': u.coins_earned,
            'coins_spent': u.coins_spent or 0,
            'coins': u.coins,
        })

    # ── Points timeline (bulk fetch) ──────────────────────────────
    played_ids = [m.id for m in played_matches]
    preds_bulk = {}
    if played_ids:
        for p in Prediction.query.filter(Prediction.match_id.in_(played_ids)).all():
            preds_bulk[(p.user_id, p.match_id)] = p.points_earned or 0

    timeline_labels, timeline_data = [], {u.id: [] for u in all_users}
    cumulative = {u.id: 0 for u in all_users}
    for m in played_matches:
        timeline_labels.append(f"{m.team1.name[:3].upper()}v{m.team2.name[:3].upper()}")
        for u in all_users:
            pts = preds_bulk.get((u.id, m.id), 0)
            cumulative[u.id] += pts
            timeline_data[u.id].append(cumulative[u.id])

    # ── Per-match analysis ────────────────────────────────────────
    match_stats = []
    for m in played_matches:
        mp = Prediction.query.filter_by(match_id=m.id).all()
        n = len(mp)
        if n == 0:
            continue
        correct_m = sum(1 for p in mp if (p.points_earned or 0) > 0)
        exact_m   = sum(1 for p in mp if (p.points_earned or 0) in (3, 6))
        sc_counts = Counter(f"{p.goals1}-{p.goals2}" for p in mp)
        top_score, top_cnt = sc_counts.most_common(1)[0]
        match_stats.append({
            'match': m,
            'total': n,
            'correct': correct_m,
            'exact': exact_m,
            'accuracy': round(correct_m / n * 100),
            'exact_pct': round(exact_m / n * 100),
            'most_pred': top_score,
            'most_pred_pct': round(top_cnt / n * 100),
        })

    # ── Prediction matrix (last 10 matches) ──────────────────────
    matrix_matches = played_matches[-10:] if len(played_matches) > 10 else played_matches
    matrix_ids     = [m.id for m in matrix_matches]
    matrix_preds   = {}
    if matrix_ids:
        for p in Prediction.query.filter(Prediction.match_id.in_(matrix_ids)).all():
            matrix_preds[(p.user_id, p.match_id)] = p

    # ── Fun facts ─────────────────────────────────────────────────
    # Best accuracy user
    best_acc  = max(user_stats, key=lambda x: (x['accuracy'], x['scored'])) if user_stats else None
    # Most exact scores
    top_exact = max(user_stats, key=lambda x: x['exact']) if user_stats else None
    # Hardest match (lowest accuracy)
    hardest   = min(match_stats, key=lambda x: x['accuracy']) if match_stats else None
    # Easiest match (highest accuracy)
    easiest   = max(match_stats, key=lambda x: x['accuracy']) if match_stats else None
    # Richest user (most coins)
    richest   = max(user_stats, key=lambda x: x['coins']) if user_stats else None
    # Most coins spent
    biggest_spender = max(user_stats, key=lambda x: x['coins_spent']) if user_stats else None

    return render_template('stats.html',
        user_stats=user_stats,
        match_stats=match_stats,
        timeline_labels=timeline_labels,
        timeline_data=timeline_data,
        matrix_matches=matrix_matches,
        matrix_preds=matrix_preds,
        all_users=users_ranked,
        global_acc=global_acc,
        total_preds=total_preds,
        correct_preds=correct_preds,
        exact_preds=exact_preds,
        played_count=len(played_matches),
        best_acc=best_acc,
        top_exact=top_exact,
        hardest=hardest,
        easiest=easiest,
        richest=richest,
        biggest_spender=biggest_spender,
    )


@app.route('/leaderboard')
@login_required
def leaderboard():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    users = User.query.all()
    ranked = sorted(users, key=lambda u: (u.total_points, u.exact_scores), reverse=True)
    rows = []
    for i, u in enumerate(ranked):
        rank = i + 1
        if i > 0 and u.total_points == ranked[i - 1].total_points and \
                u.exact_scores == ranked[i - 1].exact_scores:
            rank = rows[i - 1]['rank']
        rows.append({
            'rank': rank, 'user': u,
            'total': u.total_points,
            'match_pts': u.match_points,
            'bonus_pts': u.bonus_points,
            'worst_pts': u.worst_points,
            'exact': u.exact_scores,
        })
    settings = TournamentSettings.query.first()
    return render_template('leaderboard.html', rows=rows, settings=settings)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    teams = Team.query.order_by(Team.name).all()
    settings = TournamentSettings.query.first()
    bonus = BonusPrediction.query.filter_by(user_id=current_user.id).first()
    extra_bonus = ExtraBonusPrediction.query.filter_by(user_id=current_user.id).first()
    worst = WorstTeamAssignment.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'avatar':
            dn = request.form.get('display_name', '').strip()
            current_user.display_name = dn or current_user.username
            current_user.avatar_emoji = request.form.get('avatar_emoji', '👾')
            current_user.avatar_bg = request.form.get('avatar_bg', '#ff0066')
            db.session.commit()
            flash('¡Avatar actualizado!', 'success')
        elif action == 'bonus':
            if settings and settings.bonus_locked:
                flash('Las predicciones bonus están bloqueadas.', 'error')
            else:
                if not bonus:
                    bonus = BonusPrediction(user_id=current_user.id)
                    db.session.add(bonus)
                champ = request.form.get('champion_id')
                sub = request.form.get('runner_up_id')
                bonus.champion_id = int(champ) if champ else None
                bonus.runner_up_id = int(sub) if sub else None
                bonus.top_scorer_name = request.form.get('top_scorer_name', '').strip()
                db.session.commit()
                flash('¡Bonus guardado!', 'success')
        elif action == 'password':
            cur = request.form.get('current_password', '')
            new = request.form.get('new_password', '')
            new2 = request.form.get('new_password2', '')
            if not current_user.check_password(cur):
                flash('Contraseña actual incorrecta.', 'error')
            elif len(new) < 6:
                flash('Mínimo 6 caracteres.', 'error')
            elif new != new2:
                flash('Las contraseñas no coinciden.', 'error')
            else:
                current_user.set_password(new)
                db.session.commit()
                flash('¡Contraseña cambiada!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', teams=teams, settings=settings,
                           bonus=bonus, extra_bonus=extra_bonus, worst=worst)


# ─── ESPN CORNERS HELPERS ─────────────────────────────────────────────────────

def _espn_corners_from_comp(comp):
    """Extrae córners totales del objeto competition del scoreboard de ESPN."""
    total = 0
    found = False
    for competitor in comp.get('competitors', []):
        for stat in competitor.get('statistics', []):
            if stat.get('name') == 'cornerKicks':
                try:
                    total += int(float(stat.get('value', stat.get('displayValue', 0))))
                    found = True
                except (ValueError, TypeError):
                    pass
    return total if found else None


def _espn_corners_from_summary(event_id, req_lib):
    """Llama al endpoint /summary de ESPN para obtener córners cuando el scoreboard no los da."""
    url = (f'https://site.api.espn.com/apis/site/v2/sports/soccer'
           f'/fifa.world/summary?event={event_id}')
    try:
        r = req_lib.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        total = 0
        found = False
        for team in data.get('boxscore', {}).get('teams', []):
            for stat in team.get('statistics', []):
                if stat.get('name') == 'cornerKicks':
                    try:
                        total += int(float(stat.get('value', stat.get('displayValue', 0))))
                        found = True
                    except (ValueError, TypeError):
                        pass
        return total if found else None
    except Exception:
        return None


@app.route('/api/sync')
def api_sync():
    """
    Actualiza resultados y córners desde ESPN y recalcula puntos.
    Llamar con ?token=TU_TOKEN desde una tarea programada o cron-job.org.
    """
    SYNC_TOKEN = os.environ.get('SYNC_TOKEN', 'zurullo-sync-2026')
    if request.args.get('token', '') != SYNC_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        import requests as req
        now = datetime.utcnow()
        total_updated = 0
        corners_updated = 0

        for delta in [-1, 0, 1]:  # ayer, hoy, mañana
            day = now + timedelta(days=delta)
            url = (f'https://site.api.espn.com/apis/site/v2/sports/soccer'
                   f'/fifa.world/scoreboard?dates={day.strftime("%Y%m%d")}&limit=30')
            try:
                r = req.get(url, timeout=10,
                            headers={'User-Agent': 'Mozilla/5.0'})
                events = r.json().get('events', [])
            except Exception:
                continue

            for ev in events:
                try:
                    comp = ev['competitions'][0]
                    competitors = comp.get('competitors', [])
                    if len(competitors) < 2:
                        continue
                    home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                    away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])

                    status = comp.get('status', {}).get('type', {})
                    if not status.get('completed', False):
                        continue

                    score1 = int(home.get('score', ''))
                    score2 = int(away.get('score', ''))

                    # Intentar extraer córners (scoreboard primero, luego summary)
                    corners = _espn_corners_from_comp(comp)
                    if corners is None:
                        corners = _espn_corners_from_summary(ev.get('id', ''), req)

                    # Buscar partido en BD por equipos y fecha
                    from fetch_schedule import TEAM_MAP
                    n1 = TEAM_MAP.get(home['team']['displayName'], home['team']['displayName'])
                    n2 = TEAM_MAP.get(away['team']['displayName'], away['team']['displayName'])
                    t1 = Team.query.filter_by(name=n1).first()
                    t2 = Team.query.filter_by(name=n2).first()
                    if not t1 or not t2:
                        continue

                    for fmt in ('%Y-%m-%dT%H:%MZ', '%Y-%m-%dT%H:%M:%SZ'):
                        try:
                            dt = datetime.strptime(ev['date'], fmt)
                            break
                        except ValueError:
                            continue

                    match = Match.query.filter(
                        Match.team1_id == t1.id,
                        Match.team2_id == t2.id,
                        db.func.date(Match.match_date) == dt.date()
                    ).first()

                    if match and match.goals1 is None:
                        # Partido nuevo con resultado
                        match.goals1 = score1
                        match.goals2 = score2
                        match.is_locked = True
                        if corners is not None:
                            match.total_corners = corners
                        recalc_match(match)
                        total_updated += 1
                    elif match and match.result_entered and match.total_corners is None and corners is not None:
                        # Partido ya tiene resultado pero le faltaban los córners
                        match.total_corners = corners
                        settle_match_bets(match)
                        settle_match_parlays(match)
                        corners_updated += 1

                except Exception:
                    continue

        if total_updated or corners_updated:
            db.session.commit()
            if total_updated:
                recalc_worst_teams()
                for u in User.query.all():
                    grant_milestone_packs(u)
                db.session.commit()

        return jsonify({'ok': True, 'updated': total_updated,
                        'corners_updated': corners_updated,
                        'ts': now.strftime('%Y-%m-%d %H:%M UTC')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/sync-corners', methods=['POST'])
@login_required
@admin_required
def admin_sync_corners():
    """Busca córners en ESPN para todos los partidos completados que aún no los tienen."""
    try:
        import requests as req
    except ImportError:
        flash('Librería requests no disponible.', 'error')
        return redirect(url_for('admin_dashboard'))

    updated = 0
    errors = 0
    # Partidos con resultado pero sin córners, jugados en los últimos 7 días
    cutoff = datetime.utcnow() - timedelta(days=7)
    matches_no_corners = Match.query.filter(
        Match.goals1.isnot(None),
        Match.total_corners.is_(None),
        Match.match_date >= cutoff
    ).all()

    for match in matches_no_corners:
        # Buscar el evento en ESPN por fecha
        day = match.match_date
        url = (f'https://site.api.espn.com/apis/site/v2/sports/soccer'
               f'/fifa.world/scoreboard?dates={day.strftime("%Y%m%d")}&limit=30')
        try:
            r = req.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            events = r.json().get('events', [])
        except Exception:
            errors += 1
            continue

        found = False
        for ev in events:
            try:
                comp = ev['competitions'][0]
                competitors = comp.get('competitors', [])
                if len(competitors) < 2:
                    continue
                home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])

                from fetch_schedule import TEAM_MAP
                n1 = TEAM_MAP.get(home['team']['displayName'], home['team']['displayName'])
                n2 = TEAM_MAP.get(away['team']['displayName'], away['team']['displayName'])
                t1 = Team.query.filter_by(name=n1).first()
                t2 = Team.query.filter_by(name=n2).first()
                if not t1 or not t2:
                    continue
                if t1.id != match.team1_id or t2.id != match.team2_id:
                    continue

                corners = _espn_corners_from_comp(comp)
                if corners is None:
                    corners = _espn_corners_from_summary(ev.get('id', ''), req)
                if corners is not None:
                    match.total_corners = corners
                    settle_match_bets(match)
                    settle_match_parlays(match)
                    updated += 1
                    found = True
                    break
            except Exception:
                continue

        if not found:
            errors += 1

    if updated:
        db.session.commit()

    flash(f'Córners actualizados: {updated} partido(s). '
          f'Sin datos: {errors} partido(s).', 'success' if updated else 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/match/<int:match_id>/predictions')
@login_required
def match_predictions(match_id):
    match = Match.query.get_or_404(match_id)
    if not match.is_locked:
        return jsonify({'error': 'Las porras se revelan cuando empieza el partido.'}), 403
    data = []
    for p in Prediction.query.filter_by(match_id=match_id).all():
        data.append({
            'name': p.user.name,
            'emoji': p.user.avatar_emoji,
            'bg': p.user.avatar_bg,
            'g1': p.goals1,
            'g2': p.goals2,
            'pts': p.points_earned or 0
        })
    data.sort(key=lambda x: x['pts'], reverse=True)
    return jsonify({'result_entered': match.result_entered, 'predictions': data})


@app.route('/activity')
@login_required
def activity():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    all_users = User.query.all()
    feed = build_activity_feed()
    achievements = compute_achievements(current_user, all_users)
    # Collection: teams from exact predictions
    exact_preds = (Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.points_earned.in_([3, 6])).all())
    collected_ids = set()
    for p in exact_preds:
        collected_ids.add(p.match.team1_id)
        collected_ids.add(p.match.team2_id)
    collection = Team.query.filter(Team.id.in_(collected_ids)).all() if collected_ids else []
    total_teams = Team.query.count()
    # All users' achievements for the board
    all_achievements = {u.id: compute_achievements(u, all_users) for u in all_users}
    return render_template('activity.html', feed=feed, achievements=achievements,
                           collection=collection, total_teams=total_teams,
                           all_users=all_users, all_achievements=all_achievements)


@app.route('/extra-bonus', methods=['POST'])
@login_required
def save_extra_bonus():
    if not current_user.is_admin:
        flash('Las predicciones bonus están bloqueadas.', 'error')
        return redirect(url_for('profile'))
    settings = TournamentSettings.query.first()
    if settings and settings.bonus_locked:
        return jsonify({'error': 'Bonus bloqueados.'}), 400
    eb = ExtraBonusPrediction.query.filter_by(user_id=current_user.id).first()
    if not eb:
        eb = ExtraBonusPrediction(user_id=current_user.id)
        db.session.add(eb)
    mg = request.form.get('most_goals_id')
    mc = request.form.get('most_cards_id')
    dh = request.form.get('dark_horse_id')
    eb.most_goals_id = int(mg) if mg else None
    eb.most_cards_id = int(mc) if mc else None
    eb.dark_horse_id = int(dh) if dh else None
    db.session.commit()
    flash('¡Bonus extra guardado!', 'success')
    return redirect(url_for('profile'))


@app.route('/admin/edit-bonus/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_bonus(user_id):
    user = User.query.get_or_404(user_id)
    teams = Team.query.order_by(Team.name).all()
    bonus = BonusPrediction.query.filter_by(user_id=user_id).first()
    extra_bonus = ExtraBonusPrediction.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'bonus':
            if not bonus:
                bonus = BonusPrediction(user_id=user_id)
                db.session.add(bonus)
            champ = request.form.get('champion_id')
            sub = request.form.get('runner_up_id')
            bonus.champion_id = int(champ) if champ else None
            bonus.runner_up_id = int(sub) if sub else None
            bonus.top_scorer_name = request.form.get('top_scorer_name', '').strip()
            db.session.commit()
            flash(f'Bonus de {user.name} actualizados.', 'success')
        elif action == 'extra_bonus':
            if not extra_bonus:
                extra_bonus = ExtraBonusPrediction(user_id=user_id)
                db.session.add(extra_bonus)
            mg = request.form.get('most_goals_id')
            mc = request.form.get('most_cards_id')
            dh = request.form.get('dark_horse_id')
            extra_bonus.most_goals_id = int(mg) if mg else None
            extra_bonus.most_cards_id = int(mc) if mc else None
            extra_bonus.dark_horse_id = int(dh) if dh else None
            db.session.commit()
            flash(f'Bonus extra de {user.name} actualizados.', 'success')
        return redirect(url_for('admin_edit_bonus', user_id=user_id))
    return render_template('admin/edit_bonus.html', user=user, teams=teams,
                           bonus=bonus, extra_bonus=extra_bonus)


@app.route('/admin/album')
@login_required
@admin_required
def admin_album():
    """Vista admin del catálogo completo con estadísticas de colección."""
    from players_data import seed_players
    seed_players(db, Player, Team)
    rarity_order = db.case(
        (Player.rarity == 'ultra', 0), (Player.rarity == 'legendary', 1),
        (Player.rarity == 'epic', 2),  (Player.rarity == 'rare', 3),
        else_=4
    )
    all_players = Player.query.order_by(rarity_order, Player.name).all()
    total_users = User.query.count()
    # ownership count per player
    from sqlalchemy import func
    counts = dict(db.session.query(UserCard.player_id, func.count(UserCard.user_id))
                  .group_by(UserCard.player_id).all())
    rarity_stats = {}
    for r in ('ultra', 'legendary', 'epic', 'rare', 'common'):
        pl = [p for p in all_players if p.rarity == r]
        rarity_stats[r] = {'total': len(pl)}
    return render_template('admin/album.html', players=all_players,
                           counts=counts, total_users=total_users,
                           rarity_stats=rarity_stats)


@app.route('/admin/daily-bonus', methods=['POST'])
@login_required
@admin_required
def admin_daily_bonus():
    """Asigna aleatoriamente un partido bonus del día entre los próximos no jugados."""
    # Quitar bonus anterior
    Match.query.filter_by(is_daily_bonus=True).update({'is_daily_bonus': False})
    now = datetime.utcnow()
    candidates = Match.query.filter(
        Match.goals1.is_(None),
        Match.match_date >= now,
        Match.match_date <= now + timedelta(hours=48)
    ).all()
    if not candidates:
        flash('No hay partidos próximos para asignar el bonus.', 'error')
    else:
        chosen = random.choice(candidates)
        chosen.is_daily_bonus = True
        flash(f'⭐ Bonus del día: {chosen.team1.name} vs {chosen.team2.name}', 'success')
    db.session.commit()
    return redirect(url_for('admin_matches'))


# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

@app.route('/admin/')
@login_required
@admin_required
def admin_dashboard():
    settings = TournamentSettings.query.first()
    return render_template('admin/dashboard.html',
                           total_users=User.query.count(),
                           total_matches=Match.query.count(),
                           pending=Match.query.filter(Match.is_locked == True, Match.goals1.is_(None)).count(),
                           prize_pool=settings.prize_pool if settings else 0,
                           last_sync=settings.last_sync if settings else None,
                           now=datetime.utcnow())


@app.route('/admin/matches', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_matches():
    teams = Team.query.order_by(Team.name).all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            try:
                t1_id = int(request.form['team1_id'])
                t2_id = int(request.form['team2_id'])
                mdate = datetime.strptime(request.form['match_date'], '%Y-%m-%dT%H:%M')
                existing = Match.query.filter(
                    Match.team1_id == t1_id,
                    Match.team2_id == t2_id,
                    db.func.date(Match.match_date) == mdate.date()
                ).first()
                if existing:
                    flash('Ya existe un partido con esos equipos en esa fecha.', 'error')
                else:
                    m = Match(
                        phase=request.form['phase'],
                        team1_id=t1_id,
                        team2_id=t2_id,
                        match_date=mdate,
                        stadium=request.form.get('stadium', ''),
                        city=request.form.get('city', ''),
                        double_points=('double_points' in request.form),
                        match_number=int(request.form.get('match_number') or 0)
                    )
                    db.session.add(m)
                    db.session.commit()
                    flash('Partido añadido.', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'error')
        elif action == 'dedup':
            all_m = Match.query.order_by(Match.match_date, Match.id).all()
            seen = {}
            to_delete = []
            for m in all_m:
                key = (m.team1_id, m.team2_id, m.match_date.date())
                if key in seen:
                    keeper = seen[key]
                    # Preferir el que tiene resultado; si no, el de ID más bajo
                    if m.result_entered and not keeper.result_entered:
                        to_delete.append(keeper.id)
                        seen[key] = m
                    else:
                        to_delete.append(m.id)
                else:
                    seen[key] = m
            count = 0
            for mid in to_delete:
                dup = Match.query.get(mid)
                if dup:
                    Prediction.query.filter_by(match_id=dup.id).delete()
                    Bet.query.filter_by(match_id=dup.id).delete()
                    from models import ParlayLeg
                    ParlayLeg.query.filter_by(match_id=dup.id).delete()
                    db.session.delete(dup)
                    count += 1
            db.session.commit()
            flash(f'{count} partido(s) duplicado(s) eliminado(s).', 'success')
        elif action == 'delete':
            m = Match.query.get_or_404(int(request.form['match_id']))
            Prediction.query.filter_by(match_id=m.id).delete()
            db.session.delete(m)
            db.session.commit()
            flash('Partido eliminado.', 'success')
        elif action == 'toggle_lock':
            m = Match.query.get_or_404(int(request.form['match_id']))
            m.is_locked = not m.is_locked
            db.session.commit()
            flash('Bloqueo actualizado.', 'success')
        return redirect(url_for('admin_matches'))
    matches = Match.query.order_by(Match.match_date).all()
    return render_template('admin/matches.html', matches=matches, teams=teams)


@app.route('/admin/results', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_results():
    if request.method == 'POST':
        match_id = int(request.form['match_id'])
        match = Match.query.get_or_404(match_id)
        try:
            match.goals1 = int(request.form['goals1'])
            match.goals2 = int(request.form['goals2'])
            corners = (request.form.get('total_corners') or '').strip()
            match.total_corners = int(corners) if corners else None
            match.is_locked = True
            recalc_match(match)
            db.session.commit()
            recalc_worst_teams()
            for u in User.query.all():
                grant_milestone_packs(u)
            db.session.commit()
            flash(f'Resultado guardado: {match.team1.name} {match.goals1}-{match.goals2} {match.team2.name}', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'error')
        return redirect(url_for('admin_results'))
    matches = Match.query.order_by(Match.match_date.desc()).all()
    return render_template('admin/results.html', matches=matches)


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():
    worst_teams = Team.query.filter_by(is_worst=True).order_by(Team.name).all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'assign_worst':
            user_id = int(request.form['user_id'])
            team_id = int(request.form['team_id'])
            a = WorstTeamAssignment.query.filter_by(user_id=user_id).first()
            if a:
                a.team_id = team_id
            else:
                db.session.add(WorstTeamAssignment(user_id=user_id, team_id=team_id))
            db.session.commit()
            recalc_worst_teams()
            flash('Equipo peor asignado.', 'success')
        elif action == 'toggle_admin':
            user_id = int(request.form['user_id'])
            u = User.query.get_or_404(user_id)
            if u.id != current_user.id:
                u.is_admin = not u.is_admin
                db.session.commit()
                flash('Permisos actualizados.', 'success')
        return redirect(url_for('admin_users'))
    users = User.query.order_by(User.username).all()
    assignments = {a.user_id: a for a in WorstTeamAssignment.query.all()}
    return render_template('admin/users.html', users=users, worst_teams=worst_teams, assignments=assignments)


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    settings = TournamentSettings.query.first()
    if not settings:
        settings = TournamentSettings()
        db.session.add(settings)
        db.session.commit()
    teams = Team.query.order_by(Team.name).all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'lock_bonus':
            settings.bonus_locked = not settings.bonus_locked
            db.session.commit()
            flash(f'Bonus {"bloqueado" if settings.bonus_locked else "desbloqueado"}.', 'success')
        elif action == 'final':
            champ = request.form.get('champion_id')
            sub = request.form.get('runner_up_id')
            scorer = request.form.get('top_scorer_name', '').strip()
            settings.champion_id = int(champ) if champ else None
            settings.runner_up_id = int(sub) if sub else None
            settings.top_scorer_name = scorer
            db.session.commit()
            for u in User.query.all():
                b = BonusPrediction.query.filter_by(user_id=u.id).first()
                if b:
                    b.champion_points = 10 if b.champion_id and b.champion_id == settings.champion_id else 0
                    b.runner_up_points = 5 if b.runner_up_id and b.runner_up_id == settings.runner_up_id else 0
                    if scorer and b.top_scorer_name:
                        b.scorer_points = 5 if b.top_scorer_name.lower().strip() == scorer.lower() else 0
                    else:
                        b.scorer_points = 0
            db.session.commit()
            flash('Resultado final guardado y bonus calculados.', 'success')
        elif action == 'prize':
            settings.prize_pool = float(request.form.get('prize_pool') or 0)
            db.session.commit()
            flash('Bote actualizado.', 'success')
        elif action == 'extra_bonus':
            mg = request.form.get('most_goals_id')
            mc = request.form.get('most_cards_id')
            dh = request.form.get('dark_horse_id')
            settings.most_goals_id = int(mg) if mg else None
            settings.most_cards_id = int(mc) if mc else None
            settings.dark_horse_id = int(dh) if dh else None
            db.session.commit()
            # Calcular puntos extra bonus para todos los usuarios
            for u in User.query.all():
                eb = ExtraBonusPrediction.query.filter_by(user_id=u.id).first()
                if eb:
                    eb.most_goals_pts = 5 if eb.most_goals_id and eb.most_goals_id == settings.most_goals_id else 0
                    eb.most_cards_pts = 3 if eb.most_cards_id and eb.most_cards_id == settings.most_cards_id else 0
                    eb.dark_horse_pts = 5 if eb.dark_horse_id and eb.dark_horse_id == settings.dark_horse_id else 0
            db.session.commit()
            flash('Ganadores bonus extra guardados y puntos calculados.', 'success')
        elif action == 'recalc':
            for m in Match.query.filter(Match.goals1.isnot(None)).all():
                recalc_match(m)
            db.session.commit()
            recalc_worst_teams()
            for u in User.query.all():
                grant_milestone_packs(u)
            db.session.commit()
            flash('Todos los puntos recalculados.', 'success')
        elif action == 'settle_bets':
            settled = 0
            for m in Match.query.filter(Match.goals1.isnot(None)).all():
                pending_bets = Bet.query.filter_by(match_id=m.id, result=None).count()
                settle_match_bets(m)
                settle_match_parlays(m)
                settled += pending_bets
            db.session.commit()
            flash(f'Apuestas liquidadas: {settled} apuesta(s) procesada(s).', 'success')
        elif action == 'recalc_and_notify':
            notice_text = request.form.get('notice_text', '').strip()
            # Recalcular porras
            for m in Match.query.filter(Match.goals1.isnot(None)).all():
                recalc_match(m)
            db.session.commit()
            # Peores selecciones
            recalc_worst_teams()
            # Sobres por hitos
            for u in User.query.all():
                grant_milestone_packs(u)
            db.session.commit()
            # Notificar a todos los usuarios
            if notice_text:
                for u in User.query.all():
                    u.pending_notice = notice_text
                db.session.commit()
            flash(f'Recálculo completo. {User.query.count()} jugadores notificados.', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html', settings=settings, teams=teams)


@app.route('/admin/teams', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_teams():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            t = Team(
                name=request.form['name'],
                flag_emoji=request.form.get('flag_emoji', '🏳️'),
                group_letter=request.form.get('group_letter', '').upper().strip() or None,
                is_worst=('is_worst' in request.form),
                is_spain_group=('is_spain_group' in request.form)
            )
            db.session.add(t)
            db.session.commit()
            flash('Equipo añadido.', 'success')
        elif action == 'edit':
            t = Team.query.get_or_404(int(request.form['team_id']))
            t.name = request.form['name']
            t.flag_emoji = request.form.get('flag_emoji', '🏳️')
            t.group_letter = request.form.get('group_letter', '').upper().strip() or None
            t.is_worst = ('is_worst' in request.form)
            t.is_spain_group = ('is_spain_group' in request.form)
            db.session.commit()
            flash('Equipo actualizado.', 'success')
        elif action == 'delete':
            t = Team.query.get_or_404(int(request.form['team_id']))
            db.session.delete(t)
            db.session.commit()
            flash('Equipo eliminado.', 'success')
        return redirect(url_for('admin_teams'))
    teams = Team.query.order_by(Team.group_letter.nullslast(), Team.name).all()
    return render_template('admin/teams.html', teams=teams)


# ─── TIENDA DE SOBRES ─────────────────────────────────────────────────────────

@app.route('/buy-pack', methods=['POST'])
@login_required
def buy_pack():
    pack_type = request.form.get('pack_type', 'standard')
    cfg = PACK_TYPES.get(pack_type)
    if not cfg:
        flash('Tipo de sobre no válido.', 'error')
        return redirect(url_for('my_packs'))
    cost = cfg['cost']
    if current_user.coins < cost:
        flash(f'No tienes monedas suficientes. Necesitas {cost}🪙 y tienes {current_user.coins}🪙.', 'error')
        return redirect(url_for('my_packs'))
    current_user.coins_spent = (current_user.coins_spent or 0) + cost
    pack = UserPack(user_id=current_user.id, pack_type=pack_type)
    db.session.add(pack)
    db.session.commit()
    flash(f'{cfg["icon"]} ¡Sobre {cfg["name"]} comprado!', 'success')
    return redirect(url_for('my_packs'))


@app.route('/admin/daily-packs', methods=['POST'])
@login_required
@admin_required
def admin_daily_packs():
    """Entrega sobres diarios gratuitos a todos los usuarios."""
    granted = grant_daily_packs()
    flash(f'✅ {granted} sobres diarios repartidos.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/give-coins', methods=['POST'])
@login_required
@admin_required
def admin_give_coins():
    """Regala N monedas a todos los usuarios y deja un aviso pendiente (una vez)."""
    try:
        amount = int(request.form.get('amount') or 0)
    except ValueError:
        amount = 0
    if amount <= 0:
        flash('Indica una cantidad de monedas válida.', 'error')
        return redirect(url_for('admin_dashboard'))
    users = User.query.all()
    for u in users:
        u.gift_coins = (u.gift_coins or 0) + amount
        u.gift_alert = (u.gift_alert or 0) + amount
    db.session.commit()
    flash(f'🪙 {amount} monedas regaladas a {len(users)} jugadores.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/gift/ack', methods=['POST'])
@login_required
def ack_gift():
    """Marca el regalo del líder como visto para que la alerta no vuelva a salir."""
    current_user.gift_alert = 0
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/notice/ack', methods=['POST'])
@login_required
def ack_notice():
    """Marca el aviso del admin como leído."""
    current_user.pending_notice = None
    db.session.commit()
    return jsonify({'ok': True})


# ─── COLECCIÓN DE CROMOS ──────────────────────────────────────────────────────

@app.route('/collection')
@login_required
def collection():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    from players_data import seed_players
    seed_players(db, Player, Team)

    rarity = request.args.get('rarity', 'all')

    all_players = Player.query.all()
    owned_map = {uc.player_id: uc for uc in UserCard.query.filter_by(user_id=current_user.id).all()}
    owned_ids = set(owned_map.keys())

    rarity_rank = {'legendary': 0, 'epic': 1, 'rare': 2, 'common': 3}
    all_players.sort(key=lambda p: (rarity_rank.get(p.rarity, 4), 0 if p.id in owned_ids else 1, p.name))

    display = all_players if rarity == 'all' else [p for p in all_players if p.rarity == rarity]

    total = len(all_players)
    owned = len(owned_map)

    rarity_counts = {}
    for r in ('legendary', 'epic', 'rare', 'common'):
        total_r = sum(1 for p in all_players if p.rarity == r)
        owned_r = sum(1 for p in all_players if p.rarity == r and p.id in owned_ids)
        rarity_counts[r] = {'total': total_r, 'owned': owned_r}

    return render_template('collection.html',
                           players=display, owned_map=owned_map,
                           rarity=rarity, total=total, owned=owned,
                           rarity_counts=rarity_counts)


@app.route('/my-packs')
@login_required
def my_packs():
    if not current_user.onboarding_done:
        return redirect(url_for('onboarding'))
    packs = UserPack.query.filter_by(user_id=current_user.id, opened=False)\
        .order_by(UserPack.created_at.desc()).all()
    return render_template('packs.html', packs=packs)


@app.route('/open-pack/<int:pack_id>', methods=['POST'])
@login_required
def open_pack(pack_id):
    from players_data import seed_players
    seed_players(db, Player, Team)

    pack = UserPack.query.get_or_404(pack_id)
    if pack.user_id != current_user.id:
        flash('Sobre no encontrado.', 'error')
        return redirect(url_for('my_packs'))
    if pack.opened:
        flash('Este sobre ya fue abierto.', 'error')
        return redirect(url_for('my_packs'))

    cfg = PACK_TYPES.get(pack.pack_type) or PACK_TYPES['standard']
    cards = draw_cards(cfg['cards'], rarity_weights=cfg['weights'], guaranteed=cfg.get('guaranteed'))
    result = []
    for player in cards:
        uc = UserCard.query.filter_by(user_id=current_user.id, player_id=player.id).first()
        is_new = uc is None
        if uc:
            uc.duplicate_count += 1
        else:
            uc = UserCard(user_id=current_user.id, player_id=player.id)
            db.session.add(uc)
        result.append({
            'id': player.id,
            'name': player.name,
            'rarity': player.rarity,
            'icon': player.icon,
            'position': player.position,
            'card_type': player.card_type,
            'team': player.team.name if player.team else '',
            'flag_img': player.team.flag_img if player.team else '',
            'flag_emoji': player.team.flag_emoji if player.team else '',
            'image': player.image or '',
            'is_new': is_new,
        })

    pack.opened = True
    pack.opened_at = datetime.utcnow()
    db.session.commit()
    return render_template('pack_open.html', cards=result, pack=pack)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not TournamentSettings.query.first():
            db.session.add(TournamentSettings())
            db.session.commit()
        # Migración SQLite: añadir columnas nuevas si no existen
        from sqlalchemy import text
        with db.engine.connect() as conn:
            for sql in [
                "ALTER TABLE users ADD COLUMN bet_winnings INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN gift_coins INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN gift_alert INTEGER DEFAULT 0",
                "ALTER TABLE matches ADD COLUMN total_corners INTEGER",
            ]:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                except Exception:
                    pass  # columna ya existe
        print('Base de datos lista.')
    print('ZURULLO WORLD CUP arrancando en http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
