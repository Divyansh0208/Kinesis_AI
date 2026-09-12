import re
import logging
import json
import concurrent.futures
from typing import Dict, Any, List
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama library not installed. Diet plans will use mock data.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DietService:
    def __init__(self, default_model="llama3.2"):
        self.model_name = default_model
        self._ensure_model_available()

    def _ensure_model_available(self):
        """Auto-detects available models and switches if default is missing."""
        if not OLLAMA_AVAILABLE:
            return

        try:
            models_info = ollama.list()
            available_models = []

             # Handle object-based response (newer ollama client)
            if hasattr(models_info, 'models'):
                for m in models_info.models:
                    name = getattr(m, 'model', None) or getattr(m, 'name', None)
                    if not name and isinstance(m, dict):
                        name = m.get('model') or m.get('name')
                    if name:
                        available_models.append(name)
                    else:
                        available_models.append(str(m))

            elif isinstance(models_info, dict) and 'models' in models_info:
                 for m in models_info['models']:
                    if isinstance(m, dict):
                        name = m.get('model') or m.get('name')
                    else:
                        name = getattr(m, 'model', None) or getattr(m, 'name', None)

                    if name:
                        available_models.append(name)
                    else:
                        available_models.append(str(m))
            else:
                available_models = [str(m) for m in models_info]

            logger.info(f"DietService found available Ollama models: {available_models}")

            if self.model_name not in available_models and f"{self.model_name}:latest" not in available_models:
                preferred = ['llama3.2', 'llama3', 'mistral', 'gemma', 'tinyllama']
                found = False
                for p in preferred:
                    for av in available_models:
                        if p in av:
                            self.model_name = av
                            logger.info(f"DietService switched to available model: {self.model_name}")
                            found = True
                            break
                    if found: break

                if not found and available_models:
                    self.model_name = available_models[0]
                    logger.info(f"DietService using only available model: {self.model_name}")

            # Reasoning models (deepseek-r1 etc.) burn a lot of tokens on <think>
            # before ever emitting JSON, so give them much more room and time.
            self.is_reasoning_model = any(
                tag in self.model_name.lower() for tag in
                ['deepseek-r1', 'r1', 'qwq', 'qwen3', 'phi4-reasoning',
                 'magistral', 'gpt-oss', 'granite3.3', 'exaone']
            )

        except Exception as e:
            logger.warning(f"DietService failed to list Ollama models: {e}")
            self.is_reasoning_model = False

    def check_ollama_status(self) -> bool:
        if not OLLAMA_AVAILABLE: return False
        try:
            ollama.list()
            return True
        except Exception:
            return False

    def _extract_json(self, content: str) -> str:
        """Pulls the JSON object out of a model response, tolerant of
        unclosed <think> tags, code fences, or extra prose around it."""
        # Strip a fully-closed think block
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        # If there's an unclosed <think>, drop everything up to end of tag text,
        # keep whatever (if anything) comes after an eventual </think>
        if '<think>' in content and '</think>' not in content:
            content = content.split('<think>', 1)[1]

        content = content.strip()

        if "```json" in content:
            content = content.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]

        content = content.strip()

        if not content.startswith('{'):
            # grab the first {...} block anywhere in the text
            match = re.search(r'\{.*\}', content, flags=re.DOTALL)
            if match:
                content = match.group(0)

        return content.strip()

    def generate_diet_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a 1-day meal plan using local LLM.
        Args:
            user_profile: Dict containing 'age', 'weight', 'goal', 'preference', 'allergies'
        """
        age = user_profile.get('age', 25)
        weight = user_profile.get('weight', 70)
        goal = user_profile.get('goal', 'maintain')
        diet_type = user_profile.get('preference', 'standard')
        allergies = user_profile.get('allergies', 'none')

        logger.info(f"Generating diet plan for: {diet_type}, {goal}, allergies: {allergies}")

        if not self.check_ollama_status():
            return self._get_fallback_plan(diet_type, goal, allergies)

        prompt = f"""
        You are an expert Nutritionist. Create a detailed 1-Day Meal Plan for a person with these details:
        - Diet Preference: {diet_type}
        - Fitness Goal: {goal}
        - Allergies/Restrictions: {allergies}
        - Weight: {weight}kg

        Your response must be a valid JSON object with the following structure:
        {{
            "summary": "Brief summary of why this plan works for the goal",
            "macros": {{ "protein": "150g", "carbs": "200g", "fats": "70g", "calories": "2200" }},
            "meals": [
                {{ "type": "Breakfast", "name": "Meal Name", "ingredients": "Key ingredients list", "calories": 500 }},
                {{ "type": "Lunch", "name": "Meal Name", "ingredients": "Key ingredients list", "calories": 700 }},
                {{ "type": "Snack", "name": "Snack Name", "ingredients": "Key ingredients list", "calories": 200 }},
                {{ "type": "Dinner", "name": "Meal Name", "ingredients": "Key ingredients list", "calories": 600 }}
            ]
        }}

        Ensure the meals STRICTLY respect the diet preference (e.g. if Vegan, NO animal products).
        Return ONLY valid JSON. Do not include any text after the closing brace.
        """

        # Reasoning models need much more headroom for their thinking pass.
        num_predict = 3000 if getattr(self, 'is_reasoning_model', False) else 900
        num_ctx = 4096
        timeout_s = 120 if getattr(self, 'is_reasoning_model', False) else 60

        messages = [
            {'role': 'system', 'content': 'You are a nutritionist assistant that outputs only JSON.'},
            {'role': 'user', 'content': prompt},
        ]

        def _call(np, to, think_off):
            kwargs = dict(
                model=self.model_name,
                messages=messages,
                options={"num_predict": np, "num_ctx": num_ctx},
            )
            if think_off:
                kwargs["think"] = False  # supported on newer ollama-python; dropped below if not
            with concurrent.futures.ThreadPoolExecutor() as ex:
                try:
                    future = ex.submit(ollama.chat, **kwargs)
                    return future.result(timeout=to)
                except TypeError:
                    kwargs.pop("think", None)
                    future = ex.submit(ollama.chat, **kwargs)
                    return future.result(timeout=to)

        try:
            # First attempt: try to switch thinking off outright (cheapest fix).
            response = _call(num_predict, timeout_s, think_off=True)
            raw_content = response['message']['content']
            content = self._extract_json(raw_content)

            if not content:
                # Thinking mode likely still on and burned the whole budget.
                # Retry once with a much larger budget, thinking left on.
                logger.warning(
                    f"Empty content on first pass (raw={raw_content[:200]!r}); "
                    "retrying with larger num_predict."
                )
                bigger_np = max(num_predict * 4, 4000)
                response = _call(bigger_np, timeout_s * 2, think_off=False)
                raw_content = response['message']['content']
                content = self._extract_json(raw_content)

            if not content:
                logger.error(
                    f"Empty content after extraction on retry. Raw response was: {raw_content[:500]!r}"
                )
                raise ValueError(
                    "Model produced no JSON — likely truncated mid-<think> by num_predict. "
                    "Try a larger num_predict or a non-reasoning model."
                )

            plan = json.loads(content)
            return {"success": True, "plan": plan}

        except concurrent.futures.TimeoutError:
            logger.warning("Ollama timed out generating diet plan")
            return self._get_fallback_plan(diet_type, goal, allergies, error="ollama timeout")

        except Exception as e:
            logger.error(f"Error generating diet plan: {e}")
            return self._get_fallback_plan(diet_type, goal, allergies, error=str(e))

    def _get_fallback_plan(self, diet_type, goal, allergies="none", error=None) -> Dict[str, Any]:
        """Returns a static plan if AI is unavailable — now diet-preference aware
        instead of always serving chicken/salmon."""
        diet_type_l = (diet_type or "").lower()
        is_veg = any(k in diet_type_l for k in ["vegetarian", "vegan"])
        is_vegan = "vegan" in diet_type_l

        if is_vegan:
            meals = [
                {"type": "Breakfast", "name": "Oatmeal & Berries", "ingredients": "Oats, Blueberries, Almonds, Plant Milk, Maple Syrup", "calories": 450},
                {"type": "Lunch", "name": "Chickpea & Quinoa Bowl", "ingredients": "Chickpeas, Quinoa, Mixed Greens, Olive Oil", "calories": 650},
                {"type": "Snack", "name": "Almond Butter & Apple", "ingredients": "Apple, Almond Butter", "calories": 200},
                {"type": "Dinner", "name": "Tofu Stir-Fry", "ingredients": "Tofu, Broccoli, Brown Rice, Soy Sauce", "calories": 600},
            ]
        elif is_veg:
            meals = [
                {"type": "Breakfast", "name": "Oatmeal & Berries", "ingredients": "Oats, Blueberries, Almonds, Honey", "calories": 450},
                {"type": "Lunch", "name": "Paneer & Chickpea Salad", "ingredients": "Paneer, Chickpeas, Mixed Greens, Olive Oil", "calories": 650},
                {"type": "Snack", "name": "Greek Yogurt", "ingredients": "Yogurt, Chia Seeds", "calories": 200},
                {"type": "Dinner", "name": "Lentil & Quinoa Bowl", "ingredients": "Lentils, Quinoa, Roasted Vegetables", "calories": 600},
            ]
        else:
            meals = [
                {"type": "Breakfast", "name": "Oatmeal & Berries", "ingredients": "Oats, Blueberries, Almonds, Honey", "calories": 450},
                {"type": "Lunch", "name": "Grilled Chicken Salad", "ingredients": "Chicken Breast, Mixed Greens, Olive Oil", "calories": 650},
                {"type": "Snack", "name": "Greek Yogurt", "ingredients": "Yogurt, Chia Seeds", "calories": 200},
                {"type": "Dinner", "name": "Salmon & Asparagus", "ingredients": "Salmon Fillet, Asparagus, Quinoa", "calories": 600},
            ]

        plan = {
            "summary": f"Balanced plan for {diet_type or 'standard'} diet.",
            "macros": {"protein": "140g", "carbs": "180g", "fats": "65g", "calories": "2000"},
            "meals": meals,
        }

        result = {"success": True, "plan": plan, "is_fallback": True}
        if error:
            result["error"] = error
        return result