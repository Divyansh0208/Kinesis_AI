"""
Kinesis AI - Gemini Service
Google Gemini API client.
Used by ai_provider.py as FALLBACK when Ollama is unavailable.
"""

import os
import logging

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

_model = None


def _get_model():
    """Lazy-initialize Gemini model."""
    global _model
    if _model is None and GOOGLE_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            _model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    return _model


def is_available():
    """Check if Gemini API key is configured."""
    return bool(GOOGLE_API_KEY)


def generate(prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
    """
    Generate response using Gemini.
    Returns response text or None on failure.
    """
    model = _get_model()
    if not model:
        logger.warning("Gemini not available - no API key configured")
        return None

    try:
        import google.generativeai as genai

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = model.generate_content(full_prompt, generation_config=config)
        return response.text if response.text else ""
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        return None


def generate_coaching(context, question=None):
    """Generate coaching advice using Gemini."""
    system = (
        "You are Kinesis AI, an expert movement and sports coach. "
        "Provide concise, actionable advice. Support Hindi and English."
    )
    prompt = f"Context: {context}"
    if question:
        prompt += f"\nQuestion: {question}"
    return generate(prompt, system_prompt=system)


def generate_diet_plan(profile, goal):
    """Generate a diet plan using Gemini."""
    prompt = (
        f"Create a practical nutrition plan.\n"
        f"Profile: {profile}\nGoal: {goal}\n"
        f"Include meals, macros, and timing."
    )
    return generate(prompt, max_tokens=3000)


def generate_workout_plan(params):
    """Generate a workout plan using Gemini."""
    prompt = (
        f"Create a training plan with these parameters:\n{params}\n"
        f"Structure week by week with exercises, sets, reps, rest."
    )
    return generate(prompt, max_tokens=4000)
