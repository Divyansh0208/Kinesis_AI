"""
Kinesis AI - Ollama Service
Direct client for local Ollama API.
Used by ai_provider.py as the PRIMARY AI engine.
"""

import os
import logging
import requests
import json

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma3:4b')


def check_ollama_health():
    """Check if Ollama server is running."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def list_models():
    """List available Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            return [m.get('name', '') for m in resp.json().get('models', [])]
    except Exception:
        pass
    return []


def chat(prompt, system_prompt=None, model=None, temperature=0.7, max_tokens=2048):
    """
    Send a chat request to Ollama.
    Returns the response text or None on failure.
    """
    model = model or OLLAMA_MODEL
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
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
        return data.get("message", {}).get("content", "")
    except requests.ConnectionError:
        logger.warning("Ollama is not running")
        return None
    except Exception as e:
        logger.error(f"Ollama chat error: {e}")
        return None


def generate(prompt, model=None, temperature=0.7, max_tokens=2048):
    """
    Send a generate request to Ollama (single prompt, no chat history).
    Returns the response text or None on failure.
    """
    model = model or OLLAMA_MODEL

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
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
        return data.get("response", "")
    except requests.ConnectionError:
        logger.warning("Ollama is not running")
        return None
    except Exception as e:
        logger.error(f"Ollama generate error: {e}")
        return None
