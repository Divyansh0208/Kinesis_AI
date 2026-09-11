"""
Kinesis AI - Core Routes
Handles auth (login, register, logout), main pages, fitness exercises, yoga, diet, voice coach, and profile.
"""

from datetime import datetime, timezone, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Workout, SportsSession, Achievement, InjuryRiskRecord, TrainingPlan, UserProgress
from gamification import GamificationEngine
from diet_service import generate_diet_plan, calculate_bmr, calculate_tdee, get_macro_split
from yoga_service import YOGA_POSES
from ai_provider import get_ai

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage: 'Your Webcam. Your Movement. Your AI Coach.' with 6 core pillars."""
    ai_status = get_ai().get_status()
    return render_template('index.html', ai_status=ai_status)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        fitness_level = request.form.get('fitness_level', 'beginner')
        preferred_sport = request.form.get('preferred_sport', 'fitness')

        if not username or not email or not password:
            flash('Please fill in all required fields.', 'warning')
            return render_template('register.html')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already registered.', 'danger')
            return render_template('register.html')

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            fitness_level=fitness_level,
            preferred_sport=preferred_sport
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Award welcome badge
        gamification = GamificationEngine(db.session)
        gamification.check_badges(user.id, {'event': 'register'})

        login_user(user)
        flash('Account created successfully! Welcome to Kinesis AI.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            user.update_streak()
            db.session.commit()
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
def dashboard():
    """Unified Dashboard: Fitness, Sports, Progress, Injury Risk, Gamification."""
    user = current_user if current_user.is_authenticated else None
    user_id = user.id if user else None

    # Load stats
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.created_at.desc()).limit(10).all() if user_id else []
    sports_sessions = SportsSession.query.filter_by(user_id=user_id).order_by(SportsSession.created_at.desc()).limit(10).all() if user_id else []
    risk_records = InjuryRiskRecord.query.filter_by(user_id=user_id).order_by(InjuryRiskRecord.created_at.desc()).limit(5).all() if user_id else []
    achievements = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.earned_at.desc()).all() if user_id else []

    # Calculate aggregate summary
    total_reps = sum(w.reps for w in workouts)
    total_quality_reps = sum(w.quality_reps for w in workouts)
    avg_fitness_score = round(sum(w.form_score for w in workouts) / len(workouts), 1) if workouts else 0.0
    avg_sports_score = round(sum(s.score for s in sports_sessions) / len(sports_sessions), 1) if sports_sessions else 0.0

    gamification = GamificationEngine(db.session)
    level_info = gamification.get_user_level(user.xp if user else 0)

    ai_status = get_ai().get_status()

    return render_template(
        'dashboard.html',
        user=user,
        workouts=workouts,
        sports_sessions=sports_sessions,
        risk_records=risk_records,
        achievements=achievements,
        total_reps=total_reps,
        total_quality_reps=total_quality_reps,
        avg_fitness_score=avg_fitness_score,
        avg_sports_score=avg_sports_score,
        level_info=level_info,
        ai_status=ai_status
    )


@main_bp.route('/workout')
def workout():
    """Fitness exercise selection hub."""
    return render_template('workout.html')


@main_bp.route('/workout/<exercise_type>')
def exercise_view(exercise_type):
    """Live exercise webcam training room."""
    valid_exercises = {
        'pushup': {'title': 'Push-Up Analysis', 'desc': 'Track elbow angle, body alignment, depth & rep quality.'},
        'squat': {'title': 'Squat Analysis', 'desc': 'Analyze knee depth, torso lean, hip angles & symmetry.'},
        'lunge': {'title': 'Lunge Analysis', 'desc': 'Evaluate 90° knee angle, balance, and spine verticality.'},
        'plank': {'title': 'Plank Hold Analysis', 'desc': 'Measure core alignment, hip sagging, and holding stability.'},
        'jumping_jack': {'title': 'Jumping Jack Analysis', 'desc': 'Track arm extension, leg spread cadence, and tempo.'}
    }

    if exercise_type not in valid_exercises:
        flash('Invalid exercise selected.', 'warning')
        return redirect(url_for('main.workout'))

    info = valid_exercises[exercise_type]
    return render_template('exercise.html', exercise_type=exercise_type, title=info['title'], desc=info['desc'])


@main_bp.route('/yoga')
def yoga():
    """Yoga postures hub."""
    return render_template('yoga.html', poses=YOGA_POSES)


@main_bp.route('/yoga/<pose_key>')
def yoga_pose_view(pose_key):
    """Live yoga pose guidance room."""
    if pose_key not in YOGA_POSES:
        flash('Unknown yoga posture.', 'warning')
        return redirect(url_for('main.yoga'))
    pose_info = YOGA_POSES[pose_key]
    return render_template('yoga_view.html', pose_key=pose_key, pose=pose_info)


@main_bp.route('/diet', methods=['GET', 'POST'])
def diet():
    """AI Diet and Nutrition planner."""
    diet_plan_result = None
    macro_data = None

    if request.method == 'POST':
        age = int(request.form.get('age', 22) or 22)
        weight = float(request.form.get('weight', 70) or 70)
        height = float(request.form.get('height', 175) or 175)
        gender = request.form.get('gender', 'male')
        goal = request.form.get('goal', 'maintain')
        activity = request.form.get('activity', 'moderate')
        dietary_prefs = request.form.get('dietary_prefs', 'Indian Standard / Balanced')

        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        macro_data = get_macro_split(tdee, goal)

        user_profile = {
            'age': age,
            'weight': weight,
            'height': height,
            'gender': gender,
            'activity_level': activity,
            'dietary_preferences': dietary_prefs
        }
        diet_plan_result = generate_diet_plan(user_profile, goal)

    return render_template('diet.html', diet_plan=diet_plan_result, macro_data=macro_data)


@main_bp.route('/voice')
def voice():
    """Bilingual Hindi + English Voice Coach."""
    ai_status = get_ai().get_status()
    return render_template('voice.html', ai_status=ai_status)


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management."""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.age = int(request.form.get('age', current_user.age or 22) or 22)
        current_user.weight = float(request.form.get('weight', current_user.weight or 70) or 70)
        current_user.height = float(request.form.get('height', current_user.height or 175) or 175)
        current_user.fitness_level = request.form.get('fitness_level', current_user.fitness_level)
        current_user.preferred_sport = request.form.get('preferred_sport', current_user.preferred_sport)
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return render_template('profile.html', user=current_user)
