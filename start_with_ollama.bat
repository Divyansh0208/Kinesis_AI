@echo off
echo ========================================
echo   KINESIS AI - Start with Ollama
echo ========================================
echo.

echo [STEP 1] Starting Ollama service...
start /min "" "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
timeout /t 5 /nobreak >nul
echo [OK] Ollama service started
echo.

echo [STEP 2] Checking available models...
"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
echo.

echo [STEP 3] Starting Kinesis AI application...
echo.
echo Access URLs:
echo - Local:    http://localhost:5000
echo - Network:  http://172.16.182.227:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python run.py
