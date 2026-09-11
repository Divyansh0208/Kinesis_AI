@echo off
echo ========================================
echo   KINESIS AI - Quick Setup & Start
echo ========================================
echo.

echo [STEP 1] Starting Ollama service...
start /min "" "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
timeout /t 5 /nobreak >nul
echo [OK] Ollama service started
echo.

echo [STEP 2] Pulling a lightweight AI model (phi3)...
echo This is much smaller and faster than gemma3:4b
echo.

"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull phi3

if %errorlevel% equ 0 (
    echo [OK] phi3 model downloaded successfully
) else (
    echo [WARN] Model download failed, trying fallback...
    "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.2
)

echo.
echo [STEP 3] Updating configuration...
echo OLLAMA_MODEL=phi3 > .env.tmp
echo OLLAMA_BASE_URL=http://localhost:11434 >> .env.tmp
echo SESSION_SECRET=kinesis-team-deployment-secret-change-in-production-2026 >> .env.tmp
echo FLASK_ENV=development >> .env.tmp
echo FLASK_DEBUG=1 >> .env.tmp
echo DATABASE_URL=sqlite:///kinesis.db >> .env.tmp
echo GOOGLE_API_KEY= >> .env.tmp
move /Y .env.tmp .env

echo [OK] Configuration updated
echo.

echo [STEP 4] Starting Kinesis AI application...
echo.
echo Access URLs:
echo - Local:    http://localhost:5000
echo - Network:  http://172.16.182.227:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python run.py
