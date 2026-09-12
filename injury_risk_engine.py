"""
Injury Risk Prediction Engine.

Two layers of risk, both driven by data we already collect (per-rep form
scores from pose_detection.py, aggregated per session into Workout rows):

1. SESSION-LEVEL FATIGUE DRIFT
   Within one session, does form quality fall off as reps accumulate?
   A big drop from early reps to late reps = fatigue-driven form breakdown,
   the classic precursor to compensatory-pattern injuries (e.g. knee
   valgus creeping in on squats as the glutes tire).

2. CROSS-SESSION TREND
   Across the last N sessions of the same exercise, is average form score
   trending down over time even though the user keeps training? That's a
   compounding risk pattern — the thing the README calls out as the
   signature feature ("before it becomes an injury, not after").

Both layers produce a risk_level (low/moderate/high), a 0-100 risk_score,
a plain-language note, and a corrective drill suggestion.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Corrective drills keyed by exercise + risk theme. Kept short and generic —
# not medical advice, just a nudge toward the right correction.
CORRECTIVE_DRILLS = {
    "squat": {
        "fatigue_drift": "Drop to bodyweight squats for 2 sets of 10, focusing on knees tracking over toes.",
        "trend": "Add banded lateral walks and glute bridges 2x/week to reinforce knee tracking under fatigue.",
    },
    "pushup": {
        "fatigue_drift": "Switch to incline pushups for remaining reps to keep elbow angle and hip alignment clean.",
        "trend": "Add plank holds and scapular pushups 2x/week to build the stabilization your form is losing late in sets.",
    },
    "lunge": {
        "fatigue_drift": "Slow the tempo (3s down, 1s up) for remaining reps to rebuild control.",
        "trend": "Add single-leg balance work 2x/week to shore up the stability that's degrading over sessions.",
    },
    "plank": {
        "fatigue_drift": "End the hold now rather than letting hips sag further — quality over duration.",
        "trend": "Build hold time gradually in 10s increments rather than pushing to failure each session.",
    },
    "jumping_jack": {
        "fatigue_drift": "Slow the pace for remaining reps to keep landing mechanics soft and controlled.",
        "trend": "Add calf raises and ankle mobility work 2x/week to support repeated impact.",
    },
}

DEFAULT_DRILL = {
    "fatigue_drift": "Slow down and reset your form for the remaining reps rather than pushing through fatigue.",
    "trend": "Consider a deload week and revisit form fundamentals before increasing volume again.",
}


class InjuryRiskEngine:

    # How much form_score is allowed to drop within a session before we flag it
    FATIGUE_DRIFT_MODERATE_THRESHOLD = 12.0  # points
    FATIGUE_DRIFT_HIGH_THRESHOLD = 22.0

    # How much the trailing average form_score can drop across recent sessions
    TREND_MODERATE_THRESHOLD = 8.0
    TREND_HIGH_THRESHOLD = 15.0
    TREND_LOOKBACK_SESSIONS = 6
    TREND_LOOKBACK_DAYS = 21

    def assess_session(self, exercise_type: str, rep_form_scores: List[float]) -> Dict[str, Any]:
        """
        Compare the average form score of the first third of reps vs the
        last third, within a single session, to catch fatigue-driven drift
        while it's happening.
        """
        exercise_type = (exercise_type or "").lower()

        if not rep_form_scores or len(rep_form_scores) < 4:
            return self._no_risk("Not enough reps this session to assess fatigue drift.")

        n = len(rep_form_scores)
        third = max(1, n // 3)
        early_avg = sum(rep_form_scores[:third]) / third
        late_avg = sum(rep_form_scores[-third:]) / third
        drop = early_avg - late_avg

        drill_set = CORRECTIVE_DRILLS.get(exercise_type, DEFAULT_DRILL)

        if drop >= self.FATIGUE_DRIFT_HIGH_THRESHOLD:
            return {
                "risk_level": "high",
                "risk_score": min(100.0, 50 + drop),
                "note": (
                    f"Your form quality dropped {drop:.0f} points from your first reps to your last "
                    f"reps this session — a clear sign fatigue is breaking down your technique."
                ),
                "drill": drill_set["fatigue_drift"],
            }
        elif drop >= self.FATIGUE_DRIFT_MODERATE_THRESHOLD:
            return {
                "risk_level": "moderate",
                "risk_score": min(100.0, 30 + drop),
                "note": (
                    f"Form dipped {drop:.0f} points as this session went on. Worth watching, "
                    f"not urgent yet."
                ),
                "drill": drill_set["fatigue_drift"],
            }
        else:
            return self._no_risk("Form stayed consistent across the session — no fatigue drift detected.")

    def assess_trend(self, recent_workouts: List[Dict[str, Any]], exercise_type: str) -> Dict[str, Any]:
        """
        recent_workouts: list of dicts with 'form_score' and 'completed_at',
        already filtered to one exercise_type and ordered oldest -> newest.
        Looks for a compounding downward trend across sessions, not just
        one bad day.
        """
        exercise_type = (exercise_type or "").lower()

        scored = [w for w in recent_workouts if w.get("form_score") is not None]
        if len(scored) < 3:
            return self._no_risk("Not enough session history yet to assess a trend.")

        scored = scored[-self.TREND_LOOKBACK_SESSIONS:]

        half = max(1, len(scored) // 2)
        earlier_avg = sum(w["form_score"] for w in scored[:half]) / half
        recent_avg = sum(w["form_score"] for w in scored[half:]) / (len(scored) - half)
        drop = earlier_avg - recent_avg

        drill_set = CORRECTIVE_DRILLS.get(exercise_type, DEFAULT_DRILL)

        if drop >= self.TREND_HIGH_THRESHOLD:
            return {
                "risk_level": "high",
                "risk_score": min(100.0, 55 + drop),
                "note": (
                    f"Your average form quality on {exercise_type or 'this exercise'} has fallen "
                    f"{drop:.0f} points over your last {len(scored)} sessions — a compounding pattern "
                    f"worth addressing before it becomes an injury."
                ),
                "drill": drill_set["trend"],
            }
        elif drop >= self.TREND_MODERATE_THRESHOLD:
            return {
                "risk_level": "moderate",
                "risk_score": min(100.0, 35 + drop),
                "note": (
                    f"Form on {exercise_type or 'this exercise'} has drifted down {drop:.0f} points "
                    f"across recent sessions. Keep an eye on it."
                ),
                "drill": drill_set["trend"],
            }
        else:
            return self._no_risk("Form has been stable or improving across recent sessions.")

    def combined_risk(self, session_result: Dict[str, Any], trend_result: Dict[str, Any]) -> Dict[str, Any]:
        """Merge session + trend assessments, surfacing the more severe one."""
        levels = {"low": 0, "moderate": 1, "high": 2}
        winner = session_result if levels[session_result["risk_level"]] >= levels[trend_result["risk_level"]] else trend_result
        return {
            "risk_level": winner["risk_level"],
            "risk_score": round(winner["risk_score"], 1),
            "note": winner["note"],
            "drill": winner["drill"],
            "session": session_result,
            "trend": trend_result,
        }

    def _no_risk(self, note: str) -> Dict[str, Any]:
        return {"risk_level": "low", "risk_score": 5.0, "note": note, "drill": None}
