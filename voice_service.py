"""
Kinesis AI - Voice Service
Bilingual Hindi + English Voice Coach assistant.
Handles queries about workout form, cricket shots, football skills, diet, and training.
Routes reasoning through AIProvider (Ollama -> Gemini fallback).
"""

import logging
import re
from ai_provider import get_ai

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Kinesis AI Voice Coach, an expert bilingual (Hindi + English) movement and sports intelligence assistant for Smart India Hackathon 2026.
You provide instant, encouraging, technically precise coaching feedback for fitness (push-ups, squats, lunges, planks, jumping jacks), football (shooting, dribbling, agility), cricket (pull shot, cover drive, straight drive, bowling, stance), yoga, and nutrition.

Key Rules:
1. Detect user's language:
   - If the user asks in Hindi/Hinglish (e.g. "Mera pull shot kaisa tha?", "Squat me ghutna aage ja raha hai"), reply in natural conversational Hinglish/Hindi with English technical terms.
   - If the user asks in English, reply in crisp, motivating English.
2. Keep responses concise (2 to 4 sentences) suitable for text-to-speech audio output.
3. Be actionable, specific, and positive.
4. Never provide medical diagnosis. For injury concerns, state: "This is a movement-risk observation, not a medical diagnosis. Please consult a specialist if pain persists."
"""


def process_voice_query(query: str, context: dict = None) -> dict:
    """
    Process a voice command/question and return spoken text response.
    
    Args:
        query: Transcribed voice text from frontend
        context: Optional dict containing recent session info (scores, exercise, sport, reps)
    
    Returns:
        dict: { 'text': response_text, 'provider': 'ollama' | 'gemini' | 'rule_fallback', 'lang': 'hi' | 'en' }
    """
    if not query or not query.strip():
        return {
            'text': "I'm listening. Ask me about your form, recent drill score, or technique tips!",
            'provider': 'rule_fallback',
            'lang': 'en'
        }

    # Detect language tendency
    is_hindi = bool(re.search(r'[\u0900-\u097F]', query)) or any(
        w in query.lower() for w in ['kaisa', 'kaise', 'batao', 'mera', 'meri', 'kya', 'karo', 'thik', 'shukriya', 'namaste', 'ghutna', 'kamar']
    )

    # Build contextual prompt
    prompt_parts = []
    if context:
        prompt_parts.append(f"Recent Session Context: {context}")
    prompt_parts.append(f"User Query: {query}")
    prompt_text = "\n".join(prompt_parts)

    ai = get_ai()
    try:
        res = ai.generate(prompt=prompt_text, system_prompt=SYSTEM_PROMPT, max_tokens=300)
        return {
            'text': res.get('text', 'Great effort! Keep your form steady and focus on balanced movement.'),
            'provider': res.get('provider', 'ollama'),
            'lang': 'hi' if is_hindi else 'en'
        }
    except Exception as e:
        logger.error(f"Error in voice service AI generation: {e}")
        # Rule-based fallback
        if is_hindi:
            fallback_text = "Aapka form badhiya tha! Agle set me posture aur balance par thoda aur dhyan de."
        else:
            fallback_text = "Your movement is on track! Keep a stable core and maintain consistent cadence."
        return {
            'text': fallback_text,
            'provider': 'rule_fallback',
            'lang': 'hi' if is_hindi else 'en'
        }
