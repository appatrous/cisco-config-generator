"""
Global configuration for the Cisco Configuration Generator application.

This file centralises settings such as secret keys, supported
platforms and any other runtime parameters. Keeping configuration
separate from code allows easy adjustment without modifying the
application logic.
"""

# Secret key for session management and CSRF protection.  Replace this
# with a strong random value in production deployments.
SECRET_KEY = 'change-me-to-a-random-secret-key'

# List of supported target platforms.  Update this list to include
# additional device families as needed.
SUPPORTED_PLATFORMS = ['ios', 'nxos', 'asa']

# Default directories for configuration templates
CONFIG_TEMPLATE_DIR = 'config_templates'

## Additional configuration settings can be defined here.  For example:
#
# DEBUG = True
# PERMANENT_SESSION_LIFETIME = 3600
# API_RATE_LIMIT = '100/hour'