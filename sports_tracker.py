"""
Kinesis AI - Sports Support Modules
Sports tracker, drills, and scoring engine.
"""

# ============================================================
# sports_tracker.py - Sports Session Management
# ============================================================

import time
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SportsSessionTracker:
    """Manages a live sports training session lifecycle."""

    def __init__(self, sport, skill, user_id=None):
        self.sport = sport
        self.skill = skill
        self.user_id = user_id
        self.start_time = time.time()
        self.end_time = None
        self.is_active = True
        self.scores = []
        self.reps = 0
        self.metrics_history = []
        self.feedback_history = []
        self.risk_history = []
        self.style_inspiration = ''
        self.calibrated = False

    def start(self):
        """Begin a new session."""
        self.start_time = time.time()
        self.is_active = True
        self.scores = []
        self.reps = 0
        self.metrics_history = []
        self.feedback_history = []

    def record_frame(self, analysis_result):
        """Record analysis result from a single frame."""
        if not self.is_active:
            return

        if analysis_result.form_score > 0:
            self.scores.append(analysis_result.form_score)

        if analysis_result.rep_counted:
            self.reps += 1

        if analysis_result.metrics:
            self.metrics_history.append(analysis_result.metrics)

        if analysis_result.corrections:
            self.feedback_history.extend(analysis_result.corrections)

        if analysis_result.risk_indicators:
            self.risk_history.extend(analysis_result.risk_indicators)

    def end(self):
        """End the session and compute final stats."""
        self.end_time = time.time()
        self.is_active = False
        return self.get_summary()

    def get_summary(self):
        """Get session summary."""
        duration = (self.end_time or time.time()) - self.start_time
        avg_score = sum(self.scores) / len(self.scores) if self.scores else 0

        # Aggregate risk level
        risk_count = len(self.risk_history)
        if risk_count > 10:
            risk_level = 'high'
        elif risk_count > 3:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

        # Get top feedback (most common corrections)
        from collections import Counter
        feedback_counts = Counter(self.feedback_history)
        top_feedback = [item for item, _ in feedback_counts.most_common(5)]

        return {
            'sport': self.sport,
            'skill': self.skill,
            'score': round(avg_score, 1),
            'duration': round(duration, 1),
            'reps': self.reps,
            'risk_level': risk_level,
            'style_inspiration': self.style_inspiration,
            'top_feedback': top_feedback,
            'total_frames_analyzed': len(self.scores),
        }

    def save_to_db(self, db_session):
        """Save session to database."""
        from models import SportsSession
        summary = self.get_summary()

        session = SportsSession(
            user_id=self.user_id,
            sport=self.sport,
            sport_skill=self.skill,
            score=summary['score'],
            duration=summary['duration'],
            reps=summary['reps'],
            risk_level=summary['risk_level'],
            style_inspiration=self.style_inspiration,
        )
        session.feedback = summary['top_feedback']
        session.metrics = summary

        db_session.add(session)
        db_session.commit()
        return session
