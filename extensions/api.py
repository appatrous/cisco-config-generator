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
from config_comparison import ConfigComparator, ChangeTracker
from config_validator import ConfigValidator, ComplianceChecker

api_bp = Blueprint('api', __name__)

# Initialize managers
device_manager = DeviceManager()
config_comparator = ConfigComparator()
change_tracker = ChangeTracker()
config_validator = ConfigValidator()
compliance_checker = ComplianceChecker()

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


@api_bp.route('/configs/compare-detailed', methods=['POST'])
def compare_configs_detailed() -> Any:
    """
    Detailed configuration comparison with section awareness

    POST /api/configs/compare-detailed
    Body: {
        "old_config": "! Old configuration...",
        "new_config": "! New configuration..."
    }

    Returns: {
        "added_lines": 15,
        "removed_lines": 8,
        "modified_sections": ["interface GigabitEthernet0/1", "router ospf 1"],
        "added": [...],
        "removed": [...],
        "summary": "15 lines added, 8 lines removed, 2 sections modified",
        "risk_level": "MEDIUM",
        "affected_interfaces": ["GigabitEthernet0/1", "GigabitEthernet0/2"],
        "affected_vlans": [10, 20, 30],
        "routing_changes": {
            "ospf": true,
            "bgp": false,
            "static_routes": true
        }
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    old_config = data.get('old_config', '')
    new_config = data.get('new_config', '')

    try:
        result = config_comparator.compare_configs_detailed(old_config, new_config)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': 'Failed to compare configurations',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/configs/merge', methods=['POST'])
def merge_configs() -> Any:
    """
    Merge two configurations with intelligent conflict resolution

    POST /api/configs/merge
    Body: {
        "base_config": "! Base configuration...",
        "overlay_config": "! Overlay configuration...",
        "strategy": "overlay"  // Options: overlay, additive, replace
    }

    Returns: {
        "success": true,
        "merged_config": "! Merged configuration...",
        "conflicts": [
            {
                "section": "interface GigabitEthernet0/1",
                "base": "...",
                "overlay": "...",
                "resolution": "Used overlay version"
            }
        ],
        "strategy": "overlay",
        "sections_merged": 15
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    base_config = data.get('base_config', '')
    overlay_config = data.get('overlay_config', '')
    strategy = data.get('strategy', 'overlay')

    if strategy not in ['overlay', 'additive', 'replace']:
        return jsonify({
            'error': 'Invalid strategy. Must be: overlay, additive, or replace'
        }), 400

    try:
        result = config_comparator.merge_configs(base_config, overlay_config, strategy)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': 'Failed to merge configurations',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/configs/rollback', methods=['POST'])
def generate_rollback_config() -> Any:
    """
    Generate rollback configuration

    POST /api/configs/rollback
    Body: {
        "current_config": "! Current running configuration...",
        "target_config": "! Target (previous) configuration..."
    }

    Returns: {
        "rollback_commands": [
            "no interface GigabitEthernet0/3",
            "interface GigabitEthernet0/1",
            "ip address 192.168.1.1 255.255.255.0",
            ...
        ],
        "commands_count": 25,
        "removals": 10,
        "additions": 15,
        "estimated_time_seconds": 22
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    current_config = data.get('current_config', '')
    target_config = data.get('target_config', '')

    if not all([current_config, target_config]):
        return jsonify({
            'error': 'Both current_config and target_config are required'
        }), 400

    try:
        result = config_comparator.generate_rollback_config(current_config, target_config)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate rollback configuration',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/changes/record', methods=['POST'])
def record_config_change() -> Any:
    """
    Record a configuration change in the audit trail

    POST /api/changes/record
    Body: {
        "device_id": "device_123",
        "change_type": "push",  // Options: manual, pull, push, rollback
        "old_config": "! Previous configuration...",
        "new_config": "! New configuration...",
        "user": "admin",
        "notes": "Updated VLAN configuration"
    }

    Returns: {
        "id": "change_1640000000_device_123",
        "device_id": "device_123",
        "timestamp": "2025-01-01T12:00:00",
        "user": "admin",
        "change_type": "push",
        "notes": "Updated VLAN configuration",
        "comparison": {
            "added_lines": 5,
            "removed_lines": 2,
            "modified_sections": [...],
            "risk_level": "LOW",
            "summary": "5 lines added, 2 lines removed"
        },
        "rollback_available": true
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}

    device_id = data.get('device_id')
    change_type = data.get('change_type', 'manual')
    old_config = data.get('old_config', '')
    new_config = data.get('new_config', '')
    user = data.get('user', 'admin')
    notes = data.get('notes', '')

    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400

    try:
        change_record = change_tracker.record_change(
            device_id=device_id,
            change_type=change_type,
            old_config=old_config,
            new_config=new_config,
            user=user,
            notes=notes
        )
        return jsonify(change_record)
    except Exception as e:
        return jsonify({
            'error': 'Failed to record change',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/changes/history/<device_id>', methods=['GET'])
def get_change_history(device_id: str) -> Any:
    """
    Get configuration change history for a device

    GET /api/changes/history/device_123?limit=50

    Returns: [
        {
            "id": "change_1640000000_device_123",
            "timestamp": "2025-01-01T12:00:00",
            "user": "admin",
            "change_type": "push",
            "notes": "Updated VLAN configuration",
            "comparison": {...}
        },
        ...
    ]
    """
    limit = request.args.get('limit', 50, type=int)

    try:
        history = change_tracker.get_device_history(device_id, limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve change history',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============================================
# Configuration Validation API Endpoints
# ============================================

@api_bp.route('/validate/config', methods=['POST'])
def validate_configuration() -> Any:
    """
    Validate configuration for conflicts, best practices, and security

    POST /api/validate/config
    Body: {
        "config": "! Configuration to validate...",
        "vendor": "cisco"  // Optional
    }

    Returns: {
        "valid": true,
        "score": 85,
        "risk_level": "LOW",
        "errors": [],
        "warnings": [],
        "conflicts": [...],
        "best_practices": [...],
        "security_issues": [...]
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    config = data.get('config', '')
    vendor = data.get('vendor', 'cisco')

    if not config:
        return jsonify({'error': 'config is required'}), 400

    try:
        results = config_validator.validate_config(config, vendor)
        return jsonify(results)
    except Exception as e:
        return jsonify({
            'error': 'Validation failed',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500


@api_bp.route('/validate/compliance', methods=['POST'])
def check_compliance() -> Any:
    """
    Check configuration compliance against standards

    POST /api/validate/compliance
    Body: {
        "config": "! Configuration to check...",
        "standards": ["pci_dss", "hipaa", "general"]  // Optional
    }

    Returns: {
        "compliant": false,
        "compliance_score": 75,
        "standards_checked": ["pci_dss", "general"],
        "violations": [
            {
                "standard": "PCI-DSS",
                "requirement": "2.3",
                "severity": "HIGH",
                "message": "Telnet detected - PCI-DSS requires encrypted protocols"
            }
        ]
    }
    """
    if not request.is_json:
        return jsonify({'error': 'Expected JSON payload'}), 400

    data = request.get_json() or {}
    config = data.get('config', '')
    standards = data.get('standards', ['general'])

    if not config:
        return jsonify({'error': 'config is required'}), 400

    try:
        results = compliance_checker.check_compliance(config, standards)
        return jsonify(results)
    except Exception as e:
        return jsonify({
            'error': 'Compliance check failed',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500