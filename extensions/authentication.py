"""
Placeholder for authentication mechanisms.

In a single‑user offline tool there is typically no need for
authentication; however, for completeness or future multi‑user
expansion, this module could implement session management, user
login/logout and CSRF protection.  Not implemented.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Placeholder login handler
    return 'Authentication not implemented.'