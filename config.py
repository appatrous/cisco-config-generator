"""
Global configuration for the Cisco Configuration Generator application.

This file centralises settings such as secret keys, supported
platforms and any other runtime parameters. Keeping configuration
separate from code allows easy adjustment without modifying the
application logic.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600)))

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cisco_config.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supported platforms
    SUPPORTED_PLATFORMS = ['ios', 'nxos', 'asa', 'ios-xe', 'ios-xr']

    # Directories
    CONFIG_TEMPLATE_DIR = 'config_templates'
    UPLOAD_FOLDER = 'uploads'
    DATA_FOLDER = 'data'
    LOG_FOLDER = 'logs'

    # API Configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    API_KEY_REQUIRED = os.environ.get('API_KEY_REQUIRED', 'False').lower() == 'true'

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

    # Pagination
    ITEMS_PER_PAGE = 20

    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'cfg', 'conf', 'yaml', 'yml', 'json'}


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # In production, SECRET_KEY must be set via environment variable
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production!")


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}