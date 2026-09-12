# Kinesis AI - Security Documentation

This document outlines the security measures, best practices, and considerations for the Kinesis AI system.

## Security Principles

1. **Privacy First:** User data processed locally when possible
2. **Defense in Depth:** Multiple layers of security
3. **Least Privilege:** Minimal access required
4. **Transparency:** Clear communication about data handling
5. **Security by Design:** Security considered from the start

## Data Privacy

### Video Processing

**Current Implementation:**
- Video frames processed **locally in browser** using MediaPipe JavaScript
- **No video frames uploaded to server**
- Only structured metrics (angles, scores) sent to backend
- AI processing uses metrics, not video

**Data Flow:**
```
Webcam
  ↓ (local)
MediaPipe JS (browser)
  ↓ (landmarks only)
Flask Backend (metrics only)
  ↓ (if AI needed)
Ollama (local) or Gemini (cloud)
```

**Privacy Guarantees:**
- Video never leaves user's device
- No video storage on server
- No video sharing with third parties
- Metrics are anonymized where possible

### User Data

**Data Stored:**
- User profile (username, email, hashed password)
- Workout sessions (exercise type, reps, scores)
- Sports sessions (sport, skill, scores)
- Training plans (generated content)
- Achievements (badges, XP)

**Data Not Stored:**
- Video recordings
- Biometric data (beyond exercise metrics)
- Sensitive personal information
- Health records (explicitly not medical)

### AI Privacy

**Ollama (Local):**
- All processing on user's machine
- No data sent to external services
- Complete privacy
- Offline capability

**Gemini (Cloud):**
- Only structured metrics sent (not video)
- No PII in prompts
- Request/response logging per Google's policy
- Users can opt-out by not using cloud AI

## Authentication & Authorization

### Current Implementation

**Flask-Login:**
- Session-based authentication
- Secure session cookies
- Password hashing with Werkzeug
- CSRF protection on forms

**Password Security:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing
user.set_password('user_password')  # Uses PBKDF2 with SHA-256

# Verification
if user.check_password('input_password'):
    # Valid
```

**Session Management:**
- Secure cookie flags
- Session expiration
- Logout functionality
- Protected routes

### Recommendations for Production

1. **Enable HTTPS:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

2. **Session Security:**
```python
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

3. **Rate Limiting:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/fitness/analyze')
@limiter.limit("60 per minute")
def analyze_fitness():
    # ...
```

4. **Two-Factor Authentication (Future):**
- Implement TOTP (Time-based One-Time Password)
- SMS verification
- Email verification

## API Security

### Input Validation

**Current Implementation:**
- Type checking on expected data types
- Length limits on input fields
- Validation of exercise types
- Landmark count validation

**Example:**
```python
if len(raw_landmarks) < 33:
    return jsonify({'error': 'Insufficient landmarks'}), 400
```

**Recommendations:**
- Sanitize all user inputs
- Validate JSON schemas
- Use whitelist for allowed values
- Implement request size limits

### Output Encoding

**Current Implementation:**
- Flask's `jsonify` handles JSON encoding
- Jinja2 auto-escapes HTML in templates
- No raw HTML in user-generated content

**Recommendations:**
- Content Security Policy (CSP) headers
- X-XSS-Protection header
- X-Content-Type-Options header

### API Rate Limiting

**Recommended Limits:**
- Fitness analysis: 60 requests/minute
- Voice chat: 20 requests/minute
- Training plans: 5 requests/hour
- General API: 100 requests/minute

## Database Security

### Current Implementation

**SQLAlchemy ORM:**
- Parameterized queries (SQL injection protection)
- Connection pooling
- Type-safe operations

**Password Storage:**
- PBKDF2 with SHA-256
- Salt automatically generated
- 260,000 iterations (default)

### Recommendations for Production

1. **PostgreSQL Security:**
```sql
-- Create dedicated user
CREATE USER kinesis_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE kinesis_prod TO kinesis_app;
GRANT USAGE ON SCHEMA public TO kinesis_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kinesis_app;
```

2. **Connection Security:**
- Use SSL for database connections
- Limit database access by IP
- Regular password rotation
- Connection encryption

3. **Backup Security:**
- Encrypt backups at rest
- Secure backup storage
- Access logging for backups
- Regular backup testing

## Secrets Management

### Current Implementation

**Environment Variables:**
- API keys in `.env` file
- `.env` in `.gitignore`
- `.env.example` provided

**Secrets Required:**
```env
SESSION_SECRET=          # Flask session encryption
GOOGLE_API_KEY=          # Gemini API
DATABASE_URL=           # Database connection
OLLAMA_BASE_URL=        # Ollama endpoint
```

### Recommendations for Production

1. **Use Secret Management Service:**
- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Azure Key Vault

2. **Environment-Specific Secrets:**
- Different secrets for dev/staging/prod
- Never commit secrets to git
- Regular secret rotation
- Audit secret access

3. **CI/CD Security:**
- Use encrypted secrets in GitHub Actions
- Never log secrets
- Rotate leaked secrets immediately

## Vulnerability Management

### Dependency Security

**Current Dependencies:**
- Flask 3.1.1
- SQLAlchemy 2.0.36
- MediaPipe 0.10.21
- NumPy 1.26.4

**Recommendations:**
```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies regularly
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Use dependabot for GitHub
# Enable automated security updates
```

### Code Security

**Best Practices:**
- No `eval()` or `exec()` on user input
- No dynamic SQL queries
- Input validation on all endpoints
- Error handling without information leakage
- Logging without sensitive data

**Security Headers:**
```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Compliance Considerations

### Medical Disclaimer

**Explicit Statement:**
"This is a movement-risk indicator, not a medical diagnosis. Consult a qualified coach or healthcare professional if you experience pain or symptoms."

**Implementation:**
- Disclaimer on all risk indicators
- Disclaimer in injury risk engine
- Disclaimer in user-facing messages
- Not marketed as medical device

### Data Protection

**GDPR Considerations:**
- Right to data deletion
- Data portability
- Clear privacy policy
- User consent for data processing
- Data minimization

**HIPAA Considerations:**
- Not designed as medical device
- Not handling PHI (Protected Health Information)
- Explicitly not for medical diagnosis
- No health records storage

### Accessibility

**Current Implementation:**
- Semantic HTML
- Keyboard navigation
- Screen reader compatible
- Responsive design

**Recommendations:**
- WCAG 2.1 AA compliance
- Alt text for images
- Color contrast ratios
- Focus indicators

## Security Testing

### Automated Testing

**Security Tests:**
```python
def test_sql_injection_protection():
    """Test SQL injection attempts are blocked"""
    malicious_input = "'; DROP TABLE users; --"
    # Should not execute SQL injection
    response = client.post('/login', data={'username': malicious_input})
    assert response.status_code == 200  # Should not crash

def test_xss_protection():
    """Test XSS attempts are escaped"""
    xss_input = "<script>alert('xss')</script>"
    response = client.post('/register', data={'username': xss_input})
    assert b'<script>' not in response.data  # Should be escaped
```

### Security Scanning

**Tools:**
- Bandit: Python security linter
- Safety: Dependency vulnerability scanner
- OWASP ZAP: Web application scanner
- SSL Labs: SSL/TLS configuration

### Penetration Testing

**Recommended:**
- Annual penetration test
- Test before production launch
- Test after major changes
- Third-party security audit

## Incident Response

### Security Incident Types

1. **Data Breach:** Unauthorized access to user data
2. **Service Disruption:** DDoS, system compromise
3. **Authentication Bypass:** Unauthorized account access
4. **API Abuse:** Rate limit bypass, exploitation

### Response Plan

1. **Detection:**
   - Monitoring alerts
   - User reports
   - Automated scans

2. **Containment:**
   - Isolate affected systems
   - Block malicious IPs
   - Disable compromised accounts

3. **Eradication:**
   - Remove malware
   - Patch vulnerabilities
   - Update credentials

4. **Recovery:**
   - Restore from backups
   - Monitor for recurrence
   - Update security measures

5. **Communication:**
   - Notify affected users
   - Report to authorities (if required)
   - Post-incident analysis

## Security Checklist

### Pre-Deployment
- [ ] All secrets in environment variables
- [ ] HTTPS/SSL configured
- [ ] Database connection encrypted
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Output encoding configured
- [ ] Security headers added
- [ ] CSRF protection enabled
- [ ] Dependencies updated
- [ ] Security scan completed

### Post-Deployment
- [ ] Monitoring configured
- [ ] Logging enabled
- [ ] Alerting set up
- [ ] Backup strategy tested
- [ ] Incident response plan documented
- [ ] Security documentation available
- [ ] User privacy policy published
- [ ] Contact information for security issues

## Reporting Security Issues

**For Researchers:**
- Please report security vulnerabilities responsibly
- Email: security@example.com (to be configured)
- Allow 90 days for remediation before disclosure
- Follow responsible disclosure practices

**Bug Bounty:**
- Not currently implemented
- Consider for post-launch
- Define scope and rewards

## Security Resources

**Documentation:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Flask Security: https://flask.palletsprojects.com/en/latest/security/
- Python Security: https://python.readthedocs.io/en/latest/library/security.html

**Tools:**
- Safety: https://github.com/pyupio/safety
- Bandit: https://github.com/PyCQA/bandit
- OWASP ZAP: https://www.zaproxy.org/

---

*Last Updated: 2026-09-13*
*Kinesis AI - Smart India Hackathon 2026*
