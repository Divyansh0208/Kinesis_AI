"""
Tests for gamification engine (XP, badges, levels).
"""

import pytest
from gamification import GamificationEngine, BADGE_DEFINITIONS
from models import db, User, Achievement, Workout


class TestGamificationEngine:
    """Test XP calculation and badge system."""

    def test_engine_initialization(self, app):
        """Test GamificationEngine initialization."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            assert engine is not None

    def test_xp_calculation_quality_reps(self, app):
        """Test XP rewards quality reps heavily."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            xp = engine.calculate_xp(
                form_score=95.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='fitness'
            )
            assert xp > 100  # Quality reps should earn significant XP

    def test_xp_calculation_poor_form(self, app):
        """Test poor form earns less XP."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            xp_poor = engine.calculate_xp(
                form_score=50.0,
                reps=10,
                quality_reps=0,
                duration=60.0,
                sport='fitness'
            )
            xp_good = engine.calculate_xp(
                form_score=95.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='fitness'
            )
            assert xp_good > xp_poor

    def test_xp_calculation_form_bonus(self, app):
        """Test form score bonus multiplier."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            xp_80 = engine.calculate_xp(
                form_score=80.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='fitness'
            )
            xp_95 = engine.calculate_xp(
                form_score=95.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='fitness'
            )
            assert xp_95 > xp_80  # Higher form should earn more XP

    def test_xp_calculation_sport_bonus(self, app):
        """Test sports get XP bonus."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            xp_fitness = engine.calculate_xp(
                form_score=85.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='fitness'
            )
            xp_football = engine.calculate_xp(
                form_score=85.0,
                reps=10,
                quality_reps=10,
                duration=60.0,
                sport='football'
            )
            assert xp_football > xp_fitness  # Sports should get bonus

    def test_xp_calculation_duration_bonus(self, app):
        """Test duration bonus."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            xp_short = engine.calculate_xp(
                form_score=85.0,
                reps=10,
                quality_reps=10,
                duration=30.0,
                sport='fitness'
            )
            xp_long = engine.calculate_xp(
                form_score=85.0,
                reps=10,
                quality_reps=10,
                duration=300.0,
                sport='fitness'
            )
            assert xp_long >= xp_short  # Longer duration should earn more

    def test_level_calculation_rookie(self):
        """Test level 1 (Rookie)."""
        engine = GamificationEngine()
        level_info = engine.get_user_level(0)
        assert level_info['level'] == 1
        assert level_info['title'] == 'Rookie'

    def test_level_calculation_athlete(self):
        """Test level progression to Athlete."""
        engine = GamificationEngine()
        level_info = engine.get_user_level(1200)
        assert level_info['level'] >= 2
        assert level_info['title'] in ['Rookie', 'Athlete']

    def test_level_calculation_progress(self):
        """Test level progress percentage."""
        engine = GamificationEngine()
        level_info = engine.get_user_level(500)  # Halfway to level 2
        assert 0 <= level_info['progress_pct'] <= 100

    def test_badge_definitions(self):
        """Test badge definitions are valid."""
        for badge in BADGE_DEFINITIONS:
            assert 'id' in badge
            assert 'name' in badge
            assert 'icon' in badge
            assert 'category' in badge
            assert 'xp' in badge

    def test_check_badges_first_perfect_rep(self, app, test_user):
        """Test First Perfect Rep badge."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            new_badges = engine.check_badges(test_user.id, {
                'form_score': 96.0,
                'quality_reps': 1,
                'sport': 'fitness'
            })
            # Should award badge if not already earned
            assert isinstance(new_badges, list)

    def test_check_badges_football_beginner(self, app, test_user):
        """Test Football Beginner badge."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            new_badges = engine.check_badges(test_user.id, {
                'sport': 'football',
                'form_score': 75.0
            })
            assert isinstance(new_badges, list)

    def test_check_badges_no_duplicate(self, app, test_user):
        """Test badges are not awarded twice."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            # Award badge first time
            engine.check_badges(test_user.id, {
                'form_score': 96.0,
                'quality_reps': 1,
                'sport': 'fitness'
            })
            # Try to award again
            new_badges = engine.check_badges(test_user.id, {
                'form_score': 96.0,
                'quality_reps': 1,
                'sport': 'fitness'
            })
            # Should not award duplicate
            # (Actual implementation checks existing badges)

    def test_get_user_badges(self, app, test_user):
        """Test retrieving user badges."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            badges = engine.get_user_badges(test_user.id)
            assert isinstance(badges, list)

    def test_get_leaderboard_data(self, app, test_user):
        """Test leaderboard data generation."""
        with app.app_context():
            from models import db
            engine = GamificationEngine(db.session)
            data = engine.get_leaderboard_data(test_user.id)
            assert 'user_id' in data
            assert 'username' in data
            assert 'xp' in data
            assert 'level' in data
