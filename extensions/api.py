"""
REST API endpoints for the Cisco Configuration Generator.

This blueprint exposes programmatic access to the configuration
generation logic so that external systems can integrate with the
application.  The main endpoint ``/generate`` accepts a JSON
payload representing the configuration options and returns CLI,
JSON and YAML outputs.

Device Management API:
- /devices/pull-config: Pull running configuration from a device
- /devices/push-config: Push configuration to a device
- /devices/test-connectivity: Test device reachability
"""

from flask import Blueprint, request, jsonify
from typing import Any, Dict
import traceback

from utils.config_export import render_cli_config, serialize_config
from device_manager import DeviceManager, DeviceConnectionError

api_bp = Blueprint('api', __name__)

# Initialize device manager
device_manager = DeviceManager()

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


# ============================================
# Device Management API Endpoints
# ============================================

@api_bp.route('/devices/test-connectivity', methods=['POST'])
def test_device_connectivity() -> Any:
    """
    Test connectivity to a network device

    POST /api/devices/test-connectivity
    Body: {
        "device_id": "device_123",
        "ip_address": "192.168.1.1",
        "protocol": "ssh",
        "port": 22
    }

    Returns: {
        "reachable": true,
        "message": "Port 22 is open on 192.168.1.1",
        "latency_ms": 0
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    ip_address = data.get('ip_address')
    protocol = data.get('protocol', 'ssh')
    port = data.get('port', 22)

    if not ip_address:
        return jsonify({'error': 'ip_address is required'}), 400

    try:
        result = device_manager.test_connectivity(ip_address, port, protocol)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'reachable': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/devices/pull-config', methods=['POST'])
def pull_device_config() -> Any:
    """
    Pull running configuration from a network device via SSH

    POST /api/devices/pull-config
    Body: {
        "device_id": "device_123",
        "hostname": "CORE-SW-01",
        "ip_address": "192.168.1.1",
        "username": "admin",
        "password": "password",  // NOTE: In production, use secure credential management
        "enable_password": "enable_pass",  // Optional
        "protocol": "ssh",
        "port": 22
    }

    Returns: {
        "success": true,
        "config": "! Full device configuration...",
        "ios_version": "15.2(4)E5",
        "model": "C3850",
        "hostname": "CORE-SW-01",
        "timestamp": "2025-01-01T12:00:00",
        "size": 25000
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}

    # Required parameters
    ip_address = data.get('ip_address')
    username = data.get('username')
    password = data.get('password')

    if not all([ip_address, username, password]):
        return jsonify({
            'error': 'ip_address, username, and password are required'
        }), 400

    # Optional parameters
    enable_password = data.get('enable_password')
    port = data.get('port', 22)

    try:
        result = device_manager.pull_config_ssh(
            ip_address=ip_address,
            username=username,
            password=password,
            enable_password=enable_password,
            port=port
        )
        return jsonify(result)

    except DeviceConnectionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/devices/push-config', methods=['POST'])
def push_device_config() -> Any:
    """
    Push configuration to a network device via SSH

    POST /api/devices/push-config
    Body: {
        "device_id": "device_123",
        "hostname": "CORE-SW-01",
        "ip_address": "192.168.1.1",
        "username": "admin",
        "password": "password",
        "enable_password": "enable_pass",  // Optional
        "protocol": "ssh",
        "port": 22,
        "config": "hostname CORE-SW-01\ninterface GigabitEthernet1/0/1\n...",
        "dry_run": false,  // Set to true to test without applying
        "backup_first": true,  // Backup current config before push
        "commit_confirm": 0  // Auto-rollback timeout in minutes (0 = disabled)
    }

    Returns: {
        "success": true,
        "message": "Configuration pushed successfully",
        "errors": [],  // List of any command errors
        "backup_config": "! Backup of previous config...",
        "timestamp": "2025-01-01T12:00:00"
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}

    # Required parameters
    ip_address = data.get('ip_address')
    username = data.get('username')
    password = data.get('password')
    config = data.get('config')

    if not all([ip_address, username, password, config]):
        return jsonify({
            'error': 'ip_address, username, password, and config are required'
        }), 400

    # Optional parameters
    enable_password = data.get('enable_password')
    port = data.get('port', 22)
    dry_run = data.get('dry_run', False)
    backup_first = data.get('backup_first', True)

    try:
        result = device_manager.push_config_ssh(
            ip_address=ip_address,
            username=username,
            password=password,
            config=config,
            enable_password=enable_password,
            port=port,
            dry_run=dry_run,
            backup_first=backup_first
        )
        return jsonify(result)

    except DeviceConnectionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/devices/compare-configs', methods=['POST'])
def compare_configs() -> Any:
    """
    Compare two configurations and generate a diff

    POST /api/devices/compare-configs
    Body: {
        "old_config": "! Old configuration...",
        "new_config": "! New configuration..."
    }

    Returns: {
        "added_lines": 15,
        "removed_lines": 8,
        "unchanged_lines": 120,
        "added": ["hostname NEW-NAME", "interface Vlan100", ...],
        "removed": ["hostname OLD-NAME", "interface Vlan99", ...],
        "total_changes": 23
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}

    old_config = data.get('old_config', '')
    new_config = data.get('new_config', '')

    try:
        result = device_manager.compare_configs(old_config, new_config)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': 'Failed to compare configurations',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500