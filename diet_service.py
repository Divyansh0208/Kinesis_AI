"""
Kinesis AI - Diet Service
AI-powered diet and nutrition planning.
"""

import logging
from ai_provider import get_ai

logger = logging.getLogger(__name__)


def generate_diet_plan(user_profile, goal='general_fitness'):
    """
    Generate a personalized diet plan using AI (Ollama → Gemini fallback).
    user_profile: dict with age, weight, height, fitness_level, dietary_preferences
    goal: fitness goal string
    """
    ai = get_ai()

    profile_str = (
        f"Age: {user_profile.get('age', 'Not specified')}\n"
        f"Weight: {user_profile.get('weight', 'Not specified')} kg\n"
        f"Height: {user_profile.get('height', 'Not specified')} cm\n"
        f"Fitness Level: {user_profile.get('fitness_level', 'beginner')}\n"
        f"Dietary Preferences: {user_profile.get('dietary_preferences', 'No restrictions')}\n"
        f"Goal: {goal}"
    )

    prompt = (
        f"Create a practical, affordable daily nutrition plan for an athlete with this profile:\n"
        f"{profile_str}\n\n"
        f"Include:\n"
        f"1. Breakfast, Lunch, Dinner, and 2 Snacks\n"
        f"2. Approximate calories and macros for each meal\n"
        f"3. Pre-workout and post-workout nutrition\n"
        f"4. Hydration guidelines\n"
        f"5. Key micronutrients to focus on\n\n"
        f"Keep meals simple and practical. Include Indian food options where appropriate."
    )

    system = (
        "You are a sports nutrition advisor. Provide practical, evidence-based nutrition advice. "
        "Never diagnose medical conditions. Recommend consulting a dietitian for specific conditions."
    )

    result = ai.generate(prompt, system_prompt=system, max_tokens=3000)
    return {
        'plan': result.get('text', ''),
        'provider': result.get('provider', 'none'),
    }


def get_meal_suggestions(meal_type, calories_target=500, vegetarian=False):
    """Get quick meal suggestions for a specific meal type."""
    ai = get_ai()

    veg_str = "vegetarian" if vegetarian else "non-vegetarian or vegetarian"
    prompt = (
        f"Suggest 3 quick {veg_str} {meal_type} options, each around {calories_target} calories. "
        f"Include Indian food options. Format as a simple list with calories and key macros."
    )

    result = ai.generate(prompt, max_tokens=800)
    return {
        'suggestions': result.get('text', ''),
        'provider': result.get('provider', 'none'),
    }


def calculate_bmr(weight, height, age, gender='male'):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return round(bmr)


def calculate_tdee(bmr, activity_level='moderate'):
    """Calculate Total Daily Energy Expenditure."""
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9,
    }
    return round(bmr * multipliers.get(activity_level, 1.55))


def get_macro_split(tdee, goal='maintain'):
    """Get macro split based on goal."""
    splits = {
        'lose_weight': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},
        'maintain': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
        'gain_muscle': {'protein': 0.35, 'carbs': 0.45, 'fat': 0.20},
        'athletic': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
    }
    split = splits.get(goal, splits['maintain'])
    return {
        'protein_g': round(tdee * split['protein'] / 4),
        'carbs_g': round(tdee * split['carbs'] / 4),
        'fat_g': round(tdee * split['fat'] / 9),
        'calories': tdee,
    }
