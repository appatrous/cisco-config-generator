"""
Troubleshooting routes blueprint.

Handles displaying troubleshooting commands for protocols.
"""
from flask import Blueprint, render_template, request
from utils.troubleshoot import get_troubleshoot_commands


troubleshoot_bp = Blueprint('troubleshoot', __name__)


@troubleshoot_bp.route('/troubleshoot/<slug>')
def troubleshoot(slug: str) -> str:
    """
    Display troubleshooting commands for a given protocol slug.

    The ``device`` query parameter (if provided) is used for back navigation
    so the user can return to the protocol configuration page. If no commands
    are defined for the slug, the template will display an informative message.
    """
    device = request.args.get('device', 'router')
    commands = get_troubleshoot_commands(slug)

    return render_template(
        'protocol_troubleshoot.html',
        slug=slug,
        commands=commands,
        device=device
    )
