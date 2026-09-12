# Kinesis AI - Testing Strategy

This document outlines the comprehensive testing strategy for the Kinesis AI system.

## Testing Philosophy

- **Test Real Functionality:** Test actual features, not constants
- **Avoid Fabrication:** Never fake test results or metrics
- **Mock External Services:** Use mocks for AI APIs and external services
- **Maintain Test Independence:** Tests should not depend on each other
- **Keep Tests Fast:** Unit tests should run in seconds, not minutes

## Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── test_pose_detection.py      # Biomechanical calculations
├── test_injury_risk.py         # Movement-risk engine
├── test_gamification.py        # XP and badge system
├── test_api.py                 # API endpoints
├── test_auth.py                # Authentication system
├── test_ai_fallback.py         # AI provider fallback
├── test_models.py              # Database models
├── test_fitness_analyzer.py    # Exercise analysis
├── test_sports_analyzers.py    # Football/cricket analysis
└── test_integration.py         # End-to-end workflows
```

## Unit Tests

### Test: Pose Detection (`test_pose_detection.py`)

**Objective:** Verify biomechanical calculations are accurate

```python
def test_calculate_angle_90_degrees():
    """Test 90-degree angle calculation"""
    p1 = (0.0, 1.0)
    p2 = (0.0, 0.0)
    p3 = (1.0, 0.0)
    angle = calculate_angle(p1, p2, p3)
    assert abs(angle - 90.0) < 0.1

def test_calculate_angle_180_degrees():
    """Test straight line (180 degrees)"""
    p1 = (0.0, 1.0)
    p2 = (0.0, 0.5)
    p3 = (0.0, 0.0)
    angle = calculate_angle(p1, p2, p3)
    assert abs(angle - 180.0) < 0.1

def test_calculate_symmetry_perfect():
    """Test perfect symmetry returns 100%"""
    symmetry = calculate_symmetry(90.0, 90.0)
    assert symmetry == 100.0

def test_calculate_symmetry_half():
    """Test 50% symmetry"""
    symmetry = calculate_symmetry(90.0, 45.0)
    assert symmetry == 50.0

def test_calculate_stability_perfect():
    """Test perfect stability returns 100%"""
    positions = [(0.5, 0.5) for _ in range(15)]
    stability = calculate_stability(positions)
    assert stability == 100.0
```

### Test: Injury Risk Engine (`test_injury_risk.py`)

**Objective:** Verify risk scoring is within expected ranges

```python
def test_risk_score_range():
    """Test risk scores are between 0-100"""
    engine = InjuryRiskEngine()
    # Create mock landmarks
    landmarks = create_mock_landmarks()
    result = engine.analyze(landmarks, sport='fitness')
    assert 0 <= result['risk_score'] <= 100

def test_risk_level_classification():
    """Test risk level classification"""
    engine = InjuryRiskEngine()
    # Test low risk
    result_low = engine.analyze(create_safe_landmarks(), sport='fitness')
    assert result_low['risk_level'] == 'low'
    
    # Test high risk (extreme asymmetry)
    result_high = engine.analyze(create_asymmetric_landmarks(), sport='fitness')
    assert result_high['risk_level'] in ['moderate', 'high']

def test_disclaimer_present():
    """Test medical disclaimer is always present"""
    engine = InjuryRiskEngine()
    result = engine.analyze(create_mock_landmarks(), sport='fitness')
    assert 'disclaimer' in result
    assert 'medical diagnosis' in result['disclaimer'].lower()
```

### Test: Gamification (`test_gamification.py`)

**Objective:** Verify XP calculation and badge logic

```python
def test_xp_calculation_quality_reps():
    """Test XP rewards quality reps"""
    game = GamificationEngine(db.session)
    xp = game.calculate_xp(
        form_score=95.0,
        reps=10,
        quality_reps=10,
        duration=60.0,
        sport='fitness'
    )
    assert xp > 100  # Quality reps heavily rewarded

def test_xp_calculation_poor_form():
    """Test poor form earns less XP"""
    game = GamificationEngine(db.session)
    xp_poor = game.calculate_xp(
        form_score=50.0,
        reps=10,
        quality_reps=0,
        duration=60.0,
        sport='fitness'
    )
    xp_good = game.calculate_xp(
        form_score=95.0,
        reps=10,
        quality_reps=10,
        duration=60.0,
        sport='fitness'
    )
    assert xp_good > xp_poor

def test_level_progression():
    """Test level calculation"""
    game = GamificationEngine(db.session)
    
    # Level 1 at 0 XP
    level_1 = game.get_user_level(0)
    assert level_1['level'] == 1
    assert level_1['title'] == 'Rookie'
    
    # Level 2 at 1000 XP
    level_2 = game.get_user_level(1000)
    assert level_2['level'] == 2
```

### Test: API Endpoints (`test_api.py`)

**Objective:** Verify API responses and error handling

```python
def test_api_status():
    """Test health check endpoint"""
    with app.test_client() as client:
        response = client.get('/api/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'ai' in data

def test_api_calibration():
    """Test calibration endpoint"""
    with app.test_client() as client:
        landmarks = create_mock_landmarks_dict()
        response = client.post('/api/calibration', json={'landmarks': landmarks})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'calibrated' in data

def test_fitness_analyze_insufficient_landmarks():
    """Test error handling for insufficient landmarks"""
    with app.test_client() as client:
        response = client.post('/api/fitness/analyze', json={
            'exercise': 'pushup',
            'landmarks': []  # Empty landmarks
        })
        assert response.status_code == 400
```

### Test: Authentication (`test_auth.py`)

**Objective:** Verify user authentication and authorization

```python
def test_user_registration():
    """Test user registration"""
    with app.test_client() as client:
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!',
            'full_name': 'Test User'
        })
        assert response.status_code == 302  # Redirect after registration
        
        # Verify user exists in database
        user = User.query.filter_by(username='testuser').first()
        assert user is not None

def test_user_login():
    """Test user login"""
    with app.test_client() as client:
        # Register user first
        create_test_user()
        
        # Login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'Test123!'
        })
        assert response.status_code == 302  # Redirect after login

def test_protected_route_requires_login():
    """Test protected routes redirect to login"""
    with app.test_client() as client:
        response = client.get('/profile')
        assert response.status_code == 302  # Redirect to login
```

### Test: AI Fallback (`test_ai_fallback.py`)

**Objective:** Verify Ollama → Gemini fallback mechanism

```python
@patch('ai_provider.OllamaProvider.is_available')
@patch('ai_provider.OllamaProvider.generate')
def test_ollama_primary(mock_ollama_generate, mock_ollama_available):
    """Test Ollama is used when available"""
    mock_ollama_available.return_value = True
    mock_ollama_generate.return_value = {
        'text': 'Response from Ollama',
        'provider': 'ollama'
    }
    
    ai = get_ai()
    result = ai.generate('Test prompt')
    
    assert result['provider'] == 'ollama'
    mock_ollama_generate.assert_called_once()

@patch('ai_provider.OllamaProvider.is_available')
@patch('ai_provider.GeminiProvider.is_available')
@patch('ai_provider.GeminiProvider.generate')
def test_gemini_fallback(mock_gemini_generate, mock_gemini_available, mock_ollama_available):
    """Test Gemini fallback when Ollama unavailable"""
    mock_ollama_available.return_value = False
    mock_gemini_available.return_value = True
    mock_gemini_generate.return_value = {
        'text': 'Response from Gemini',
        'provider': 'gemini'
    }
    
    ai = get_ai()
    result = ai.generate('Test prompt')
    
    assert result['provider'] == 'gemini'
    mock_gemini_generate.assert_called_once()

def test_both_unavailable():
    """Test fallback message when both unavailable"""
    with patch('ai_provider.OllamaProvider.is_available', return_value=False), \
         patch('ai_provider.GeminiProvider.is_available', return_value=False):
        ai = get_ai()
        result = ai.generate('Test prompt')
        
        assert result['provider'] == 'none'
        assert 'unavailable' in result['text'].lower()
```

## Integration Tests

### Test: End-to-End Workout Flow (`test_integration.py`)

**Objective:** Verify complete workout pipeline

```python
def test_complete_workout_flow():
    """Test full workout: login → exercise → save → dashboard"""
    with app.test_client() as client:
        # 1. Register and login
        client.post('/register', data=test_user_data)
        client.post('/login', data=test_login_data)
        
        # 2. Start exercise session
        session_data = {
            'exercise_type': 'pushup',
            'reps': 10,
            'quality_reps': 8,
            'duration': 60.0,
            'form_score': 85.0,
            'fatigue_level': 'low',
            'metrics': {}
        }
        
        # 3. Save session
        response = client.post('/api/fitness/save', json=session_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['xp_earned'] > 0
        
        # 4. Verify dashboard shows session
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'pushup' in response.data
```

## Test Configuration

### Pytest Configuration (`conftest.py`)

```python
import pytest
from app import create_app
from models import db, User

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('Test123!')
        db.session.add(user)
        db.session.commit()
        return user
```

## Running Tests

### Run All Tests

```bash
# Using pytest
pytest tests/

# With coverage
pytest tests/ --cov=. --cov-report=html

# With verbose output
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_pose_detection.py
pytest tests/test_api.py -v
```

### Run Specific Test

```bash
pytest tests/test_pose_detection.py::test_calculate_angle_90_degrees
```

### Run Tests by Marker

```bash
# Add markers to tests: @pytest.mark.unit, @pytest.mark.integration
pytest tests/ -m unit
pytest tests/ -m integration
```

## Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Pose Detection | 90% | To be measured |
| Injury Risk | 85% | To be measured |
| Gamification | 90% | To be measured |
| API Routes | 80% | To be measured |
| Authentication | 85% | To be measured |
| AI Provider | 75% | To be measured |
| Models | 80% | To be measured |

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Manual Testing Checklist

### Core Functionality
- [ ] User can register and login
- [ ] User can start fitness exercise
- [ ] Camera calibration works
- [ ] Real-time form scoring updates
- [ ] Rep counting increments correctly
- [ ] Session saves to database
- [ ] Dashboard shows workout history
- [ ] XP awarded after session

### Sports Analysis
- [ ] Football shooting analysis works
- [ ] Cricket shot analysis works
- [ ] Style coaching displays
- [ ] Sports session saves correctly

### AI Features
- [ ] Voice coach responds to queries
- [ ] Training plan generates (with AI configured)
- [ ] Diet plan generates (with AI configured)
- [ ] Fallback message shows when AI unavailable

### Edge Cases
- [ ] Handles camera permission denial
- [ ] Handles insufficient landmarks
- [ ] Handles network errors
- [ ] Handles database connection errors
- [ ] Handles AI service failures

## Testing Best Practices

1. **Test Isolation:** Each test should be independent
2. **Clear Names:** Test names should describe what they test
3. **Arrange-Act-Assert:** Structure tests clearly
4. **Mock External Dependencies:** Don't call real APIs in tests
5. **Test Edge Cases:** Test boundary conditions and error cases
6. **Keep Tests Fast:** Unit tests should run in milliseconds
7. **Test One Thing:** Each test should verify one behavior
8. **Use Fixtures:** Reuse test setup with pytest fixtures

## Known Testing Limitations

1. **Pose Detection Accuracy:** Requires labeled dataset for ground truth
2. **AI Responses:** Hard to test generative AI responses deterministically
3. **Camera Hardware:** Tests cannot verify real camera behavior
4. **Performance:** Load testing requires separate infrastructure
5. **Cross-Browser:** Requires manual testing on different browsers

## Future Testing Enhancements

1. **Visual Regression Testing:** Compare UI screenshots
2. **Load Testing:** Use Locust for concurrent user testing
3. **E2E Testing:** Use Selenium for browser automation
4. **A/B Testing:** Test different algorithm variations
5. **Chaos Testing:** Test system resilience to failures

---

*Last Updated: 2026-09-13*
*Kinesis AI - Smart India Hackathon 2026*
