"""
Kinesis AI - Yoga Service
Analyzes yoga poses using MediaPipe pose landmarks.
Supports Warrior II, Tree Pose, Downward Dog, Cobra, Triangle, and Mountain Pose.
"""

import math
import logging
from pose_detection import (
    calculate_angle, calculate_symmetry, calculate_stability,
    get_landmark_xy, landmarks_visible,
    NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
    LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
    LEFT_ANKLE, RIGHT_ANKLE, LEFT_HEEL, RIGHT_HEEL, LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX
)

logger = logging.getLogger(__name__)

YOGA_POSES = {
    'warrior_2': {
        'name': 'Warrior II (Virabhadrasana II)',
        'target': 'Strength & Hip Mobility',
        'difficulty': 'Intermediate',
        'description': 'A standing posture that strengthens the legs, opens the hips, and stretches the chest.'
    },
    'tree_pose': {
        'name': 'Tree Pose (Vrikshasana)',
        'target': 'Balance & Stability',
        'difficulty': 'Beginner',
        'description': 'A balancing posture that strengthens ankles, calves, and promotes mental focus.'
    },
    'downward_dog': {
        'name': 'Downward-Facing Dog (Adho Mukha Svanasana)',
        'target': 'Hamstring & Shoulder Flexibility',
        'difficulty': 'Beginner',
        'description': 'An inversion that energizes the body, strengthens arms and legs, and stretches the spine.'
    },
    'cobra_pose': {
        'name': 'Cobra Pose (Bhujangasana)',
        'target': 'Spine Flexibility & Core',
        'difficulty': 'Beginner',
        'description': 'A gentle backbend that stretches chest, shoulders, and strengthens the spine.'
    },
    'triangle_pose': {
        'name': 'Triangle Pose (Trikonasana)',
        'target': 'Hamstrings & Lateral Flexibility',
        'difficulty': 'Intermediate',
        'description': 'A standing side stretch that improves posture, balance, and spine flexibility.'
    },
    'mountain_pose': {
        'name': 'Mountain Pose (Tadasana)',
        'target': 'Posture & Alignment',
        'difficulty': 'Beginner',
        'description': 'The foundation of all standing poses, promoting alignment and steady breathing.'
    }
}


class YogaPoseAnalyzer:
    """Analyzes yoga postures from 33 body landmarks."""

    def __init__(self, pose_type='warrior_2'):
        self.pose_type = pose_type

    def analyze(self, landmarks):
        """Analyze landmarks for the current pose and return score, metrics, and corrections."""
        if self.pose_type == 'warrior_2':
            return self._analyze_warrior_2(landmarks)
        elif self.pose_type == 'tree_pose':
            return self._analyze_tree_pose(landmarks)
        elif self.pose_type == 'downward_dog':
            return self._analyze_downward_dog(landmarks)
        elif self.pose_type == 'cobra_pose':
            return self._analyze_cobra(landmarks)
        elif self.pose_type == 'triangle_pose':
            return self._analyze_triangle(landmarks)
        elif self.pose_type == 'mountain_pose':
            return self._analyze_mountain(landmarks)
        else:
            return self._analyze_warrior_2(landmarks)

    def _analyze_warrior_2(self, lm):
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        r_sh = get_landmark_xy(lm, RIGHT_SHOULDER)
        l_el = get_landmark_xy(lm, LEFT_ELBOW)
        r_el = get_landmark_xy(lm, RIGHT_ELBOW)
        l_wr = get_landmark_xy(lm, LEFT_WRIST)
        r_wr = get_landmark_xy(lm, RIGHT_WRIST)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ank = get_landmark_xy(lm, LEFT_ANKLE)
        r_ank = get_landmark_xy(lm, RIGHT_ANKLE)

        # Arms should be horizontal (180 deg shoulder-elbow-wrist & level height)
        l_arm_angle = calculate_angle(l_sh, l_el, l_wr)
        r_arm_angle = calculate_angle(r_sh, r_el, r_wr)
        arm_straightness = (l_arm_angle + r_arm_angle) / 2

        # Arm height level with shoulders
        arm_level_diff = abs((l_wr[1] - l_sh[1]) + (r_wr[1] - r_sh[1])) * 100

        # One knee should bend ~90, the other straight ~180
        l_knee_angle = calculate_angle(l_hip, l_knee, l_ank)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ank)
        front_knee = min(l_knee_angle, r_knee_angle)
        back_knee = max(l_knee_angle, r_knee_angle)

        score = 100.0
        corrections = []
        positives = []

        # Check front knee ~90
        if 80 <= front_knee <= 105:
            positives.append("Excellent front knee flexion (near 90°)")
        elif front_knee > 115:
            score -= 15
            corrections.append("Bend your front knee deeper towards 90°")
        elif front_knee < 75:
            score -= 15
            corrections.append("Don't over-bend front knee past your ankle")

        # Check back leg straight ~170+
        if back_knee >= 165:
            positives.append("Back leg is well engaged and straight")
        else:
            score -= 15
            corrections.append("Keep your back leg straight and grounded")

        # Check arms straight and parallel
        if arm_straightness >= 160:
            positives.append("Strong arm extension")
        else:
            score -= 10
            corrections.append("Extend your arms straight at shoulder height")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Warrior II',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'front_knee_angle': front_knee,
                'back_knee_angle': back_knee,
                'arm_straightness': round(arm_straightness, 1)
            }
        }

    def _analyze_tree_pose(self, lm):
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ank = get_landmark_xy(lm, LEFT_ANKLE)
        r_ank = get_landmark_xy(lm, RIGHT_ANKLE)
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        r_sh = get_landmark_xy(lm, RIGHT_SHOULDER)

        l_knee_angle = calculate_angle(l_hip, l_knee, l_ank)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ank)

        standing_leg_angle = max(l_knee_angle, r_knee_angle)
        bent_leg_angle = min(l_knee_angle, r_knee_angle)

        score = 100.0
        corrections = []
        positives = []

        if standing_leg_angle >= 165:
            positives.append("Solid standing leg base")
        else:
            score -= 20
            corrections.append("Straighten your supporting leg firmly")

        if bent_leg_angle <= 70:
            positives.append("Good hip opening on bent leg")
        elif bent_leg_angle > 90:
            score -= 15
            corrections.append("Bring the sole of your foot higher on inner thigh or calf (avoid the knee joint)")

        # Torso verticality
        mid_sh = ((l_sh[0] + r_sh[0])/2, (l_sh[1] + r_sh[1])/2)
        mid_hip = ((l_hip[0] + r_hip[0])/2, (l_hip[1] + r_hip[1])/2)
        tilt = abs(mid_sh[0] - mid_hip[0]) * 100
        if tilt < 5:
            positives.append("Great upright spine posture")
        else:
            score -= 10
            corrections.append("Keep your spine upright and avoid leaning sideways")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Tree Pose',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'standing_leg_angle': standing_leg_angle,
                'bent_leg_angle': bent_leg_angle,
                'torso_tilt': round(tilt, 2)
            }
        }

    def _analyze_downward_dog(self, lm):
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        l_ank = get_landmark_xy(lm, LEFT_ANKLE)
        l_wr = get_landmark_xy(lm, LEFT_WRIST)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)

        hip_angle = calculate_angle(l_sh, l_hip, l_ank)
        knee_angle = calculate_angle(l_hip, l_knee, l_ank)
        shoulder_angle = calculate_angle(l_wr, l_sh, l_hip)

        score = 100.0
        corrections = []
        positives = []

        if 65 <= hip_angle <= 100:
            positives.append("Great inverted V shape at the hips")
        else:
            score -= 20
            corrections.append("Lift your hips up and back to form an inverted V shape")

        if knee_angle >= 160:
            positives.append("Legs well extended")
        else:
            score -= 10
            corrections.append("Gently lengthen through your hamstrings and heels")

        if shoulder_angle >= 150:
            positives.append("Open chest and shoulders")
        else:
            score -= 10
            corrections.append("Press firmly into your palms and lengthen through shoulders")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Downward Dog',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'hip_angle': hip_angle,
                'knee_angle': knee_angle,
                'shoulder_angle': shoulder_angle
            }
        }

    def _analyze_cobra(self, lm):
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        l_el = get_landmark_xy(lm, LEFT_ELBOW)
        l_wr = get_landmark_xy(lm, LEFT_WRIST)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)

        back_arch = calculate_angle(l_sh, l_hip, l_knee)
        elbow_angle = calculate_angle(l_sh, l_el, l_wr)

        score = 100.0
        corrections = []
        positives = []

        if 130 <= back_arch <= 165:
            positives.append("Healthy spinal extension")
        else:
            score -= 15
            corrections.append("Gently lift your chest using your back muscles without straining")

        if elbow_angle < 160:
            positives.append("Elbows soft and tucked close to ribs")
        else:
            score -= 10
            corrections.append("Keep a soft bend in your elbows and shoulders away from ears")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Cobra Pose',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'back_arch_angle': back_arch,
                'elbow_angle': elbow_angle
            }
        }

    def _analyze_triangle(self, lm):
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        r_hip = get_landmark_xy(lm, RIGHT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        r_knee = get_landmark_xy(lm, RIGHT_KNEE)
        l_ank = get_landmark_xy(lm, LEFT_ANKLE)
        r_ank = get_landmark_xy(lm, RIGHT_ANKLE)
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        r_sh = get_landmark_xy(lm, RIGHT_SHOULDER)

        l_knee_angle = calculate_angle(l_hip, l_knee, l_ank)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ank)

        score = 100.0
        corrections = []
        positives = []

        if l_knee_angle >= 160 and r_knee_angle >= 160:
            positives.append("Both legs straight and engaged")
        else:
            score -= 15
            corrections.append("Keep both legs straight without locking the front knee")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Triangle Pose',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'left_knee_angle': l_knee_angle,
                'right_knee_angle': r_knee_angle
            }
        }

    def _analyze_mountain(self, lm):
        l_sh = get_landmark_xy(lm, LEFT_SHOULDER)
        l_hip = get_landmark_xy(lm, LEFT_HIP)
        l_knee = get_landmark_xy(lm, LEFT_KNEE)
        l_ank = get_landmark_xy(lm, LEFT_ANKLE)

        body_line = calculate_angle(l_sh, l_hip, l_ank)
        knee_line = calculate_angle(l_hip, l_knee, l_ank)

        score = 100.0
        corrections = []
        positives = []

        if body_line >= 170:
            positives.append("Excellent neutral spine alignment")
        else:
            score -= 15
            corrections.append("Align ears, shoulders, hips, and ankles in one vertical line")

        if knee_line >= 170:
            positives.append("Legs grounded and active")
        else:
            score -= 10
            corrections.append("Straighten knees gently without hyperextending")

        score = max(0, min(100, round(score, 1)))
        return {
            'pose': 'Mountain Pose',
            'score': score,
            'positives': positives,
            'corrections': corrections,
            'metrics': {
                'body_alignment': body_line,
                'knee_alignment': knee_line
            }
        }
