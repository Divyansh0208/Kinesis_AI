# Kinesis AI - Deployment Guide

This document provides instructions for deploying Kinesis AI in development and production environments.

## Development Deployment

### Prerequisites

- Python 3.10 - 3.12
- Git
- Webcam (for testing)
- Modern browser

### Local Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/Divyansh0208/Kinesis_AI.git
cd Kinesis_AI
```

2. **Create Virtual Environment**
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your settings
# Notepad on Windows
notepad .env

# Nano on Linux/Mac
nano .env
```

Required environment variables:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
GOOGLE_API_KEY=your_gemini_api_key_here
SESSION_SECRET=change-this-to-a-random-secret-key
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///kinesis.db
```

5. **Initialize Database**
```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

6. **Run Development Server**
```bash
python run.py
```

The application will be available at http://localhost:5000

### Development Tools

**Run Tests:**
```bash
python test_suite.py
# Or with pytest
pytest tests/
```

**Check AI Status:**
```bash
python test_ai.py
```

**Database Shell:**
```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.session.execute('SELECT * FROM users')"
```

## Production Deployment

### Platform Options

**Recommended Platforms:**
- **Heroku:** Easy deployment, managed PostgreSQL
- **Railway:** Modern deployment, good free tier
- **DigitalOcean:** Full control, scalable
- **AWS/Azure/GCP:** Enterprise-grade, complex setup

### Production Configuration

1. **Environment Variables**

Update `.env` for production:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
GOOGLE_API_KEY=your_production_gemini_api_key
SESSION_SECRET=<generate-random-32-char-string>
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql://user:password@host:5432/kinesis_prod
SECRET_KEY=<another-random-string>
```

Generate secure secrets:
```python
import secrets
print(secrets.token_hex(32))
```

2. **Database Migration**

**Option A: PostgreSQL (Recommended)**
```sql
-- Create database
CREATE DATABASE kinesis_prod;
CREATE USER kinesis_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE kinesis_prod TO kinesis_user;
```

Update `DATABASE_URL`:
```env
DATABASE_URL=postgresql://kinesis_user:secure_password@localhost:5432/kinesis_prod
```

**Option B: SQLite (Simple)**
```env
DATABASE_URL=sqlite:///kinesis_prod.db
```

3. **WSGI Server**

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Gunicorn options:
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--timeout 120`: Increase timeout for AI requests
- `--access-logfile -`: Log to stdout
- `--error-logfile -`: Log errors to stdout

4. **Process Manager (Systemd)**

Create `/etc/systemd/system/kinesis.service`:
```ini
[Unit]
Description=Kinesis AI Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kinesis
Environment="PATH=/var/www/kinesis/venv/bin"
ExecStart=/var/www/kinesis/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kinesis
sudo systemctl start kinesis
sudo systemctl status kinesis
```

### Heroku Deployment

1. **Create Heroku App**
```bash
heroku create kinesis-ai
```

2. **Set Environment Variables**
```bash
heroku config:set SESSION_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set GOOGLE_API_KEY=your_api_key
heroku config:set OLLAMA_BASE_URL=http://localhost:11434
```

3. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Create Procfile**

Create `Procfile` in project root:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"
```

5. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Railway Deployment

1. **Create Railway Project**
```bash
railway login
railway init
```

2. **Add PostgreSQL**
```bash
railway add postgresql
```

3. **Configure Environment Variables**
Use Railway dashboard to set:
- `SESSION_SECRET`
- `GOOGLE_API_KEY`
- `OLLAMA_BASE_URL`
- `DATABASE_URL` (auto-set by Railway)

4. **Deploy**
```bash
railway up
```

### Docker Deployment

1. **Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

2. **Create .dockerignore**
```
venv/
__pycache__/
*.pyc
.env
.git
.gitignore
instance/
*.db
```

3. **Build and Run**
```bash
docker build -t kinesis-ai .
docker run -p 5000:5000 --env-file .env kinesis-ai
```

### Nginx Reverse Proxy

1. **Install Nginx**
```bash
sudo apt update
sudo apt install nginx
```

2. **Configure Nginx**

Create `/etc/nginx/sites-available/kinesis`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/kinesis/static;
    }

    client_max_body_size 16M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/kinesis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

3. **SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Health Check

### Health Endpoint

The application provides a health check endpoint:

```bash
curl http://localhost:5000/api/status
```

Response:
```json
{
  "status": "healthy",
  "ai": {
    "ollama_available": true,
    "gemini_available": false,
    "primary": "ollama"
  },
  "version": "2.0.0 (SIH 2026 Edition)"
}
```

### Monitoring

**Basic Monitoring:**
```bash
# Check process
ps aux | grep gunicorn

# Check logs
sudo journalctl -u kinesis -f

# Check port
netstat -tlnp | grep 5000
```

**Advanced Monitoring:**
- Use Sentry for error tracking
- Use New Relic or Datadog for APM
- Use Prometheus + Grafana for metrics

## Backup Strategy

### Database Backup

**PostgreSQL:**
```bash
# Backup
pg_dump -U kinesis_user kinesis_prod > backup_$(date +%Y%m%d).sql

# Restore
psql -U kinesis_user kinesis_prod < backup_20240913.sql
```

**SQLite:**
```bash
# Backup
cp kinesis_prod.db backup_$(date +%Y%m%d).db

# Restore
cp backup_20240913.db kinesis_prod.db
```

### Automated Backup

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * pg_dump -U kinesis_user kinesis_prod > /backups/kinesis_$(date +\%Y\%m\%d).sql
```

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

**2. Database Connection Error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
echo $DATABASE_URL
```

**3. Permission Denied**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/kinesis
sudo chmod -R 755 /var/www/kinesis
```

**4. AI Not Working**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check environment variables
heroku config  # Heroku
railway variables  # Railway
```

## Performance Tuning

### Gunicorn Workers

Calculate workers: `(2 x CPU cores) + 1`

```bash
# 4 core CPU
gunicorn -w 9 -b 0.0.0.0:5000 "app:create_app()"
```

### Database Connection Pool

Update `app.py`:
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}
```

### Static File Serving

For production, use Nginx or CDN for static files:
```nginx
location /static {
    alias /var/www/kinesis/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Security Checklist

- [ ] Change `SESSION_SECRET` to random value
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only necessary ports)
- [ ] Set up fail2ban for brute force protection
- [ ] Enable log rotation
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migration tested
- [ ] Backup strategy in place
- [ ] SSL certificate ready
- [ ] Domain DNS configured
- [ ] Monitoring set up
- [ ] Error tracking configured

### Post-Deployment
- [ ] Health check endpoint responding
- [ ] Database connections working
- [ ] AI services accessible
- [ ] Static files loading
- [ ] User registration/login working
- [ ] Core functionality tested
- [ ] Performance monitored
- [ ] Logs reviewed

---

*Last Updated: 2026-09-13*
*Kinesis AI - Smart India Hackathon 2026*
