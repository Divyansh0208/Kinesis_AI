"""
Kinesis AI - AI Provider Abstraction
Ollama-first, Gemini-fallback architecture.
Automatically detects Ollama availability and falls back transparently.
"""

import os
import time
import logging
import requests
import json

logger = logging.getLogger(__name__)


class AIProvider:
    """Base AI provider interface."""

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
        """Generate a text response. Returns dict with 'text' and 'provider' keys."""
        raise NotImplementedError

    def is_available(self):
        """Check if this provider is currently available."""
        raise NotImplementedError


class OllamaProvider(AIProvider):
    """Local Ollama AI provider - privacy-first."""

    def __init__(self, base_url=None, model=None):
        self.base_url = (base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')).rstrip('/')
        self.model = model or os.getenv('OLLAMA_MODEL', 'gemma3:4b')
        self._available = None
        self._last_check = 0
        self._check_interval = 30  # Re-check every 30 seconds

    def is_available(self):
        """Check if Ollama is running and has a model available."""
        now = time.time()
        if self._available is not None and (now - self._last_check) < self._check_interval:
            return self._available

        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                # Check if our preferred model exists, or use any available model
                if self.model in model_names:
                    self._available = True
                elif model_names:
                    # Use the first available model
                    self.model = model_names[0]
                    logger.info(f"Ollama: preferred model not found, using {self.model}")
                    self._available = True
                else:
                    logger.warning("Ollama is running but has no models installed")
                    self._available = False
            else:
                self._available = False
        except (requests.ConnectionError, requests.Timeout):
            self._available = False
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            self._available = False

        self._last_check = now
        return self._available

    def get_models(self):
        """List available Ollama models."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return [m.get('name', '') for m in resp.json().get('models', [])]
        except Exception:
            pass
        return []

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
        """Generate response using Ollama."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("message", {}).get("content", "")
            return {"text": text, "provider": "ollama", "model": self.model}
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise


class GeminiProvider(AIProvider):
    """Google Gemini AI provider - cloud fallback."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY', '')
        self._model = None

    def _get_model(self):
        if self._model is None and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                logger.error(f"Gemini initialization failed: {e}")
        return self._model

    def is_available(self):
        """Check if Gemini API key is configured."""
        return bool(self.api_key)

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
        """Generate response using Gemini."""
        model = self._get_model()
        if not model:
            raise RuntimeError("Gemini not configured - no API key")

        try:
            import google.generativeai as genai

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            text = response.text if response.text else ""
            return {"text": text, "provider": "gemini", "model": "gemini-2.0-flash"}
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise


class KinesisAI:
    """
    Unified AI interface for Kinesis.
    Ollama is PRIMARY. Gemini is FALLBACK.
    Automatically detects availability and routes requests.
    """

    def __init__(self):
        self.ollama = OllamaProvider()
        self.gemini = GeminiProvider()
        self._system_prompt = (
            "You are Kinesis AI, an expert movement and sports coach. "
            "You provide personalized fitness guidance, sports technique coaching, "
            "and training recommendations. You support Hindi and English. "
            "Never provide medical diagnoses. Always recommend consulting a professional "
            "for pain or injuries. Be concise, actionable, and encouraging."
        )

    def get_status(self):
        """Return current AI provider status."""
        ollama_ok = self.ollama.is_available()
        gemini_ok = self.gemini.is_available()
        return {
            "ollama_available": ollama_ok,
            "gemini_available": gemini_ok,
            "primary": "ollama" if ollama_ok else ("gemini" if gemini_ok else "none"),
            "ollama_models": self.ollama.get_models() if ollama_ok else [],
            "ollama_model": self.ollama.model if ollama_ok else None,
        }

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
        """
        Generate AI response. Tries Ollama first, falls back to Gemini.
        Returns dict: {text, provider, model}
        """
        sys = system_prompt or self._system_prompt

        # Try Ollama first (privacy-first)
        if self.ollama.is_available():
            try:
                result = self.ollama.generate(prompt, sys, temperature, max_tokens)
                logger.info(f"AI response from Ollama ({self.ollama.model})")
                return result
            except Exception as e:
                logger.warning(f"Ollama failed, falling back to Gemini: {e}")

        # Fallback to Gemini
        if self.gemini.is_available():
            try:
                result = self.gemini.generate(prompt, sys, temperature, max_tokens)
                logger.info("AI response from Gemini (fallback)")
                return result
            except Exception as e:
                logger.error(f"Gemini fallback also failed: {e}")

        # Both unavailable
        return {
            "text": "AI coaching is currently unavailable. Please check your Ollama installation or Gemini API key.",
            "provider": "none",
            "model": None,
        }

    def coach(self, context, question=None):
        """Generate coaching response with exercise/sport context."""
        prompt = f"Exercise/Sport Context:\n{context}"
        if question:
            prompt += f"\n\nUser Question: {question}"
        prompt += "\n\nProvide concise, actionable coaching advice."
        return self.generate(prompt)

    def generate_training_plan(self, sport, position, skill_level, goal, equipment, weeks=4):
        """Generate a structured training plan."""
        prompt = (
            f"Create a {weeks}-week training plan.\n"
            f"Sport: {sport}\n"
            f"Position/Role: {position}\n"
            f"Skill Level: {skill_level}\n"
            f"Primary Goal: {goal}\n"
            f"Available Equipment: {equipment}\n\n"
            f"Structure the plan week by week with specific exercises, sets, reps, and rest periods. "
            f"Include warm-up and cool-down. Focus on progressive overload and injury prevention."
        )
        return self.generate(prompt, max_tokens=4096)

    def analyze_session(self, session_data):
        """Generate post-session AI analysis."""
        prompt = (
            f"Analyze this training session and provide coaching feedback:\n"
            f"{json.dumps(session_data, indent=2)}\n\n"
            f"Provide: 1) What went well 2) Areas to improve 3) Specific drills to practice"
        )
        return self.generate(prompt)

    def generate_diet_plan(self, user_profile, goal):
        """Generate a diet/nutrition plan."""
        prompt = (
            f"Create a nutrition plan for:\n"
            f"Profile: {json.dumps(user_profile)}\n"
            f"Goal: {goal}\n\n"
            f"Include meals, macros, and timing. Keep it practical and affordable."
        )
        return self.generate(prompt, max_tokens=3000)


# Singleton instance
_kinesis_ai = None


def get_ai():
    """Get the singleton KinesisAI instance."""
    global _kinesis_ai
    if _kinesis_ai is None:
        _kinesis_ai = KinesisAI()
    return _kinesis_ai
