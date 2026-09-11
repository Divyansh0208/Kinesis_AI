from models import db, Achievement, User, Workout, SportsSession
from datetime import datetime, timedelta

BADGE_DEFINITIONS = [
    {'id': 'first_perfect_rep', 'name': 'First Perfect Rep', 'icon': '⭐', 'desc': 'Score 95+ on a single rep', 'category': 'form', 'xp': 50},
    {'id': 'ten_quality_reps', 'name': '10 Quality Reps', 'icon': '🔥', 'desc': 'Complete 10 quality reps in a session', 'category': 'fitness', 'xp': 100},
    {'id': 'football_beginner', 'name': 'Football Beginner', 'icon': '⚽', 'desc': 'Complete first football training', 'category': 'football', 'xp': 75},
    {'id': 'cricket_technique', 'name': 'Cricket Technique', 'icon': '🏏', 'desc': 'Score 80+ on a cricket drill', 'category': 'cricket', 'xp': 100},
    {'id': 'seven_day_streak', 'name': '7 Day Streak', 'icon': '🔥', 'desc': 'Train for 7 consecutive days', 'category': 'streak', 'xp': 200},
    {'id': 'form_master', 'name': 'Form Master', 'icon': '🏆', 'desc': 'Average 90+ form score over 50 reps', 'category': 'form', 'xp': 300},
    {'id': 'sports_explorer', 'name': 'Sports Explorer', 'icon': '🌟', 'desc': 'Try all sports categories', 'category': 'general', 'xp': 150},
    {'id': 'iron_plank', 'name': 'Iron Plank', 'icon': '💪', 'desc': 'Hold plank with 85+ score for 60 seconds', 'category': 'fitness', 'xp': 150},
    {'id': 'consistency_king', 'name': 'Consistency King', 'icon': '👑', 'desc': '30 day streak', 'category': 'streak', 'xp': 500},
    {'id': 'century_reps', 'name': 'Century Club', 'icon': '💯', 'desc': 'Complete 100 quality reps total', 'category': 'fitness', 'xp': 250},
]

class GamificationEngine:
    def __init__(self, db_session):
        self.db = db_session

    def calculate_xp(self, form_score, reps, quality_reps, duration, sport=None) -> int:
        """
        Calculates XP based on form quality, reps, and duration.
        """
        # Base XP: quality reps are heavily rewarded
        xp = quality_reps * 10

        # Form bonus
        if form_score >= 90:
            xp = int(xp * 2.0)  # +100%
        elif form_score > 80:
            xp = int(xp * 1.5)  # +50%

        # Duration bonus: 5 XP per 5 minutes
        duration_mins = duration / 60.0
        duration_bonus = int((duration_mins / 5.0) * 5)
        xp += duration_bonus

        # Sport bonus multiplier
        if sport and sport.lower() in ['football', 'cricket']:
            xp = int(xp * 1.2)
            
        return xp

    def check_badges(self, user_id, session_data) -> list:
        """
        Check all badge conditions and award new ones.
        session_data expects: form_score, reps, quality_reps, sport, duration
        Returns list of newly earned badge dictionaries.
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            return []

        existing_badges = self.db.query(Achievement).filter_by(user_id=user_id).all()
        existing_badge_ids = set([b.badge_id for b in existing_badges])
        
        new_badges = []
        
        # Helper to award
        def award(badge_def):
            if badge_def['id'] not in existing_badge_ids:
                new_ach = Achievement(
                    user_id=user_id,
                    badge_id=badge_def['id'],
                    name=badge_def['name'],
                    earned_at=datetime.utcnow()
                )
                self.db.add(new_ach)
                user.xp += badge_def['xp']
                new_badges.append(badge_def)
                existing_badge_ids.add(badge_def['id'])

        # Check logic for each badge
        form_score = session_data.get('form_score', 0)
        quality_reps = session_data.get('quality_reps', 0)
        sport = session_data.get('sport', '').lower()
        
        for badge in BADGE_DEFINITIONS:
            bid = badge['id']
            if bid in existing_badge_ids:
                continue
                
            if bid == 'first_perfect_rep' and form_score >= 95 and quality_reps >= 1:
                award(badge)
            elif bid == 'ten_quality_reps' and quality_reps >= 10:
                award(badge)
            elif bid == 'football_beginner' and sport == 'football':
                award(badge)
            elif bid == 'cricket_technique' and sport == 'cricket' and form_score >= 80:
                award(badge)
            # Complex badges would need aggregate queries. Approximating some for the session:
            elif bid == 'iron_plank' and sport == 'plank' and form_score >= 85 and session_data.get('duration', 0) >= 60:
                award(badge)

        self.db.commit()
        return new_badges

    def get_user_level(self, xp) -> dict:
        """
        Calculate user level and progress based on XP.
        """
        # Simple progression: 1000 XP per level tier roughly
        level = 1
        base_xp = 0
        next_xp = 1000

        while xp >= next_xp:
            level += 1
            base_xp = next_xp
            next_xp = int(next_xp * 1.5)  # Scaling requirement

        if level <= 5:
            title = 'Rookie'
        elif level <= 10:
            title = 'Athlete'
        elif level <= 15:
            title = 'Pro'
        elif level <= 20:
            title = 'Elite'
        else:
            title = 'Legend'

        progress_pct = ((xp - base_xp) / (next_xp - base_xp)) * 100 if next_xp > base_xp else 100.0

        return {
            'level': level,
            'title': title,
            'xp_current': xp,
            'xp_next': next_xp,
            'progress_pct': round(progress_pct, 2)
        }

    def get_user_badges(self, user_id) -> list:
        """
        Return all badges earned by the user.
        """
        achievements = self.db.query(Achievement).filter_by(user_id=user_id).all()
        earned_ids = {ach.badge_id: ach.earned_at for ach in achievements}
        
        user_badges = []
        for badge in BADGE_DEFINITIONS:
            if badge['id'] in earned_ids:
                badge_copy = badge.copy()
                badge_copy['earned_at'] = earned_ids[badge['id']].isoformat()
                user_badges.append(badge_copy)
                
        return user_badges

    def get_leaderboard_data(self, user_id) -> dict:
        """
        Return user stats summary for dashboard leaderboard.
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            return {}

        # Mocking rank calculation - in a real app, we'd query:
        # count = db.query(User).filter(User.xp > user.xp).count() + 1
        
        level_info = self.get_user_level(user.xp)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'xp': user.xp,
            'level': level_info['level'],
            'title': level_info['title'],
            'rank': 1, # Placeholder for actual rank
            'recent_badges': self.get_user_badges(user_id)[-3:] # last 3 badges
        }
