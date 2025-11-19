"""
Main UI routes blueprint.

Handles home page, form, and configuration generation.
"""
from flask import Blueprint, render_template, request
from typing import Dict, Any
import config as app_config
from utils.config_export import render_cli_config, serialize_config
from schemas.config_schemas import ConfigGenerationRequest
from pydantic import ValidationError


main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index() -> str:
    """Render the home page with device selection cards."""
    return render_template('home.html')


@main_bp.route('/form', methods=['GET'])
def form() -> str:
    """Render the legacy configuration form for advanced input."""
    return render_template('form.html', platforms=app_config.SUPPORTED_PLATFORMS)


@main_bp.route('/generate', methods=['POST'])
def generate() -> str:
    """Generate configuration from submitted form data and show results."""
    # Collect all form values
    form_data: Dict[str, Any] = request.form.to_dict(flat=False)

    # Determine selected platform. If missing, default to IOS
    platform_list = form_data.get('platform', ['ios'])
    platform = platform_list[0] if isinstance(platform_list, list) else platform_list

    # Build a structured data model
    config_data: Dict[str, Any] = {
        'platform': platform,
        'static_routes': [],
        'ospf': None,
        'vlans': [],
        'ntp_servers': [],
        'aaa': None,
    }

    # Parse static routes if provided
    networks = form_data.get('route_network', [])
    masks = form_data.get('route_mask', [])
    next_hops = form_data.get('route_next_hop', [])

    if networks and masks and next_hops:
        for net, mask, hop in zip(networks, masks, next_hops):
            if net.strip() and mask.strip() and hop.strip():
                config_data['static_routes'].append({
                    'network': net.strip(),
                    'mask': mask.strip(),
                    'next_hop': hop.strip()
                })

    # Parse OSPF configuration
    ospf_process = form_data.get('ospf_process', [''])[0]
    ospf_router_id = form_data.get('ospf_router_id', [''])[0]
    ospf_networks = form_data.get('ospf_network', [])
    ospf_wildcards = form_data.get('ospf_wildcard', [])
    ospf_areas = form_data.get('ospf_area', [])

    if ospf_process.strip():
        config_data['ospf'] = {
            'process_id': int(ospf_process),
            'router_id': ospf_router_id if ospf_router_id.strip() else None,
            'networks': []
        }

        if ospf_networks and ospf_wildcards and ospf_areas:
            for net, wc, area in zip(ospf_networks, ospf_wildcards, ospf_areas):
                if net.strip() and wc.strip() and area.strip():
                    config_data['ospf']['networks'].append({
                        'network': net.strip(),
                        'wildcard': wc.strip(),
                        'area': int(area)
                    })

    # Parse VLANs
    vlan_ids = form_data.get('vlan_id', [])
    vlan_names = form_data.get('vlan_name', [])

    if vlan_ids and vlan_names:
        for vid, vname in zip(vlan_ids, vlan_names):
            if vid.strip() and vname.strip():
                config_data['vlans'].append({
                    'vlan_id': int(vid),
                    'name': vname.strip()
                })

    # Parse NTP servers
    ntp_list = form_data.get('ntp_server', [])
    if ntp_list:
        config_data['ntp_servers'] = [
            srv.strip() for srv in ntp_list if srv.strip()
        ]

    # Parse AAA configuration
    aaa_enable = form_data.get('aaa_enable', [''])[0]
    if aaa_enable == 'on':
        tacacs_servers = form_data.get('tacacs_server', [])
        config_data['aaa'] = {
            'new_model': True,
            'tacacs_servers': [s.strip() for s in tacacs_servers if s.strip()]
        }

    # Generate CLI configuration using utils
    cli_output = render_cli_config(platform, config_data)
    json_output, yaml_output = serialize_config(config_data)

    # Render result page with outputs
    return render_template(
        'result.html',
        cli_config=cli_output,
        json_config=json_output,
        yaml_config=yaml_output,
        platform=platform,
    )
