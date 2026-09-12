import numpy as np
from collections import deque
from pose_detection import (
    calculate_angle, 
    calculate_distance, 
    calculate_symmetry, 
    calculate_stability, 
    calculate_range_of_motion, 
    get_landmark_xy,
    LEFT_SHOULDER, RIGHT_SHOULDER,
    LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE,
    LEFT_ANKLE, RIGHT_ANKLE
)

class InjuryRiskEngine:
    """
    Movement-risk indicator system for Kinesis AI.
    WARNING: This is a movement-risk indicator, not a medical diagnosis.
    Consult a qualified coach or healthcare professional if you experience pain or symptoms.
    """
    def __init__(self):
        # History buffers for tracking patterns
        self.angle_history = {}  # {body_part: deque}
        self.asymmetry_history = deque(maxlen=100)
        self.form_score_history = deque(maxlen=100)
        self.alert_count = 0
        self.disclaimer = "This is a movement-risk indicator, not a medical diagnosis. Consult a qualified coach or healthcare professional if you experience pain or symptoms."

    def _get_angle_history(self, body_part):
        if body_part not in self.angle_history:
            self.angle_history[body_part] = deque(maxlen=100)
        return self.angle_history[body_part]

    def analyze(self, landmarks, sport='general') -> dict:
        """
        Analyzes landmarks and returns risk indicators.
        Returns: {risk_level, risk_score, indicators, body_areas, recommendations, disclaimer}
        """
        if not landmarks:
            return {}

        indicators = []
        body_areas = set()
        risk_score = 0.0

        # Check Left/right asymmetry detection
        # Extract landmark coordinates
        left_hip = get_landmark_xy(landmarks, LEFT_HIP)
        left_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        left_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        right_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        right_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        
        # Calculate knee angles for symmetry calculation
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        symmetry = calculate_symmetry(left_knee_angle, right_knee_angle)
        self.asymmetry_history.append(symmetry)
        if symmetry < 0.8:
            indicators.append("Significant knee asymmetry detected.")
            body_areas.add("Knees")
            risk_score += 15.0

        # Check joint-angle deviation (e.g. knee varus/valgus proxy)
        # (Angles already calculated above for symmetry)
        
        self._get_angle_history('left_knee').append(left_knee_angle)
        self._get_angle_history('right_knee').append(right_knee_angle)

        if left_knee_angle < 10 or right_knee_angle < 10:
            indicators.append("Extreme knee angle deviation.")
            body_areas.add("Knees")
            risk_score += 20.0

        # Stability deterioration
        # Create position history for stability calculation
        ankle_positions = [left_ankle, right_ankle]
        stability = calculate_stability(ankle_positions)
        if stability < 0.5:
            indicators.append("Poor lower body stability.")
            body_areas.add("Ankles/Base")
            risk_score += 15.0

        # Sport specific risks
        sport_risks = self.get_sport_specific_risks(landmarks, sport)
        for risk in sport_risks:
            indicators.append(risk['message'])
            if risk.get('area'):
                body_areas.add(risk['area'])
            risk_score += risk.get('weight', 10.0)

        # Repeated poor alignment tracking & fatigue
        if len(self.asymmetry_history) == 100:
            avg_sym = sum(self.asymmetry_history) / 100
            if avg_sym < 0.85:
                indicators.append("Consistent asymmetry indicating fatigue or poor alignment over time.")
                risk_score += 25.0

        risk_score = min(risk_score, 100.0)

        if risk_score > 60:
            risk_level = 'high'
        elif risk_score > 30:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
            if not indicators:
                indicators.append("Movement pattern is within safe limits.")

        recommendations = []
        if 'Knees' in body_areas:
            recommendations.append("Focus on knee tracking over toes during flexion.")
        if 'Ankles/Base' in body_areas:
            recommendations.append("Ensure balanced weight distribution across both feet.")
        if not recommendations:
            recommendations.append("Maintain current form and monitor fatigue.")

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'indicators': indicators,
            'body_areas': list(body_areas),
            'recommendations': recommendations,
            'disclaimer': self.disclaimer
        }

    def get_sport_specific_risks(self, landmarks, sport) -> list:
        risks = []
        if sport.lower() == 'football':
            # Check knee alignment and ankle stability for landing mechanics
            left_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
            right_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
            left_knee = get_landmark_xy(landmarks, LEFT_KNEE)
            right_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
            
            # Calculate distances for symmetry approximation
            ankle_dist = calculate_distance(left_ankle, right_ankle)
            knee_dist = calculate_distance(left_knee, right_knee)
            sym = calculate_symmetry(ankle_dist, knee_dist)
            if sym < 0.7:
                risks.append({'message': 'Unstable ankle alignment, elevated risk for landing mechanics.', 'area': 'Ankles', 'weight': 20})
            
            # For knee symmetry, use angle-based calculation
            left_hip = get_landmark_xy(landmarks, LEFT_HIP)
            right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
            left_ankle_lm = get_landmark_xy(landmarks, LEFT_ANKLE)
            right_ankle_lm = get_landmark_xy(landmarks, RIGHT_ANKLE)
            
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle_lm)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle_lm)
            knee_sym = calculate_symmetry(left_knee_angle, right_knee_angle)
            if knee_sym < 0.7:
                risks.append({'message': 'Poor knee alignment during movement.', 'area': 'Knees', 'weight': 15})
                
        elif sport.lower() == 'cricket':
            # Check lower-back posture proxy (shoulder to hip alignment)
            left_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
            right_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)
            left_hip = get_landmark_xy(landmarks, LEFT_HIP)
            right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
            
            shoulder_dist = calculate_distance(left_shoulder, right_shoulder)
            hip_dist = calculate_distance(left_hip, right_hip)
            if shoulder_dist > 0 and hip_dist / shoulder_dist > 1.5:
                risks.append({'message': 'Uneven shoulder-hip loading detected.', 'area': 'Lower Back/Shoulders', 'weight': 15})
                
        else:
            # General fitness
            left_hip = get_landmark_xy(landmarks, LEFT_HIP)
            right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
            hip_positions = [left_hip, right_hip]
            stability = calculate_stability(hip_positions)
            if stability < 0.6:
                risks.append({'message': 'Inconsistent body alignment detected.', 'area': 'Core/Hips', 'weight': 10})
                
        return risks

    def get_risk_summary(self) -> dict:
        avg_sym = sum(self.asymmetry_history) / len(self.asymmetry_history) if self.asymmetry_history else 1.0
        
        trend = 'Stable'
        if len(self.asymmetry_history) >= 20:
            recent_sym = sum(list(self.asymmetry_history)[-20:]) / 20
            if recent_sym < avg_sym - 0.1:
                trend = 'Deteriorating'
            elif recent_sym > avg_sym + 0.1:
                trend = 'Improving'

        return {
            'overall_trend': trend,
            'average_symmetry': round(avg_sym, 2),
            'history_points_analyzed': len(self.asymmetry_history),
            'disclaimer': self.disclaimer
        }
