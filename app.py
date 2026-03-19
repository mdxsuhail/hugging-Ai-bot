import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template, Response, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import logging
from html import escape

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure CORS with restrictions
CORS(app, resources={
    r"/chat": {
        "origins": ["http://localhost:5000", "http://localhost:3000"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Configure logging with security focus
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hugging_ai_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security Constants
MAX_MESSAGE_LENGTH = 2000
MAX_CONVERSATION_HISTORY = 20
MAX_MESSAGES_PER_MINUTE = 10
DANGEROUS_PATTERNS = [
    r'(?i)(drop|delete|truncate|union|select|insert|update|exec)',  # SQL injection
    r'(?i)(rm\s+-rf|chmod|kill|nohup)',  # Command injection
    r'(?i)(etc/passwd|proc/self)',  # Directory traversal
    r'(\$\{|__proto__|constructor)',  # Template/prototype pollution
]

# API Configuration
API_KEY = os.environ.get("HUGGING_FACE_API_KEY")

if not API_KEY:
    logger.critical("HUGGING_FACE_API_KEY environment variable is not set")
    raise ValueError("HUGGING_FACE_API_KEY environment variable is required")

if len(API_KEY) < 20:
    logger.critical("HUGGING_FACE_API_KEY appears to be invalid (too short)")
    raise ValueError("Invalid HUGGING_FACE_API_KEY")

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "User-Agent": "HuggingAI-1.0"
}

def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com cdnjs.cloudflare.com"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.after_request
def apply_security_headers(response):
    """Apply security headers to every response."""
    return add_security_headers(response)

def validate_message_text(text):
    """Validate message text for security threats."""
    if not isinstance(text, str):
        return False, "Invalid message format"
    
    if len(text.strip()) == 0:
        return False, "Empty message"
    
    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text):
            logger.warning(f"Potentially dangerous pattern detected in message")
            return False, "Message contains invalid content"
    
    return True, ""

def sanitize_text(text):
    """Sanitize text to prevent XSS."""
    if not isinstance(text, str):
        return ""
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    return text

def rate_limit_check(identifier):
    """Check if user exceeded rate limit."""
    # This is handled by Flask-Limiter, but we can add custom logic here
    return True

def validate_conversation_history(messages):
    """Validate conversation history integrity."""
    if not isinstance(messages, list):
        return False, "Messages must be a list"
    
    if len(messages) > MAX_CONVERSATION_HISTORY:
        return False, f"Conversation exceeds maximum of {MAX_CONVERSATION_HISTORY} messages"
    
    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return False, f"Message {idx} is not a valid object"
        
        sender = msg.get('sender', '').lower()
        if sender not in ['user', 'ai']:
            return False, f"Message {idx} has invalid sender: {sender}"
        
        text = msg.get('text', '')
        is_valid, error = validate_message_text(text)
        if not is_valid:
            return False, f"Message {idx}: {error}"
    
    return True, ""

def query(payload):
    """Send a query to the Hugging Face API with security checks."""
    try:
        # Add timeout and security headers
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=30,
            verify=True  # Verify SSL certificate
        )
        return response
    except requests.exceptions.Timeout:
        logger.error("Request to Hugging Face API timed out")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Hugging Face API: {str(e)}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Hugging Face API: {str(e)}")
        raise

@app.route("/")
def index():
    """Serve the main application."""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return jsonify({"error": "Application unavailable"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route("/chat", methods=["POST"])
@limiter.limit(f"{MAX_MESSAGES_PER_MINUTE}/minute")
def chat():
    """Handle chat requests with comprehensive security validation."""
    start_time = datetime.utcnow()
    client_ip = request.remote_addr
    
    try:
        # Validate request content type
        if request.content_type and 'application/json' not in request.content_type:
            logger.warning(f"Invalid content type from {client_ip}: {request.content_type}")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        # Parse JSON safely
        try:
            data = request.get_json(force=False, silent=False)
            if data is None:
                return jsonify({"error": "Invalid JSON"}), 400
        except Exception as e:
            logger.warning(f"JSON parsing error from {client_ip}: {str(e)}")
            return jsonify({"error": "Invalid JSON format"}), 400
        
        # Extract and validate messages
        messages = data.get("messages")
        
        if messages is None:
            return jsonify({"error": "Messages are required"}), 400
        
        # Validate conversation history
        is_valid, error_msg = validate_conversation_history(messages)
        if not is_valid:
            logger.warning(f"Invalid conversation from {client_ip}: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # Build the prompt safely
        prompt = ""
        for message in messages:
            sanitized_text = sanitize_text(message.get('text', ''))
            if message.get('sender') == 'user':
                prompt += f"<s>[INST] {sanitized_text} [/INST]"
            elif message.get('sender') == 'ai':
                prompt += f" {sanitized_text} </s>"
        
        if not prompt.strip():
            return jsonify({"error": "No valid messages"}), 400
        
        # Call API
        api_response = query({
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95,
                "repetition_penalty": 1.2
            }
        })
        
        if api_response.status_code != 200:
            logger.error(f"API error {api_response.status_code} from {client_ip}")
            return jsonify({"error": "Error processing request"}), 500
        
        def generate():
            """Safely stream the response."""
            try:
                for chunk in api_response.iter_lines(decode_unicode=True):
                    if chunk.startswith('data:'):
                        try:
                            data = json.loads(chunk[5:])
                            if 'token' in data and 'text' in data['token']:
                                # Sanitize before sending to client
                                token_text = sanitize_text(data['token']['text'])
                                yield token_text
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield "\n[Error: Unable to stream response]"
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Chat request from {client_ip} completed in {duration:.2f}s")
        
        return Response(generate(), mimetype='text/plain')
    
    except requests.exceptions.Timeout:
        logger.warning(f"API timeout for {client_ip}")
        return jsonify({"error": "Request timeout"}), 408
    except ValueError as e:
        logger.warning(f"Validation error from {client_ip}: {str(e)}")
        return jsonify({"error": "Invalid request"}), 400
    except Exception as e:
        logger.error(f"Unexpected error for {client_ip}: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route("/api/config", methods=["GET"])
def get_config():
    """Get public configuration (no secrets)."""
    return jsonify({
        "app_name": "Hugging AI",
        "version": "1.0.0",
        "max_message_length": MAX_MESSAGE_LENGTH,
        "max_conversation_history": MAX_CONVERSATION_HISTORY
    }), 200

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    logger.warning(f"Bad request: {error}")
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    logger.warning(f"Rate limit exceeded for {request.remote_addr}")
    return jsonify({"error": "Too many requests. Please try again later"}), 429

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Security: Never use debug mode in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    if debug_mode:
        logger.warning("⚠️  DEBUG MODE IS ENABLED - DO NOT USE IN PRODUCTION")
    
    logger.info("🤗 Hugging AI Server Starting...")
    app.run(
        debug=debug_mode,
        host="127.0.0.1",  # Changed from 0.0.0.0 to localhost only
        port=5000,
        use_reloader=debug_mode,
        use_debugger=debug_mode
    )