from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from extensions to avoid circular imports
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    fitness_level = db.Column(db.String(20), default='beginner')
    fitness_goals = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exercise_type = db.Column(db.String(50))
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    reps_completed = db.Column(db.Integer)
    form_score = db.Column(db.Float)
    difficulty = db.Column(db.String(20), default='medium')
    notes = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('workouts', lazy=True, cascade='all, delete-orphan'))


class UserStats(db.Model):
    """Cumulative gamification state, one row per user."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_workout_date = db.Column(db.Date, nullable=True)
    badges = db.Column(db.Text, default='[]')  # JSON list of badge ids earned

    user = db.relationship('User', backref=db.backref('stats', uselist=False, cascade='all, delete-orphan'))


class InjuryRiskLog(db.Model):
    """One row per session risk assessment, so trend can be tracked over weeks."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_type = db.Column(db.String(50))
    risk_level = db.Column(db.String(20))  # low / moderate / high
    risk_score = db.Column(db.Float)       # 0-100
    note = db.Column(db.Text)
    drill = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('injury_logs', lazy=True, cascade='all, delete-orphan'))
