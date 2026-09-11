"""
Kinesis AI - Sports Scoring Engine
Unified scoring with consistent /100 format, breakdowns, and feedback generation.
"""

import logging

logger = logging.getLogger(__name__)


def calculate_component_score(value, ideal_min, ideal_max, tolerance=10):
    """
    Calculate a 0-100 score for a metric value against ideal range.
    Full score within ideal range, linear decay outside with tolerance.
    """
    if ideal_min <= value <= ideal_max:
        return 100.0
    if value < ideal_min:
        diff = ideal_min - value
    else:
        diff = value - ideal_max
    penalty = min(100, (diff / max(tolerance, 1)) * 50)
    return round(max(0, 100 - penalty), 1)


def generate_score_breakdown(components):
    """
    Generate a weighted overall score from component scores.
    components: list of (name, score, weight)
    Returns: (overall_score, breakdown_dict)
    """
    total_weight = sum(w for _, _, w in components)
    if total_weight == 0:
        return 0, {}

    weighted_sum = sum(s * w for _, s, w in components)
    overall = round(weighted_sum / total_weight, 1)

    breakdown = {}
    for name, score, weight in components:
        breakdown[name] = round(score, 1)

    return overall, breakdown


def generate_feedback(breakdown, thresholds=None):
    """
    Generate positive and corrective feedback from score breakdown.
    thresholds: dict of {metric: (good_threshold, message_good, message_improve)}
    Returns: (positives, corrections)
    """
    if thresholds is None:
        thresholds = {}

    positives = []
    corrections = []

    for metric, score in breakdown.items():
        if metric in thresholds:
            good_th, msg_good, msg_improve = thresholds[metric]
            if score >= good_th:
                positives.append(f"✓ {msg_good}")
            else:
                corrections.append(f"⚠ {msg_improve}")
        else:
            if score >= 85:
                positives.append(f"✓ Good {metric.replace('_', ' ').title()}")
            elif score < 60:
                corrections.append(f"⚠ Improve {metric.replace('_', ' ').title()}")

    return positives, corrections


def get_score_grade(score):
    """Convert numeric score to letter grade."""
    if score >= 95:
        return 'S'
    elif score >= 85:
        return 'A'
    elif score >= 75:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 40:
        return 'D'
    return 'F'


def get_score_label(score):
    """Convert numeric score to descriptive label."""
    if score >= 90:
        return 'Excellent'
    elif score >= 75:
        return 'Good'
    elif score >= 60:
        return 'Average'
    elif score >= 40:
        return 'Needs Work'
    return 'Poor'


# ---- Sport-Specific Scoring Profiles ----

FOOTBALL_SHOOTING_THRESHOLDS = {
    'plant_foot': (80, 'Stable plant foot', 'Improve plant foot positioning'),
    'hip_rotation': (75, 'Good hip rotation', 'Increase hip rotation for more power'),
    'knee_position': (75, 'Correct knee position', 'Adjust knee flexion angle'),
    'torso_position': (80, 'Good torso position', 'Torso leaning too far backward'),
    'balance': (80, 'Good balance throughout', 'Improve balance during shot'),
    'follow_through': (75, 'Strong follow-through', 'Extend follow-through more'),
}

FOOTBALL_DRIBBLING_THRESHOLDS = {
    'body_balance': (80, 'Stable body balance', 'Lower center of gravity for better balance'),
    'posture': (80, 'Good dribbling posture', 'Keep body more upright'),
    'direction_efficiency': (70, 'Efficient direction changes', 'Work on quicker direction changes'),
    'agility': (75, 'Good agility', 'Improve lateral quickness'),
}

CRICKET_BATTING_THRESHOLDS = {
    'stance': (80, 'Solid batting stance', 'Widen stance for better stability'),
    'weight_transfer': (75, 'Good weight transfer', 'Transfer weight earlier'),
    'hip_rotation': (75, 'Good hip rotation', 'Rotate hips more through the shot'),
    'head_stability': (85, 'Stable head position', 'Keep head still and eyes level'),
    'follow_through': (70, 'Good follow-through', 'Extend follow-through for better timing'),
    'shoulder_alignment': (80, 'Good shoulder alignment', 'Level shoulders through the shot'),
}

CRICKET_BOWLING_THRESHOLDS = {
    'run_up_posture': (75, 'Balanced run-up', 'Maintain upright posture in run-up'),
    'front_arm': (75, 'Good front arm drive', 'Use front arm more effectively'),
    'shoulder_rotation': (80, 'Strong shoulder rotation', 'Increase shoulder rotation'),
    'hip_alignment': (75, 'Good hip alignment', 'Align hips towards target'),
    'front_leg': (80, 'Stable front leg brace', 'Brace front leg more firmly'),
    'follow_through': (70, 'Complete follow-through', 'Follow through towards target'),
}


def score_football_shooting(metrics):
    """Score a football shooting attempt."""
    components = [
        ('plant_foot', metrics.get('plant_foot', 70), 1.0),
        ('hip_rotation', metrics.get('hip_rotation', 70), 1.2),
        ('knee_position', metrics.get('knee_position', 70), 1.0),
        ('torso_position', metrics.get('torso_position', 70), 0.8),
        ('balance', metrics.get('balance', 70), 1.0),
        ('follow_through', metrics.get('follow_through', 70), 1.0),
    ]
    overall, breakdown = generate_score_breakdown(components)
    positives, corrections = generate_feedback(breakdown, FOOTBALL_SHOOTING_THRESHOLDS)
    return {
        'score': overall,
        'grade': get_score_grade(overall),
        'label': get_score_label(overall),
        'breakdown': breakdown,
        'positives': positives,
        'corrections': corrections,
    }


def score_cricket_batting(shot_type, metrics):
    """Score a cricket batting shot."""
    components = [
        ('stance', metrics.get('stance', 70), 1.0),
        ('weight_transfer', metrics.get('weight_transfer', 70), 1.2),
        ('hip_rotation', metrics.get('hip_rotation', 70), 1.0),
        ('head_stability', metrics.get('head_stability', 70), 1.2),
        ('follow_through', metrics.get('follow_through', 70), 0.8),
        ('shoulder_alignment', metrics.get('shoulder_alignment', 70), 0.8),
    ]
    overall, breakdown = generate_score_breakdown(components)
    positives, corrections = generate_feedback(breakdown, CRICKET_BATTING_THRESHOLDS)
    return {
        'score': overall,
        'grade': get_score_grade(overall),
        'label': get_score_label(overall),
        'shot_type': shot_type,
        'breakdown': breakdown,
        'positives': positives,
        'corrections': corrections,
    }
