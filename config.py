"""
Global configuration for the Cisco Configuration Generator application.

This file centralises settings such as secret keys, supported
platforms and any other runtime parameters. Keeping configuration
separate from code allows easy adjustment without modifying the
application logic.

IMPORTANT: All sensitive configuration values are now loaded from
environment variables. Never commit secrets to version control!
"""
import os
import sys

# Secret key for session management and CSRF protection.
# MUST be set via environment variable in production!
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    if os.getenv('FLASK_ENV') == 'production':
        print("ERROR: SECRET_KEY environment variable is required in production!")
        sys.exit(1)
    else:
        # Development fallback - generates a random key per session
        import secrets
        SECRET_KEY = secrets.token_urlsafe(32)
        print(f"WARNING: Using auto-generated SECRET_KEY for development. Set SECRET_KEY env var for persistence.")

# Debug mode
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# List of supported target platforms.  Update this list to include
# additional device families as needed.
SUPPORTED_PLATFORMS = ['ios', 'nxos', 'asa', 'eos', 'junos']

# Default directories for configuration templates
CONFIG_TEMPLATE_DIR = os.getenv('CONFIG_TEMPLATE_DIR', 'config_templates')

# Session configuration
PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', '3600'))  # 1 hour default

# API rate limiting (if implemented)
API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/hour')

# File upload settings
MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE', str(16 * 1024 * 1024)))  # 16MB default
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')