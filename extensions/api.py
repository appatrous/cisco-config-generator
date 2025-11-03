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
from utils.payload_validation import validate_api_payload

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
        return jsonify({'errors': ['Expected JSON payload']}), 400

    data: Dict[str, Any] = request.get_json() or {}
    sanitised, errors = validate_api_payload(data)
    if errors:
        return jsonify({'errors': errors}), 400

    cli_output = render_cli_config(sanitised['platform'], sanitised)
    json_output, yaml_output = serialize_config(sanitised)
    return jsonify({
        'cli': cli_output,
        'json': json_output,
        'yaml': yaml_output,
    })
