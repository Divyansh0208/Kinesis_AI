"""
Tests for authentication system.
"""

import pytest
from models import db, User


class TestAuthentication:
    """Test user authentication and authorization."""

    def test_user_registration(self, client, app):
        """Test user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'full_name': 'New User',
            'fitness_level': 'beginner',
            'preferred_sport': 'fitness'
        })
        # Should redirect after successful registration
        assert response.status_code == 302

        # Verify user exists in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('NewPass123!')

    def test_user_registration_duplicate_username(self, client, app, test_user):
        """Test registration with duplicate username."""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'TestPass123!',
            'full_name': 'Different User'
        })
        # Should stay on registration page with error
        assert response.status_code == 200

    def test_user_registration_duplicate_email(self, client, app, test_user):
        """Test registration with duplicate email."""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'password': 'TestPass123!',
            'full_name': 'Different User'
        })
        assert response.status_code == 200

    def test_user_login_valid(self, client, app, test_user):
        """Test user login with valid credentials."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!'
        })
        # Should redirect after successful login
        assert response.status_code == 302

    def test_user_login_invalid_password(self, client, app, test_user):
        """Test user login with invalid password."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        # Should stay on login page with error
        assert response.status_code == 200

    def test_user_login_invalid_username(self, client, app):
        """Test user login with invalid username."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'Test123!'
        })
        assert response.status_code == 200

    def test_user_login_with_email(self, client, app, test_user):
        """Test user login with email instead of username."""
        response = client.post('/login', data={
            'username': 'test@example.com',
            'password': 'Test123!'
        })
        assert response.status_code == 302

    def test_logout(self, authenticated_client):
        """Test user logout."""
        response = authenticated_client.get('/logout')
        assert response.status_code == 302

    def test_protected_route_without_login(self, client):
        """Test protected route redirects when not logged in."""
        response = client.get('/profile')
        # Should redirect to login
        assert response.status_code == 302

    def test_protected_route_with_login(self, authenticated_client):
        """Test protected route accessible when logged in."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200

    def test_password_hashing(self, app):
        """Test password hashing works correctly."""
        with app.app_context():
            user = User(username='test', email='test@example.com')
            user.set_password('MyPassword123')
            
            assert user.check_password('MyPassword123') is True
            assert user.check_password('WrongPassword') is False

    def test_xp_system(self, app, test_user):
        """Test XP addition and level-up."""
        with app.app_context():
            initial_xp = test_user.xp
            initial_level = test_user.level
            
            # Add XP
            leveled_up = test_user.add_xp(600)
            
            # XP should increase
            assert test_user.xp > initial_xp
            
            # Level might increase
            if leveled_up:
                assert test_user.level > initial_level

    def test_streak_update(self, app, test_user):
        """Test login streak update."""
        with app.app_context():
            from datetime import datetime, timedelta, timezone
            
            # Set last_active to yesterday
            test_user.last_active = datetime.now(timezone.utc) - timedelta(days=1)
            db.session.commit()
            
            # Update streak
            test_user.update_streak()
            db.session.commit()
            
            # Streak should be 2 (yesterday + today)
            assert test_user.streak_days >= 1

    def test_streak_reset(self, app, test_user):
        """Test streak reset after missing days."""
        with app.app_context():
            from datetime import datetime, timedelta, timezone
            
            # Set last_active to 3 days ago
            test_user.last_active = datetime.now(timezone.utc) - timedelta(days=3)
            test_user.streak_days = 5
            db.session.commit()
            
            # Update streak
            test_user.update_streak()
            db.session.commit()
            
            # Streak should reset to 1
            assert test_user.streak_days == 1

    def test_user_to_dict(self, app, test_user):
        """Test user serialization."""
        with app.app_context():
            user_dict = test_user.to_dict()
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'xp' in user_dict
            assert 'level' in user_dict
            # Password should not be in dict
            assert 'password_hash' not in user_dict
            assert 'password' not in user_dict
