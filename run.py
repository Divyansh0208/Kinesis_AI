"""
Kinesis AI - Application Entry Point
Run: python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', '1') == '1'
    port = int(os.getenv('PORT', '5000'))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"[START] Starting Kinesis AI Server...")
    print(f"[ACCESS] URL: http://{host}:{port}")
    print(f"[LOCAL] URL: http://localhost:{port}")
    print(f"[NETWORK] URL: http://172.16.182.227:{port}")
    print(f"[AI] Ollama Primary, Gemini Fallback")
    
    app.run(host=host, port=port, debug=debug_mode)
