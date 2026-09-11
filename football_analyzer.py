import math
import time
from typing import Dict, List, Any, Optional

from pose_detection import (
    NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW, 
    LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, 
    RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE, LEFT_HEEL, RIGHT_HEEL, 
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX,
    calculate_angle, calculate_distance, calculate_midpoint, 
    calculate_velocity, calculate_symmetry, calculate_stability, 
    calculate_range_of_motion, get_landmark_xy, landmarks_visible,
    MovementAnalyzer, AnalysisResult
)

class FootballAnalyzer(MovementAnalyzer):
    def __init__(self):
        super().__init__()
        self.kicking_leg = 'right'
        self.plant_leg = 'left'
        self.shooting_phase = 'setup' # setup, windup, contact, follow_through
        self.last_time = time.time()
        
    def _determine_legs(self, left_ankle_y, right_ankle_y):
        if right_ankle_y < left_ankle_y - 0.05:
            self.kicking_leg = 'right'
            self.plant_leg = 'left'
        elif left_ankle_y < right_ankle_y - 0.05:
            self.kicking_leg = 'left'
            self.plant_leg = 'right'

    def analyze_shooting(self, landmarks) -> AnalysisResult:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        required_landmarks = [
            LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
            LEFT_ANKLE, RIGHT_ANKLE, LEFT_SHOULDER, RIGHT_SHOULDER,
            LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX
        ]
        
        if not landmarks_visible(landmarks, required_landmarks, 0.5):
            return AnalysisResult(0, "Waiting for full body visibility", [], [], {}, False, False, 0.0, [])
            
        left_hip = get_landmark_xy(landmarks, LEFT_HIP)
        right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        left_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        right_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        left_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        right_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        left_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        right_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)
        
        self._determine_legs(left_ankle[1], right_ankle[1])
        
        if self.kicking_leg == 'right':
            kick_hip, kick_knee, kick_ankle = right_hip, right_knee, right_ankle
            plant_hip, plant_knee, plant_ankle = left_hip, left_knee, left_ankle
            kick_shoulder, plant_shoulder = right_shoulder, left_shoulder
        else:
            kick_hip, kick_knee, kick_ankle = left_hip, left_knee, left_ankle
            plant_hip, plant_knee, plant_ankle = right_hip, right_knee, right_ankle
            kick_shoulder, plant_shoulder = left_shoulder, right_shoulder

        kick_knee_angle = calculate_angle(kick_hip, kick_knee, kick_ankle)
        plant_knee_angle = calculate_angle(plant_hip, plant_knee, plant_ankle)
        
        self.angle_history.setdefault('kick_knee', []).append(kick_knee_angle)
        self.angle_history.setdefault('plant_knee', []).append(plant_knee_angle)
        
        torso_angle = calculate_angle(plant_shoulder, plant_hip, (plant_hip[0], 0))
        
        score_components = {
            'Plant Foot': 0,
            'Hip Rotation': 0,
            'Knee Position': 0,
            'Torso Position': 0,
            'Balance': 0,
            'Follow Through': 0
        }
        feedback = []
        corrections = []
        positives = []
        risk_indicators = []
        
        # Plant leg analysis
        if 160 <= plant_knee_angle <= 180:
            score_components['Plant Foot'] = 15
            positives.append("Stable plant foot with good extension.")
        elif plant_knee_angle < 160:
            score_components['Plant Foot'] = 10
            corrections.append("Straighten plant leg slightly for better stability.")
        
        # Knee flexion of kicking leg
        if kick_knee_angle < 100:
            score_components['Knee Position'] = 20
            positives.append("Excellent knee flexion in windup.")
        elif kick_knee_angle < 130:
            score_components['Knee Position'] = 15
        else:
            score_components['Knee Position'] = 5
            corrections.append("Bend your kicking knee more for increased power.")
            
        # Torso lean
        if 160 <= torso_angle <= 180:
            score_components['Torso Position'] = 15
            positives.append("Good torso position over the ball.")
        elif torso_angle < 160:
            score_components['Torso Position'] = 5
            corrections.append("Lean forward slightly over the ball to keep the shot down.")
            
        # Hip rotation (distance between hips as proxy for rotation)
        hip_dist = calculate_distance(left_hip, right_hip)
        if hip_dist > 0.1:
            score_components['Hip Rotation'] = 15
            positives.append("Good hip rotation.")
        else:
            score_components['Hip Rotation'] = 10
            
        # Balance & Stability
        hip_midpoint = calculate_midpoint(left_hip, right_hip)
        self.position_history.setdefault('center_of_mass', []).append(hip_midpoint)
        stability = calculate_stability(self.position_history['center_of_mass'], window=10)
        
        if stability < 0.05:
            score_components['Balance'] = 15
            positives.append("Excellent balance maintained.")
        else:
            score_components['Balance'] = 8
            corrections.append("Improve core stability during the shot.")
            risk_indicators.append("Poor balance detected, potential for awkward landing.")
            
        # Follow through (if kicking ankle is higher than plant knee after shot)
        if kick_ankle[1] < plant_knee[1]:
            score_components['Follow Through'] = 20
            positives.append("Strong follow through.")
        else:
            score_components['Follow Through'] = 10
            
        # Risk indicators
        if plant_knee_angle < 140 and stability > 0.08:
            risk_indicators.append("Knee alignment warning: excessive bend with instability.")
            
        total_score = sum(score_components.values())
        self.form_score_history.append(total_score)
        
        main_feedback = "Good shooting technique." if total_score > 75 else "Needs improvement on technique."
        if not positives and not corrections:
            main_feedback = "Keep practicing the shooting motion."
            
        fatigue = self.detect_fatigue()
        if fatigue > 0.7:
            risk_indicators.append("High fatigue detected, consider resting to prevent injury.")
            
        metrics = {
            'Kick Knee Angle': f"{kick_knee_angle:.1f}",
            'Plant Knee Angle': f"{plant_knee_angle:.1f}",
            'Torso Angle': f"{torso_angle:.1f}",
            'Stability Index': f"{stability:.3f}"
        }
            
        return AnalysisResult(
            form_score=total_score,
            feedback=main_feedback,
            corrections=corrections,
            positives=positives,
            metrics=metrics,
            rep_counted=False,
            quality_rep=(total_score > 80),
            fatigue_level=fatigue,
            risk_indicators=risk_indicators
        )

    def analyze_dribbling(self, landmarks) -> AnalysisResult:
        # Pose-based dribbling analysis (does NOT track the ball)
        required_landmarks = [
            LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
            LEFT_ANKLE, RIGHT_ANKLE, LEFT_SHOULDER, RIGHT_SHOULDER
        ]
        
        if not landmarks_visible(landmarks, required_landmarks, 0.5):
            return AnalysisResult(0, "Waiting for full body visibility", [], [], {}, False, False, 0.0, [])
            
        left_hip = get_landmark_xy(landmarks, LEFT_HIP)
        right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        left_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        right_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        left_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        right_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)
        
        hip_midpoint = calculate_midpoint(left_hip, right_hip)
        shoulder_midpoint = calculate_midpoint(left_shoulder, right_shoulder)
        
        self.position_history.setdefault('dribble_hips', []).append(hip_midpoint)
        self.position_history.setdefault('dribble_shoulders', []).append(shoulder_midpoint)
        
        stability = calculate_stability(self.position_history['dribble_hips'], window=15)
        
        # Center of gravity (hips relative to shoulders)
        cog_y_diff = hip_midpoint[1] - shoulder_midpoint[1]
        
        left_knee_angle = calculate_angle(left_hip, left_knee, get_landmark_xy(landmarks, LEFT_ANKLE))
        right_knee_angle = calculate_angle(right_hip, right_knee, get_landmark_xy(landmarks, RIGHT_ANKLE))
        
        score_components = {
            'Dribbling Control': 0, # Inferred from pose
            'Body Balance': 0,
            'Change-of-Direction Efficiency': 0,
            'Posture': 0
        }
        
        feedback = []
        corrections = []
        positives = []
        risk_indicators = []
        
        # Posture & Center of gravity (lower is better for dribbling)
        if cog_y_diff > 0.4 and (left_knee_angle < 160 or right_knee_angle < 160):
            score_components['Posture'] = 25
            positives.append("Excellent low center of gravity.")
        else:
            score_components['Posture'] = 15
            corrections.append("Lower your center of gravity by bending knees slightly.")
            
        # Balance
        if stability < 0.03:
            score_components['Body Balance'] = 25
            positives.append("Very stable upper body control.")
        else:
            score_components['Body Balance'] = 15
            corrections.append("Keep your upper body still while your legs move.")
            
        # Change of direction (approximated by hip shift)
        if len(self.position_history['dribble_hips']) > 10:
            prev_hip = self.position_history['dribble_hips'][-10]
            hip_shift = abs(hip_midpoint[0] - prev_hip[0])
            if hip_shift > 0.05:
                score_components['Change-of-Direction Efficiency'] = 25
                positives.append("Good explosive hip shift.")
            else:
                score_components['Change-of-Direction Efficiency'] = 15
        else:
            score_components['Change-of-Direction Efficiency'] = 20
            
        score_components['Dribbling Control'] = 25 # Base score, as we don't track the ball
        
        total_score = sum(score_components.values())
        self.form_score_history.append(total_score)
        
        fatigue = self.detect_fatigue()
        
        metrics = {
            'Center of Gravity': f"{cog_y_diff:.2f}",
            'Left Knee Angle': f"{left_knee_angle:.1f}",
            'Right Knee Angle': f"{right_knee_angle:.1f}",
            'Stability': f"{stability:.3f}"
        }
        
        return AnalysisResult(
            form_score=total_score,
            feedback="Pose-based dribbling analysis active.",
            corrections=corrections,
            positives=positives,
            metrics=metrics,
            rep_counted=False,
            quality_rep=(total_score > 80),
            fatigue_level=fatigue,
            risk_indicators=risk_indicators
        )

    def analyze_agility(self, landmarks, drill_type='side_shuffle') -> AnalysisResult:
        required_landmarks = [
            LEFT_HIP, RIGHT_HIP, LEFT_ANKLE, RIGHT_ANKLE
        ]
        
        if not landmarks_visible(landmarks, required_landmarks, 0.5):
            return AnalysisResult(0, "Waiting for full body visibility", [], [], {}, False, False, 0.0, [])
            
        left_hip = get_landmark_xy(landmarks, LEFT_HIP)
        right_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        left_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        right_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        
        hip_midpoint = calculate_midpoint(left_hip, right_hip)
        self.position_history.setdefault('agility_hips', []).append(hip_midpoint)
        
        metrics = {}
        corrections = []
        positives = []
        risk_indicators = []
        score = 80
        
        # Reaction time (proxy: movement from rest)
        if len(self.position_history['agility_hips']) > 5:
            velocity = calculate_distance(self.position_history['agility_hips'][-1], self.position_history['agility_hips'][-5])
            metrics['Movement Velocity'] = f"{velocity:.3f}"
            if velocity > 0.1:
                score += 10
                positives.append("Explosive movement detected.")
            else:
                score -= 10
                
        # Movement symmetry
        stride_left = calculate_distance(left_hip, left_ankle)
        stride_right = calculate_distance(right_hip, right_ankle)
        symmetry = calculate_symmetry(stride_left, stride_right)
        
        metrics['Stride Symmetry'] = f"{symmetry:.2f}"
        if symmetry > 0.85:
            score += 10
            positives.append("Good movement symmetry.")
        else:
            score -= 10
            corrections.append("Focus on equal push-off from both legs.")
            risk_indicators.append("Asymmetrical movement may indicate compensation or injury risk.")
            
        # Drill specific checks
        if drill_type == 'side_shuffle':
            ankle_dist = calculate_distance(left_ankle, right_ankle)
            if ankle_dist < 0.1:
                corrections.append("Don't let your heels click during shuffle.")
                score -= 10
                
        score = max(0, min(100, score))
        self.form_score_history.append(score)
        
        return AnalysisResult(
            form_score=score,
            feedback=f"Agility analysis: {drill_type}",
            corrections=corrections,
            positives=positives,
            metrics=metrics,
            rep_counted=False,
            quality_rep=(score > 85),
            fatigue_level=self.detect_fatigue(),
            risk_indicators=risk_indicators
        )

    def get_style_coaching(self, style: str) -> dict:
        styles = {
            'technical_dribbler': {
                'style_name': 'Technical Dribbler',
                'description': 'Focuses on close touches, low center of gravity, and rapid direction changes.',
                'focus_areas': ['Close control', 'Agility', 'Acceleration'],
                'coaching_tips': [
                    'Maintain a low center of gravity to improve balance.',
                    'Keep your touches tight and close to your body.',
                    'Use Messi-inspired close-control principles: short strides and quick touches.'
                ]
            },
            'explosive_winger': {
                'style_name': 'Explosive Winger',
                'description': 'Relies on speed, acceleration, and driving past defenders on the outside.',
                'focus_areas': ['Sprint mechanics', 'Explosive start', 'Crossing form'],
                'coaching_tips': [
                    'Drive knees forward during acceleration phase.',
                    'Lean forward slightly when sprinting to maximize momentum.',
                    'Focus on explosive push-off from the plant foot.'
                ]
            },
            'creative_playmaker': {
                'style_name': 'Creative Playmaker',
                'description': 'Emphasizes vision, passing range, and scanning the field.',
                'focus_areas': ['Body shape open to field', 'Passing mechanics', 'Scanning'],
                'coaching_tips': [
                    'Keep your head up and scan before receiving the ball.',
                    'Open your body shape to see as much of the pitch as possible.',
                    'Focus on a smooth follow-through on your passes.'
                ]
            },
            'finishing_focus': {
                'style_name': 'Finishing Focus',
                'description': 'Prioritizes shooting technique, composure, and striking the ball cleanly.',
                'focus_areas': ['Shooting mechanics', 'Balance', 'Composure'],
                'coaching_tips': [
                    'Lock your ankle when striking through the ball.',
                    'Keep your torso over the ball to keep shots low.',
                    'Ensure a strong plant foot pointing towards the target.'
                ]
            },
            'balanced': {
                'style_name': 'Balanced All-Rounder',
                'description': 'A versatile profile focusing on solid fundamentals across all areas.',
                'focus_areas': ['Core fundamentals', 'Stability', 'Endurance'],
                'coaching_tips': [
                    'Maintain good posture and balance in all movements.',
                    'Work on both feet equally to improve versatility.',
                    'Focus on clean technique over raw power.'
                ]
            }
        }
        
        return styles.get(style, styles['balanced'])
