"""
Pytest configuration and fixtures for Kinesis AI tests.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            fitness_level='intermediate',
            preferred_sport='fitness'
        )
        user.set_password('Test123!')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
    return client


class LandmarkPoint:
    """Helper class for creating mock landmarks."""
    def __init__(self, x=0.5, y=0.5, z=0.0, visibility=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


@pytest.fixture
def mock_landmarks():
    """Create mock 33-point landmarks for testing."""
    return [LandmarkPoint() for _ in range(33)]


@pytest.fixture
def mock_landmarks_dict():
    """Create mock landmarks as dictionary for API testing."""
    return [{'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0} for _ in range(33)]
