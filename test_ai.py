"""
Kinesis AI - AI Configuration Test Script
Tests Ollama and Gemini integration
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("  KINESIS AI - AI PROVIDER TEST")
print("=" * 60)

# Test 1: Ollama Connection
print("\n[1/3] Testing Ollama Connection...")
ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
ollama_model = os.getenv('OLLAMA_MODEL', 'gemma3:4b')

try:
    # Check if Ollama is running
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        model_names = [m.get('name', '') for m in models]
        
        print(f"  [OK] Ollama is running at {ollama_url}")
        print(f"  Available models: {', '.join(model_names[:5])}")
        
        if ollama_model in model_names:
            print(f"  [OK] Model '{ollama_model}' is available")
        else:
            print(f"  [WARN] Model '{ollama_model}' not found")
            if model_names:
                print(f"  -> Using first available model: {model_names[0]}")
                ollama_model = model_names[0]
        
        # Test actual generation
        print(f"\n  Testing generation with '{ollama_model}'...")
        test_response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": "Say 'Hello from Kinesis AI!' in one sentence.",
                "stream": False
            },
            timeout=30
        )
        
        if test_response.status_code == 200:
            result = test_response.json().get('response', '')
            print(f"  [OK] Ollama generation successful")
            print(f"  Response: {result[:100]}...")
        else:
            print(f"  [FAIL] Generation failed: {test_response.status_code}")
            
    else:
        print(f"  [FAIL] Ollama returned status {response.status_code}")
        
except requests.ConnectionError:
    print(f"  [X] Ollama is not running at {ollama_url}")
    print(f"  -> Start Ollama with: ollama serve")
except Exception as e:
    print(f"  [X] Error: {e}")

# Test 2: Gemini API
print("\n[2/3] Testing Gemini API...")
gemini_key = os.getenv('GOOGLE_API_KEY', '')

if gemini_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print(f"  [OK] Gemini API key is configured")
        
        # Test generation
        print(f"  Testing Gemini generation...")
        response = model.generate_content("Say 'Hello from Kinesis AI!' in one sentence.")
        
        if response.text:
            print(f"  [OK] Gemini generation successful")
            print(f"  Response: {response.text[:100]}...")
        else:
            print(f"  [WARN] Gemini returned empty response")
            
    except ImportError:
        print(f"  [FAIL] google-generativeai not installed")
        print(f"  -> Install with: pip install google-generativeai")
    except Exception as e:
        print(f"  [FAIL] Gemini error: {e}")
else:
    print(f"  [WARN] Gemini API key not configured")
    print(f"  -> Add GOOGLE_API_KEY to .env file")
    print(f"  -> Get key from: https://makersuite.google.com/app/apikey")

# Test 3: Application AI Provider
print("\n[3/3] Testing Application AI Provider...")
try:
    from ai_provider import get_ai
    ai = get_ai()
    status = ai.get_status()
    
    print(f"  Primary AI: {status['primary']}")
    print(f"  Ollama available: {status['ollama_available']}")
    print(f"  Gemini available: {status['gemini_available']}")
    
    if status['ollama_available'] or status['gemini_available']:
        print(f"  Testing AI coaching response...")
        result = ai.coach(
            context="User is doing push-ups with good form",
            question="How can I improve my push-up technique?"
        )
        
        if result and result.get('text'):
            print(f"  [OK] AI coaching successful")
            print(f"  Provider: {result.get('provider')}")
            print(f"  Response: {result['text'][:150]}...")
        else:
            print(f"  [FAIL] AI coaching failed")
    else:
        print(f"  [FAIL] No AI provider available")
        
except Exception as e:
    print(f"  [FAIL] Application AI test failed: {e}")

print("\n" + "=" * 60)
print("  AI TEST COMPLETE")
print("=" * 60)
