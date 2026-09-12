"""
Tests for AI provider fallback mechanism (Ollama → Gemini).
"""

import pytest
from unittest.mock import patch, MagicMock
from ai_provider import get_ai, KinesisAI, OllamaProvider, GeminiProvider


class TestAIProvider:
    """Test AI provider abstraction and fallback."""

    def test_get_ai_singleton(self):
        """Test get_ai returns singleton instance."""
        ai1 = get_ai()
        ai2 = get_ai()
        assert ai1 is ai2

    def test_ai_status(self):
        """Test AI status check."""
        ai = get_ai()
        status = ai.get_status()
        assert 'ollama_available' in status
        assert 'gemini_available' in status
        assert 'primary' in status

    @patch('ai_provider.OllamaProvider.is_available')
    @patch('ai_provider.OllamaProvider.generate')
    def test_ollama_primary(self, mock_generate, mock_available):
        """Test Ollama is used when available."""
        mock_available.return_value = True
        mock_generate.return_value = {
            'text': 'Response from Ollama',
            'provider': 'ollama',
            'model': 'gemma3:4b'
        }

        ai = get_ai()
        result = ai.generate('Test prompt')

        assert result['provider'] == 'ollama'
        mock_generate.assert_called_once()

    @patch('ai_provider.OllamaProvider.is_available')
    @patch('ai_provider.GeminiProvider.is_available')
    @patch('ai_provider.GeminiProvider.generate')
    def test_gemini_fallback(self, mock_gemini_generate, mock_gemini_available, mock_ollama_available):
        """Test Gemini fallback when Ollama unavailable."""
        mock_ollama_available.return_value = False
        mock_gemini_available.return_value = True
        mock_gemini_generate.return_value = {
            'text': 'Response from Gemini',
            'provider': 'gemini',
            'model': 'gemini-2.0-flash'
        }

        ai = get_ai()
        result = ai.generate('Test prompt')

        assert result['provider'] == 'gemini'
        mock_gemini_generate.assert_called_once()

    @patch('ai_provider.OllamaProvider.is_available')
    @patch('ai_provider.GeminiProvider.is_available')
    def test_both_unavailable(self, mock_gemini_available, mock_ollama_available):
        """Test fallback message when both unavailable."""
        mock_ollama_available.return_value = False
        mock_gemini_available.return_value = False

        ai = get_ai()
        result = ai.generate('Test prompt')

        assert result['provider'] == 'none'
        assert 'unavailable' in result['text'].lower()

    @patch('ai_provider.OllamaProvider.is_available')
    @patch('ai_provider.OllamaProvider.generate')
    @patch('ai_provider.GeminiProvider.is_available')
    @patch('ai_provider.GeminiProvider.generate')
    def test_ollama_fails_falls_back_to_gemini(self, mock_gemini_gen, mock_gem_avail, mock_ollama_gen, mock_ollama_avail):
        """Test fallback when Ollama fails with exception."""
        mock_ollama_avail.return_value = True
        mock_ollama_gen.side_effect = Exception("Ollama error")
        mock_gem_avail.return_value = True
        mock_gemini_gen.return_value = {
            'text': 'Response from Gemini',
            'provider': 'gemini'
        }

        ai = get_ai()
        result = ai.generate('Test prompt')

        assert result['provider'] == 'gemini'

    def test_coach_method(self):
        """Test coach method."""
        ai = get_ai()
        # This will use fallback since no AI is configured
        result = ai.coach(context={'exercise': 'pushup'}, question='How was my form?')
        assert 'text' in result
        assert 'provider' in result

    def test_generate_training_plan(self):
        """Test training plan generation."""
        ai = get_ai()
        result = ai.generate_training_plan(
            sport='football',
            position='Forward',
            skill_level='intermediate',
            goal='Speed',
            equipment='Basic',
            weeks=4
        )
        assert 'text' in result
        assert 'provider' in result

    def test_analyze_session(self):
        """Test session analysis."""
        ai = get_ai()
        session_data = {
            'exercise_type': 'pushup',
            'reps': 10,
            'form_score': 85.0
        }
        result = ai.analyze_session(session_data)
        assert 'text' in result
        assert 'provider' in result

    def test_generate_diet_plan(self):
        """Test diet plan generation."""
        ai = get_ai()
        user_profile = {
            'age': 25,
            'weight': 70,
            'height': 175
        }
        result = ai.generate_diet_plan(user_profile, goal='maintain')
        assert 'text' in result
        assert 'provider' in result


class TestOllamaProvider:
    """Test Ollama provider specifically."""

    def test_initialization(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider()
        assert provider.base_url is not None
        assert provider.model is not None

    def test_initialization_custom_params(self):
        """Test Ollama with custom parameters."""
        provider = OllamaProvider(
            base_url='http://custom:11434',
            model='custom-model'
        )
        assert provider.base_url == 'http://custom:11434'
        assert provider.model == 'custom-model'

    @patch('requests.get')
    def test_is_available_success(self, mock_get):
        """Test availability check when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'models': [{'name': 'gemma3:4b'}]}
        mock_get.return_value = mock_response

        provider = OllamaProvider()
        available = provider.is_available()
        assert available is True

    @patch('requests.get')
    def test_is_available_connection_error(self, mock_get):
        """Test availability check when Ollama is not running."""
        mock_get.side_effect = Exception("Connection refused")

        provider = OllamaProvider()
        available = provider.is_available()
        assert available is False

    @patch('requests.get')
    def test_get_models(self, mock_get):
        """Test getting available models."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [
                {'name': 'gemma3:4b'},
                {'name': 'mistral'}
            ]
        }
        mock_get.return_value = mock_response

        provider = OllamaProvider()
        models = provider.get_models()
        assert 'gemma3:4b' in models
        assert 'mistral' in models


class TestGeminiProvider:
    """Test Gemini provider specifically."""

    def test_initialization(self):
        """Test Gemini provider initialization."""
        provider = GeminiProvider()
        assert provider.api_key is not None or provider.api_key == ''

    def test_initialization_with_key(self):
        """Test Gemini with API key."""
        provider = GeminiProvider(api_key='test-key')
        assert provider.api_key == 'test-key'

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        provider = GeminiProvider(api_key='test-key')
        available = provider.is_available()
        assert available is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        provider = GeminiProvider(api_key='')
        available = provider.is_available()
        assert available is False
