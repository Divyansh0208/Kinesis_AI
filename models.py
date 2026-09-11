"""
Kinesis AI - Database Models
SQLAlchemy models for users, workouts, sports sessions, achievements, and progress tracking.
SQLite for development, PostgreSQL-compatible.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account with authentication and profile."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default='')
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    fitness_level = db.Column(db.String(20), default='beginner')  # beginner/intermediate/advanced
    preferred_sport = db.Column(db.String(30), default='')
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workouts = db.relationship('Workout', backref='user', lazy='dynamic')
    sports_sessions = db.relationship('SportsSession', backref='user', lazy='dynamic')
    achievements = db.relationship('Achievement', backref='user', lazy='dynamic')
    training_plans = db.relationship('TrainingPlan', backref='user', lazy='dynamic')
    injury_risk_records = db.relationship('InjuryRiskRecord', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_xp(self, amount):
        """Add XP and handle level-ups. Returns True if leveled up."""
        self.xp += amount
        new_level = 1 + self.xp // 500  # Level up every 500 XP
        leveled_up = new_level > self.level
        self.level = new_level
        return leveled_up

    def update_streak(self):
        """Update login streak. Call once per active day."""
        now = datetime.now(timezone.utc)
        if self.last_active:
            delta = (now.date() - self.last_active.date()).days
            if delta == 1:
                self.streak_days += 1
            elif delta > 1:
                self.streak_days = 1
            # delta == 0: same day, no change
        else:
            self.streak_days = 1
        self.last_active = now

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'fitness_level': self.fitness_level,
            'xp': self.xp,
            'level': self.level,
            'streak_days': self.streak_days,
            'preferred_sport': self.preferred_sport,
        }


class Workout(db.Model):
    """Fitness exercise session (push-ups, squats, etc.)."""
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exercise_type = db.Column(db.String(50), nullable=False)  # pushup, squat, lunge, plank, jumping_jack
    reps = db.Column(db.Integer, default=0)
    quality_reps = db.Column(db.Integer, default=0)
    duration = db.Column(db.Float, default=0.0)  # seconds
    form_score = db.Column(db.Float, default=0.0)  # 0-100
    calories_estimated = db.Column(db.Float, default=0.0)
    avg_tempo = db.Column(db.Float, default=0.0)  # seconds per rep
    fatigue_level = db.Column(db.String(20), default='low')  # low/moderate/high
    metrics_json = db.Column(db.Text, default='{}')  # Detailed metrics as JSON
    xp_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def metrics(self):
        try:
            return json.loads(self.metrics_json) if self.metrics_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @metrics.setter
    def metrics(self, value):
        self.metrics_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'exercise_type': self.exercise_type,
            'reps': self.reps,
            'quality_reps': self.quality_reps,
            'duration': self.duration,
            'form_score': self.form_score,
            'calories_estimated': self.calories_estimated,
            'fatigue_level': self.fatigue_level,
            'xp_earned': self.xp_earned,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SportsSession(db.Model):
    """Sports training session (football, cricket drills)."""
    __tablename__ = 'sports_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sport = db.Column(db.String(30), nullable=False)  # football, cricket
    sport_skill = db.Column(db.String(50), nullable=False)  # shooting, dribbling, pull_shot, cover_drive...
    drill_type = db.Column(db.String(50), default='')  # agility, technique, etc.
    score = db.Column(db.Float, default=0.0)  # 0-100
    duration = db.Column(db.Float, default=0.0)  # seconds
    reps = db.Column(db.Integer, default=0)
    risk_level = db.Column(db.String(20), default='low')  # low/moderate/high
    style_inspiration = db.Column(db.String(50), default='')  # e.g. "Technical Dribbler"
    breakdown_json = db.Column(db.Text, default='{}')  # Score breakdown
    feedback_json = db.Column(db.Text, default='[]')  # Feedback items
    metrics_json = db.Column(db.Text, default='{}')  # Detailed metrics
    xp_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def breakdown(self):
        try:
            return json.loads(self.breakdown_json) if self.breakdown_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @breakdown.setter
    def breakdown(self, value):
        self.breakdown_json = json.dumps(value)

    @property
    def feedback(self):
        try:
            return json.loads(self.feedback_json) if self.feedback_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    @feedback.setter
    def feedback(self, value):
        self.feedback_json = json.dumps(value)

    @property
    def metrics(self):
        try:
            return json.loads(self.metrics_json) if self.metrics_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @metrics.setter
    def metrics(self, value):
        self.metrics_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'sport': self.sport,
            'sport_skill': self.sport_skill,
            'drill_type': self.drill_type,
            'score': self.score,
            'duration': self.duration,
            'reps': self.reps,
            'risk_level': self.risk_level,
            'style_inspiration': self.style_inspiration,
            'breakdown': self.breakdown,
            'feedback': self.feedback,
            'metrics': self.metrics,
            'xp_earned': self.xp_earned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class MovementMetric(db.Model):
    """Individual movement metric data point."""
    __tablename__ = 'movement_metrics'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_type = db.Column(db.String(20), nullable=False)  # workout / sports
    session_id = db.Column(db.Integer, nullable=False)
    metric_name = db.Column(db.String(50), nullable=False)  # joint_angle, symmetry, stability...
    metric_value = db.Column(db.Float, nullable=False)
    body_part = db.Column(db.String(30), default='')
    side = db.Column(db.String(10), default='')  # left/right/center
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class FormScore(db.Model):
    """Time-series form score tracking within a session."""
    __tablename__ = 'form_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_type = db.Column(db.String(20), nullable=False)
    session_id = db.Column(db.Integer, nullable=False)
    rep_number = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, nullable=False)  # 0-100
    details_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def details(self):
        try:
            return json.loads(self.details_json) if self.details_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @details.setter
    def details(self, value):
        self.details_json = json.dumps(value)


class InjuryRiskRecord(db.Model):
    """Movement-risk indicator record (NOT medical diagnosis)."""
    __tablename__ = 'injury_risk_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_type = db.Column(db.String(20), nullable=False)
    session_id = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # low/moderate/high
    risk_score = db.Column(db.Float, default=0.0)  # 0-100
    sport = db.Column(db.String(30), default='general')
    indicators_json = db.Column(db.Text, default='[]')  # List of risk indicators
    body_areas_json = db.Column(db.Text, default='[]')  # Affected body areas
    recommendations_json = db.Column(db.Text, default='[]')  # Safety recommendations
    disclaimer = db.Column(db.String(200),
                           default='This is a movement-risk indicator, not a medical diagnosis.')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def indicators(self):
        try:
            return json.loads(self.indicators_json) if self.indicators_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    @indicators.setter
    def indicators(self, value):
        self.indicators_json = json.dumps(value)

    @property
    def body_areas(self):
        try:
            return json.loads(self.body_areas_json) if self.body_areas_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    @body_areas.setter
    def body_areas(self, value):
        self.body_areas_json = json.dumps(value)

    @property
    def recommendations(self):
        try:
            return json.loads(self.recommendations_json) if self.recommendations_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    @recommendations.setter
    def recommendations(self, value):
        self.recommendations_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'sport': self.sport,
            'indicators': self.indicators,
            'body_areas': self.body_areas,
            'recommendations': self.recommendations,
            'disclaimer': self.disclaimer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TrainingPlan(db.Model):
    """AI-generated training plan."""
    __tablename__ = 'training_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan_type = db.Column(db.String(30), nullable=False)  # fitness / football / cricket
    sport = db.Column(db.String(30), default='general')
    position = db.Column(db.String(30), default='')
    skill_level = db.Column(db.String(20), default='beginner')
    goal = db.Column(db.String(50), default='')
    equipment = db.Column(db.String(30), default='none')
    plan_json = db.Column(db.Text, default='{}')  # Full training plan
    duration_weeks = db.Column(db.Integer, default=4)
    ai_provider = db.Column(db.String(20), default='')  # ollama / gemini
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def plan(self):
        try:
            return json.loads(self.plan_json) if self.plan_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @plan.setter
    def plan(self, value):
        self.plan_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'plan_type': self.plan_type,
            'sport': self.sport,
            'position': self.position,
            'skill_level': self.skill_level,
            'goal': self.goal,
            'duration_weeks': self.duration_weeks,
            'ai_provider': self.ai_provider,
            'is_active': self.is_active,
            'plan': self.plan,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Achievement(db.Model):
    """Gamification badges and achievements."""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    badge_id = db.Column(db.String(50), nullable=False)  # Unique badge identifier
    badge_name = db.Column(db.String(100), nullable=False)
    badge_description = db.Column(db.String(200), default='')
    badge_icon = db.Column(db.String(10), default='🏆')  # Emoji icon
    category = db.Column(db.String(30), default='general')  # fitness/football/cricket/streak/form
    xp_reward = db.Column(db.Integer, default=0)
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Ensure a user can only earn each badge once
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),)

    def to_dict(self):
        return {
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'badge_icon': self.badge_icon,
            'category': self.category,
            'xp_reward': self.xp_reward,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
        }


class UserProgress(db.Model):
    """Daily progress summary for dashboard charts."""
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    total_workouts = db.Column(db.Integer, default=0)
    total_sports_sessions = db.Column(db.Integer, default=0)
    total_reps = db.Column(db.Integer, default=0)
    avg_form_score = db.Column(db.Float, default=0.0)
    total_xp = db.Column(db.Integer, default=0)
    total_duration = db.Column(db.Float, default=0.0)  # minutes
    risk_level = db.Column(db.String(20), default='low')
    summary_json = db.Column(db.Text, default='{}')

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='uq_user_date'),)

    @property
    def summary(self):
        try:
            return json.loads(self.summary_json) if self.summary_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    @summary.setter
    def summary(self, value):
        self.summary_json = json.dumps(value)
