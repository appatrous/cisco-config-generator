"""
Device-specific routes blueprint.

Handles router, switch, and firewall pages.
"""
from flask import Blueprint, render_template


devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/router')
def router_page() -> str:
    """Render the router feature selection page."""
    return render_template('router.html')


@devices_bp.route('/switch')
def switch_page() -> str:
    """Render the switch feature selection page."""
    return render_template('switch.html')


@devices_bp.route('/firewall')
def firewall_page() -> str:
    """Render the firewall feature selection page."""
    return render_template('firewall.html')
