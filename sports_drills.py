"""
Kinesis AI - Sports Drills Module
General athletic drills: agility, speed, balance, reaction time.
"""

import time
import logging
from collections import deque
from pose_detection import (
    MovementAnalyzer, AnalysisResult,
    calculate_angle, calculate_distance, calculate_midpoint,
    calculate_symmetry, calculate_stability, calculate_velocity,
    get_landmark_xy, landmarks_visible,
    LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE,
    LEFT_HEEL, RIGHT_HEEL, LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX,
    NOSE
)

logger = logging.getLogger(__name__)


class DrillAnalyzer(MovementAnalyzer):
    """Analyzes general athletic drills using pose estimation."""

    DRILL_TYPES = {
        'side_shuffle': 'Side Shuffle',
        'cone_drill': 'Cone-Style Movement',
        'sprint_stop': 'Sprint & Stop',
        'direction_change': 'Direction Change',
        'lateral_movement': 'Lateral Movement',
        'balance_hold': 'Balance Hold',
        'high_knees': 'High Knees',
    }

    def __init__(self, drill_type='side_shuffle'):
        super().__init__()
        self.drill_type = drill_type
        self.reaction_start = None
        self.reaction_time = None
        self.movement_started = False
        self.direction_changes = 0
        self.hip_center_history = deque(maxlen=150)
        self.last_direction = None

    def analyze_frame(self, landmarks):
        """Route to appropriate drill analysis."""
        self.frame_count += 1
        if self.drill_type == 'side_shuffle':
            return self._analyze_side_shuffle(landmarks)
        elif self.drill_type == 'sprint_stop':
            return self._analyze_sprint_stop(landmarks)
        elif self.drill_type == 'direction_change':
            return self._analyze_direction_change(landmarks)
        elif self.drill_type == 'lateral_movement':
            return self._analyze_lateral_movement(landmarks)
        elif self.drill_type == 'balance_hold':
            return self._analyze_balance(landmarks)
        elif self.drill_type == 'high_knees':
            return self._analyze_high_knees(landmarks)
        else:
            return self._analyze_side_shuffle(landmarks)

    def _get_center_of_mass(self, landmarks):
        """Estimate center of mass from hip midpoint."""
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        return calculate_midpoint(l_hip, r_hip)

    def _detect_direction(self, landmarks):
        """Detect movement direction from hip center history."""
        com = self._get_center_of_mass(landmarks)
        self.hip_center_history.append(com)
        if len(self.hip_center_history) < 5:
            return 'stationary'
        recent = list(self.hip_center_history)
        dx = recent[-1][0] - recent[-5][0]
        if dx > 0.01:
            return 'right'
        elif dx < -0.01:
            return 'left'
        return 'stationary'

    def _analyze_side_shuffle(self, landmarks):
        result = AnalysisResult()
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        l_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)

        com = self._get_center_of_mass(landmarks)
        self.position_history.append(com)

        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
        avg_knee = (l_knee_angle + r_knee_angle) / 2

        stability = calculate_stability(self.position_history)
        symmetry = calculate_symmetry(l_knee_angle, r_knee_angle)

        direction = self._detect_direction(landmarks)
        if self.last_direction and direction != self.last_direction and direction != 'stationary':
            self.direction_changes += 1
        if direction != 'stationary':
            self.last_direction = direction
            if not self.movement_started:
                self.movement_started = True

        score = 100.0
        if avg_knee > 160:
            score -= 15
            result.corrections.append("Lower your center of gravity. Bend knees more.")
        elif avg_knee < 100:
            score -= 10
            result.corrections.append("Don't crouch too low. Maintain athletic stance.")
        else:
            result.positives.append("Good athletic stance.")

        if symmetry < 80:
            score -= 10
            result.corrections.append("Keep both knees equally bent for balanced movement.")

        mid_shoulder = calculate_midpoint(l_shoulder, r_shoulder)
        torso_lean = abs(mid_shoulder[0] - com[0]) * 100
        if torso_lean > 10:
            score -= 10
            result.corrections.append("Keep torso centered over hips.")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.metrics = {
            'knee_bend': round(avg_knee, 1),
            'symmetry': symmetry,
            'stability': stability,
            'direction_changes': self.direction_changes,
            'movement_direction': direction,
        }
        self.form_score_history.append(score)
        result.fatigue_level = self.detect_fatigue()
        return result

    def _analyze_sprint_stop(self, landmarks):
        result = AnalysisResult()
        com = self._get_center_of_mass(landmarks)
        self.position_history.append(com)

        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)

        velocity = calculate_velocity(self.position_history)
        stability = calculate_stability(self.position_history)
        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)

        score = 100.0
        is_stopping = velocity < 0.002 and len(self.position_history) > 10

        if is_stopping:
            if stability > 80:
                result.positives.append("Good deceleration control!")
            else:
                score -= 15
                result.corrections.append("Work on stopping with better balance.")
            avg_knee = (l_knee_angle + r_knee_angle) / 2
            if avg_knee > 170:
                score -= 10
                result.corrections.append("Bend knees when stopping for better control.")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.metrics = {
            'velocity': round(velocity * 1000, 2),
            'stability': stability,
            'is_stopping': is_stopping,
        }
        self.form_score_history.append(score)
        result.fatigue_level = self.detect_fatigue()
        return result

    def _analyze_direction_change(self, landmarks):
        result = AnalysisResult()
        com = self._get_center_of_mass(landmarks)
        self.position_history.append(com)

        direction = self._detect_direction(landmarks)
        stability = calculate_stability(self.position_history)

        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)

        symmetry = calculate_symmetry(
            calculate_angle(l_hip, l_knee, l_ankle),
            calculate_angle(r_hip, r_knee, r_ankle)
        )

        if self.last_direction and direction != self.last_direction and direction != 'stationary':
            self.direction_changes += 1
        if direction != 'stationary':
            self.last_direction = direction

        score = 100.0
        if stability < 70:
            score -= 15
            result.corrections.append("Maintain balance during direction changes.")
        if symmetry < 80:
            score -= 10
            result.corrections.append("Keep body balanced on both sides.")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.metrics = {
            'direction_changes': self.direction_changes,
            'stability': stability,
            'symmetry': symmetry,
            'current_direction': direction,
        }
        self.form_score_history.append(score)
        result.fatigue_level = self.detect_fatigue()
        return result

    def _analyze_lateral_movement(self, landmarks):
        return self._analyze_side_shuffle(landmarks)

    def _analyze_balance(self, landmarks):
        result = AnalysisResult()
        com = self._get_center_of_mass(landmarks)
        self.position_history.append(com)

        nose = get_landmark_xy(landmarks, NOSE)
        stability = calculate_stability(self.position_history)

        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        base_width = calculate_distance(l_ankle, r_ankle)

        score = stability
        if stability > 90:
            result.positives.append("Excellent balance!")
        elif stability > 70:
            result.positives.append("Good balance. Stay focused.")
        else:
            result.corrections.append("Focus on a fixed point. Engage your core.")

        result.form_score = round(max(0, min(100, score)), 1)
        result.metrics = {
            'stability': stability,
            'hold_time': self.get_session_duration(),
            'base_width': round(base_width, 4),
        }
        self.form_score_history.append(result.form_score)
        result.fatigue_level = self.detect_fatigue()
        return result

    def _analyze_high_knees(self, landmarks):
        result = AnalysisResult()
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)

        l_knee_height = l_hip[1] - l_knee[1]
        r_knee_height = r_hip[1] - r_knee[1]

        max_height = max(l_knee_height, r_knee_height)
        self.angle_history.append(max_height)

        score = 100.0
        rep_counted = False
        quality_rep = False

        if max_height > 0.02:
            if self.rep_state.phase in ('idle', 'down'):
                self.rep_state.phase = 'up'
        elif self.rep_state.phase == 'up':
            self.rep_state.phase = 'down'
            self.rep_state.count += 1
            self.rep_state.timestamps.append(time.time())
            rep_counted = True
            if max_height > 0.0:
                self.rep_state.quality_count += 1
                quality_rep = True

        symmetry = calculate_symmetry(abs(l_knee_height), abs(r_knee_height))
        if symmetry < 75:
            score -= 15
            result.corrections.append("Raise both knees equally high.")

        score = max(0, min(100, score))
        result.form_score = round(score, 1)
        result.rep_counted = rep_counted
        result.quality_rep = quality_rep
        result.metrics = {
            'left_knee_height': round(l_knee_height, 4),
            'right_knee_height': round(r_knee_height, 4),
            'symmetry': symmetry,
        }
        self.form_score_history.append(score)
        result.fatigue_level = self.detect_fatigue()
        return result
