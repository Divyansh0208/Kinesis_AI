# Kinesis AI - Team Deployment Setup Guide

## 🚀 Quick Start for Team Access

### 1. Install Ollama (Required for Local AI)

#### Windows Installation:
1. Download from: https://ollama.com/download
2. Run the installer: `OllamaSetup.exe`
3. Open command prompt and verify: `ollama --version`

#### Pull the AI Model:
```bash
ollama pull gemma3:4b
```

Alternative models (if preferred):
```bash
ollama pull mistral
ollama pull llama2
```

### 2. Configure Gemini API (Optional Fallback)

1. Go to: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add it to `.env` file:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 3. Start the Application

```bash
cd C:\Users\HP\Downloads\KinesisFX
python run.py
```

### 4. Team Access URLs

The application will be accessible at:
- **Local**: http://localhost:5000
- **Network**: http://172.16.182.227:5000
- **Your IP**: Check with `ipconfig` command

Share the network URL with your teammates!

## 🔧 Configuration Options

### Environment Variables (.env file)

```bash
# Server Settings
HOST=0.0.0.0              # Allow network access
PORT=5000                 # Port number
FLASK_DEBUG=1             # Debug mode (set to 0 for production)

# AI Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b     # Or mistral, llama2, etc.
GOOGLE_API_KEY=           # Optional Gemini fallback

# Database
DATABASE_URL=sqlite:///kinesis.db
```

### AI Provider Priority

1. **Ollama (Primary)**: Local, privacy-first, no internet needed
2. **Gemini (Fallback)**: Cloud-based, requires internet and API key

## 🌐 Network Setup for Team Access

### Firewall Configuration

Allow port 5000 through Windows Firewall:
```powershell
New-NetFirewallRule -DisplayName "Kinesis AI" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### Check Your IP Address
```bash
ipconfig
```
Look for "IPv4 Address" under your network adapter.

### Share with Team
Share: `http://YOUR_IP:5000`
Example: `http://192.168.1.100:5000`

## 🧪 Testing AI Features

### Test Ollama Integration
```bash
# Start Ollama service
ollama serve

# Test model
ollama run gemma3:4b "Hello, can you provide some fitness advice?"
```

### Test in Application
1. Navigate to http://localhost:5000
2. Go to Sports → Workout Generator
3. Generate a training plan
4. Check which AI provider is used

## 🐛 Troubleshooting

### Ollama Issues
- **Connection refused**: Make sure Ollama is running (`ollama serve`)
- **Model not found**: Pull the model (`ollama pull gemma3:4b`)
- **Slow response**: Try a smaller model (`ollama pull mistral`)

### Network Access Issues
- **Teammates can't connect**: Check Windows Firewall
- **Wrong IP**: Verify your current IP with `ipconfig`
- **Port blocked**: Ensure port 5000 is not used by other apps

### AI Not Working
- **Both providers unavailable**: Check Ollama status and Gemini API key
- **Fallback not working**: Verify Gemini API key is valid
- **Timeout errors**: Check internet connection for Gemini

## 🚀 Production Deployment

For production deployment, consider:

1. **Use Gunicorn instead of Flask dev server**
2. **Set up PostgreSQL database**
3. **Configure HTTPS/SSL**
4. **Use environment-specific configs**
5. **Set up proper logging**
6. **Configure backup strategies**

## 📞 Support

For issues or questions:
- Check the PROJECT_STATUS.md for current system status
- Review logs in the terminal for error messages
- Test individual components (Ollama, Flask, Database)

---

**Happy Training! 🏆**
