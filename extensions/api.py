"""
REST API endpoints for the Cisco Configuration Generator.

This blueprint exposes programmatic access to the configuration
generation logic so that external systems can integrate with the
application.  The main endpoint ``/generate`` accepts a JSON
payload representing the configuration options and returns CLI,
JSON and YAML outputs.
"""

from flask import Blueprint, request, jsonify
from typing import Any, Dict

from utils.config_export import render_cli_config, serialize_config

api_bp = Blueprint('api', __name__)

@api_bp.route('/generate', methods=['POST'])
def api_generate() -> Any:
    """Generate configuration via API.

    Expects a JSON body with at minimum a ``platform`` key.  All other
    keys correspond to the fields accepted by the web form.  The
    response is a JSON object with ``cli``, ``json`` and ``yaml`` fields
    containing the respective outputs.
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400
    data: Dict[str, Any] = request.get_json() or {}
    platform = data.get('platform', 'ios')
    # Use the same helpers as the web form handler; simply pass the
    # incoming JSON through without modification.  The templates will
    # handle missing keys gracefully.
    cli_output = render_cli_config(platform, data)
    json_output, yaml_output = serialize_config(data)
    return jsonify({
        'cli': cli_output,
        'json': json_output,
        'yaml': yaml_output,
    })