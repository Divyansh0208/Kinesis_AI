import numpy as np
import logging
import time
from typing import Dict, List, Tuple, Optional

class PoseAnalyzer:
    """Analyze poses for different exercises and provide form feedback"""

    def __init__(self):
        self.exercise_counters = {
            'pushup': PushupCounter(),
            'squat': SquatCounter(),
            'jumping_jack': JumpingJackCounter(),
            'plank': PlankCounter(),
            'lunge': LungeCounter(),
            'bicep_curl': BicepCurlCounter(),
            'mountain_climber': MountainClimberCounter(),
            'situp': SitupCounter()
        }

    def analyze_pose(self, landmarks: List[Dict], exercise_type: str) -> Dict:
        """Analyze pose and return form score and feedback"""
        try:
            if exercise_type not in self.exercise_counters:
                return {"error": "Unsupported exercise type"}

            if not landmarks or len(landmarks) < 33:
                return {"error": "Insufficient landmarks detected"}

            counter = self.exercise_counters[exercise_type]
            result = counter.analyze(landmarks)
            
            # Ensure consistent return format
            return {
                "reps": result.get("reps", 0),
                "form_score": result.get("form_score", 0),
                "feedback": result.get("feedback", ["No feedback available"]),
                "success": True
            }

        except Exception as e:
            logging.error(f"Error in pose analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "reps": 0,
                "form_score": 0,
                "feedback": ["Analysis error occurred"],
                "success": False
            }

class PushupCounter:
    """Pushup form analysis and counting"""

    def __init__(self):
        self.state = "up"  # up, down
        self.rep_count = 0
        self.last_angle = 180

    def analyze(self, landmarks: List[Dict]) -> Dict:
        """Analyze pushup form and count reps"""
        try:
            # Get key points for pushup analysis
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_elbow = landmarks[13]
            right_elbow = landmarks[14]
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            left_hip = landmarks[23]
            right_hip = landmarks[24]

            # Calculate arm angles
            left_arm_angle = self._calculate_angle(
                [left_shoulder['x'], left_shoulder['y']],
                [left_elbow['x'], left_elbow['y']],
                [left_wrist['x'], left_wrist['y']]
            )

            right_arm_angle = self._calculate_angle(
                [right_shoulder['x'], right_shoulder['y']],
                [right_elbow['x'], right_elbow['y']],
                [right_wrist['x'], right_wrist['y']]
            )

            avg_arm_angle = (left_arm_angle + right_arm_angle) / 2

            # Calculate body alignment
            body_alignment_score = self._calculate_body_alignment(
                left_shoulder, right_shoulder, left_hip, right_hip
            )

            # Count reps based on arm angle with stricter thresholds
            if self.state == "up" and avg_arm_angle < 90:
                self.state = "down"
            elif self.state == "down" and avg_arm_angle > 160:
                self.state = "up"
                self.rep_count += 1

            # Calculate form score (0-100)
            form_score = self._calculate_pushup_form_score(avg_arm_angle, body_alignment_score)

            # Generate feedback
            feedback = self._generate_pushup_feedback(avg_arm_angle, body_alignment_score)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "arm_angle": round(avg_arm_angle, 1),
                "body_alignment": round(body_alignment_score, 1),
                "state": self.state
            }

        except Exception as e:
            logging.error(f"Error in pushup analysis: {e}")
            return {"error": "Pushup analysis failed"}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def _calculate_body_alignment(self, left_shoulder: Dict, right_shoulder: Dict,
                                left_hip: Dict, right_hip: Dict) -> float:
        """Calculate body alignment score (higher is better)"""
        # Check if shoulders and hips are aligned (straight line)
        shoulder_center = [(left_shoulder['x'] + right_shoulder['x']) / 2,
                          (left_shoulder['y'] + right_shoulder['y']) / 2]
        hip_center = [(left_hip['x'] + right_hip['x']) / 2,
                     (left_hip['y'] + right_hip['y']) / 2]

        # Calculate deviation from straight line
        vertical_deviation = abs(shoulder_center[1] - hip_center[1])

        # Convert to score (lower deviation = higher score)
        alignment_score = max(0, 100 - (vertical_deviation * 1000))
        return min(100, alignment_score)

    def _calculate_pushup_form_score(self, arm_angle: float, body_alignment: float) -> float:
        """Calculate overall form score for pushup"""
        # Ideal arm angle range: 60-90 degrees at bottom, 160-180 at top
        if 60 <= arm_angle <= 90 or 160 <= arm_angle <= 180:
            angle_score = 100
        elif 90 < arm_angle < 160:
            # Transition zone - moderate score
            angle_score = 70
        else:
            angle_score = max(0, 100 - abs(arm_angle - 90) * 2)

        # Combine scores
        form_score = (angle_score * 0.7) + (body_alignment * 0.3)
        return min(100, max(0, form_score))

    def _generate_pushup_feedback(self, arm_angle: float, body_alignment: float) -> List[str]:
        """Generate feedback for pushup form"""
        feedback = []

        if arm_angle < 60:
            feedback.append("Don't go too low - protect your shoulders")
        elif arm_angle < 90 and self.state == "down":
            feedback.append("Good depth! Now push up")
        elif arm_angle > 120 and arm_angle < 160:
            feedback.append("Push all the way up")
        elif arm_angle >= 160:
            feedback.append("Great form!")

        if body_alignment < 70:
            feedback.append("Keep your body straight - avoid sagging")

        if not feedback:
            feedback.append("Excellent form!")

        return feedback


class SquatCounter:
    """Squat form analysis and counting"""

    def __init__(self):
        self.state = "up"  # up, down
        self.rep_count = 0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        """Analyze squat form and count reps"""
        try:
            # Get key points for squat analysis
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]

            # Calculate knee angles
            left_knee_angle = self._calculate_angle(
                [left_hip['x'], left_hip['y']],
                [left_knee['x'], left_knee['y']],
                [left_ankle['x'], left_ankle['y']]
            )

            right_knee_angle = self._calculate_angle(
                [right_hip['x'], right_hip['y']],
                [right_knee['x'], right_knee['y']],
                [right_ankle['x'], right_ankle['y']]
            )

            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2

            # Count reps based on knee angle with better thresholds
            if self.state == "up" and avg_knee_angle < 120:
                self.state = "down"
            elif self.state == "down" and avg_knee_angle > 160:
                self.state = "up"
                self.rep_count += 1

            # Calculate form score
            form_score = self._calculate_squat_form_score(avg_knee_angle)

            # Generate feedback
            feedback = self._generate_squat_feedback(avg_knee_angle)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "knee_angle": round(avg_knee_angle, 1),
                "state": self.state
            }

        except Exception as e:
            logging.error(f"Error in squat analysis: {e}")
            return {"error": "Squat analysis failed"}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def _calculate_squat_form_score(self, knee_angle: float) -> float:
        """Calculate overall form score for squat"""
        # Ideal knee angle range: 80-120 degrees at bottom, 160-180 at top
        if 80 <= knee_angle <= 120 or 160 <= knee_angle <= 180:
            return 100
        elif 120 < knee_angle < 160:
            # Transition zone
            return 70
        else:
            return max(0, 100 - abs(knee_angle - 100) * 1.5)

    def _generate_squat_feedback(self, knee_angle: float) -> List[str]:
        """Generate feedback for squat form"""
        feedback = []

        if knee_angle < 80:
            feedback.append("Don't squat too deep")
        elif knee_angle <= 120 and self.state == "down":
            feedback.append("Perfect depth! Now stand up")
        elif knee_angle > 130 and knee_angle < 160:
            feedback.append("Stand up completely")
        elif knee_angle >= 160:
            feedback.append("Great squat!")

        if not feedback:
            feedback.append("Excellent form!")

        return feedback


class JumpingJackCounter:
    """Jumping jack form analysis and counting"""

    def __init__(self):
        self.state = "closed"  # closed, open
        self.rep_count = 0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        """Analyze jumping jack form and count reps"""
        try:
            # Get key points
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            nose = landmarks[0]

            # Calculate spreads
            arm_spread = abs(right_wrist['x'] - left_wrist['x'])
            leg_spread = abs(right_ankle['x'] - left_ankle['x'])

            # Normalize by body height
            body_height = abs(nose['y'] - min(left_ankle['y'], right_ankle['y']))
            arm_ratio = arm_spread / body_height if body_height > 0 else 0
            leg_ratio = leg_spread / body_height if body_height > 0 else 0

            # Determine position
            is_open = arm_ratio > 0.3 and leg_ratio > 0.2

            # Count reps
            if self.state == "closed" and is_open:
                self.state = "open"
            elif self.state == "open" and not is_open:
                self.state = "closed"
                self.rep_count += 1

            # Calculate form score
            form_score = self._calculate_jumping_jack_form_score(arm_ratio, leg_ratio)

            # Generate feedback
            feedback = self._generate_jumping_jack_feedback(arm_ratio, leg_ratio)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "state": self.state,
                "arm_ratio": round(arm_ratio, 2),
                "leg_ratio": round(leg_ratio, 2)
            }

        except Exception as e:
            logging.error(f"Error in jumping jack analysis: {e}")
            return {"error": "Jumping jack analysis failed"}

    def _calculate_jumping_jack_form_score(self, arm_ratio: float, leg_ratio: float) -> float:
        """Calculate overall form score for jumping jack"""
        # Good coordination when arms and legs move together
        coordination_diff = abs(arm_ratio - leg_ratio)
        coordination_score = max(0, 100 - (coordination_diff * 200))
        
        # Good range of motion
        range_score = min(100, (arm_ratio + leg_ratio) * 100)
        
        return (coordination_score * 0.6) + (range_score * 0.4)

    def _generate_jumping_jack_feedback(self, arm_ratio: float, leg_ratio: float) -> List[str]:
        """Generate feedback for jumping jack form"""
        feedback = []

        if arm_ratio < 0.2:
            feedback.append("Raise your arms higher")
        if leg_ratio < 0.15:
            feedback.append("Jump with wider legs")
        
        coordination_diff = abs(arm_ratio - leg_ratio)
        if coordination_diff > 0.1:
            feedback.append("Coordinate arms and legs together")
        
        if not feedback:
            feedback.append("Perfect jumping jacks!")

        return feedback


class PlankCounter:
    """Plank hold-time and alignment analysis.

    Unlike the rep-based counters above, a plank has no discrete rep —
    quality is about sustaining a straight shoulder-hip-ankle line over
    time. We track elapsed hold duration in seconds, and count each
    completed 10-second block as one "rep" so downstream code
    (gamification XP, /api/complete-session rep_form_scores) that
    expects a rep count + per-rep form scores keeps working unchanged.

    A hold resets (rep progress lost, timer restarts) if form breaks
    badly (form_score below FORM_BREAK_THRESHOLD) for several
    consecutive frames — this treats a real hip-sag/pike collapse as
    ending that hold, rather than the user just re-triggering the pose
    exactly, in-line with the drills already defined in
    injury_risk_engine.py's CORRECTIVE_DRILLS for "plank".
    """

    HOLD_BLOCK_SECONDS = 10.0
    FORM_BREAK_THRESHOLD = 40.0
    BREAK_FRAME_LIMIT = 5  # consecutive bad frames before we reset the hold

    def __init__(self):
        self.rep_count = 0
        self.hold_start_time: Optional[float] = None
        self.consecutive_bad_frames = 0
        self.elapsed_in_current_block = 0.0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        """Analyze plank alignment and track hold duration."""
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]

            shoulder_mid = self._midpoint(left_shoulder, right_shoulder)
            hip_mid = self._midpoint(left_hip, right_hip)
            ankle_mid = self._midpoint(left_ankle, right_ankle)

            # Unsigned bend angle at the hip — how far the body is from a
            # straight line, regardless of direction.
            alignment_angle = self._calculate_angle(
                [shoulder_mid['x'], shoulder_mid['y']],
                [hip_mid['x'], hip_mid['y']],
                [ankle_mid['x'], ankle_mid['y']]
            )

            # Signed perpendicular offset of the hip from the
            # shoulder-ankle line, via the z-component of the cross
            # product (line vector) x (shoulder-to-hip vector). This is
            # what actually tells sag apart from pike — the unsigned
            # angle alone can't, since both bend the line by a similar
            # magnitude in opposite directions.
            line_x = ankle_mid['x'] - shoulder_mid['x']
            line_y = ankle_mid['y'] - shoulder_mid['y']
            hip_x = hip_mid['x'] - shoulder_mid['x']
            hip_y = hip_mid['y'] - shoulder_mid['y']
            cross_z = line_x * hip_y - line_y * hip_x
            # Positive cross_z: hip sits below the shoulder-ankle line in
            # image coordinates (y grows downward) => hips sagging down.
            # Negative: hip sits above the line => hips piked up.
            is_sagging = cross_z > 0

            form_score = self._calculate_plank_form_score(alignment_angle)
            feedback = self._generate_plank_feedback(alignment_angle, is_sagging, form_score)

            now = time.time()
            if form_score < self.FORM_BREAK_THRESHOLD:
                self.consecutive_bad_frames += 1
                if self.consecutive_bad_frames >= self.BREAK_FRAME_LIMIT:
                    # Hold broken — reset the in-progress block, keep
                    # completed reps (blocks) already banked.
                    self.hold_start_time = None
                    self.elapsed_in_current_block = 0.0
                    self.consecutive_bad_frames = 0
            else:
                self.consecutive_bad_frames = 0
                if self.hold_start_time is None:
                    self.hold_start_time = now
                self.elapsed_in_current_block = now - self.hold_start_time

                if self.elapsed_in_current_block >= self.HOLD_BLOCK_SECONDS:
                    self.rep_count += 1
                    self.hold_start_time = now
                    self.elapsed_in_current_block = 0.0

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "alignment_angle": round(alignment_angle, 1),
                "hold_seconds_in_block": round(self.elapsed_in_current_block, 1)
            }

        except Exception as e:
            logging.error(f"Error in plank analysis: {e}")
            return {"error": "Plank analysis failed"}

    def _midpoint(self, a: Dict, b: Dict) -> Dict:
        return {"x": (a['x'] + b['x']) / 2, "y": (a['y'] + b['y']) / 2}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculate angle between three points (identical to other counters)."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def _calculate_plank_form_score(self, alignment_angle: float) -> float:
        """Ideal plank alignment is a straight line, ~165-180 degrees at the hip."""
        deviation = abs(180 - alignment_angle)
        if deviation <= 10:
            return 100.0
        elif deviation <= 25:
            return max(0.0, 100 - (deviation - 10) * 3)
        else:
            return max(0.0, 55 - (deviation - 25) * 2)

    def _generate_plank_feedback(self, alignment_angle: float, is_sagging: bool, form_score: float) -> List[str]:
        feedback = []
        deviation = abs(180 - alignment_angle)

        if deviation > 15:
            if is_sagging:
                feedback.append("Hips are sagging — engage your core and lift them up")
            else:
                feedback.append("Hips are too high — lower into a straight line")

        if not feedback:
            if form_score >= 90:
                feedback.append("Great plank line — hold it")
            else:
                feedback.append("Almost straight — small adjustment to your hip height")

        return feedback

class LungeCounter:
    """Lunge form analysis and counting.

    Rep is driven by the deeper (front) knee's hip-knee-ankle angle,
    same convention as SquatCounter. Form adds two lunge-specific
    checks squats don't need: front knee shouldn't travel past the
    toes, and the torso should stay upright rather than folding
    forward for momentum.
    """

    def __init__(self):
        self.state = "up"  # up, down
        self.rep_count = 0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]

            left_knee_angle = self._calculate_angle(
                [left_hip['x'], left_hip['y']], [left_knee['x'], left_knee['y']], [left_ankle['x'], left_ankle['y']]
            )
            right_knee_angle = self._calculate_angle(
                [right_hip['x'], right_hip['y']], [right_knee['x'], right_knee['y']], [right_ankle['x'], right_ankle['y']]
            )

            # The front (working) leg is whichever is more bent this frame.
            front_is_left = left_knee_angle <= right_knee_angle
            front_knee_angle = left_knee_angle if front_is_left else right_knee_angle
            front_knee = left_knee if front_is_left else right_knee
            front_ankle = left_ankle if front_is_left else right_ankle

            hip_mid = self._midpoint(left_hip, right_hip)
            shoulder_mid = self._midpoint(left_shoulder, right_shoulder)
            hip_width = abs(left_hip['x'] - right_hip['x']) or 0.15

            # Knee-over-toe: how far the front knee has traveled past the
            # front ankle horizontally, normalized by hip width.
            knee_forward_offset = abs(front_knee['x'] - front_ankle['x']) / hip_width

            # Torso lean: horizontal drift of shoulders from hips,
            # normalized by hip width. Near zero = upright.
            torso_lean = abs(shoulder_mid['x'] - hip_mid['x']) / hip_width

            min_knee_angle = min(left_knee_angle, right_knee_angle)

            if self.state == "up" and min_knee_angle < 100:
                self.state = "down"
            elif self.state == "down" and min_knee_angle > 160:
                self.state = "up"
                self.rep_count += 1

            form_score = self._calculate_form_score(front_knee_angle, knee_forward_offset, torso_lean)
            feedback = self._generate_feedback(front_knee_angle, knee_forward_offset, torso_lean)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "front_knee_angle": round(front_knee_angle, 1),
                "state": self.state
            }
        except Exception as e:
            logging.error(f"Error in lunge analysis: {e}")
            return {"error": "Lunge analysis failed"}

    def _midpoint(self, a: Dict, b: Dict) -> Dict:
        return {"x": (a['x'] + b['x']) / 2, "y": (a['y'] + b['y']) / 2}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        a = np.array(a); b = np.array(b); c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def _calculate_form_score(self, front_knee_angle: float, knee_forward_offset: float, torso_lean: float) -> float:
        if 80 <= front_knee_angle <= 100 or 160 <= front_knee_angle <= 180:
            depth_score = 100
        elif 100 < front_knee_angle < 160:
            depth_score = 70
        else:
            depth_score = max(0, 100 - abs(front_knee_angle - 90) * 2)

        knee_position_score = max(0, 100 - max(0, knee_forward_offset - 0.4) * 150)
        torso_score = max(0, 100 - torso_lean * 150)

        return (depth_score * 0.5) + (knee_position_score * 0.3) + (torso_score * 0.2)

    def _generate_feedback(self, front_knee_angle: float, knee_forward_offset: float, torso_lean: float) -> List[str]:
        feedback = []
        if knee_forward_offset > 0.55:
            feedback.append("Keep your front knee behind your toes")
        if torso_lean > 0.4:
            feedback.append("Keep your torso upright, don't lean forward")
        if front_knee_angle < 80:
            feedback.append("Don't drop too low on the front knee")
        elif 100 < front_knee_angle < 160:
            feedback.append("Lower further for a full lunge")
        if not feedback:
            feedback.append("Great lunge form!")
        return feedback


class BicepCurlCounter:
    """Bicep curl form analysis and counting.

    Rep driven by elbow angle (shoulder-elbow-wrist), averaged across
    both arms. Form penalizes "swinging" — the elbow drifting away
    from the torso to use momentum instead of the bicep.
    """

    def __init__(self):
        self.state = "extended"  # extended, curled
        self.rep_count = 0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_elbow = landmarks[13]
            right_elbow = landmarks[14]
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            left_hip = landmarks[23]
            right_hip = landmarks[24]

            left_angle = self._calculate_angle(
                [left_shoulder['x'], left_shoulder['y']], [left_elbow['x'], left_elbow['y']], [left_wrist['x'], left_wrist['y']]
            )
            right_angle = self._calculate_angle(
                [right_shoulder['x'], right_shoulder['y']], [right_elbow['x'], right_elbow['y']], [right_wrist['x'], right_wrist['y']]
            )
            avg_angle = (left_angle + right_angle) / 2

            shoulder_mid = self._midpoint(left_shoulder, right_shoulder)
            hip_mid = self._midpoint(left_hip, right_hip)
            torso_len = abs(shoulder_mid['y'] - hip_mid['y']) or 0.3

            elbow_mid_x = (left_elbow['x'] + right_elbow['x']) / 2
            elbow_swing = abs(elbow_mid_x - shoulder_mid['x']) / torso_len

            if self.state == "extended" and avg_angle < 50:
                self.state = "curled"
            elif self.state == "curled" and avg_angle > 150:
                self.state = "extended"
                self.rep_count += 1

            form_score = self._calculate_form_score(avg_angle, elbow_swing)
            feedback = self._generate_feedback(avg_angle, elbow_swing)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "elbow_angle": round(avg_angle, 1),
                "state": self.state
            }
        except Exception as e:
            logging.error(f"Error in bicep curl analysis: {e}")
            return {"error": "Bicep curl analysis failed"}

    def _midpoint(self, a: Dict, b: Dict) -> Dict:
        return {"x": (a['x'] + b['x']) / 2, "y": (a['y'] + b['y']) / 2}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        a = np.array(a); b = np.array(b); c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def _calculate_form_score(self, angle: float, elbow_swing: float) -> float:
        if angle <= 50 or angle >= 150:
            angle_score = 100
        elif 50 < angle < 150:
            angle_score = 70
        else:
            angle_score = max(0, 100 - abs(angle - 100))

        stability_score = max(0, 100 - max(0, elbow_swing - 0.15) * 300)
        return (angle_score * 0.7) + (stability_score * 0.3)

    def _generate_feedback(self, angle: float, elbow_swing: float) -> List[str]:
        feedback = []
        if elbow_swing > 0.3:
            feedback.append("Keep your elbow pinned to your side, don't swing")
        if angle < 50 and self.state == "curled":
            feedback.append("Good squeeze at the top! Now lower slowly")
        elif angle > 150:
            feedback.append("Nice full extension")
        if not feedback:
            feedback.append("Great curl form!")
        return feedback


class MountainClimberCounter:
    """Mountain climber form analysis and counting.

    Each leg is tracked independently by the hip angle (shoulder-hip-
    knee) — driving a knee toward the chest closes this angle, and
    each leg's drive->reset cycle counts as one rep, matching how most
    fitness apps count mountain climbers (both legs contribute).
    Quality is scored primarily on keeping the plank line (hips level,
    reusing the same shoulder-hip-ankle alignment idea as PlankCounter)
    while the legs move.
    """

    DRIVE_THRESHOLD = 100.0
    RESET_THRESHOLD = 155.0

    def __init__(self):
        self.rep_count = 0
        self.left_state = "extended"
        self.right_state = "extended"

    def analyze(self, landmarks: List[Dict]) -> Dict:
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]

            left_hip_angle = self._calculate_angle(
                [left_shoulder['x'], left_shoulder['y']], [left_hip['x'], left_hip['y']], [left_knee['x'], left_knee['y']]
            )
            right_hip_angle = self._calculate_angle(
                [right_shoulder['x'], right_shoulder['y']], [right_hip['x'], right_hip['y']], [right_knee['x'], right_knee['y']]
            )

            if self.left_state == "extended" and left_hip_angle < self.DRIVE_THRESHOLD:
                self.left_state = "driven"
            elif self.left_state == "driven" and left_hip_angle > self.RESET_THRESHOLD:
                self.left_state = "extended"
                self.rep_count += 1

            if self.right_state == "extended" and right_hip_angle < self.DRIVE_THRESHOLD:
                self.right_state = "driven"
            elif self.right_state == "driven" and right_hip_angle > self.RESET_THRESHOLD:
                self.right_state = "extended"
                self.rep_count += 1

            shoulder_mid = self._midpoint(left_shoulder, right_shoulder)
            hip_mid = self._midpoint(left_hip, right_hip)
            ankle_mid = self._midpoint(left_ankle, right_ankle)
            plank_angle = self._calculate_angle(
                [shoulder_mid['x'], shoulder_mid['y']], [hip_mid['x'], hip_mid['y']], [ankle_mid['x'], ankle_mid['y']]
            )
            plank_deviation = abs(180 - plank_angle)

            drive_depth = min(left_hip_angle, right_hip_angle)
            form_score = self._calculate_form_score(plank_deviation, drive_depth)
            feedback = self._generate_feedback(plank_deviation, drive_depth)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "plank_deviation": round(plank_deviation, 1)
            }
        except Exception as e:
            logging.error(f"Error in mountain climber analysis: {e}")
            return {"error": "Mountain climber analysis failed"}

    def _midpoint(self, a: Dict, b: Dict) -> Dict:
        return {"x": (a['x'] + b['x']) / 2, "y": (a['y'] + b['y']) / 2}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        a = np.array(a); b = np.array(b); c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def _calculate_form_score(self, plank_deviation: float, drive_depth: float) -> float:
        plank_score = max(0, 100 - plank_deviation * 3)
        drive_score = 100 if drive_depth < self.DRIVE_THRESHOLD else max(0, 100 - (drive_depth - self.DRIVE_THRESHOLD))
        return (plank_score * 0.6) + (drive_score * 0.4)

    def _generate_feedback(self, plank_deviation: float, drive_depth: float) -> List[str]:
        feedback = []
        if plank_deviation > 15:
            feedback.append("Keep your hips level — don't let them rise or sag while climbing")
        if drive_depth > self.DRIVE_THRESHOLD + 15:
            feedback.append("Drive your knee further toward your chest")
        if not feedback:
            feedback.append("Great pace and form!")
        return feedback


class SitupCounter:
    """Sit-up / crunch form analysis and counting.

    Rep driven by torso angle at the hip (shoulder-hip-knee): near
    straight while lying back, closing sharply on the crunch up. Form
    penalizes using the legs/momentum instead of the abs — flagged
    when the knee angle straightens out sharply during the crunch,
    which usually means the person kicked their legs to help lift.
    """

    def __init__(self):
        self.state = "lying"  # lying, crunched
        self.rep_count = 0

    def analyze(self, landmarks: List[Dict]) -> Dict:
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]

            left_torso_angle = self._calculate_angle(
                [left_shoulder['x'], left_shoulder['y']], [left_hip['x'], left_hip['y']], [left_knee['x'], left_knee['y']]
            )
            right_torso_angle = self._calculate_angle(
                [right_shoulder['x'], right_shoulder['y']], [right_hip['x'], right_hip['y']], [right_knee['x'], right_knee['y']]
            )
            avg_torso_angle = (left_torso_angle + right_torso_angle) / 2

            left_knee_angle = self._calculate_angle(
                [left_hip['x'], left_hip['y']], [left_knee['x'], left_knee['y']], [left_ankle['x'], left_ankle['y']]
            )
            right_knee_angle = self._calculate_angle(
                [right_hip['x'], right_hip['y']], [right_knee['x'], right_knee['y']], [right_ankle['x'], right_ankle['y']]
            )
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2

            if self.state == "lying" and avg_torso_angle < 100:
                self.state = "crunched"
            elif self.state == "crunched" and avg_torso_angle > 150:
                self.state = "lying"
                self.rep_count += 1

            form_score = self._calculate_form_score(avg_torso_angle, avg_knee_angle)
            feedback = self._generate_feedback(avg_torso_angle, avg_knee_angle)

            return {
                "reps": self.rep_count,
                "form_score": round(form_score, 1),
                "feedback": feedback,
                "torso_angle": round(avg_torso_angle, 1),
                "state": self.state
            }
        except Exception as e:
            logging.error(f"Error in situp analysis: {e}")
            return {"error": "Situp analysis failed"}

    def _calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        a = np.array(a); b = np.array(b); c = np.array(c)
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def _calculate_form_score(self, torso_angle: float, knee_angle: float) -> float:
        if torso_angle <= 100 or torso_angle >= 160:
            rom_score = 100
        elif 100 < torso_angle < 160:
            rom_score = 70
        else:
            rom_score = max(0, 100 - abs(torso_angle - 130))

        knee_stability_score = 100 if knee_angle < 140 else max(0, 100 - (knee_angle - 140) * 3)
        return (rom_score * 0.7) + (knee_stability_score * 0.3)

    def _generate_feedback(self, torso_angle: float, knee_angle: float) -> List[str]:
        feedback = []
        if knee_angle >= 140:
            feedback.append("Keep your knees bent, don't kick your legs to cheat the rep")
        if 100 < torso_angle < 150 and self.state == "crunched":
            feedback.append("Curl up higher for a full rep")
        elif torso_angle <= 100:
            feedback.append("Good crunch! Now lower with control")
        elif torso_angle >= 150:
            feedback.append("Don't use momentum — control the movement")
        if not feedback:
            feedback.append("Great sit-up form!")
        return feedback