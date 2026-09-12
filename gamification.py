"""
Gamification Engine.

XP is earned from real form-quality data, not just attendance — per the
README's promise ("tied to real form-quality data, not just attendance").
A sloppy 30-rep set earns less than a clean 15-rep set.
"""

import json
import logging
from datetime import date, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# XP required to reach each level (index 0 = level 1 threshold, cumulative)
LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1400, 2100, 3000, 4200, 5700, 7500]

BADGES = {
    "first_workout": {
        "name": "First Rep",
        "description": "Completed your first tracked workout.",
        "check": lambda ctx: ctx["total_workouts"] >= 1,
    },
    "streak_3": {
        "name": "On a Roll",
        "description": "3-day workout streak.",
        "check": lambda ctx: ctx["current_streak"] >= 3,
    },
    "streak_7": {
        "name": "Week Warrior",
        "description": "7-day workout streak.",
        "check": lambda ctx: ctx["current_streak"] >= 7,
    },
    "streak_30": {
        "name": "Iron Habit",
        "description": "30-day workout streak.",
        "check": lambda ctx: ctx["current_streak"] >= 30,
    },
    "form_perfectionist": {
        "name": "Form Perfectionist",
        "description": "Logged a session with 95+ average form score.",
        "check": lambda ctx: ctx.get("session_form_score", 0) >= 95,
    },
    "century_club": {
        "name": "Century Club",
        "description": "Completed 100 total workouts.",
        "check": lambda ctx: ctx["total_workouts"] >= 100,
    },
    "level_5": {
        "name": "Rising Athlete",
        "description": "Reached level 5.",
        "check": lambda ctx: ctx["level"] >= 5,
    },
}


class GamificationEngine:

    def calculate_xp(self, reps_completed: int, form_score: float, duration_minutes: int) -> int:
        """
        Base XP from effort (reps + time), scaled by a form-quality
        multiplier so sloppy volume doesn't out-earn clean technique.
        """
        reps_completed = reps_completed or 0
        duration_minutes = duration_minutes or 0
        form_score = form_score if form_score is not None else 60.0

        base_xp = (reps_completed * 2) + (duration_minutes * 3)

        # Quality multiplier: 0.6x at 0 form score, 1.5x at 100 form score
        quality_multiplier = 0.6 + (form_score / 100.0) * 0.9

        xp = int(round(base_xp * quality_multiplier))
        return max(xp, 5)  # every logged session is worth something

    def level_for_xp(self, total_xp: int) -> int:
        level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if total_xp >= threshold:
                level = i + 1
        return level

    def xp_to_next_level(self, total_xp: int) -> Optional[int]:
        level = self.level_for_xp(total_xp)
        if level >= len(LEVEL_THRESHOLDS):
            return None  # maxed out
        return LEVEL_THRESHOLDS[level] - total_xp

    def update_streak(self, last_workout_date: Optional[date], current_streak: int,
                       longest_streak: int, today: Optional[date] = None) -> Dict[str, int]:
        """
        Call once per completed workout. Same-day workouts don't double-count;
        a gap of more than 1 day resets the streak.
        """
        today = today or date.today()

        if last_workout_date is None:
            new_streak = 1
        elif last_workout_date == today:
            new_streak = current_streak or 1  # already logged today, no change
        elif last_workout_date == today - timedelta(days=1):
            new_streak = (current_streak or 0) + 1
        else:
            new_streak = 1  # streak broken

        new_longest = max(longest_streak or 0, new_streak)

        return {
            "current_streak": new_streak,
            "longest_streak": new_longest,
            "last_workout_date": today,
        }

    def check_new_badges(self, context: Dict[str, Any], already_earned: List[str]) -> List[Dict[str, str]]:
        """
        context should include: total_workouts, current_streak, level,
        and optionally session_form_score for this specific session.
        Returns list of newly-earned badge dicts (id, name, description).
        """
        newly_earned = []
        for badge_id, badge in BADGES.items():
            if badge_id in already_earned:
                continue
            try:
                if badge["check"](context):
                    newly_earned.append({
                        "id": badge_id,
                        "name": badge["name"],
                        "description": badge["description"],
                    })
            except Exception as e:
                logger.warning(f"Badge check failed for {badge_id}: {e}")
        return newly_earned

    def process_workout(self, stats_row, reps_completed: int, form_score: float,
                         duration_minutes: int, total_workouts: int) -> Dict[str, Any]:
        """
        Full pipeline for one completed workout. `stats_row` is expected to
        expose .xp, .level, .current_streak, .longest_streak,
        .last_workout_date, .badges (JSON string) — i.e. a UserStats row.
        Mutates nothing; returns the new values for the caller to persist.
        """
        xp_earned = self.calculate_xp(reps_completed, form_score, duration_minutes)
        new_total_xp = (stats_row.xp or 0) + xp_earned
        new_level = self.level_for_xp(new_total_xp)
        leveled_up = new_level > (stats_row.level or 1)

        streak_info = self.update_streak(
            stats_row.last_workout_date, stats_row.current_streak, stats_row.longest_streak
        )

        already_earned = json.loads(stats_row.badges or '[]')
        context = {
            "total_workouts": total_workouts,
            "current_streak": streak_info["current_streak"],
            "level": new_level,
            "session_form_score": form_score,
        }
        new_badges = self.check_new_badges(context, already_earned)
        updated_badge_list = already_earned + [b["id"] for b in new_badges]

        return {
            "xp_earned": xp_earned,
            "total_xp": new_total_xp,
            "level": new_level,
            "leveled_up": leveled_up,
            "xp_to_next_level": self.xp_to_next_level(new_total_xp),
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "last_workout_date": streak_info["last_workout_date"],
            "new_badges": new_badges,
            "badges": updated_badge_list,
        }

    def leaderboard(self, user_stats_rows: List[Any], limit: int = 10) -> List[Dict[str, Any]]:
        """user_stats_rows: list of UserStats-like rows with .user.username and .xp"""
        ranked = sorted(user_stats_rows, key=lambda r: r.xp or 0, reverse=True)[:limit]
        return [
            {
                "rank": i + 1,
                "username": row.user.username,
                "xp": row.xp,
                "level": row.level,
                "current_streak": row.current_streak,
            }
            for i, row in enumerate(ranked)
        ]
