"""
Kinesis AI - REST API Endpoints
Real-time pose analysis, calibration checks, session persistence, voice coach chat, AI training analysis, and gamification rewards.
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user
from models import db, Workout, SportsSession, InjuryRiskRecord, UserProgress
from pose_detection import check_calibration, FitnessAnalyzer
from football_analyzer import FootballAnalyzer
from cricket_analyzer import CricketAnalyzer
from sports_drills import DrillAnalyzer
from injury_risk_engine import InjuryRiskEngine
from yoga_service import YogaPoseAnalyzer
from voice_service import process_voice_query
from gamification import GamificationEngine
from google_fit_service import GoogleFitService
from ai_provider import get_ai

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Active analyzer state per session (keyed by session_token or type)
fitness_analyzers = {}
football_analyzers = {}
cricket_analyzers = {}
drill_analyzers = {}
injury_engines = {}


class LandmarkPoint:
    """Helper to convert JSON landmark dict to object with .x, .y, .z, .visibility attributes."""
    def __init__(self, data):
        self.x = data.get('x', 0.0)
        self.y = data.get('y', 0.0)
        self.z = data.get('z', 0.0)
        self.visibility = data.get('visibility', 1.0)


def parse_landmarks(raw_landmarks):
    """Parse list of landmark dicts into list of LandmarkPoint objects."""
    return [LandmarkPoint(lm) for lm in raw_landmarks]


# ============================================================
# Calibration & System Status
# ============================================================

@api_bp.route('/status', methods=['GET'])
def system_status():
    """Check AI provider availability and backend status."""
    ai = get_ai()
    status = ai.get_status()
    return jsonify({
        'status': 'healthy',
        'ai': status,
        'version': '2.0.0 (SIH 2026 Edition)'
    })


@api_bp.route('/calibration', methods=['POST'])
def check_camera_calibration():
    """Verify full-body visibility and posture before session starts."""
    data = request.get_json() or {}
    raw_landmarks = data.get('landmarks', [])
    if len(raw_landmarks) < 33:
        return jsonify({'calibrated': False, 'messages': ['Stand where your full body is visible.']})

    landmarks = parse_landmarks(raw_landmarks)
    is_calibrated, messages = check_calibration(landmarks)
    return jsonify({
        'calibrated': is_calibrated,
        'messages': messages
    })


# ============================================================
# Fitness Real-Time Analysis & Save
# ============================================================

@api_bp.route('/fitness/analyze', methods=['POST'])
def analyze_fitness_frame():
    """Analyze a single video frame for a fitness exercise."""
    data = request.get_json() or {}
    exercise = data.get('exercise', 'pushup')
    session_id = data.get('session_id', 'default')
    raw_landmarks = data.get('landmarks', [])

    if len(raw_landmarks) < 33:
        return jsonify({'error': 'Insufficient landmarks'}), 400

    landmarks = parse_landmarks(raw_landmarks)

    # Get or create analyzer
    key = f"{session_id}_{exercise}"
    if key not in fitness_analyzers:
        fitness_analyzers[key] = FitnessAnalyzer(exercise_type=exercise)
    analyzer = fitness_analyzers[key]

    result = analyzer.analyze_frame(landmarks)

    # Also run movement risk evaluation
    if session_id not in injury_engines:
        injury_engines[session_id] = InjuryRiskEngine()
    risk_info = injury_engines[session_id].analyze(landmarks, sport='fitness')

    return jsonify({
        'form_score': result.form_score,
        'rep_counted': result.rep_counted,
        'quality_rep': result.quality_rep,
        'current_reps': analyzer.rep_state.count,
        'quality_reps': analyzer.rep_state.quality_count,
        'avg_form_score': analyzer.rep_state.avg_form_score,
        'fatigue_level': result.fatigue_level,
        'corrections': result.corrections,
        'positives': result.positives,
        'metrics': result.metrics,
        'risk': risk_info
    })


@api_bp.route('/fitness/save', methods=['POST'])
def save_fitness_session():
    """Save completed fitness workout to DB, update XP, check badges."""
    data = request.get_json() or {}
    exercise_type = data.get('exercise_type', 'pushup')
    reps = int(data.get('reps', 0))
    quality_reps = int(data.get('quality_reps', 0))
    duration = float(data.get('duration', 0.0))
    form_score = float(data.get('form_score', 0.0))
    fatigue_level = data.get('fatigue_level', 'low')
    metrics = data.get('metrics', {})

    # Calculate calories estimated
    cal_per_rep = {'pushup': 0.6, 'squat': 0.7, 'lunge': 0.5, 'jumping_jack': 0.3, 'plank': 0.15}
    calories = round(reps * cal_per_rep.get(exercise_type, 0.5) + (duration / 60.0) * 4.0, 1)

    user_id = current_user.id if current_user.is_authenticated else None
    xp_earned = 0
    new_badges = []
    level_up = False

    if user_id:
        gamification = GamificationEngine(db.session)
        xp_earned = gamification.calculate_xp(
            form_score=form_score,
            reps=reps,
            quality_reps=quality_reps,
            duration=duration,
            sport='fitness'
        )

        workout = Workout(
            user_id=user_id,
            exercise_type=exercise_type,
            reps=reps,
            quality_reps=quality_reps,
            duration=duration,
            form_score=form_score,
            calories_estimated=calories,
            fatigue_level=fatigue_level,
            xp_earned=xp_earned
        )
        workout.metrics = metrics
        db.session.add(workout)

        # Update user XP
        level_up = current_user.add_xp(xp_earned)
        db.session.commit()

        # Check badges
        new_badges = gamification.check_badges(user_id, {
            'exercise_type': exercise_type,
            'reps': reps,
            'quality_reps': quality_reps,
            'form_score': form_score,
            'duration': duration
        })

        # Sync to Google Fit / Local Health
        fit_svc = GoogleFitService()
        fit_svc.sync_workout(user_id, workout.to_dict())

    return jsonify({
        'status': 'success',
        'xp_earned': xp_earned,
        'level_up': level_up,
        'new_badges': new_badges,
        'calories_estimated': calories
    })


# ============================================================
# Football Real-Time Analysis & Save
# ============================================================

@api_bp.route('/football/analyze', methods=['POST'])
def analyze_football_frame():
    """Analyze a single video frame for football skill."""
    data = request.get_json() or {}
    skill = data.get('skill', 'shooting')  # shooting, dribbling, agility
    session_id = data.get('session_id', 'fb_default')
    style = data.get('style_inspiration', 'technical_dribbler')
    raw_landmarks = data.get('landmarks', [])

    if len(raw_landmarks) < 33:
        return jsonify({'error': 'Insufficient landmarks'}), 400

    landmarks = parse_landmarks(raw_landmarks)

    key = f"{session_id}_{skill}"
    if key not in football_analyzers:
        football_analyzers[key] = FootballAnalyzer()
    analyzer = football_analyzers[key]

    if skill == 'shooting':
        result = analyzer.analyze_shooting(landmarks)
    elif skill == 'dribbling':
        result = analyzer.analyze_dribbling(landmarks)
    elif skill == 'agility':
        result = analyzer.analyze_agility(landmarks, drill_type=data.get('drill_type', 'side_shuffle'))
    else:
        result = analyzer.analyze_shooting(landmarks)

    # Risk evaluation
    if session_id not in injury_engines:
        injury_engines[session_id] = InjuryRiskEngine()
    risk_info = injury_engines[session_id].analyze(landmarks, sport='football')

    style_coaching = analyzer.get_style_coaching(style)

    return jsonify({
        'score': result.form_score,
        'positives': result.positives,
        'corrections': result.corrections,
        'metrics': result.metrics,
        'fatigue_level': result.fatigue_level,
        'risk': risk_info,
        'style_coaching': style_coaching
    })


# ============================================================
# Cricket Real-Time Analysis & Save
# ============================================================

@api_bp.route('/cricket/analyze', methods=['POST'])
def analyze_cricket_frame():
    """Analyze a single video frame for cricket shot or bowling."""
    data = request.get_json() or {}
    skill = data.get('skill', 'pull_shot')
    session_id = data.get('session_id', 'cric_default')
    kohli_mode = bool(data.get('kohli_mode', False))
    raw_landmarks = data.get('landmarks', [])

    if len(raw_landmarks) < 33:
        return jsonify({'error': 'Insufficient landmarks'}), 400

    landmarks = parse_landmarks(raw_landmarks)

    key = f"{session_id}_{skill}"
    if key not in cricket_analyzers:
        cricket_analyzers[key] = CricketAnalyzer()
    analyzer = cricket_analyzers[key]

    if skill == 'pull_shot':
        result = analyzer.analyze_pull_shot(landmarks)
    elif skill == 'cover_drive':
        result = analyzer.analyze_cover_drive(landmarks, kohli_mode=kohli_mode)
    elif skill == 'straight_drive':
        result = analyzer.analyze_straight_drive(landmarks)
    elif skill == 'batting_stance':
        result = analyzer.analyze_batting_stance(landmarks)
    elif skill == 'bowling':
        result = analyzer.analyze_bowling(landmarks)
    else:
        result = analyzer.analyze_pull_shot(landmarks)

    if session_id not in injury_engines:
        injury_engines[session_id] = InjuryRiskEngine()
    risk_info = injury_engines[session_id].analyze(landmarks, sport='cricket')

    return jsonify({
        'score': result.form_score,
        'positives': result.positives,
        'corrections': result.corrections,
        'metrics': result.metrics,
        'fatigue_level': result.fatigue_level,
        'risk': risk_info
    })


# ============================================================
# Sports Session Save Endpoint
# ============================================================

@api_bp.route('/sports/save', methods=['POST'])
def save_sports_session():
    """Save sports drill / technique session to DB."""
    data = request.get_json() or {}
    sport = data.get('sport', 'football')
    skill = data.get('sport_skill', 'shooting')
    drill_type = data.get('drill_type', 'technique')
    score = float(data.get('score', 0.0))
    duration = float(data.get('duration', 0.0))
    reps = int(data.get('reps', 0))
    risk_level = data.get('risk_level', 'low')
    style_inspiration = data.get('style_inspiration', '')
    breakdown = data.get('breakdown', {})
    feedback = data.get('feedback', [])
    metrics = data.get('metrics', {})

    user_id = current_user.id if current_user.is_authenticated else None
    xp_earned = 0
    new_badges = []
    level_up = False

    if user_id:
        gamification = GamificationEngine(db.session)
        xp_earned = gamification.calculate_xp(
            form_score=score,
            reps=reps,
            quality_reps=reps,
            duration=duration,
            sport=sport
        )

        session_obj = SportsSession(
            user_id=user_id,
            sport=sport,
            sport_skill=skill,
            drill_type=drill_type,
            score=score,
            duration=duration,
            reps=reps,
            risk_level=risk_level,
            style_inspiration=style_inspiration,
            xp_earned=xp_earned
        )
        session_obj.breakdown = breakdown
        session_obj.feedback = feedback
        session_obj.metrics = metrics
        db.session.add(session_obj)

        level_up = current_user.add_xp(xp_earned)
        db.session.commit()

        # Save movement risk record if moderate/high
        if risk_level in ('moderate', 'high'):
            risk_rec = InjuryRiskRecord(
                user_id=user_id,
                session_type='sports',
                session_id=session_obj.id,
                risk_level=risk_level,
                risk_score=round(100.0 - score, 1),
                sport=sport
            )
            risk_rec.indicators = feedback
            db.session.add(risk_rec)
            db.session.commit()

        # Badge checks
        new_badges = gamification.check_badges(user_id, {
            'sport': sport,
            'sport_skill': skill,
            'score': score,
            'duration': duration,
            'reps': reps
        })

        # Sync to external health
        fit_svc = GoogleFitService()
        fit_svc.sync_sports_session(user_id, session_obj.to_dict())

    return jsonify({
        'status': 'success',
        'xp_earned': xp_earned,
        'level_up': level_up,
        'new_badges': new_badges
    })


# ============================================================
# Yoga Real-Time Analysis
# ============================================================

@api_bp.route('/yoga/analyze', methods=['POST'])
def analyze_yoga_frame():
    """Analyze a single video frame for yoga posture."""
    data = request.get_json() or {}
    pose_key = data.get('pose', 'warrior_2')
    raw_landmarks = data.get('landmarks', [])

    if len(raw_landmarks) < 33:
        return jsonify({'error': 'Insufficient landmarks'}), 400

    landmarks = parse_landmarks(raw_landmarks)
    analyzer = YogaPoseAnalyzer(pose_type=pose_key)
    analysis = analyzer.analyze(landmarks)

    return jsonify(analysis)


# ============================================================
# Bilingual Voice Coach API
# ============================================================

@api_bp.route('/voice/chat', methods=['POST'])
def voice_coach_chat():
    """Process user voice transcription and return spoken coaching response."""
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    context = data.get('context', {})

    res = process_voice_query(query=query, context=context)
    return jsonify(res)


# ============================================================
# Post-Session AI Coach Deep Dive
# ============================================================

@api_bp.route('/ai/session-coach', methods=['POST'])
def ai_session_coach():
    """Generate in-depth post-session personalized training advice."""
    data = request.get_json() or {}
    ai = get_ai()
    analysis = ai.analyze_session(data)
    return jsonify(analysis)
