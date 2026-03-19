# 🤗 Hugging AI - Complete Documentation

A modern, open-source AI chatbot application powered by Hugging Face's Mistral-7B model. Built with Flask and featuring a beautiful, responsive frontend with real-time streaming responses and **production-grade security**.

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [How It Works](#how-it-works)
6. [Security Overview](#security-overview)
7. [Security Features (Detailed)](#security-features-detailed)
8. [Configuration](#configuration)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Performance Optimization](#performance-optimization)
12. [Learning Resources](#learning-resources)
13. [Future Enhancements](#future-enhancements)

---

## ✨ Features

- **Real-time Streaming**: Get AI responses as they're generated with streaming support
- **Modern UI**: Beautiful, dark-themed interface with smooth animations
- **Code Highlighting**: Syntax highlighting for code blocks in responses
- **Copy-to-Clipboard**: Easy code copying with a single click
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Conversation History**: Maintains context across multiple messages
- **Error Handling**: Graceful error messages and user feedback
- **Security First**: 
  - ✅ Rate limiting (10 req/min, 50 req/hour, 200 req/day)
  - ✅ Input validation & sanitization
  - ✅ XSS/SQL injection prevention
  - ✅ CSRF protection
  - ✅ Security headers (CSP, HSTS, etc.)
  - ✅ API key stored securely as environment variable
  - ✅ Comprehensive logging & monitoring
  - ✅ Subresource integrity on external libraries

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Hugging Face API key ([Get one free](https://huggingface.co/settings/tokens))

### Installation

1. **Clone or download the repository**
   ```bash
   cd hugging-ai
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Hugging Face API key**
   
   **Windows (PowerShell):**
   ```powershell
   $env:HUGGING_FACE_API_KEY = 'api key here'
   ```

   **Windows (Command Prompt):**
   ```cmd
   set HUGGING_FACE_API_KEY=api key here
   ```

   **macOS/Linux:**
   ```bash
   export HUGGING_FACE_API_KEY='api key here'
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in your browser**
   
   Navigate to: `http://localhost:5000`

---

## 📁 Project Structure

```
hugging-ai/
├── app.py                    # Flask backend with security features
├── index.html               # Main HTML template with CSP/SRI
├── static/
│   ├── script.js           # Frontend JavaScript with input validation
│   └── style.css           # Beautiful responsive styling
├── requirements.txt         # Python dependencies
├── .env.example            # Configuration template
├── README.md               # Complete documentation (this file)
└── hugging_ai_security.log # Security event logs
```

---

## 🛠️ Technology Stack

- **Backend**: Flask 3.0.0 (Python)
- **Frontend**: Vanilla JavaScript, HTML, CSS
- **AI Model**: Mistral-7B-Instruct (via Hugging Face Inference API)
- **Security**: Flask-Limiter, CSP, HSTS, SRI
- **Syntax Highlighting**: Highlight.js
- **Icons**: Font Awesome
- **Fonts**: Google Fonts Inter

---

## 📝 How It Works

1. User enters a message in the chat interface
2. Frontend validates input (length, content, rate limiting)
3. Message is sent to Flask backend via secure POST request
4. Backend validates and sanitizes the message
5. Request is sent to Hugging Face Inference API with rate limiting
6. Response streams back to the frontend in real-time
7. Frontend processes and displays the response with syntax highlighting
8. Conversation history is maintained for context (max 20 messages)

---

## 🔐 Security Overview

Hugging AI has been hardened with production-grade security features to protect against common web vulnerabilities and attacks.

### Security Improvements Summary

| Feature | Status |
|---------|--------|
| Rate Limiting | ✅ 10/min, 50/hr, 200/day |
| Input Validation | ✅ Comprehensive |
| XSS Protection | ✅ Advanced (CSP, sanitization) |
| CSRF Protection | ✅ SameSite cookies |
| SQL Injection Prevention | ✅ Pattern detection |
| Command Injection Prevention | ✅ Pattern detection |
| API Key Management | ✅ Enforced environment variable |
| Security Headers | ✅ 6+ headers added |
| Error Handling | ✅ Secure with logging |
| CORS Configuration | ✅ Restricted |
| Logging & Monitoring | ✅ File-based security logs |
| Session Security | ✅ Secure cookies + 1 hour timeout |

---

## 🔐 SECURITY FEATURES (DETAILED)

### 1. Backend Security (Flask)

#### Rate Limiting
- **Max requests per minute**: 10 requests/minute per IP
- **Max requests per hour**: 50 requests/hour per IP
- **Max requests per day**: 200 requests/day per IP
- Protects against brute force and DoS attacks

#### Input Validation & Sanitization
- Message length validation (max 2000 characters)
- Conversation history limits (max 20 messages)
- Pattern-based threat detection:
  - SQL injection attempts (DROP, SELECT, UNION, INSERT, UPDATE, EXEC)
  - Command injection attempts (rm, chmod, kill, nohup)
  - Directory traversal attempts (/etc/passwd, /proc/self)
  - Template/prototype pollution attempts ($${}, __proto__, constructor)
- HTML/XSS sanitization on all inputs
- Control character filtering

#### Security Headers
- **X-Content-Type-Options**: `nosniff` - Prevents MIME-type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking
- **X-XSS-Protection**: `1; mode=block` - Legacy XSS protection
- **Strict-Transport-Security**: HSTS enabled (1 year)
- **Content-Security-Policy**: Restrictive CSP prevents inline scripts
- **Referrer-Policy**: `strict-origin-when-cross-origin`

#### Authentication & Session
- Secure session cookies (HTTPONLY, SECURE, SAMESITE=Lax)
- Session timeout: 1 hour
- Automatic session expiration

#### CORS Configuration
- Only allows requests from same origin
- Methods restricted to POST for /chat
- Credentials mode: same-origin only
- Whitelist: `http://localhost:5000`, `http://localhost:3000`

#### API Communication
- SSL/TLS certificate verification enabled
- Request timeout: 30 seconds
- Secure User-Agent header
- Proper error handling without information leakage

#### Logging & Monitoring
- File-based security logs (`hugging_ai_security.log`)
- All security events logged:
  - Invalid requests
  - Rate limit violations
  - Potentially dangerous patterns
  - API errors
- Client IP tracking
- Request duration tracking

#### Error Handling
- No sensitive information in error messages
- Custom error handlers for all HTTP codes
- Detailed logging without exposing details to users
- Proper HTTP status codes (400, 404, 429, 500)

### 2. Frontend Security (JavaScript)

#### Input Validation
- Input length validation (client-side)
- XSS prevention pattern detection
- Input trimming and validation
- Suspicious tag detection (<script>, <iframe>, <embed>, <object>)

#### XSS Prevention
- Uses `textContent` instead of `innerHTML` where possible
- HTML escaping for error messages and user input
- Strict code block regex validation
- Only allows whitelisted language identifiers
- Response sanitization (removes control characters)

#### Rate Limiting
- Client-side rate limiting (10 requests per second max)
- Request queuing prevention
- User feedback on rate limits

#### API Security
- Same-origin-only requests
- `X-Requested-With` header for CSRF detection
- Credentials: `same-origin` only
- Proper Content-Type validation
- Safe JSON parsing

#### Data Sanitization
- Response text sanitization (removes control characters)
- Code block content safe extraction
- No HTML injection in streaming responses
- Whitelist validation for code language identifiers

#### Accessibility & UX
- Proper ARIA labels for screen readers
- Semantic HTML
- Accessibility attributes on interactive elements
- Accidental data loss prevention (beforeunload listener)

### 3. HTML Security

#### Content Security Policy (Meta Tag)
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com cdnjs.cloudflare.com; connect-src 'self'">
```

#### Subresource Integrity (SRI)
- All external libraries include integrity hashes
- Prevents compromised CDN attacks
- Font-Awesome, Highlight.js protected with hash verification
- CDN fallback configuration recommended

#### Security Meta Tags
- `X-UA-Compatible`: IE compatibility mode
- `referrer`: Controls referrer information
- `theme-color`: Basic metadata
- `X-Content-Type-Options`: Prevents MIME sniffing

#### Accessibility & Security Features
- Proper ARIA labels and roles
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly

### 4. Environment Configuration

#### Required Environment Variables
```bash
export HUGGING_FACE_API_KEY='your_actual_key_here'
export FLASK_ENV='production'  # Never 'development'
export SECRET_KEY='your_random_secret_key'  # Generated if not set
```

#### Production Setup
- Debug mode disabled by default
- Host bound to 127.0.0.1 (localhost only)
- HTTPS/SSL required for production deployment
- Environment-based configuration

---

## ⚙️ Configuration

### API Parameters

The application uses the following parameters:
- **max_new_tokens**: 512 (maximum response length)
- **temperature**: 0.7 (creativity level: 0-1)
- **top_p**: 0.95 (diversity parameter)
- **repetition_penalty**: 1.2 (discourages repetition)

Modify these in `app.py` in the `chat()` function.

### Rate Limiting Configuration

In `app.py`, adjust these limits:
```python
default_limits=["200 per day", "50 per hour"]
```

For individual route limiting:
```python
@limiter.limit(f"{MAX_MESSAGES_PER_MINUTE}/minute")
```

### Color Customization

Modify CSS variables in `static/style.css`:
```css
:root {
    --user-message-color: #ff6b6b;
    --ai-message-color: #4a5568;
    --accent-color: #ffd700;
    --background-color: #0f0f1e;
}
```

### Installation Requirements Version

See `requirements.txt`:
```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-Limiter==3.5.0
requests==2.31.0
Werkzeug==3.0.1
```

---

## 🔒 Security Best Practices

### For Users
- Never share your Hugging Face API key
- Don't paste sensitive personal information in chat
- Clear chat history when needed
- Use on trusted networks
- Keep your browser updated

### For Development
- Install dependencies from `requirements.txt` only
- Keep all packages updated: `pip install --upgrade -r requirements.txt`
- Review security logs regularly (`hugging_ai_security.log`)
- Never commit API keys to version control
- Use environment variables for all secrets
- Test input validation with malicious payloads
- Keep Flask updated for security patches

### For Deployment
1. **Use HTTPS/TLS** in production (required)
2. **Run behind a reverse proxy** (Nginx, Apache)
3. **Set strong SECRET_KEY** (at least 32 random characters)
4. **Configure rate limiting** appropriately for your use case
5. **Monitor logs** for suspicious activity
6. **Implement WAF** (Web Application Firewall) if needed
7. **Regular security audits** and penetration testing
8. **Run as non-root user** on Unix-like systems
9. **Enable firewall rules** to restrict access
10. **Keep Python and dependencies updated**

### Vulnerability Reporting

If you discover a security vulnerability, please:
1. **Do NOT** post it publicly
2. **Email** with details and proof-of-concept
3. **Allow 30 days** for patching before disclosure
4. **Avoid** accessing unauthorized data

### Protected Against

- ✅ SQL Injection
- ✅ Command Injection
- ✅ Cross-Site Scripting (XSS)
- ✅ Cross-Site Request Forgery (CSRF)
- ✅ Directory Traversal
- ✅ Brute Force Attacks
- ✅ DoS/DDoS (rate limiting)
- ✅ MIME Sniffing
- ✅ Clickjacking
- ✅ Man-in-the-Middle (with HTTPS)
- ✅ Template/Prototype Pollution

---

## 🐛 Troubleshooting

### "API Key not found" error
```bash
# Verify the environment variable is set
# PowerShell
echo $env:HUGGING_FACE_API_KEY

# Command Prompt
echo %HUGGING_FACE_API_KEY%

# Linux/Mac
echo $HUGGING_FACE_API_KEY
```

### "Connection timeout" error
- Check your internet connection
- Verify Hugging Face API is accessible
- Try again (API might be temporarily slow)
- Check firewall settings

### "Rate limit exceeded" error
- Wait a moment before sending more messages
- Frontend enforces 10 requests/second
- Backend enforces: 10/min, 50/hour, 200/day per IP

### Responses are slow
- Mistral-7B runs on shared infrastructure
- This is normal for free tier
- Upgrade Hugging Face account for faster inference
- Consider using a smaller model

### Port 5000 already in use
```python
# In app.py, change the last line:
app.run(debug=False, host="127.0.0.1", port=5001)
```

### ImportError for Flask-Limiter
```bash
pip install --upgrade Flask-Limiter
```

### Certificate verification errors
- Ensure requests library is up to date
- Check system certificate store
- Consider SSL verification settings (for development only)

---

## 📊 Performance Optimization

- Streaming responses for perceived speed increase
- Efficient conversation history management (max 20 messages)
- CSS animations use hardware acceleration
- Lazy loading ready (can be extended)
- Minimal dependencies (only Flask, CORS, Limiter, requests)
- Client-side input validation reduces server load

### Performance Tips
- Use modern browsers for best performance
- Keep history limited to avoid memory issues
- Optimize network connection for faster response times
- Consider CDN for static assets in production

---

## 📚 Learning Resources

- [Hugging Face API Docs](https://huggingface.co/docs/api-inference)
- [Flask Security](https://flask.palletsprojects.com/security/)
- [OWASP Web Security](https://owasp.org/)
- [Mistral Model](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## Testing Security

### Recommended Tools
- **OWASP ZAP**: Application security scanning (free)
- **Burp Suite Community**: Web vulnerability testing (free)
- **pip-audit**: Python dependency checking
- **Snyk**: Continuous vulnerability monitoring

### Manual Testing Checklist
```
[ ] Test XSS: <script>alert('XSS')</script>
[ ] Test SQL Injection: ' OR '1'='1
[ ] Test rate limiting: Send > 50 requests/minute
[ ] Test CORS violations: Request from different origin
[ ] Test session timeout: Wait 1+ hour
[ ] Test API key exposure: Check response headers
[ ] Test error messages: Look for information leakage
[ ] Test input limits: Send 3000+ character messages
[ ] Test special characters: Unicode, emoji, control chars
[ ] Test headers: Verify all security headers present
```

### Maintenance Schedule

#### Daily
- Check `hugging_ai_security.log` for errors
- Monitor for unusual patterns

#### Weekly
- Review rate limiting statistics
- Check for dependency updates

#### Monthly
- Run security audit
- Update dependencies if needed
- Review access patterns

#### Quarterly
- Full penetration test
- Security assessment
- Policy review

#### Annually
- Full vulnerability assessment
- Update all dependencies to latest
- Review and update security policies
- Rotate SECRET_KEY

---

## 🚀 Future Enhancements

- [ ] User authentication system
- [ ] Conversation persistence/history
- [ ] Theme switching (light/dark mode)
- [ ] Multiple AI model selection
- [ ] Export conversations to markdown/PDF
- [ ] Rich text formatting support
- [ ] Image input support (when available)
- [ ] User accounts with persistent storage
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC)
- [ ] API key rotation
- [ ] Advanced audit logging to database
- [ ] WAF (Web Application Firewall) integration
- [ ] DLP (Data Loss Prevention) features

---

## 💡 Tips & Tricks

- **Code requests**: Ask for code in a specific language
- **Follow-ups**: Ask clarifying questions for detailed answers
- **Format requests**: Ask for formatted output (JSON, CSV, etc.)
- **Debugging**: Paste errors and ask for solutions
- **Explanations**: Ask complex topics to be explained simply

---

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Feel free to fork, modify, and improve this project! For security issues, please report responsibly.

---

## ⚠️ Security Disclaimer

While this application implements production-grade security measures, no system is 100% secure. For production deployments:
- Consider additional hardening
- Perform regular security audits
- Monitor logs and alerts
- Keep all software updated
- Use HTTPS/TLS
- Implement additional authentication
- Review and test before deployment

---

## 📋 Deployment Guide

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGING_FACE_API_KEY='your_key'
export FLASK_ENV='development'

# Run
python app.py
```

### Production Setup
```bash
# Use HTTPS (required)
# Run behind reverse proxy (Nginx/Apache)
# Use strong SECRET_KEY
# Enable firewall rules
# Monitor security logs
```

### Docker Setup (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_APP=app.py

CMD ["python", "app.py"]
```

---

**Made with ❤️ for the Open Source Community**

**Latest Update**: March 2026  
**Security Level**: Production-Grade ✅  
**Version**: 1.0.0

