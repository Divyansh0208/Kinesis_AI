"""
Kinesis AI - Pose Detection & Movement Analysis
Core computer vision module using MediaPipe Pose.
Provides reusable biomechanical calculations and movement analysis abstractions.

Architecture:
    MovementAnalyzer (base)
        ├── FitnessAnalyzer  (push-ups, squats, lunges, planks, jumping jacks)
        ├── FootballAnalyzer  (imported from football_analyzer.py)
        └── CricketAnalyzer   (imported from cricket_analyzer.py)
"""

import math
import time
import logging
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MediaPipe Landmark Indices (reference constants)
# ---------------------------------------------------------------------------
NOSE = 0
LEFT_EYE_INNER = 1; LEFT_EYE = 2; LEFT_EYE_OUTER = 3
RIGHT_EYE_INNER = 4; RIGHT_EYE = 5; RIGHT_EYE_OUTER = 6
LEFT_EAR = 7; RIGHT_EAR = 8
MOUTH_LEFT = 9; MOUTH_RIGHT = 10
LEFT_SHOULDER = 11; RIGHT_SHOULDER = 12
LEFT_ELBOW = 13; RIGHT_ELBOW = 14
LEFT_WRIST = 15; RIGHT_WRIST = 16
LEFT_PINKY = 17; RIGHT_PINKY = 18
LEFT_INDEX = 19; RIGHT_INDEX = 20
LEFT_THUMB = 21; RIGHT_THUMB = 22
LEFT_HIP = 23; RIGHT_HIP = 24
LEFT_KNEE = 25; RIGHT_KNEE = 26
LEFT_ANKLE = 27; RIGHT_ANKLE = 28
LEFT_HEEL = 29; RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31; RIGHT_FOOT_INDEX = 32


# ---------------------------------------------------------------------------
# Core Biomechanical Functions (reusable across all analyzers)
# ---------------------------------------------------------------------------

def calculate_angle(a, b, c):
    """
    Calculate the angle at point b formed by points a-b-c.
    Each point is (x, y) or (x, y, z).
    Returns angle in degrees [0, 180].
    """
    a = np.array(a[:2])
    b = np.array(b[:2])
    c = np.array(c[:2])

    ba = a - b
    bc = c - b

    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_angle))
    return round(angle, 1)


def calculate_angle_3d(a, b, c):
    """Calculate angle in 3D space at point b."""
    a = np.array(a[:3])
    b = np.array(b[:3])
    c = np.array(c[:3])

    ba = a - b
    bc = c - b

    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return round(np.degrees(np.arccos(cos_angle)), 1)


def calculate_distance(p1, p2):
    """Euclidean distance between two points (2D)."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calculate_distance_3d(p1, p2):
    """Euclidean distance between two points (3D)."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1[:3], p2[:3])))


def calculate_midpoint(p1, p2):
    """Midpoint between two points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def calculate_velocity(positions, dt=1 / 30):
    """
    Calculate velocity from a deque of positions.
    Returns pixels/second (or normalized units/sec).
    """
    if len(positions) < 2:
        return 0.0
    p1 = positions[-2]
    p2 = positions[-1]
    dist = calculate_distance(p1, p2)
    return dist / dt if dt > 0 else 0.0


def calculate_symmetry(left_value, right_value):
    """
    Calculate left/right symmetry as a percentage (100 = perfect symmetry).
    """
    if left_value == 0 and right_value == 0:
        return 100.0
    max_val = max(abs(left_value), abs(right_value))
    if max_val == 0:
        return 100.0
    diff = abs(left_value - right_value)
    return round(max(0, 100 - (diff / max_val) * 100), 1)


def calculate_stability(positions, window=15):
    """
    Calculate stability score from a deque of positions.
    Lower variance = higher stability. Returns 0-100.
    """
    if len(positions) < 3:
        return 100.0

    recent = list(positions)[-window:]
    xs = [p[0] for p in recent]
    ys = [p[1] for p in recent]

    variance = np.var(xs) + np.var(ys)
    # Map variance to 0-100 (lower variance = higher score)
    # Calibrated for normalized coordinates [0,1]
    stability = max(0, 100 - variance * 50000)
    return round(min(100, stability), 1)


def calculate_range_of_motion(angle_history):
    """
    Calculate range of motion from angle history.
    Returns (min_angle, max_angle, range).
    """
    if not angle_history:
        return 0, 0, 0
    min_a = min(angle_history)
    max_a = max(angle_history)
    return round(min_a, 1), round(max_a, 1), round(max_a - min_a, 1)


def get_landmark_coords(landmarks, idx):
    """Extract (x, y, z, visibility) from a landmark by index."""
    lm = landmarks[idx]
    return (lm.x, lm.y, lm.z, lm.visibility)


def get_landmark_xy(landmarks, idx):
    """Extract (x, y) from a landmark by index (normalized 0-1)."""
    lm = landmarks[idx]
    return (lm.x, lm.y)


def landmarks_visible(landmarks, indices, threshold=0.5):
    """Check if all specified landmarks have sufficient visibility."""
    for idx in indices:
        if landmarks[idx].visibility < threshold:
            return False
    return True


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

def check_calibration(landmarks):
    """
    Check if the user is properly positioned for analysis.
    Returns (is_calibrated, messages).
    """
    messages = []
    is_ok = True

    # Check key body parts are visible
    key_points = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP,
                  LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE]

    low_vis = []
    for idx in key_points:
        if landmarks[idx].visibility < 0.5:
            low_vis.append(idx)

    if low_vis:
        is_ok = False
        if any(i in low_vis for i in [LEFT_ANKLE, RIGHT_ANKLE, LEFT_KNEE, RIGHT_KNEE]):
            messages.append("Move farther from the camera so your full body is visible.")
        else:
            messages.append("Keep your full body inside the frame.")

    # Check centering - shoulders should be roughly centered
    ls = landmarks[LEFT_SHOULDER]
    rs = landmarks[RIGHT_SHOULDER]
    mid_x = (ls.x + rs.x) / 2
    if mid_x < 0.2 or mid_x > 0.8:
        messages.append("Move to the center of the frame.")
        is_ok = False

    # Check if person is too close (shoulders too wide)
    shoulder_width = abs(ls.x - rs.x)
    if shoulder_width > 0.6:
        messages.append("Move farther from the camera.")
        is_ok = False

    if not messages:
        messages.append("Calibration OK. Ready to begin!")

    return is_ok, messages


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class RepState:
    """Tracks repetition state for an exercise."""
    count: int = 0
    quality_count: int = 0
    phase: str = 'idle'  # idle, up, down, hold
    last_angle: float = 0.0
    form_scores: list = field(default_factory=list)
    timestamps: list = field(default_factory=list)

    @property
    def avg_form_score(self):
        return round(sum(self.form_scores) / len(self.form_scores), 1) if self.form_scores else 0.0

    @property
    def avg_tempo(self):
        if len(self.timestamps) < 2:
            return 0.0
        diffs = [self.timestamps[i] - self.timestamps[i - 1] for i in range(1, len(self.timestamps))]
        return round(sum(diffs) / len(diffs), 2) if diffs else 0.0


@dataclass
class AnalysisResult:
    """Result from a single frame analysis."""
    form_score: float = 0.0
    feedback: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    positives: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    rep_counted: bool = False
    quality_rep: bool = False
    fatigue_level: str = 'low'
    risk_indicators: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            'form_score': self.form_score,
            'feedback': self.feedback,
            'corrections': self.corrections,
            'positives': self.positives,
            'metrics': self.metrics,
            'rep_counted': self.rep_counted,
            'quality_rep': self.quality_rep,
            'fatigue_level': self.fatigue_level,
            'risk_indicators': self.risk_indicators,
        }


# ---------------------------------------------------------------------------
# Movement Analyzer Base Class
# ---------------------------------------------------------------------------

class MovementAnalyzer:
    """
    Base class for all movement analysis.
    Provides shared state tracking, fatigue detection, and scoring.
    """

    def __init__(self):
        self.rep_state = RepState()
        self.angle_history = deque(maxlen=300)  # ~10 seconds at 30fps
        self.position_history = deque(maxlen=90)  # ~3 seconds
        self.form_score_history = deque(maxlen=60)
        self.session_start = time.time()
        self.frame_count = 0

    def reset(self):
        """Reset analyzer state for a new session."""
        self.rep_state = RepState()
        self.angle_history.clear()
        self.position_history.clear()
        self.form_score_history.clear()
        self.session_start = time.time()
        self.frame_count = 0

    def detect_fatigue(self):
        """
        Detect fatigue by analyzing form score degradation over time.
        Returns fatigue level: low / moderate / high.
        """
        if len(self.form_score_history) < 10:
            return 'low'

        scores = list(self.form_score_history)
        first_half = scores[:len(scores) // 2]
        second_half = scores[len(scores) // 2:]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        degradation = avg_first - avg_second

        if degradation > 15:
            return 'high'
        elif degradation > 7:
            return 'moderate'
        return 'low'

    def get_session_duration(self):
        """Get elapsed session time in seconds."""
        return round(time.time() - self.session_start, 1)

    def get_session_summary(self):
        """Get a summary of the current session."""
        return {
            'reps': self.rep_state.count,
            'quality_reps': self.rep_state.quality_count,
            'avg_form_score': self.rep_state.avg_form_score,
            'avg_tempo': self.rep_state.avg_tempo,
            'fatigue_level': self.detect_fatigue(),
            'duration': self.get_session_duration(),
        }


# ---------------------------------------------------------------------------
# Fitness Analyzer
# ---------------------------------------------------------------------------

class FitnessAnalyzer(MovementAnalyzer):
    """
    Analyzes fitness exercises: push-ups, squats, lunges, planks, jumping jacks.
    Uses deterministic Python calculations for real-time feedback.
    """

    EXERCISES = {
        'pushup': 'Push-Up',
        'squat': 'Squat',
        'lunge': 'Lunge',
        'plank': 'Plank',
        'jumping_jack': 'Jumping Jack',
    }

    def __init__(self, exercise_type='pushup'):
        super().__init__()
        self.exercise_type = exercise_type

    def analyze_frame(self, landmarks):
        """
        Analyze a single frame of landmarks for the configured exercise.
        Returns AnalysisResult.
        """
        self.frame_count += 1

        if self.exercise_type == 'pushup':
            return self._analyze_pushup(landmarks)
        elif self.exercise_type == 'squat':
            return self._analyze_squat(landmarks)
        elif self.exercise_type == 'lunge':
            return self._analyze_lunge(landmarks)
        elif self.exercise_type == 'plank':
            return self._analyze_plank(landmarks)
        elif self.exercise_type == 'jumping_jack':
            return self._analyze_jumping_jack(landmarks)
        else:
            return AnalysisResult(feedback=["Unknown exercise type."])

    # ---- PUSH-UP ----
    def _analyze_pushup(self, lm):
        result = AnalysisResult()

        # Key landmarks
        l_shoulder = get_landmark_xy(lm, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(lm, RIGHT_SHOULDER)
        l_elbow = get_landmark_xy(lm, LEFT_ELBOW)
        r_elbow = get_landmark_xy(lm, RIGHT_ELBOW)
        l_wrist = get_landmark_xy(lm, LEFT_WRIST)
        r_wrist = get_landmark_xy(lm, RIGHT_WRIST)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ankle = get_landmark_xy(lm, LEFT_ANKLE)
        r_ankle = get_landmark_xy(lm, RIGHT_ANKLE)

        # Calculate angles
        l_elbow_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
        r_elbow_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
        avg_elbow = (l_elbow_angle + r_elbow_angle) / 2

        # Body alignment (shoulder-hip-ankle should be ~180)
        l_body_angle = calculate_angle(l_shoulder, l_hip, l_ankle)
        r_body_angle = calculate_angle(r_shoulder, r_hip, r_ankle)
        avg_body = (l_body_angle + r_body_angle) / 2

        # Hip sag check (shoulder-hip-knee)
        l_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)
        r_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)

        result.metrics = {
            'left_elbow_angle': l_elbow_angle,
            'right_elbow_angle': r_elbow_angle,
            'body_alignment': avg_body,
            'elbow_symmetry': calculate_symmetry(l_elbow_angle, r_elbow_angle),
        }

        # Form scoring
        score = 100.0

        # Body alignment (should be 160-180 for straight body)
        if avg_body < 150:
            penalty = min(30, (150 - avg_body) * 1.5)
            score -= penalty
            if avg_body < 140:
                result.corrections.append("Keep your body in a straight line. Hips are sagging.")
            else:
                result.corrections.append("Slight hip sag detected. Engage your core.")
        else:
            result.positives.append("Good body alignment.")

        # Elbow symmetry
        symmetry = calculate_symmetry(l_elbow_angle, r_elbow_angle)
        if symmetry < 85:
            score -= 10
            result.corrections.append("Keep both arms even.")

        # Rep counting: down when elbows < 100, up when > 160
        self.angle_history.append(avg_elbow)

        rep_counted = False
        quality_rep = False

        if self.rep_state.phase in ('idle', 'up') and avg_elbow < 100:
            self.rep_state.phase = 'down'
        elif self.rep_state.phase == 'down' and avg_elbow > 155:
            self.rep_state.phase = 'up'
            self.rep_state.count += 1
            self.rep_state.timestamps.append(time.time())
            rep_counted = True

            # Quality check: good form on the way down
            if score >= 60 and avg_elbow < 100:
                self.rep_state.quality_count += 1
                quality_rep = True
                result.positives.append("Quality rep!")

        # Depth check
        if self.rep_state.phase == 'down':
            if avg_elbow > 120:
                result.corrections.append("Go deeper. Bend elbows to 90°.")
                score -= 10
            elif avg_elbow < 70:
                result.positives.append("Great depth!")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.rep_counted = rep_counted
        result.quality_rep = quality_rep
        self.form_score_history.append(score)
        self.rep_state.form_scores.append(score)
        result.fatigue_level = self.detect_fatigue()

        return result

    # ---- SQUAT ----
    def _analyze_squat(self, lm):
        result = AnalysisResult()

        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ankle = get_landmark_xy(lm, LEFT_ANKLE)
        r_ankle = get_landmark_xy(lm, RIGHT_ANKLE)
        l_shoulder = get_landmark_xy(lm, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(lm, RIGHT_SHOULDER)

        # Knee angles (hip-knee-ankle)
        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
        avg_knee = (l_knee_angle + r_knee_angle) / 2

        # Hip angles (shoulder-hip-knee)
        l_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)
        r_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)
        avg_hip = (l_hip_angle + r_hip_angle) / 2

        # Torso lean (vertical alignment)
        mid_shoulder = calculate_midpoint(l_shoulder, r_shoulder)
        mid_hip = calculate_midpoint(l_hip, r_hip)
        torso_lean = abs(mid_shoulder[0] - mid_hip[0]) * 100

        result.metrics = {
            'left_knee_angle': l_knee_angle,
            'right_knee_angle': r_knee_angle,
            'avg_knee_angle': avg_knee,
            'hip_angle': avg_hip,
            'knee_symmetry': calculate_symmetry(l_knee_angle, r_knee_angle),
            'torso_lean': round(torso_lean, 1),
        }

        score = 100.0

        # Knee alignment check - knees should track over toes
        knee_symmetry = calculate_symmetry(l_knee_angle, r_knee_angle)
        if knee_symmetry < 85:
            score -= 10
            result.corrections.append("Keep both knees aligned equally.")
        else:
            result.positives.append("Good knee symmetry.")

        # Torso position
        if torso_lean > 15:
            score -= 10
            result.corrections.append("Keep your torso more upright.")
        else:
            result.positives.append("Good torso position.")

        # Knee over toe check (simplified: knee x vs ankle x)
        l_knee_past = l_knee[0] - l_ankle[0]
        r_knee_past = r_knee[0] - r_ankle[0]
        if abs(l_knee_past) > 0.05 or abs(r_knee_past) > 0.05:
            # This is actually acceptable for deep squats, so mild penalty
            pass

        # Rep counting: down when knees < 100, up when > 160
        self.angle_history.append(avg_knee)

        rep_counted = False
        quality_rep = False

        if self.rep_state.phase in ('idle', 'up') and avg_knee < 110:
            self.rep_state.phase = 'down'
        elif self.rep_state.phase == 'down' and avg_knee > 160:
            self.rep_state.phase = 'up'
            self.rep_state.count += 1
            self.rep_state.timestamps.append(time.time())
            rep_counted = True

            if score >= 60:
                self.rep_state.quality_count += 1
                quality_rep = True

        # Depth feedback
        if self.rep_state.phase == 'down':
            if avg_knee > 120:
                result.corrections.append("Go deeper. Aim for thighs parallel to ground.")
                score -= 10
            elif avg_knee < 80:
                result.positives.append("Excellent depth!")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.rep_counted = rep_counted
        result.quality_rep = quality_rep
        self.form_score_history.append(score)
        self.rep_state.form_scores.append(score)
        result.fatigue_level = self.detect_fatigue()

        return result

    # ---- LUNGE ----
    def _analyze_lunge(self, lm):
        result = AnalysisResult()

        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ankle = get_landmark_xy(lm, LEFT_ANKLE)
        r_ankle = get_landmark_xy(lm, RIGHT_ANKLE)
        l_shoulder = get_landmark_xy(lm, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(lm, RIGHT_SHOULDER)

        # Determine which leg is forward (lower knee y = forward in image coords)
        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)

        # The leg with a lower y (higher on screen) is the back leg typically in a lunge
        # More reliably: the leg with the more bent knee is the front leg during descent
        front_knee = min(l_knee_angle, r_knee_angle)
        back_knee = max(l_knee_angle, r_knee_angle)

        # Torso uprightness
        mid_shoulder = calculate_midpoint(l_shoulder, r_shoulder)
        mid_hip = calculate_midpoint(l_hip, r_hip)
        torso_vertical = abs(mid_shoulder[0] - mid_hip[0]) * 100

        result.metrics = {
            'front_knee_angle': front_knee,
            'back_knee_angle': back_knee,
            'torso_lean': round(torso_vertical, 1),
            'knee_symmetry': calculate_symmetry(l_knee_angle, r_knee_angle),
        }

        score = 100.0

        # Front knee should reach ~90° at bottom
        if self.rep_state.phase == 'down' or front_knee < 120:
            if front_knee > 110:
                result.corrections.append("Lunge deeper. Front knee should reach 90°.")
                score -= 10
            elif front_knee < 70:
                result.corrections.append("Don't over-bend the front knee.")
                score -= 10
            else:
                result.positives.append("Good front knee angle.")

        # Torso
        if torso_vertical > 12:
            score -= 10
            result.corrections.append("Keep torso upright during lunge.")
        else:
            result.positives.append("Good upright posture.")

        # Rep counting
        self.angle_history.append(front_knee)

        rep_counted = False
        quality_rep = False

        if self.rep_state.phase in ('idle', 'up') and front_knee < 110:
            self.rep_state.phase = 'down'
        elif self.rep_state.phase == 'down' and front_knee > 155:
            self.rep_state.phase = 'up'
            self.rep_state.count += 1
            self.rep_state.timestamps.append(time.time())
            rep_counted = True
            if score >= 60:
                self.rep_state.quality_count += 1
                quality_rep = True

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.rep_counted = rep_counted
        result.quality_rep = quality_rep
        self.form_score_history.append(score)
        self.rep_state.form_scores.append(score)
        result.fatigue_level = self.detect_fatigue()

        return result

    # ---- PLANK ----
    def _analyze_plank(self, lm):
        result = AnalysisResult()

        l_shoulder = get_landmark_xy(lm, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(lm, RIGHT_SHOULDER)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_ankle = get_landmark_xy(lm, LEFT_ANKLE)
        r_ankle = get_landmark_xy(lm, RIGHT_ANKLE)
        l_elbow = get_landmark_xy(lm, LEFT_ELBOW)
        r_elbow = get_landmark_xy(lm, RIGHT_ELBOW)

        # Body alignment (shoulder-hip-ankle should be ~180 for plank)
        l_body = calculate_angle(l_shoulder, l_hip, l_ankle)
        r_body = calculate_angle(r_shoulder, r_hip, r_ankle)
        avg_body = (l_body + r_body) / 2

        # Shoulder-elbow alignment
        l_arm = calculate_angle(l_shoulder, l_elbow, l_hip)

        # Hip position relative to shoulder-ankle line
        mid_shoulder = calculate_midpoint(l_shoulder, r_shoulder)
        mid_hip = calculate_midpoint(l_hip, r_hip)
        mid_ankle = calculate_midpoint(l_ankle, r_ankle)

        # Track hip position for stability
        self.position_history.append(mid_hip)
        hip_stability = calculate_stability(self.position_history)

        result.metrics = {
            'body_alignment': avg_body,
            'hip_stability': hip_stability,
            'symmetry': calculate_symmetry(l_body, r_body),
            'duration': self.get_session_duration(),
        }

        score = 100.0

        # Body alignment
        if avg_body < 155:
            penalty = min(30, (155 - avg_body) * 1.5)
            score -= penalty
            if avg_body < 145:
                result.corrections.append("Hips are sagging. Engage your core and lift hips.")
            else:
                result.corrections.append("Slight hip drop. Tighten your core.")
        elif avg_body > 185:
            score -= 15
            result.corrections.append("Hips are too high. Lower them to form a straight line.")
        else:
            result.positives.append("Excellent body alignment!")

        # Stability
        if hip_stability < 80:
            score -= 10
            result.corrections.append("Stay stable. Minimize body movement.")
        else:
            result.positives.append("Good stability!")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        self.form_score_history.append(score)
        result.fatigue_level = self.detect_fatigue()

        # Plank is time-based, not rep-based
        duration = self.get_session_duration()
        result.metrics['hold_time'] = duration

        return result

    # ---- JUMPING JACK ----
    def _analyze_jumping_jack(self, lm):
        result = AnalysisResult()

        l_shoulder = get_landmark_xy(lm, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(lm, RIGHT_SHOULDER)
        l_elbow = get_landmark_xy(lm, LEFT_ELBOW)
        r_elbow = get_landmark_xy(lm, RIGHT_ELBOW)
        l_wrist = get_landmark_xy(lm, LEFT_WRIST)
        r_wrist = get_landmark_xy(lm, RIGHT_WRIST)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_ankle = get_landmark_xy(lm, LEFT_ANKLE)
        r_ankle = get_landmark_xy(lm, RIGHT_ANKLE)

        # Arm angle (how high arms are raised)
        # Measure angle at shoulder: hip-shoulder-wrist
        l_arm_angle = calculate_angle(l_hip, l_shoulder, l_wrist)
        r_arm_angle = calculate_angle(r_hip, r_shoulder, r_wrist)
        avg_arm = (l_arm_angle + r_arm_angle) / 2

        # Leg spread (distance between ankles relative to hip width)
        ankle_dist = calculate_distance(l_ankle, r_ankle)
        hip_width = calculate_distance(l_hip, r_hip)
        leg_spread_ratio = ankle_dist / (hip_width + 1e-8)

        result.metrics = {
            'left_arm_angle': l_arm_angle,
            'right_arm_angle': r_arm_angle,
            'arm_symmetry': calculate_symmetry(l_arm_angle, r_arm_angle),
            'leg_spread': round(leg_spread_ratio, 2),
        }

        score = 100.0

        # Arm symmetry
        arm_sym = calculate_symmetry(l_arm_angle, r_arm_angle)
        if arm_sym < 85:
            score -= 10
            result.corrections.append("Raise both arms evenly.")

        # Rep counting: arms up (angle > 150) and legs spread (ratio > 2)
        # then arms down and legs together
        self.angle_history.append(avg_arm)

        is_open = avg_arm > 140 and leg_spread_ratio > 1.8
        is_closed = avg_arm < 60 and leg_spread_ratio < 1.3

        rep_counted = False
        quality_rep = False

        if self.rep_state.phase in ('idle', 'down') and is_open:
            self.rep_state.phase = 'up'
        elif self.rep_state.phase == 'up' and is_closed:
            self.rep_state.phase = 'down'
            self.rep_state.count += 1
            self.rep_state.timestamps.append(time.time())
            rep_counted = True
            if score >= 60:
                self.rep_state.quality_count += 1
                quality_rep = True

        # Full range of motion check
        if self.rep_state.phase == 'up':
            if avg_arm < 150:
                result.corrections.append("Raise arms fully overhead.")
                score -= 10
            else:
                result.positives.append("Good arm extension!")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.rep_counted = rep_counted
        result.quality_rep = quality_rep
        self.form_score_history.append(score)
        self.rep_state.form_scores.append(score)
        result.fatigue_level = self.detect_fatigue()

        return result
