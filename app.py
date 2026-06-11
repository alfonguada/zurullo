from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from markupsafe import Markup
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import os

from models import db, User, Team, Match, Prediction, BonusPrediction, WorstTeamAssignment, TournamentSettings

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zurullo-wc-2026-secret')
_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zurullo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
                                         match.double_points)


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
        assignment.points_earned = gf + (ga // 3)
    db.session.commit()


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
            is_first = User.query.count() == 0
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
            return jsonify({'ok': True, 'redirect': url_for('dashboard')})
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
    return render_template('profile.html', teams=teams, settings=settings, bonus=bonus, worst=worst)


@app.route('/api/sync')
def api_sync():
    """
    Actualiza resultados desde ESPN y recalcula puntos.
    Llamar con ?token=TU_TOKEN desde una tarea programada o cron-job.org.
    """
    SYNC_TOKEN = os.environ.get('SYNC_TOKEN', 'zurullo-sync-2026')
    if request.args.get('token', '') != SYNC_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        import requests as req
        now = datetime.utcnow()
        total_updated = 0

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
                        match.goals1 = score1
                        match.goals2 = score2
                        match.is_locked = True
                        recalc_match(match)
                        total_updated += 1

                except Exception:
                    continue

        if total_updated:
            db.session.commit()
            recalc_worst_teams()

        return jsonify({'ok': True, 'updated': total_updated,
                        'ts': now.strftime('%Y-%m-%d %H:%M UTC')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/match/<int:match_id>/predictions')
@login_required
def match_predictions(match_id):
    match = Match.query.get_or_404(match_id)
    if not match.result_entered:
        return jsonify({'error': 'Resultado no disponible aún.'}), 403
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
    return jsonify(data)


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
                m = Match(
                    phase=request.form['phase'],
                    team1_id=int(request.form['team1_id']),
                    team2_id=int(request.form['team2_id']),
                    match_date=datetime.strptime(request.form['match_date'], '%Y-%m-%dT%H:%M'),
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
            match.is_locked = True
            recalc_match(match)
            db.session.commit()
            recalc_worst_teams()
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
        elif action == 'recalc':
            for m in Match.query.filter(Match.goals1.isnot(None)).all():
                recalc_match(m)
            db.session.commit()
            recalc_worst_teams()
            flash('Todos los puntos recalculados.', 'success')
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not TournamentSettings.query.first():
            db.session.add(TournamentSettings())
            db.session.commit()
        print('Base de datos lista.')
    print('ZURULLO WORLD CUP arrancando en http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
