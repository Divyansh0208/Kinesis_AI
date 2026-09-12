"""
Tests for pose detection and biomechanical calculations.
"""

import pytest
from pose_detection import (
    calculate_angle,
    calculate_angle_3d,
    calculate_distance,
    calculate_distance_3d,
    calculate_symmetry,
    calculate_stability,
    calculate_range_of_motion,
    check_calibration,
    FitnessAnalyzer,
    AnalysisResult
)


class TestBiomechanicalCalculations:
    """Test core biomechanical calculation functions."""

    def test_calculate_angle_90_degrees(self):
        """Test 90-degree angle calculation."""
        p1 = (0.0, 1.0)
        p2 = (0.0, 0.0)
        p3 = (1.0, 0.0)
        angle = calculate_angle(p1, p2, p3)
        assert abs(angle - 90.0) < 0.1

    def test_calculate_angle_180_degrees(self):
        """Test straight line (180 degrees)."""
        p1 = (0.0, 1.0)
        p2 = (0.0, 0.5)
        p3 = (0.0, 0.0)
        angle = calculate_angle(p1, p2, p3)
        assert abs(angle - 180.0) < 0.1

    def test_calculate_angle_45_degrees(self):
        """Test 45-degree angle."""
        p1 = (0.0, 1.0)
        p2 = (0.0, 0.0)
        p3 = (1.0, 1.0)
        angle = calculate_angle(p1, p2, p3)
        assert abs(angle - 45.0) < 0.1

    def test_calculate_angle_3d(self):
        """Test 3D angle calculation."""
        p1 = (0.0, 1.0, 0.0)
        p2 = (0.0, 0.0, 0.0)
        p3 = (1.0, 0.0, 0.0)
        angle = calculate_angle_3d(p1, p2, p3)
        assert abs(angle - 90.0) < 0.1

    def test_calculate_distance(self):
        """Test Euclidean distance calculation."""
        p1 = (0.0, 0.0)
        p2 = (3.0, 4.0)
        distance = calculate_distance(p1, p2)
        assert abs(distance - 5.0) < 0.1

    def test_calculate_distance_3d(self):
        """Test 3D Euclidean distance."""
        p1 = (0.0, 0.0, 0.0)
        p2 = (1.0, 2.0, 2.0)
        distance = calculate_distance_3d(p1, p2)
        assert abs(distance - 3.0) < 0.1

    def test_calculate_symmetry_perfect(self):
        """Test perfect symmetry returns 100%."""
        symmetry = calculate_symmetry(90.0, 90.0)
        assert symmetry == 100.0

    def test_calculate_symmetry_half(self):
        """Test 50% symmetry."""
        symmetry = calculate_symmetry(90.0, 45.0)
        assert symmetry == 50.0

    def test_calculate_symmetry_zero(self):
        """Test zero value symmetry."""
        symmetry = calculate_symmetry(0.0, 0.0)
        assert symmetry == 100.0

    def test_calculate_stability_perfect(self):
        """Test perfect stability returns 100%."""
        positions = [(0.5, 0.5) for _ in range(15)]
        stability = calculate_stability(positions)
        assert stability == 100.0

    def test_calculate_stability_with_movement(self):
        """Test stability with some movement."""
        positions = [(0.5 + i*0.01, 0.5) for i in range(15)]
        stability = calculate_stability(positions)
        assert 0 <= stability < 100

    def test_calculate_range_of_motion(self):
        """Test range of motion calculation."""
        angles = [45.0, 90.0, 135.0, 90.0, 45.0]
        min_a, max_a, range_a = calculate_range_of_motion(angles)
        assert min_a == 45.0
        assert max_a == 135.0
        assert range_a == 90.0

    def test_calculate_range_of_motion_empty(self):
        """Test range of motion with empty list."""
        min_a, max_a, range_a = calculate_range_of_motion([])
        assert min_a == 0
        assert max_a == 0
        assert range_a == 0


class TestCalibration:
    """Test camera calibration logic."""

    def test_calibration_good_position(self, mock_landmarks):
        """Test calibration with good body position."""
        # Center the landmarks
        for i, lm in enumerate(mock_landmarks):
            lm.x = 0.5
            lm.y = 0.3 + (i * 0.02)
            lm.visibility = 0.9

        is_calibrated, messages = check_calibration(mock_landmarks)
        assert is_calibrated is True
        assert len(messages) > 0

    def test_calibration_off_center(self, mock_landmarks):
        """Test calibration with off-center position."""
        for lm in mock_landmarks:
            lm.x = 0.1  # Too far left
            lm.visibility = 0.9

        is_calibrated, messages = check_calibration(mock_landmarks)
        assert is_calibrated is False
        assert any("center" in msg.lower() for msg in messages)

    def test_calibration_low_visibility(self, mock_landmarks):
        """Test calibration with low landmark visibility."""
        for lm in mock_landmarks:
            lm.visibility = 0.3  # Too low

        is_calibrated, messages = check_calibration(mock_landmarks)
        assert is_calibrated is False


class TestFitnessAnalyzer:
    """Test fitness exercise analyzer."""

    def test_analyzer_initialization(self):
        """Test FitnessAnalyzer initialization."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        assert analyzer.exercise_type == 'pushup'
        assert analyzer.rep_state.count == 0

    def test_analyzer_reset(self):
        """Test analyzer state reset."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        analyzer.rep_state.count = 10
        analyzer.reset()
        assert analyzer.rep_state.count == 0

    def test_analyze_frame_unknown_exercise(self, mock_landmarks):
        """Test analysis with unknown exercise type."""
        analyzer = FitnessAnalyzer(exercise_type='unknown')
        result = analyzer.analyze_frame(mock_landmarks)
        assert isinstance(result, AnalysisResult)
        assert len(result.feedback) > 0

    def test_detect_fatigue_low(self):
        """Test fatigue detection with no fatigue."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        analyzer.form_score_history.extend([90, 91, 92, 90, 91] * 2)
        fatigue = analyzer.detect_fatigue()
        assert fatigue == 'low'

    def test_detect_fatigue_high(self):
        """Test fatigue detection with high fatigue."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        analyzer.form_score_history.extend([95, 94, 93, 70, 65, 60, 55, 50, 45, 40])
        fatigue = analyzer.detect_fatigue()
        assert fatigue == 'high'

    def test_get_session_duration(self):
        """Test session duration calculation."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        import time
        time.sleep(0.1)  # Small delay
        duration = analyzer.get_session_duration()
        assert duration >= 0.1

    def test_get_session_summary(self):
        """Test session summary generation."""
        analyzer = FitnessAnalyzer(exercise_type='pushup')
        analyzer.rep_state.count = 10
        analyzer.rep_state.quality_count = 8
        summary = analyzer.get_session_summary()
        assert summary['reps'] == 10
        assert summary['quality_reps'] == 8


class TestAnalysisResult:
    """Test AnalysisResult dataclass."""

    def test_analysis_result_defaults(self):
        """Test AnalysisResult default values."""
        result = AnalysisResult()
        assert result.form_score == 0.0
        assert result.rep_counted is False
        assert result.quality_rep is False
        assert result.fatigue_level == 'low'

    def test_analysis_result_to_dict(self):
        """Test AnalysisResult serialization."""
        result = AnalysisResult(
            form_score=85.0,
            corrections=["Keep back straight"],
            positives=["Good depth"]
        )
        data = result.to_dict()
        assert data['form_score'] == 85.0
        assert len(data['corrections']) == 1
        assert len(data['positives']) == 1
