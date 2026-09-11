import math
from pose_detection import (
    NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW, LEFT_WRIST, RIGHT_WRIST,
    LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE, LEFT_HEEL, RIGHT_HEEL,
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX,
    calculate_angle, calculate_distance, calculate_midpoint, calculate_velocity,
    calculate_symmetry, calculate_stability, get_landmark_xy, landmarks_visible,
    MovementAnalyzer, AnalysisResult
)

class CricketAnalyzer(MovementAnalyzer):
    def __init__(self):
        super().__init__()
        self.disclaimer = "This is pose-based analysis. Consult a qualified coach for detailed technique assessment."

    def analyze_pull_shot(self, landmarks):
        feedback = []
        corrections = []
        positives = []
        metrics = {}
        risk_indicators = []
        
        required_landmarks = [NOSE, LEFT_HIP, RIGHT_HIP, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE]
        if not landmarks_visible(landmarks, required_landmarks, 0.5):
            return AnalysisResult(form_score=0, feedback=["Cannot clearly see necessary landmarks for pull shot analysis."], 
                                  corrections=[], positives=[], metrics={}, rep_counted=False, quality_rep=False, 
                                  fatigue_level=0, risk_indicators=[])

        nose = get_landmark_xy(landmarks, NOSE)
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)

        # Track nose position history for head stability
        if 'nose' not in self.position_history:
            self.position_history['nose'] = []
        self.position_history['nose'].append(nose)
        
        stance_score = 100
        weight_transfer_score = 100
        hip_rotation_score = 100
        head_stability_score = 100
        follow_through_score = 100
        
        # Analyze head stability
        if len(self.position_history['nose']) > 5:
            stability = calculate_stability(self.position_history['nose'], window=5)
            if stability > 0.1:
                head_stability_score -= 20
                corrections.append("Keep your head more stable during the shot.")
            else:
                positives.append("Your head remains stable.")
                
        # Analyze weight transfer (back foot emphasis for pull shot)
        # Assuming right handed batsman: weight goes to right leg
        weight_diff = abs(r_knee[0] - r_ankle[0])
        if weight_diff > 0.15:
            weight_transfer_score -= 15
            corrections.append("Weight transfer seems slightly misaligned, ensure you are anchoring well on the back foot.")
        else:
            positives.append("Good back-foot anchor position based on pose.")
            
        # Analyze hip and shoulder rotation
        hip_dist = calculate_distance(l_hip, r_hip)
        shoulder_dist = calculate_distance(l_shoulder, r_shoulder)
        
        if shoulder_dist < 0.05:
            hip_rotation_score -= 20
            corrections.append("Ensure fuller shoulder and hip rotation.")
            
        total_score = (stance_score + weight_transfer_score + hip_rotation_score + head_stability_score + follow_through_score) / 5
        
        feedback.append(f"Pull shot form score: {total_score:.1f}/100. " + self.disclaimer)
        metrics = {
            "stance": stance_score,
            "weight_transfer": weight_transfer_score,
            "hip_rotation": hip_rotation_score,
            "head_stability": head_stability_score,
            "follow_through": follow_through_score
        }

        return AnalysisResult(form_score=total_score, feedback=feedback, corrections=corrections, 
                              positives=positives, metrics=metrics, rep_counted=True, 
                              quality_rep=(total_score > 80), fatigue_level=self.detect_fatigue(), 
                              risk_indicators=risk_indicators)

    def analyze_cover_drive(self, landmarks, kohli_mode=False):
        feedback = []
        corrections = []
        positives = []
        metrics = {}
        risk_indicators = []
        
        required_landmarks = [NOSE, LEFT_KNEE, RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE, LEFT_SHOULDER, RIGHT_SHOULDER]
        if not landmarks_visible(landmarks, required_landmarks, 0.5):
            return AnalysisResult(0, ["Missing key landmarks."], [], [], {}, False, False, 0, [])

        nose = get_landmark_xy(landmarks, NOSE)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        l_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        r_shoulder = get_landmark_xy(landmarks, RIGHT_SHOULDER)
        
        # Front-foot stride and head over front knee (assuming right-handed: left knee is front)
        head_knee_align = abs(nose[0] - l_knee[0])
        score = 100
        
        if head_knee_align > 0.1:
            score -= 20
            corrections.append("Lean forward more to get your head over the front knee.")
        else:
            positives.append("Excellent head-over-knee alignment.")

        if kohli_mode:
            feedback.append("Applying Virat Kohli-inspired technical focus:")
            positives.append("Focusing on strong base, front-foot commitment, stable head, efficient weight transfer, controlled extension, balanced follow-through.")
            
        feedback.append(self.disclaimer)
        metrics['head_alignment'] = head_knee_align
        
        return AnalysisResult(form_score=score, feedback=feedback, corrections=corrections, 
                              positives=positives, metrics=metrics, rep_counted=True, 
                              quality_rep=(score > 80), fatigue_level=self.detect_fatigue(), 
                              risk_indicators=risk_indicators)

    def analyze_straight_drive(self, landmarks):
        feedback = []
        corrections = []
        positives = []
        metrics = {}
        risk_indicators = []
        
        score = 100
        nose = get_landmark_xy(landmarks, NOSE)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        
        if nose and l_knee:
            alignment = abs(nose[0] - l_knee[0])
            if alignment > 0.12:
                score -= 15
                corrections.append("Try to lean slightly more into the drive, head over the front foot.")
            else:
                positives.append("Good head and front foot alignment for a straight drive.")
                
        feedback.append("Analyzed straight drive pose. " + self.disclaimer)
        
        return AnalysisResult(form_score=score, feedback=feedback, corrections=corrections, 
                              positives=positives, metrics=metrics, rep_counted=True, 
                              quality_rep=(score > 80), fatigue_level=self.detect_fatigue(), 
                              risk_indicators=risk_indicators)

    def analyze_batting_stance(self, landmarks):
        feedback = []
        corrections = []
        positives = []
        metrics = {}
        
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        r_knee = get_landmark_xy(landmarks, RIGHT_KNEE)
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        r_hip = get_landmark_xy(landmarks, RIGHT_HIP)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        r_ankle = get_landmark_xy(landmarks, RIGHT_ANKLE)
        
        score = 100
        
        if l_knee and r_knee and l_hip and l_ankle:
            l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            
            if l_knee_angle > 170 or r_knee_angle > 170:
                score -= 20
                corrections.append("Bend your knees slightly more for an athletic stance.")
            else:
                positives.append("Good athletic bend in the knees.")
                
        feedback.append("Analyzed batting stance. " + self.disclaimer)
        
        return AnalysisResult(form_score=score, feedback=feedback, corrections=corrections, 
                              positives=positives, metrics=metrics, rep_counted=True, 
                              quality_rep=(score > 80), fatigue_level=self.detect_fatigue(), 
                              risk_indicators=[])

    def analyze_bowling(self, landmarks):
        feedback = []
        corrections = []
        positives = []
        metrics = {}
        risk_indicators = []
        
        score = 100
        
        l_shoulder = get_landmark_xy(landmarks, LEFT_SHOULDER)
        l_hip = get_landmark_xy(landmarks, LEFT_HIP)
        l_knee = get_landmark_xy(landmarks, LEFT_KNEE)
        l_ankle = get_landmark_xy(landmarks, LEFT_ANKLE)
        
        if l_shoulder and l_hip and l_knee and l_ankle:
            back_angle = calculate_angle(l_shoulder, l_hip, l_knee)
            if back_angle < 150:
                score -= 15
                corrections.append("Avoid over-arching the lower back during the delivery stride.")
                risk_indicators.append("lower-back posture")
                
            front_leg_angle = calculate_angle(l_hip, l_knee, l_ankle)
            if front_leg_angle < 160:
                score -= 10
                corrections.append("Brace the front leg better for optimal energy transfer.")
            else:
                positives.append("Good front-leg stability.")
                
        feedback.append("Analyzed bowling posture. " + self.disclaimer)
        
        return AnalysisResult(form_score=score, feedback=feedback, corrections=corrections, 
                              positives=positives, metrics=metrics, rep_counted=True, 
                              quality_rep=(score > 80), fatigue_level=self.detect_fatigue(), 
                              risk_indicators=risk_indicators)
