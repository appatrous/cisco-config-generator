"""
Centralized logging configuration for the application.

Provides structured logging with color-coded console output and
file rotation.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import colorlog


def setup_logger(app=None, log_level='INFO', log_file='logs/app.log'):
    """
    Configure application logging with console and file handlers.

    Args:
        app: Flask application instance (optional)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger('cisco_config_generator')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Console handler with color
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s%(reset)s - '
        '%(cyan)s%(name)s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # If Flask app provided, integrate with Flask's logger
    if app:
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)

    logger.info('=' * 80)
    logger.info(f'Logging initialized - Level: {log_level}')
    logger.info(f'Log file: {log_file}')
    logger.info('=' * 80)

    return logger


def log_request(logger, request, user=None):
    """
    Log HTTP request details.

    Args:
        logger: Logger instance
        request: Flask request object
        user: Optional user identifier
    """
    user_info = f" - User: {user}" if user else ""
    logger.info(
        f"{request.method} {request.path} - IP: {request.remote_addr}"
        f"{user_info} - UA: {request.user_agent.string[:50]}"
    )


def log_error(logger, error, request=None, context=None):
    """
    Log error with detailed context.

    Args:
        logger: Logger instance
        error: Exception or error message
        request: Flask request object (optional)
        context: Additional context dictionary (optional)
    """
    error_msg = f"ERROR: {str(error)}"

    if request:
        error_msg += f" | Path: {request.path} | Method: {request.method}"
        error_msg += f" | IP: {request.remote_addr}"

    if context:
        error_msg += f" | Context: {context}"

    logger.error(error_msg, exc_info=True)


def log_config_generation(logger, platform, protocol, user=None, success=True):
    """
    Log configuration generation events.

    Args:
        logger: Logger instance
        platform: Device platform (ios, nxos, asa)
        protocol: Protocol being configured
        user: User identifier (optional)
        success: Whether generation succeeded
    """
    status = "SUCCESS" if success else "FAILED"
    user_info = f" by {user}" if user else ""
    logger.info(f"Config generation {status}: {platform}/{protocol}{user_info}")


def log_security_event(logger, event_type, details, user=None, severity='WARNING'):
    """
    Log security-related events.

    Args:
        logger: Logger instance
        event_type: Type of security event
        details: Event details
        user: User identifier (optional)
        severity: Log level (INFO, WARNING, ERROR, CRITICAL)
    """
    user_info = f" - User: {user}" if user else ""
    message = f"SECURITY [{event_type}]: {details}{user_info}"

    log_func = getattr(logger, severity.lower(), logger.warning)
    log_func(message)


class RequestLogger:
    """Context manager for logging request processing."""

    def __init__(self, logger, request, operation):
        self.logger = logger
        self.request = request
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation} - {self.request.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            self.logger.error(
                f"Failed {self.operation} after {duration:.2f}s - {exc_val}",
                exc_info=True
            )
        else:
            self.logger.info(f"Completed {self.operation} in {duration:.2f}s")

        return False  # Don't suppress exceptions
