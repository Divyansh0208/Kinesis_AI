@echo off
echo ========================================
echo   KINESIS AI - Team Deployment Startup
echo ========================================
echo.

echo [1/4] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Ollama not found. Please install from https://ollama.com/download
    echo   Press any key to open download page...
    pause >nul
    start https://ollama.com/download
    exit /b 1
)
echo   OK: Ollama is installed
echo.

echo [2/4] Checking Ollama model...
ollama list | findstr "gemma3:4b" >nul 2>&1
if %errorlevel% neq 0 (
    echo   WARNING: gemma3:4b model not found
    echo   Pulling model now (this may take a few minutes)...
    ollama pull gemma3:4b
    if %errorlevel% neq 0 (
        echo   ERROR: Failed to pull model
        exit /b 1
    )
)
echo   OK: gemma3:4b model is available
echo.

echo [3/4] Starting Ollama service...
start /min ollama serve
timeout /t 3 /nobreak >nul
echo   OK: Ollama service started
echo.

echo [4/4] Starting Kinesis AI application...
echo   Access URLs:
echo   - Local:    http://localhost:5000
echo   - Network: http://172.16.182.227:5000
echo   - Team:     Share network URL with teammates
echo.
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

python run.py
