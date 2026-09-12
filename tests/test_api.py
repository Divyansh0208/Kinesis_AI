"""
Tests for API endpoints.
"""

import pytest
import json
from flask import Flask


class TestAPIEndpoints:
    """Test REST API endpoints."""

    def test_api_status(self, client):
        """Test health check endpoint."""
        response = client.get('/api/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'ai' in data
        assert 'version' in data

    def test_api_calibration_with_valid_landmarks(self, client, mock_landmarks_dict):
        """Test calibration endpoint with valid landmarks."""
        response = client.post('/api/calibration', json={'landmarks': mock_landmarks_dict})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'calibrated' in data
        assert 'messages' in data

    def test_api_calibration_insufficient_landmarks(self, client):
        """Test calibration with insufficient landmarks."""
        response = client.post('/api/calibration', json={'landmarks': []})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['calibrated'] is False

    def test_fitness_analyze_insufficient_landmarks(self, client):
        """Test fitness analysis with insufficient landmarks."""
        response = client.post('/api/fitness/analyze', json={
            'exercise': 'pushup',
            'landmarks': []
        })
        assert response.status_code == 400

    def test_fitness_analyze_with_landmarks(self, client, mock_landmarks_dict):
        """Test fitness analysis with valid landmarks."""
        response = client.post('/api/fitness/analyze', json={
            'exercise': 'pushup',
            'session_id': 'test_session',
            'landmarks': mock_landmarks_dict
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'form_score' in data
        assert 'rep_counted' in data
        assert 'quality_rep' in data

    def test_fitness_save(self, client):
        """Test saving fitness session."""
        response = client.post('/api/fitness/save', json={
            'exercise_type': 'pushup',
            'reps': 10,
            'quality_reps': 8,
            'duration': 60.0,
            'form_score': 85.0,
            'fatigue_level': 'low',
            'metrics': {}
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_fitness_save_authenticated(self, authenticated_client):
        """Test saving fitness session with authenticated user."""
        response = authenticated_client.post('/api/fitness/save', json={
            'exercise_type': 'pushup',
            'reps': 10,
            'quality_reps': 8,
            'duration': 60.0,
            'form_score': 85.0,
            'fatigue_level': 'low',
            'metrics': {}
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        # Authenticated users should earn XP
        assert 'xp_earned' in data

    def test_football_analyze_insufficient_landmarks(self, client):
        """Test football analysis with insufficient landmarks."""
        response = client.post('/api/football/analyze', json={
            'skill': 'shooting',
            'landmarks': []
        })
        assert response.status_code == 400

    def test_football_analyze_with_landmarks(self, client, mock_landmarks_dict):
        """Test football analysis with valid landmarks."""
        response = client.post('/api/football/analyze', json={
            'skill': 'shooting',
            'session_id': 'test_session',
            'landmarks': mock_landmarks_dict
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert 'positives' in data
        assert 'corrections' in data

    def test_cricket_analyze_insufficient_landmarks(self, client):
        """Test cricket analysis with insufficient landmarks."""
        response = client.post('/api/cricket/analyze', json={
            'skill': 'pull_shot',
            'landmarks': []
        })
        assert response.status_code == 400

    def test_cricket_analyze_with_landmarks(self, client, mock_landmarks_dict):
        """Test cricket analysis with valid landmarks."""
        response = client.post('/api/cricket/analyze', json={
            'skill': 'pull_shot',
            'session_id': 'test_session',
            'landmarks': mock_landmarks_dict
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert 'positives' in data
        assert 'corrections' in data

    def test_sports_save(self, client):
        """Test saving sports session."""
        response = client.post('/api/sports/save', json={
            'sport': 'football',
            'sport_skill': 'shooting',
            'drill_type': 'technique',
            'score': 85.0,
            'duration': 60.0,
            'reps': 5,
            'risk_level': 'low',
            'style_inspiration': '',
            'breakdown': {},
            'feedback': [],
            'metrics': {}
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_yoga_analyze_insufficient_landmarks(self, client):
        """Test yoga analysis with insufficient landmarks."""
        response = client.post('/api/yoga/analyze', json={
            'pose': 'warrior_2',
            'landmarks': []
        })
        assert response.status_code == 400

    def test_yoga_analyze_with_landmarks(self, client, mock_landmarks_dict):
        """Test yoga analysis with valid landmarks."""
        response = client.post('/api/yoga/analyze', json={
            'pose': 'warrior_2',
            'landmarks': mock_landmarks_dict
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert 'positives' in data
        assert 'corrections' in data

    def test_voice_chat_empty_query(self, client):
        """Test voice chat with empty query."""
        response = client.post('/api/voice/chat', json={
            'query': '',
            'context': {}
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'text' in data
        assert 'provider' in data

    def test_voice_chat_with_query(self, client):
        """Test voice chat with valid query."""
        response = client.post('/api/voice/chat', json={
            'query': 'How was my form?',
            'context': {'exercise': 'pushup', 'score': 85}
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'text' in data
        assert 'provider' in data

    def test_ai_session_coach(self, client):
        """Test AI session coaching endpoint."""
        response = client.post('/api/ai/session-coach', json={
            'exercise_type': 'pushup',
            'reps': 10,
            'form_score': 85.0
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should return AI analysis or fallback
        assert 'text' in data or 'error' in data
