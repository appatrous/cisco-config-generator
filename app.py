"""
Main Flask application entry point for the Cisco Configuration Generator.

This module sets up the Flask app, loads configuration from
``config.py`` and wires routes for the web UI and API.  The UI
consists of a form where users can input configuration parameters for
IOS, NX‑OS and ASA platforms.  Upon submission the app generates
configuration in CLI, JSON and YAML formats using Jinja2 templates.
"""

from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, send_file
from typing import Dict, Any

# Troubleshooting command dictionary mapping protocol slugs to a list of common
# show/debug commands that help diagnose issues with each feature.  These
# commands are displayed to the user when they click the "Troubleshoot"
# button on a protocol page.  Unknown slugs will result in a default
# message.
troubleshoot_commands: Dict[str, list[str]] = {
    # Routing protocols and static routes
    'static-routing': [
        'show ip route static',
        'show ipv6 route static'
    ],
    'ospf': [
        'show ip ospf',
        'show ip ospf neighbor',
        'show ip ospf database'
    ],
    'eigrp': [
        'show ip eigrp neighbors',
        'show ip eigrp topology',
        'show ip eigrp interfaces'
    ],
    'rip': [
        'show ip rip database',
        'show ip rip interface',
        'debug ip rip'
    ],
    'bgp4-plus': [
        'show ip bgp summary',
        'show ip bgp',
        'show ip bgp neighbors'
    ],
    # IPv6 variants reuse same commands as IPv4 where appropriate
    'ospfv3': [
        'show ipv6 ospf',
        'show ipv6 ospf neighbor',
        'show ipv6 ospf database'
    ],
    'eigrpv6': [
        'show ipv6 eigrp neighbors',
        'show ipv6 eigrp topology'
    ],

    # High availability and redundancy protocols
    'vrrp': [
        'show vrrp',
        'debug vrrp'
    ],
    'hsrp': [
        'show standby',
        'debug standby'
    ],
    'glbp': [
        'show glbp',
        'debug glbp'
    ],

    # Address translation
    'static-nat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],
    'dynamic-nat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],
    'pat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],

    # VLAN and Layer 2
    'vlan': [
        'show vlan brief',
        'show interfaces status'
    ],
    'vtp': [
        'show vtp status',
        'show vtp counters'
    ],
    'stp': [
        'show spanning-tree',
        'show spanning-tree vlan'
    ],
    'pvst-plus': [
        'show spanning-tree',
        'show spanning-tree vlan'
    ],
    'etherchannel': [
        'show etherchannel summary',
        'show interfaces port-channel'
    ],
    'lacp': [
        'show etherchannel summary',
        'show lacp neighbor'
    ],
    'private-vlan': [
        'show vlan private-vlan',
        'show interfaces switchport'
    ],
    'voice-vlan': [
        'show interfaces status',
        'show run interface <port>'
    ],
    'stackwise': [
        'show switch',
        'show switch stack-ports'
    ],

    # Discovery protocols and mirroring
    'cdp': [
        'show cdp neighbors',
        'show cdp neighbors detail'
    ],
    'lldp': [
        'show lldp neighbors',
        'show lldp neighbors detail'
    ],
    'span': [
        'show monitor session',
        'show run | section monitor session'
    ],
    'rspan': [
        'show monitor session',
        'show vlan remote-span'
    ],
    'erspan': [
        'show monitor session',
        'show run interface tunnel'
    ],

    # Access control and security
    'acl': [
        'show access-lists',
        'show ip access-lists'
    ],
    'object-groups': [
        'show run object-group'
    ],
    'asa-failover-clustering': [
        'show failover',
        'show failover history'
    ],
    'unicast-rpf': [
        'show ip interface',
        'show cef interface',
        'show ip verify source'
    ],

    # IPv6 and multicast
    'igmp': [
        'show ip igmp groups',
        'show ip igmp interface'
    ],
    'pim': [
        'show ip pim neighbors',
        'show ip pim interface',
        'show ip pim rp-map'
    ],
    'multicast-routing': [
        'show ip mroute',
        'show ip pim rp-mappings'
    ],

    # Services and performance
    'netflow': [
        'show ip cache flow',
        'show ip flow export'
    ],
    'qos': [
        'show policy-map interface',
        'show policy-map'
    ],
    'ntp-ptp': [
        'show ntp status',
        'show ntp associations'
    ],
    'aaa': [
        'show aaa servers',
        'debug aaa authentication'
    ],
    'snmp': [
        'show snmp',
        'show snmp community'
    ],
    'syslog': [
        'show logging',
        'show logging history'
    ],
    'dhcp-server-relay': [
        'show ip dhcp pool',
        'show ip dhcp binding',
        'show ip dhcp server statistics'
    ],
    'dhcp-snooping': [
        'show ip dhcp snooping',
        'show ip dhcp snooping binding'
    ],
    'dynamic-arp-inspection': [
        'show ip arp inspection',
        'show ip arp inspection statistics'
    ],
    'ip-source-guard': [
        'show ip verify source'
    ],
    'igmp-snooping': [
        'show ip igmp snooping',
        'show ip igmp snooping groups'
    ],

    # VPN and tunnels
    'gre': [
        'show interface tunnel',
        'show ip route'
    ],
    'ipsec': [
        'show crypto isakmp sa',
        'show crypto ipsec sa',
        'debug crypto isakmp'
    ],
    'ipsec-vpn': [
        'show crypto isakmp sa',
        'show crypto ipsec sa',
        'debug crypto isakmp'
    ],

    # Firewall and security features
    'ids-ips': [
        'show ips',
        'show ips statistics'
    ],
    'ssl-tls-inspection': [
        'show policy-map type inspect ssl',
        'show ssl cert'
    ],
    'gnoc': [
        'show run | section gnoc'
    ],
    'threat-detection': [
        'show threat-detection',
        'show threat-detection statistics'
    ],
    'embedded-event-manager': [
        'show event manager policy registered',
        'show event manager history events'
    ],
    'ssl-vpn': [
        'show vpn-sessiondb anyconnect',
        'show webvpn session'
    ],
    'anyconnect': [
        'show vpn-sessiondb anyconnect',
        'show webvpn session'
    ],
    'zone-based-firewall': [
        'show policy-map type inspect zone-pair',
        'show zone-pair security'
    ]
}

# Import application configuration
import config as app_config

# Utilities for generating and exporting configs
from utils.config_export import render_cli_config, serialize_config

# Import API blueprint (defined in extensions.api)
try:
    from extensions.api import api_bp
except Exception:
    api_bp = None  # API may not be implemented yet


def create_app() -> Flask:
    """Factory to create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(app_config)
    app.secret_key = app_config.SECRET_KEY

    # Register API blueprint if available
    if api_bp:
        app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/', methods=['GET'])
    def index() -> str:
        """Render the home page with device selection cards."""
        # The home page provides navigation to device‑specific feature pages.
        return render_template('home.html')

    @app.route('/form', methods=['GET'])
    def form() -> str:
        """Render the legacy configuration form for advanced input."""
        # Pass supported platforms to the form so the user can choose device type.
        return render_template('form.html', platforms=app_config.SUPPORTED_PLATFORMS)

    @app.route('/generate', methods=['POST'])
    def generate() -> str:
        """Generate configuration from submitted form data and show results."""
        # Collect all form values.  ``request.form`` collects multi‑value entries
        form_data: Dict[str, Any] = request.form.to_dict(flat=False)

        # Determine selected platform.  If missing, default to IOS.
        platform_list = form_data.get('platform', ['ios'])
        platform = platform_list[0] if isinstance(platform_list, list) else platform_list

        # Build a structured data model.  This simple example collects a few
        # fields; extend this logic when adding more features.
        config_data: Dict[str, Any] = {
            'platform': platform,
            'static_routes': [],
            'ospf': None,
            'vlans': [],
            'ntp_servers': [],
            'aaa': None,
        }

        # Helper to normalise repeated fields into lists
        def get_list(key: str) -> list:
            value = form_data.get(key)
            if value is None:
                return []
            return value if isinstance(value, list) else [value]

        # Static routes
        dests = get_list('static_dest_network')
        next_hops = get_list('static_next_hop')
        distances = get_list('static_distance')
        for dest, nh, dist in zip(dests, next_hops, distances):
            if dest and nh:
                config_data['static_routes'].append({
                    'destination': dest,
                    'next_hop': nh,
                    'distance': dist or None,
                })

        # OSPF
        if 'ospf_enable' in form_data:
            ospf_version = get_list('ospf_version')[0] if get_list('ospf_version') else 'v2'
            process_id = get_list('ospf_process_id')[0] if get_list('ospf_process_id') else None
            router_id = get_list('ospf_router_id')[0] if get_list('ospf_router_id') else None
            networks = []
            ospf_nets = get_list('ospf_network')
            ospf_areas = get_list('ospf_area')
            for net, area in zip(ospf_nets, ospf_areas):
                if net:
                    networks.append({'network': net, 'area': area or '0'})
            config_data['ospf'] = {
                'version': ospf_version,
                'process_id': process_id,
                'router_id': router_id,
                'networks': networks,
            }

        # VLANs
        vlan_ids = get_list('vlan_id')
        vlan_names = get_list('vlan_name')
        for vid, vname in zip(vlan_ids, vlan_names):
            if vid:
                config_data['vlans'].append({'id': vid, 'name': vname or None})

        # NTP servers
        for srv in get_list('ntp_server'):
            if srv:
                config_data['ntp_servers'].append(srv)

        # AAA configuration
        if 'aaa_enable' in form_data:
            aaa = {
                'use_tacacs': 'aaa_use_tacacs' in form_data,
                'tacacs_servers': [srv for srv in get_list('tacacs_server') if srv],
                'use_radius': 'aaa_use_radius' in form_data,
                'radius_servers': [srv for srv in get_list('radius_server') if srv],
                'local_users': [],
            }
            user_names = get_list('local_user_name')
            user_pwds = get_list('local_user_password')
            user_privs = get_list('local_user_priv')
            for uname, upwd, upriv in zip(user_names, user_pwds, user_privs):
                if uname and upwd:
                    aaa['local_users'].append({
                        'username': uname,
                        'password': upwd,
                        'privilege': upriv or '15',
                    })
            config_data['aaa'] = aaa

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

    @app.route('/router')
    def router_page() -> str:
        """Render the router feature selection page."""
        return render_template('router.html')

    @app.route('/switch')
    def switch_page() -> str:
        """Render the switch feature selection page."""
        return render_template('switch.html')

    @app.route('/firewall')
    def firewall_page() -> str:
        """Render the firewall feature selection page."""
        return render_template('firewall.html')

    @app.route('/protocol/<slug>', methods=['GET', 'POST'])
    def protocol_page(slug: str) -> str:
        """Render or process a dedicated configuration page for a selected protocol.

        When a user clicks on a protocol card, they are redirected here.  On
        GET requests, a form tailored to the given protocol is rendered.  On
        POST requests, the submitted data is parsed and a summary of the
        configuration is appended to a persistent file in ``data/generated_config.txt``.
        """
        # Mapping of protocol slugs to template filenames
        template_map = {
            'static-routing': 'protocol_static_routing.html',
            'ospf': 'protocol_ospf.html',
            'static-nat': 'protocol_static_nat.html',
            'dynamic-nat': 'protocol_dynamic_nat.html',
            'pat': 'protocol_pat.html',
            'vlan': 'protocol_vlan.html',
            # Previously added protocols
            'eigrp': 'protocol_eigrp.html',
            'vrrp': 'protocol_vrrp.html',
            'hsrp': 'protocol_hsrp.html',
            'glbp': 'protocol_glbp.html',
            'ntp-ptp': 'protocol_ntp.html',
            # Newly added protocols
            'rip': 'protocol_rip.html',
            'vrf': 'protocol_vrf.html',
            'mpls': 'protocol_vrf.html',
            'gre': 'protocol_gre.html',
            'ipsec': 'protocol_ipsec.html',
            'ipsec-vpn': 'protocol_ipsec.html',
            'dhcp-server-relay': 'protocol_dhcp.html',
            'vtp': 'protocol_vtp.html',
            'stp': 'protocol_stp.html',
            'pvst-plus': 'protocol_stp.html',
            'etherchannel': 'protocol_etherchannel.html',
            'lacp': 'protocol_etherchannel.html',
            'cdp': 'protocol_discovery.html',
            'lldp': 'protocol_discovery.html',
            'span': 'protocol_span.html',
            'rspan': 'protocol_span.html',
            'erspan': 'protocol_span.html',
            'acl': 'protocol_acl.html',
            'object-groups': 'protocol_object_groups.html',
            'asa-failover-clustering': 'protocol_asa_failover.html',
            'unicast-rpf': 'protocol_unicast_rpf.html',
            'bgp4-plus': 'protocol_bgp.html',
            'ospfv3': 'protocol_ospf.html',
            'eigrpv6': 'protocol_eigrp.html',
            'aaa': 'protocol_aaa.html',
            'snmp': 'protocol_snmp.html',
            'syslog': 'protocol_syslog.html',
            # Additional protocols
            'igmp': 'protocol_igmp.html',
            'pim': 'protocol_pim.html',
            'multicast-routing': 'protocol_multicast_routing.html',
            'netflow': 'protocol_netflow.html',
            'qos': 'protocol_qos.html',
            'private-vlan': 'protocol_private_vlan.html',
            'voice-vlan': 'protocol_voice_vlan.html',
            'stackwise': 'protocol_stackwise.html',
            'ip-source-guard': 'protocol_ip_source_guard.html',
            'dynamic-arp-inspection': 'protocol_dynamic_arp_inspection.html',
            'dhcp-snooping': 'protocol_dhcp_snooping.html',
            'igmp-snooping': 'protocol_igmp_snooping.html',
            'zone-based-firewall': 'protocol_zone_based_firewall.html',
            'ssl-vpn': 'protocol_ssl_vpn.html',
            'anyconnect': 'protocol_anyconnect.html',
            'ids-ips': 'protocol_ids_ips.html',
            'ssl-tls-inspection': 'protocol_ssl_tls_inspection.html',
            'gnoc': 'protocol_gnoc.html',
            'threat-detection': 'protocol_threat_detection.html',
            'embedded-event-manager': 'protocol_embedded_event_manager.html',
            # Default fallback mapping can be added for unhandled protocols
        }
        # Determine device context (router, switch, firewall) from query or form
        device = request.args.get('device') or request.form.get('device') or None
        # On POST, process form submission
        if request.method == 'POST':
            # Ensure data directory exists
            import os
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, 'generated_config.txt')

            # Collect a descriptive entry based on protocol slug
            entry = f"{slug}: "
            # Flatten form data (list to single values if multiple)
            form_data: Dict[str, Any] = request.form.to_dict(flat=False)

            def get_single(name: str) -> str | None:
                value = form_data.get(name)
                if not value:
                    return None
                return value[0] if isinstance(value, list) else value

            if slug == 'static-routing':
                # Generate CLI for static routes
                dests = form_data.get('static_dest_network', [])
                nhs = form_data.get('static_next_hop', [])
                dists = form_data.get('static_distance', [])
                cli_lines = []
                cli_lines.append('! Static routing')
                for d, nh, dist in zip(dests, nhs, dists):
                    if d and nh:
                        line = f'ip route {d} {nh}'
                        if dist:
                            line += f' {dist}'
                        cli_lines.append(line)
                if len(cli_lines) <= 1:
                    cli_lines.append('! no static routes provided')
                entry = "\n".join(cli_lines)
            elif slug == 'ospf':
                enabled = 'ospf_enable' in form_data
                # Generate CLI for OSPF configuration
                if not enabled:
                    entry = '! OSPF disabled'
                else:
                    version = get_single('ospf_version') or 'v2'
                    pid = get_single('ospf_process_id') or '1'
                    rid = get_single('ospf_router_id') or ''
                    nets = form_data.get('ospf_network', [])
                    areas = form_data.get('ospf_area', [])
                    cli_lines = []
                    cli_lines.append('! OSPF configuration')
                    if version == 'v3':
                        cli_lines.append(f'ipv6 router ospf {pid}')
                    else:
                        cli_lines.append(f'router ospf {pid}')
                    if rid:
                        cli_lines.append(f' router-id {rid}')
                    for n, a in zip(nets, areas):
                        if n:
                            cli_lines.append(f' network {n} area {a}')
                    cli_lines.append(' exit')
                    entry = "\n".join(cli_lines)
            elif slug == 'static-nat':
                local = get_single('inside_local_ip') or ''
                global_ip = get_single('inside_global_ip') or ''
                cli_lines = []
                cli_lines.append('! Static NAT')
                if local and global_ip:
                    cli_lines.append(f'ip nat inside source static {local} {global_ip}')
                else:
                    cli_lines.append('! no static NAT entry provided')
                entry = "\n".join(cli_lines)
            elif slug == 'dynamic-nat':
                inside_net = get_single('inside_network') or ''
                start_ip = get_single('pool_start_ip') or ''
                end_ip = get_single('pool_end_ip') or ''
                mask = get_single('subnet_mask') or ''
                cli_lines = []
                cli_lines.append('! Dynamic NAT')
                if inside_net and start_ip and end_ip and mask:
                    cli_lines.append(f'ip nat pool DYN_POOL {start_ip} {end_ip} netmask {mask}')
                    # Create an access-list matching inside network.  Placeholder ACL name NAT_ACL
                    cli_lines.append(f'access-list NAT_ACL permit ip {inside_net} any')
                    cli_lines.append('ip nat inside source list NAT_ACL pool DYN_POOL')
                else:
                    cli_lines.append('! incomplete dynamic NAT parameters provided')
                entry = "\n".join(cli_lines)
            elif slug == 'pat':
                local_ip = get_single('inside_local_ip') or ''
                local_port = get_single('inside_local_port') or ''
                global_ip = get_single('inside_global_ip') or ''
                global_port = get_single('inside_global_port') or ''
                cli_lines = []
                cli_lines.append('! Port Address Translation')
                if local_ip and local_port and global_ip and global_port:
                    # Assume TCP for PAT
                    cli_lines.append(f'ip nat inside source static tcp {local_ip} {local_port} {global_ip} {global_port}')
                else:
                    cli_lines.append('! incomplete PAT parameters provided')
                entry = "\n".join(cli_lines)
            elif slug == 'vlan':
                # Generate CLI for VLAN creation.  Each VLAN ID/name becomes its own stanza.
                vlan_ids = form_data.get('vlan_id', [])
                vlan_names = form_data.get('vlan_name', [])
                # Build CLI lines instead of a summary string
                cli_lines = []
                cli_lines.append('! VLAN configuration')
                for vid, name in zip(vlan_ids, vlan_names):
                    if vid:
                        cli_lines.append(f'vlan {vid}')
                        if name:
                            cli_lines.append(f' name {name}')
                        cli_lines.append(' exit')
                # If no VLANs provided, emit a comment
                if not any(vlan_ids):
                    cli_lines.append('! no VLANs provided')
                entry = "\n".join(cli_lines)
            elif slug == 'eigrp':
                # Generate CLI for EIGRP configuration
                as_num = get_single('eigrp_as_number') or ''
                rid = get_single('eigrp_router_id') or ''
                variance = get_single('eigrp_variance') or ''
                passive = get_single('eigrp_passive_interfaces') or ''
                nets = form_data.get('eigrp_network', [])
                wilds = form_data.get('eigrp_wildcard', [])
                cli_lines = []
                cli_lines.append('! EIGRP configuration')
                if as_num:
                    cli_lines.append(f'router eigrp {as_num}')
                    if rid:
                        cli_lines.append(f' eigrp router-id {rid}')
                    if variance:
                        cli_lines.append(f' variance {variance}')
                    if passive:
                        # Passive interfaces provided as comma-separated list
                        for iface in [i.strip() for i in passive.split(',') if i.strip()]:
                            cli_lines.append(f' passive-interface {iface}')
                    # Network statements
                    for net, wc in zip(nets, wilds):
                        if net:
                            if wc:
                                cli_lines.append(f' network {net} {wc}')
                            else:
                                cli_lines.append(f' network {net}')
                    cli_lines.append(' exit')
                else:
                    cli_lines.append('! no EIGRP AS number provided')
                entry = "\n".join(cli_lines)
            elif slug == 'vrrp':
                # Generate CLI for VRRP configuration
                gids = form_data.get('vrrp_group_id', [])
                vips = form_data.get('vrrp_virtual_ip', [])
                prios = form_data.get('vrrp_priority', [])
                preempts = form_data.get('vrrp_preempt', [])
                cli_lines = []
                cli_lines.append('! VRRP configuration')
                max_len = max(len(gids), len(vips), len(prios), len(preempts))
                added = False
                for i in range(max_len):
                    gid = gids[i] if i < len(gids) else ''
                    vip = vips[i] if i < len(vips) else ''
                    prio = prios[i] if i < len(prios) else ''
                    pre = preempts[i] if i < len(preempts) else ''
                    if gid and vip:
                        added = True
                        cli_lines.append(f'vrrp {gid} ip {vip}')
                        if prio:
                            cli_lines.append(f'vrrp {gid} priority {prio}')
                        if pre:
                            cli_lines.append(f'vrrp {gid} preempt')
                if not added:
                    cli_lines.append('! no VRRP groups provided')
                entry = "\n".join(cli_lines)
            elif slug == 'hsrp':
                # Generate CLI for HSRP configuration
                gids = form_data.get('hsrp_group_id', [])
                vips = form_data.get('hsrp_virtual_ip', [])
                prios = form_data.get('hsrp_priority', [])
                preempts = form_data.get('hsrp_preempt', [])
                cli_lines = []
                cli_lines.append('! HSRP configuration')
                max_len = max(len(gids), len(vips), len(prios), len(preempts))
                added = False
                for i in range(max_len):
                    gid = gids[i] if i < len(gids) else ''
                    vip = vips[i] if i < len(vips) else ''
                    prio = prios[i] if i < len(prios) else ''
                    pre = preempts[i] if i < len(preempts) else ''
                    if gid and vip:
                        added = True
                        cli_lines.append(f'standby {gid} ip {vip}')
                        if prio:
                            cli_lines.append(f'standby {gid} priority {prio}')
                        if pre:
                            cli_lines.append(f'standby {gid} preempt')
                if not added:
                    cli_lines.append('! no HSRP groups provided')
                entry = "\n".join(cli_lines)
            elif slug == 'glbp':
                # Generate CLI for GLBP configuration
                gids = form_data.get('glbp_group_id', [])
                vips = form_data.get('glbp_virtual_ip', [])
                prios = form_data.get('glbp_priority', [])
                preempts = form_data.get('glbp_preempt', [])
                cli_lines = []
                cli_lines.append('! GLBP configuration')
                max_len = max(len(gids), len(vips), len(prios), len(preempts))
                added = False
                for i in range(max_len):
                    gid = gids[i] if i < len(gids) else ''
                    vip = vips[i] if i < len(vips) else ''
                    prio = prios[i] if i < len(prios) else ''
                    pre = preempts[i] if i < len(preempts) else ''
                    if gid and vip:
                        added = True
                        cli_lines.append(f'glbp {gid} ip {vip}')
                        if prio:
                            cli_lines.append(f'glbp {gid} priority {prio}')
                        if pre:
                            cli_lines.append(f'glbp {gid} preempt')
                if not added:
                    cli_lines.append('! no GLBP groups provided')
                entry = "\n".join(cli_lines)
            elif slug == 'ntp-ptp':
                # Generate CLI for NTP/PTP configuration
                servers = [srv for srv in form_data.get('ntp_server', []) if srv]
                stratum = get_single('ntp_master_stratum') or ''
                cli_lines = []
                cli_lines.append('! NTP/PTP configuration')
                for srv in servers:
                    cli_lines.append(f'ntp server {srv}')
                if stratum:
                    cli_lines.append(f'ntp master {stratum}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no NTP servers provided')
                entry = "\n".join(cli_lines)
            elif slug == 'rip':
                # Generate CLI for RIP configuration
                version = get_single('rip_version') or ''
                nets = [n for n in form_data.get('rip_network', []) if n]
                cli_lines = []
                cli_lines.append('! RIP configuration')
                cli_lines.append('router rip')
                if version:
                    cli_lines.append(f' version {version}')
                for net in nets:
                    cli_lines.append(f' network {net}')
                cli_lines.append(' no auto-summary')
                cli_lines.append(' exit')
                entry = "\n".join(cli_lines)
            elif slug in ('vrf', 'mpls'):
                # Generate CLI for VRF/MPLS configuration
                names = form_data.get('vrf_name', [])
                rds = form_data.get('vrf_rd', [])
                rts = form_data.get('vrf_rt', [])
                cli_lines = []
                cli_lines.append('! VRF/MPLS configuration')
                max_len = max(len(names), len(rds), len(rts))
                added = False
                for i in range(max_len):
                    name = names[i] if i < len(names) else ''
                    rd = rds[i] if i < len(rds) else ''
                    rt = rts[i] if i < len(rts) else ''
                    if name:
                        added = True
                        cli_lines.append(f'ip vrf {name}')
                        if rd:
                            cli_lines.append(f' rd {rd}')
                        if rt:
                            # Use both import and export for simplicity
                            cli_lines.append(f' route-target both {rt}')
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no VRFs provided')
                entry = "\n".join(cli_lines)
            elif slug == 'gre':
                # Generate CLI for GRE tunnel configuration
                ids = form_data.get('gre_tunnel_id', [])
                srcs = form_data.get('gre_source', [])
                dests = form_data.get('gre_destination', [])
                ips = form_data.get('gre_tunnel_ip', [])
                cli_lines = []
                cli_lines.append('! GRE tunnel configuration')
                max_len = max(len(ids), len(srcs), len(dests), len(ips))
                added = False
                for i in range(max_len):
                    t_id = ids[i] if i < len(ids) else ''
                    src = srcs[i] if i < len(srcs) else ''
                    dst = dests[i] if i < len(dests) else ''
                    ip = ips[i] if i < len(ips) else ''
                    if dst:
                        added = True
                        # Default tunnel number if not provided
                        tun_id = t_id if t_id else str(i)
                        cli_lines.append(f'interface Tunnel{tun_id}')
                        if ip:
                            cli_lines.append(f' ip address {ip}')
                        if src:
                            cli_lines.append(f' tunnel source {src}')
                        cli_lines.append(f' tunnel destination {dst}')
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no GRE tunnels provided')
                entry = "\n".join(cli_lines)
            elif slug in ('ipsec', 'ipsec-vpn'):
                # Generate CLI for IPsec VPN configuration (simplified)
                peer = get_single('ipsec_peer_ip') or ''
                psk = get_single('ipsec_psk') or ''
                ike = get_single('ipsec_ike_version') or ''
                enc = get_single('ipsec_encryption') or ''
                hash_alg = get_single('ipsec_hash') or ''
                dh = get_single('ipsec_dh_group') or ''
                loc_int = get_single('ipsec_local_interface') or ''
                cli_lines = []
                cli_lines.append('! IPsec VPN configuration (simplified)')
                if peer and psk:
                    # ISAKMP/IKE policy
                    cli_lines.append('crypto isakmp policy 10')
                    if enc:
                        cli_lines.append(f' encryption {enc}')
                    if hash_alg:
                        cli_lines.append(f' hash {hash_alg}')
                    if dh:
                        cli_lines.append(f' group {dh}')
                    cli_lines.append(' authentication pre-share')
                    cli_lines.append(' exit')
                    cli_lines.append(f'crypto isakmp key {psk} address {peer}')
                    # Placeholder for transform-set and crypto map
                    cli_lines.append('! Define transform-set and crypto map based on your design')
                else:
                    cli_lines.append('! incomplete IPsec parameters provided')
                entry = "\n".join(cli_lines)
            elif slug == 'dhcp-server-relay':
                # Generate CLI for DHCP Server and Relay configuration
                pool_names = form_data.get('dhcp_pool_name', [])
                pool_networks = form_data.get('dhcp_pool_network', [])
                pool_routers = form_data.get('dhcp_pool_router', [])
                pool_dns = form_data.get('dhcp_pool_dns', [])
                pool_excl_start = form_data.get('dhcp_exclude_start', [])
                pool_excl_end = form_data.get('dhcp_exclude_end', [])
                rel_ifaces = form_data.get('dhcp_relay_interface', [])
                rel_addrs = form_data.get('dhcp_relay_address', [])
                cli_lines = []
                cli_lines.append('! DHCP Server/Relay configuration')
                # Pools
                max_len = max(len(pool_names), len(pool_networks), len(pool_routers), len(pool_dns), len(pool_excl_start), len(pool_excl_end))
                pools_added = False
                for i in range(max_len):
                    name = pool_names[i] if i < len(pool_names) else ''
                    net = pool_networks[i] if i < len(pool_networks) else ''
                    router = pool_routers[i] if i < len(pool_routers) else ''
                    dns = pool_dns[i] if i < len(pool_dns) else ''
                    excl_start = pool_excl_start[i] if i < len(pool_excl_start) else ''
                    excl_end = pool_excl_end[i] if i < len(pool_excl_end) else ''
                    if name and net:
                        pools_added = True
                        # Exclude addresses if provided
                        if excl_start and excl_end:
                            cli_lines.append(f'ip dhcp excluded-address {excl_start} {excl_end}')
                        cli_lines.append(f'ip dhcp pool {name}')
                        cli_lines.append(f' network {net}')
                        if router:
                            cli_lines.append(f' default-router {router}')
                        if dns:
                            # DNS servers comma-separated; convert to space separated
                            dns_list = " ".join([d.strip() for d in dns.split(',') if d.strip()])
                            cli_lines.append(f' dns-server {dns_list}')
                        cli_lines.append(' exit')
                # Relays
                relays_added = False
                for iface, addr in zip(rel_ifaces, rel_addrs):
                    if iface and addr:
                        relays_added = True
                        cli_lines.append(f'interface {iface}')
                        cli_lines.append(f' ip helper-address {addr}')
                        cli_lines.append(' exit')
                if not pools_added and not relays_added:
                    cli_lines.append('! no DHCP pools or relays provided')
                entry = "\n".join(cli_lines)
            elif slug == 'vtp':
                # Generate CLI for VTP configuration
                mode = get_single('vtp_mode') or ''
                domain = get_single('vtp_domain') or ''
                pwd = get_single('vtp_password') or ''
                cli_lines = []
                cli_lines.append('! VTP configuration')
                if mode:
                    cli_lines.append(f'vtp mode {mode}')
                if domain:
                    cli_lines.append(f'vtp domain {domain}')
                if pwd:
                    cli_lines.append(f'vtp password {pwd}')
                entry = "\n".join(cli_lines)
            elif slug in ('stp', 'pvst-plus'):
                # Generate CLI for spanning-tree protocol configuration
                mode = get_single('stp_mode') or ''
                prio = get_single('stp_priority') or ''
                cli_lines = []
                cli_lines.append('! Spanning Tree configuration')
                if mode:
                    cli_lines.append(f'spanning-tree mode {mode}')
                if prio:
                    # Apply priority globally (bridge priority) when specified
                    cli_lines.append(f'spanning-tree priority {prio}')
                entry = "\n".join(cli_lines)
            elif slug in ('etherchannel', 'lacp'):
                # Generate CLI for EtherChannel / LACP configuration
                channel_ids = form_data.get('ec_channel_id', [])
                members = form_data.get('ec_members', [])
                modes = form_data.get('ec_mode', [])
                cli_lines = []
                cli_lines.append('! EtherChannel configuration')
                for cid, mems, mode in zip(channel_ids, members, modes):
                    if cid and mems:
                        # Assume members are comma-separated interfaces or a range
                        cli_lines.append(f'interface range {mems}')
                        cli_lines.append(f' channel-group {cid} mode {mode}')
                        cli_lines.append('!')
                        cli_lines.append(f'interface Port-channel{cid}')
                        # Default to switchport; user can modify as needed
                        cli_lines.append(' switchport')
                if not cli_lines or len(cli_lines) <= 1:
                    cli_lines.append('! no channels provided')
                entry = "\n".join(cli_lines)
            elif slug in ('cdp', 'lldp'):
                # Generate CLI for CDP/LLDP toggle
                cdp_on = 'cdp_enable' in form_data
                lldp_on = 'lldp_enable' in form_data
                cli_lines = []
                cli_lines.append('! Discovery protocols configuration')
                if cdp_on:
                    cli_lines.append('cdp run')
                else:
                    cli_lines.append('no cdp run')
                if lldp_on:
                    cli_lines.append('lldp run')
                else:
                    cli_lines.append('no lldp run')
                entry = "\n".join(cli_lines)
            elif slug in ('span', 'rspan', 'erspan'):
                # Generate CLI for SPAN/RSPAN/ERSPAN sessions
                session_ids = form_data.get('span_session_id', [])
                srcs = form_data.get('span_source_interface', [])
                dirs = form_data.get('span_direction', [])
                dsts = form_data.get('span_dest_interface', [])
                cli_lines = []
                cli_lines.append('! SPAN configuration')
                for sid, src, direction, dst in zip(session_ids, srcs, dirs, dsts):
                    if sid and src and dst:
                        # Direction mapping: both -> both; rx -> ingress; tx -> egress
                        dir_map = {'both': 'both', 'rx': 'rx', 'tx': 'tx'}
                        dir_val = dir_map.get(direction, direction)
                        cli_lines.append(f'monitor session {sid} source interface {src} {dir_val}')
                        cli_lines.append(f'monitor session {sid} destination interface {dst}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no SPAN sessions provided')
                entry = "\n".join(cli_lines)
            elif slug == 'acl':
                # Generate CLI for Access Control List
                actions = form_data.get('acl_action', [])
                protocols = form_data.get('acl_protocol', [])
                srcs = form_data.get('acl_src', [])
                dsts = form_data.get('acl_dst', [])
                cli_lines = []
                cli_lines.append('! Access Control List')
                # Name ACL generically
                cli_lines.append('ip access-list extended ACL_1')
                seq = 10
                added = False
                for act, proto, src, dst in zip(actions, protocols, srcs, dsts):
                    if src and dst:
                        added = True
                        line = f' {seq} {act.lower()} {proto.lower()} '
                        # If source or dest contains spaces, keep as is
                        line += f'{src} {dst}'
                        cli_lines.append(line)
                        seq += 10
                cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no ACL entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'object-groups':
                # Generate CLI for Object Groups
                names = form_data.get('og_name', [])
                types = form_data.get('og_type', [])
                members = form_data.get('og_members', [])
                cli_lines = []
                cli_lines.append('! Object Groups configuration')
                added = False
                for name, typ, mem in zip(names, types, members):
                    if name and mem:
                        added = True
                        # Determine type: network or service
                        typ_lower = typ.lower() if typ else 'network'
                        if typ_lower == 'network':
                            cli_lines.append(f'object-group network {name}')
                            # Members may be comma-separated or space-separated
                            for m in [x.strip() for x in mem.split(',') if x.strip()]:
                                cli_lines.append(f' network-object {m}')
                            cli_lines.append(' exit')
                        elif typ_lower == 'service':
                            cli_lines.append(f'object-group service {name}')
                            # Without protocol we default to tcp
                            for m in [x.strip() for x in mem.split(',') if x.strip()]:
                                cli_lines.append(f' port-object {m}')
                            cli_lines.append(' exit')
                        else:
                            cli_lines.append(f'! unsupported object-group type {typ_lower}')
                if not added:
                    cli_lines.append('! no object-groups provided')
                entry = "\n".join(cli_lines)
            elif slug == 'asa-failover-clustering':
                # Generate CLI for ASA Failover/Clustering
                mode = get_single('failover_mode') or ''
                iface = get_single('failover_interface') or ''
                key_val = get_single('failover_key') or ''
                prim = get_single('failover_primary_ip') or ''
                sec = get_single('failover_secondary_ip') or ''
                mask = get_single('failover_netmask') or ''
                cli_lines = []
                cli_lines.append('! ASA Failover configuration')
                cli_lines.append('failover')
                if mode:
                    # Use simplified mode declaration; user must adjust
                    cli_lines.append(f'failover mode {mode}')
                if iface and prim and sec and mask:
                    cli_lines.append(f'failover interface {iface} {prim} {sec} {mask}')
                if key_val:
                    cli_lines.append(f'failover key {key_val}')
                entry = "\n".join(cli_lines)
            elif slug == 'unicast-rpf':
                # Generate CLI for Unicast Reverse Path Forwarding
                ifaces = form_data.get('urpf_interface', [])
                modes_val = form_data.get('urpf_mode', [])
                allow_defaults = form_data.get('urpf_allow_default', [])
                cli_lines = []
                cli_lines.append('! Unicast RPF configuration')
                max_len = max(len(ifaces), len(modes_val), len(allow_defaults))
                added = False
                for i in range(max_len):
                    iface = ifaces[i] if i < len(ifaces) else ''
                    mode_val = modes_val[i] if i < len(modes_val) else ''
                    allow = allow_defaults[i] if i < len(allow_defaults) else ''
                    if iface:
                        added = True
                        cli_lines.append(f'interface {iface}')
                        # Map mode to CLI directive
                        if mode_val == 'strict':
                            line = ' ip verify unicast source reachable-via rx'
                        else:
                            line = ' ip verify unicast source reachable-via any'
                        if allow:
                            line += ' allow-default'
                        cli_lines.append(line)
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no uRPF entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'igmp':
                # Generate CLI for IGMP configuration
                interfaces = form_data.get('igmp_interface', [])
                versions = form_data.get('igmp_version', [])
                cli_lines = []
                cli_lines.append('! IGMP configuration')
                max_len = max(len(interfaces), len(versions))
                added = False
                for i in range(max_len):
                    intf = interfaces[i] if i < len(interfaces) else ''
                    ver = versions[i] if i < len(versions) else ''
                    if intf:
                        added = True
                        cli_lines.append(f'interface {intf}')
                        if ver:
                            cli_lines.append(f' ip igmp version {ver}')
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no IGMP interfaces provided')
                entry = "\n".join(cli_lines)
            elif slug == 'pim':
                # Generate CLI for PIM configuration
                mode = get_single('pim_mode') or ''
                ifaces = form_data.get('pim_interface', [])
                rp = get_single('pim_rp_address') or ''
                grp = get_single('pim_group_range') or ''
                cli_lines = []
                cli_lines.append('! PIM configuration')
                added = False
                # Configure PIM on interfaces
                for iface in ifaces:
                    if iface:
                        added = True
                        cli_lines.append(f'interface {iface}')
                        if mode:
                            # Convert mode to CLI (e.g. sparse -> sparse-mode)
                            cli_lines.append(f' ip pim {mode}-mode')
                        cli_lines.append(' exit')
                # RP configuration
                if rp:
                    added = True
                    if grp:
                        cli_lines.append(f'ip pim rp-address {rp} {grp}')
                    else:
                        cli_lines.append(f'ip pim rp-address {rp}')
                if not added:
                    cli_lines.append('! no PIM entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'multicast-routing':
                # Generate CLI for multicast routing
                enable = 'multicast_enable' in form_data
                ssm = get_single('multicast_ssm_range') or ''
                rp_enable = 'multicast_rp_enable' in form_data
                rp_addr = get_single('multicast_rp_address') or ''
                bsr = 'multicast_bsr_enable' in form_data
                cli_lines = []
                cli_lines.append('! Multicast Routing configuration')
                if enable:
                    cli_lines.append('ip multicast-routing')
                if ssm:
                    cli_lines.append(f'ip pim ssm range {ssm}')
                if rp_enable and rp_addr:
                    cli_lines.append(f'ip pim rp-address {rp_addr}')
                if bsr:
                    # Generic BSR candidate statement; device-specific details omitted
                    cli_lines.append('! BSR candidate configuration required')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no multicast routing entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'netflow':
                # Generate CLI for NetFlow configuration
                collector_ips = form_data.get('netflow_collector_ip', [])
                collector_ports = form_data.get('netflow_collector_port', [])
                versions = form_data.get('netflow_version', [])
                interfaces = get_single('netflow_interfaces') or ''
                cli_lines = []
                cli_lines.append('! NetFlow configuration')
                max_len = max(len(collector_ips), len(collector_ports), len(versions))
                added = False
                for i in range(max_len):
                    ip = collector_ips[i] if i < len(collector_ips) else ''
                    port = collector_ports[i] if i < len(collector_ports) else ''
                    ver = versions[i] if i < len(versions) else ''
                    if ip:
                        added = True
                        # Use ip flow-export commands for simplicity
                        cli_lines.append(f'ip flow-export destination {ip} {port}')
                        if ver:
                            cli_lines.append(f'ip flow-export version {ver}')
                if interfaces:
                    added = True
                    # Interfaces may be comma-separated
                    for iface in [x.strip() for x in interfaces.split(',') if x.strip()]:
                        cli_lines.append(f'interface {iface}')
                        cli_lines.append(' ip flow ingress')
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no NetFlow entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'qos':
                # Generate CLI for QoS configuration
                class_names = form_data.get('qos_class_name', [])
                bws = form_data.get('qos_bandwidth', [])
                prios = form_data.get('qos_priority', [])
                dscps = form_data.get('qos_dscp', [])
                cli_lines = []
                cli_lines.append('! QoS configuration')
                policy_name = 'QOS_POLICY'
                added = False
                max_len = max(len(class_names), len(bws), len(prios), len(dscps))
                # Create class-maps and policy-map
                for i in range(max_len):
                    cn = class_names[i] if i < len(class_names) else ''
                    bw = bws[i] if i < len(bws) else ''
                    pr = prios[i] if i < len(prios) else ''
                    dc = dscps[i] if i < len(dscps) else ''
                    if cn:
                        added = True
                        # Define class-map
                        cli_lines.append(f'class-map match-any {cn}')
                        # If DSCP provided, match on DSCP
                        if dc:
                            cli_lines.append(f'  match dscp {dc}')
                        cli_lines.append(' exit')
                if added:
                    cli_lines.append(f'policy-map {policy_name}')
                    for i in range(max_len):
                        cn = class_names[i] if i < len(class_names) else ''
                        bw = bws[i] if i < len(bws) else ''
                        pr = prios[i] if i < len(prios) else ''
                        dc = dscps[i] if i < len(dscps) else ''
                        if cn:
                            cli_lines.append(f' class {cn}')
                            if bw:
                                cli_lines.append(f'  bandwidth {bw}')
                            if pr:
                                cli_lines.append('  priority')
                            if dc:
                                cli_lines.append(f'  set dscp {dc}')
                            cli_lines.append(' exit')
                    cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no QoS classes provided')
                entry = "\n".join(cli_lines)
            elif slug == 'private-vlan':
                # Generate CLI for Private VLAN configuration
                primaries = form_data.get('pvlan_primary', [])
                secs = form_data.get('pvlan_secondary', [])
                types = form_data.get('pvlan_type', [])
                cli_lines = []
                cli_lines.append('! Private VLAN configuration')
                # Build a dictionary of primary VLAN to list of (secondary, type)
                pv_dict = {}
                max_len = max(len(primaries), len(secs), len(types))
                for i in range(max_len):
                    prim = primaries[i] if i < len(primaries) else ''
                    sec = secs[i] if i < len(secs) else ''
                    t = types[i] if i < len(types) else ''
                    if prim and sec:
                        pv_dict.setdefault(prim, []).append((sec, t))
                for prim, sec_list in pv_dict.items():
                    # Define primary VLAN
                    cli_lines.append(f'vlan {prim}')
                    cli_lines.append(' private-vlan primary')
                    cli_lines.append(' exit')
                    # Define each secondary VLAN and type
                    for sec, t in sec_list:
                        cli_lines.append(f'vlan {sec}')
                        if t and t.lower() == 'community':
                            cli_lines.append(' private-vlan community')
                        else:
                            cli_lines.append(' private-vlan isolated')
                        cli_lines.append(' exit')
                    # Associate secondary VLANs with primary
                    sec_ids = [sec for sec, _ in sec_list]
                    cli_lines.append(f'vlan {prim}')
                    # Build association list for this primary
                    assoc = ",".join(sec_ids)
                    cli_lines.append(f' private-vlan association {assoc}')
                    cli_lines.append(' exit')
                if not pv_dict:
                    cli_lines.append('! no PVLANs provided')
                entry = "\n".join(cli_lines)
            elif slug == 'voice-vlan':
                # Generate CLI for Voice VLAN assignment
                interfaces = form_data.get('voice_interface', [])
                vlans = form_data.get('voice_vlan_id', [])
                cli_lines = []
                cli_lines.append('! Voice VLAN configuration')
                max_len = max(len(interfaces), len(vlans))
                for i in range(max_len):
                    intf = interfaces[i] if i < len(interfaces) else ''
                    vid = vlans[i] if i < len(vlans) else ''
                    if intf and vid:
                        cli_lines.append(f'interface {intf}')
                        cli_lines.append(' switchport mode access')
                        cli_lines.append(f' switchport voice vlan {vid}')
                        cli_lines.append(' exit')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no voice VLANs provided')
                entry = "\n".join(cli_lines)
            elif slug == 'stackwise':
                # Generate CLI for StackWise switch priority
                sw_nums = form_data.get('stack_switch_number', [])
                sw_prios = form_data.get('stack_priority', [])
                cli_lines = []
                cli_lines.append('! StackWise configuration')
                max_len = max(len(sw_nums), len(sw_prios))
                for i in range(max_len):
                    num = sw_nums[i] if i < len(sw_nums) else ''
                    prio = sw_prios[i] if i < len(sw_prios) else ''
                    if num:
                        cli_lines.append(f'switch {num} priority {prio}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no stack members provided')
                entry = "\n".join(cli_lines)
            elif slug == 'ip-source-guard':
                # Generate CLI for IP Source Guard
                ifaces = form_data.get('ipsg_interface', [])
                modes = form_data.get('ipsg_mode', [])
                cli_lines = []
                cli_lines.append('! IP Source Guard configuration')
                max_len = max(len(ifaces), len(modes))
                for i in range(max_len):
                    iface = ifaces[i] if i < len(ifaces) else ''
                    mode = modes[i] if i < len(modes) else ''
                    if iface:
                        cli_lines.append(f'interface {iface}')
                        # Determine verification based on mode
                        if mode == 'mac':
                            cli_lines.append(' ip verify source mac')
                        else:
                            cli_lines.append(' ip verify source')
                        cli_lines.append(' exit')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no IP Source Guard entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'dynamic-arp-inspection':
                # Generate CLI for Dynamic ARP Inspection
                vlans = get_single('dai_vlans') or ''
                trusted = get_single('dai_trusted_interfaces') or ''
                rate = get_single('dai_rate_limit') or ''
                cli_lines = []
                cli_lines.append('! Dynamic ARP Inspection configuration')
                if vlans:
                    cli_lines.append(f'ip arp inspection vlan {vlans}')
                    cli_lines.append('ip arp inspection validate src-mac dst-mac ip')
                if trusted:
                    for iface in [i.strip() for i in trusted.split(',') if i.strip()]:
                        cli_lines.append(f'interface {iface}')
                        cli_lines.append(' ip arp inspection trust')
                        cli_lines.append(' exit')
                if rate:
                    cli_lines.append(f'ip arp inspection limit rate {rate}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no DAI entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'dhcp-snooping':
                # Generate CLI for DHCP Snooping
                vlans = get_single('dhcp_snoop_vlans') or ''
                trusted = get_single('dhcp_snoop_trusted_interfaces') or ''
                rate = get_single('dhcp_snoop_rate_limit') or ''
                cli_lines = []
                cli_lines.append('! DHCP Snooping configuration')
                cli_lines.append('ip dhcp snooping')
                if vlans:
                    cli_lines.append(f'ip dhcp snooping vlan {vlans}')
                    cli_lines.append('ip dhcp snooping information option')
                if trusted:
                    for iface in [i.strip() for i in trusted.split(',') if i.strip()]:
                        cli_lines.append(f'interface {iface}')
                        cli_lines.append(' ip dhcp snooping trust')
                        cli_lines.append(' exit')
                if rate:
                    cli_lines.append(f'ip dhcp snooping limit rate {rate}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no DHCP Snooping entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'igmp-snooping':
                # Generate CLI for IGMP Snooping
                vlans = get_single('igmp_snoop_vlans') or ''
                version = get_single('igmp_snoop_version') or ''
                cli_lines = []
                cli_lines.append('! IGMP Snooping configuration')
                cli_lines.append('ip igmp snooping')
                if vlans:
                    cli_lines.append(f'ip igmp snooping vlan {vlans}')
                if version:
                    cli_lines.append(f'ip igmp snooping version {version}')
                # Use a default last-member query interval as per best practice
                cli_lines.append('ip igmp snooping last-member-query-interval 1000')
                entry = "\n".join(cli_lines)
            elif slug == 'zone-based-firewall':
                # Generate CLI for Zone-Based Firewall configuration
                z_names = form_data.get('zbf_zone_name', [])
                z_ifaces = form_data.get('zbf_zone_interfaces', [])
                zp_src = form_data.get('zbf_source_zone', [])
                zp_dst = form_data.get('zbf_destination_zone', [])
                zp_act = form_data.get('zbf_action', [])
                cli_lines = []
                cli_lines.append('! Zone-Based Firewall configuration')
                # Define zones and assign interfaces
                for name, ifs in zip(z_names, z_ifaces):
                    if name:
                        cli_lines.append(f'zone security {name}')
                        if ifs:
                            for iface in [x.strip() for x in ifs.split(',') if x.strip()]:
                                cli_lines.append(f' zone-member interface {iface}')
                        cli_lines.append(' exit')
                # Define zone pairs and policies
                max_len = max(len(zp_src), len(zp_dst), len(zp_act))
                for i in range(max_len):
                    s = zp_src[i] if i < len(zp_src) else ''
                    d = zp_dst[i] if i < len(zp_dst) else ''
                    a = zp_act[i] if i < len(zp_act) else ''
                    if s and d:
                        # Create class-map and policy-map names based on zones
                        class_name = f'CLASS_{s}_TO_{d}'.replace('-', '_')
                        policy_name = f'POLICY_{s}_TO_{d}'.replace('-', '_')
                        zonepair_name = f'{s}_to_{d}'.replace(' ', '_')
                        # Class-map for matching all IP traffic
                        cli_lines.append(f'class-map type inspect match-any {class_name}')
                        cli_lines.append(' match protocol ip')
                        cli_lines.append(' exit')
                        # Policy-map to apply inspect or drop
                        cli_lines.append(f'policy-map type inspect {policy_name}')
                        cli_lines.append(f' class type inspect {class_name}')
                        if a and a.lower() in ('deny', 'drop'):
                            cli_lines.append('  drop')
                        else:
                            # Default action is inspect
                            cli_lines.append('  inspect')
                        cli_lines.append(' exit')
                        # Zone-pair linking source/destination zones with service-policy
                        cli_lines.append(f'zone-pair security {zonepair_name} source {s} destination {d}')
                        cli_lines.append(f' service-policy type inspect {policy_name}')
                        cli_lines.append(' exit')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no zone-based firewall entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'ssl-vpn':
                # Generate CLI for SSL VPN configuration (simplified)
                ip_addr = get_single('ssl_public_ip') or ''
                port = get_single('ssl_port') or ''
                tg = get_single('ssl_tunnel_group') or ''
                auth = get_single('ssl_auth_method') or ''
                cli_lines = []
                cli_lines.append('! SSL VPN configuration')
                # We assume ASA style webvpn section; specify port if provided
                if port:
                    cli_lines.append('webvpn')
                    cli_lines.append(f' port {port}')
                    cli_lines.append(' exit')
                # Tunnel-group configuration
                if tg:
                    cli_lines.append(f'tunnel-group {tg} type remote-access')
                    cli_lines.append(f'tunnel-group {tg} general-attributes')
                    if auth:
                        cli_lines.append(f' authentication-server-group {auth}')
                    cli_lines.append(' exit')
                # Public IP comment
                if ip_addr:
                    cli_lines.append(f'! public IP for SSL VPN: {ip_addr}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no SSL VPN entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'anyconnect':
                # Generate CLI for AnyConnect configuration (simplified)
                portal = get_single('anyconnect_portal_address') or ''
                gp = get_single('anyconnect_group_policy') or ''
                proto = get_single('anyconnect_protocol') or ''
                cli_lines = []
                cli_lines.append('! AnyConnect configuration')
                # WebVPN portal and enable AnyConnect
                if portal:
                    cli_lines.append('webvpn')
                    cli_lines.append(f' url-listen {portal}')
                    cli_lines.append(' anyconnect enable')
                    cli_lines.append(' exit')
                # Group-policy configuration
                if gp:
                    cli_lines.append(f'group-policy {gp} internal')
                    cli_lines.append(f'group-policy {gp} attributes')
                    if proto:
                        cli_lines.append(f' vpn-tunnel-protocol {proto}')
                    cli_lines.append(' exit')
                    # Tunnel-group using group policy
                    cli_lines.append(f'tunnel-group {gp} type remote-access')
                    cli_lines.append(f'tunnel-group {gp} general-attributes')
                    cli_lines.append(f' default-group-policy {gp}')
                    cli_lines.append(' exit')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no AnyConnect entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'ids-ips':
                # Generate CLI for IDS/IPS configuration (simplified)
                enabled = 'ids_enable' in form_data
                updates = 'ids_sigs_update' in form_data
                cli_lines = []
                cli_lines.append('! IDS/IPS configuration')
                if enabled:
                    # Placeholder for enabling IDS/IPS; actual configuration may vary by platform
                    cli_lines.append('ip ips notify log')
                    if updates:
                        cli_lines.append('! signature updates enabled')
                else:
                    cli_lines.append('! IDS/IPS disabled')
                entry = "\n".join(cli_lines)
            elif slug == 'ssl-tls-inspection':
                # Generate CLI for SSL/TLS Inspection (simplified)
                enabled = 'ssli_enable' in form_data
                cert = get_single('ssli_certificate') or ''
                cli_lines = []
                cli_lines.append('! SSL/TLS Inspection configuration')
                if enabled:
                    if cert:
                        cli_lines.append(f'ssl trustpoint {cert}')
                    # Define a simple policy-map for SSL inspection
                    cli_lines.append('policy-map type inspect ssl SSL_POLICY')
                    cli_lines.append(' class type inspect ssl')
                    cli_lines.append('  inspect ssl')
                    cli_lines.append(' exit')
                else:
                    cli_lines.append('! SSL/TLS inspection disabled')
                entry = "\n".join(cli_lines)
            elif slug == 'gnoc':
                # Generate CLI for GNOC configuration (generic)
                p1 = get_single('gnoc_param1') or ''
                p2 = get_single('gnoc_param2') or ''
                cli_lines = []
                cli_lines.append('! GNOC configuration')
                # Document parameters as comments since specifics are unknown
                cli_lines.append(f'! param1: {p1}')
                cli_lines.append(f'! param2: {p2}')
                entry = "\n".join(cli_lines)
            elif slug == 'threat-detection':
                # Generate CLI for Threat Detection configuration
                enabled = 'td_enable' in form_data
                rate = get_single('td_rate') or ''
                cli_lines = []
                cli_lines.append('! Threat Detection configuration')
                if enabled:
                    cli_lines.append('threat-detection basic')
                    if rate:
                        cli_lines.append(f'threat-detection rate {rate}')
                else:
                    cli_lines.append('! threat detection disabled')
                entry = "\n".join(cli_lines)
            elif slug == 'embedded-event-manager':
                # Generate CLI for Embedded Event Manager configuration
                names = form_data.get('eem_name', [])
                ev_types = form_data.get('eem_event_type', [])
                ev_data = form_data.get('eem_event_data', [])
                actions = form_data.get('eem_action_cli', [])
                cli_lines = []
                cli_lines.append('! Embedded Event Manager configuration')
                added = False
                max_len = max(len(names), len(ev_types), len(ev_data), len(actions))
                for i in range(max_len):
                    name = names[i] if i < len(names) else ''
                    et = ev_types[i] if i < len(ev_types) else ''
                    ed = ev_data[i] if i < len(ev_data) else ''
                    act = actions[i] if i < len(actions) else ''
                    if name:
                        added = True
                        cli_lines.append(f'event manager applet {name}')
                        # Configure the event trigger based on type
                        if et == 'syslog' and ed:
                            cli_lines.append(f' event syslog pattern "{ed}"')
                        elif et == 'timer' and ed:
                            # Use cron format for timer events
                            cli_lines.append(f' event timer cron "{ed}"')
                        elif et == 'cli' and ed:
                            cli_lines.append(f' event cli pattern "{ed}"')
                        # Define actions; split actions by semicolon into multiple action lines
                        if act:
                            cmds = [c.strip() for c in act.split(';') if c.strip()]
                            idx = 1
                            for cmd in cmds:
                                cli_lines.append(f' action {idx}.0 cli command "{cmd}"')
                                idx += 1
                        cli_lines.append(' exit')
                if not added:
                    cli_lines.append('! no EEM applets provided')
                entry = "\n".join(cli_lines)
            elif slug == 'aaa':
                # Generate CLI configuration for AAA
                # Determine which authentication methods are enabled and collect server info
                use_tacacs = 'aaa_use_tacacs' in form_data
                tacacs_servers = [s for s in form_data.get('tacacs_server', []) if s]
                use_radius = 'aaa_use_radius' in form_data
                radius_servers = [s for s in form_data.get('radius_server', []) if s]
                user_names = form_data.get('local_user_name', [])
                user_pwds = form_data.get('local_user_password', [])
                user_privs = form_data.get('local_user_priv', [])
                # Build CLI lines
                cli_lines = []
                cli_lines.append('! AAA configuration')
                # Always enable AAA if any method is configured
                if use_tacacs or use_radius or any(u for u in user_names):
                    cli_lines.append('aaa new-model')
                # TACACS+ servers and method list
                if use_tacacs and tacacs_servers:
                    for ip in tacacs_servers:
                        # Use legacy tacacs-server host command for simplicity
                        cli_lines.append(f'tacacs-server host {ip}')
                    # Define authentication order: TACACS+ then local fallback
                    cli_lines.append('aaa authentication login default group tacacs+ local')
                # RADIUS servers and method list
                if use_radius and radius_servers:
                    for ip in radius_servers:
                        cli_lines.append(f'radius-server host {ip}')
                    # Define authentication order: RADIUS then local fallback
                    cli_lines.append('aaa authentication login default group radius local')
                # Local user accounts
                max_len = max(len(user_names), len(user_pwds), len(user_privs))
                for i in range(max_len):
                    name = user_names[i] if i < len(user_names) else ''
                    pwd = user_pwds[i] if i < len(user_pwds) else ''
                    priv = user_privs[i] if i < len(user_privs) else ''
                    if name and pwd:
                        priv_val = priv or '15'
                        # Use secret for password storage
                        cli_lines.append(f'username {name} privilege {priv_val} secret {pwd}')
                # Fallback when no AAA configuration provided
                if len(cli_lines) <= 1:
                    cli_lines.append('! no AAA entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'snmp':
                # Generate CLI configuration for SNMP
                communities = form_data.get('snmp_community', [])
                accesses = form_data.get('snmp_community_access', [])
                acls = form_data.get('snmp_community_acl', [])
                v3_users = form_data.get('snmp_v3_user', [])
                v3_auths = form_data.get('snmp_v3_auth', [])
                v3_auth_pwds = form_data.get('snmp_v3_auth_pwd', [])
                v3_privs = form_data.get('snmp_v3_priv', [])
                v3_priv_pwds = form_data.get('snmp_v3_priv_pwd', [])
                location = get_single('snmp_location') or ''
                contact = get_single('snmp_contact') or ''
                traps = [t for t in form_data.get('snmp_trap_server', []) if t]
                cli_lines = []
                cli_lines.append('! SNMP configuration')
                # SNMPv2 communities
                max_len = max(len(communities), len(accesses), len(acls))
                for i in range(max_len):
                    comm = communities[i] if i < len(communities) else ''
                    acc = accesses[i] if i < len(accesses) else ''
                    acl = acls[i] if i < len(acls) else ''
                    if comm:
                        line = f'snmp-server community {comm} {acc}' if acc else f'snmp-server community {comm}'
                        if acl:
                            line += f' {acl}'
                        cli_lines.append(line)
                # SNMPv3 users
                # If any v3 user is configured, define a generic group
                if v3_users:
                    group_name = 'V3GROUP'
                    cli_lines.append(f'snmp-server group {group_name} v3 priv')
                    max_v3 = max(len(v3_users), len(v3_auths), len(v3_auth_pwds), len(v3_privs), len(v3_priv_pwds))
                    for i in range(max_v3):
                        usr = v3_users[i] if i < len(v3_users) else ''
                        auth = v3_auths[i] if i < len(v3_auths) else ''
                        authpwd = v3_auth_pwds[i] if i < len(v3_auth_pwds) else ''
                        priv = v3_privs[i] if i < len(v3_privs) else ''
                        privpwd = v3_priv_pwds[i] if i < len(v3_priv_pwds) else ''
                        if usr:
                            user_line = f'snmp-server user {usr} {group_name} v3'
                            if auth and authpwd:
                                user_line += f' auth {auth} {authpwd}'
                            if priv and privpwd:
                                user_line += f' priv {priv} {privpwd}'
                            cli_lines.append(user_line)
                # Location and contact
                if location:
                    cli_lines.append(f'snmp-server location {location}')
                if contact:
                    cli_lines.append(f'snmp-server contact {contact}')
                # Trap servers
                for trap in traps:
                    cli_lines.append(f'snmp-server host {trap}')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no SNMP entries provided')
                entry = "\n".join(cli_lines)
            elif slug == 'syslog':
                # Generate CLI configuration for Syslog
                ips = form_data.get('syslog_server_ip', [])
                ports = form_data.get('syslog_server_port', [])
                lvls = form_data.get('syslog_server_level', [])
                cli_lines = []
                cli_lines.append('! Syslog configuration')
                max_len = max(len(ips), len(ports), len(lvls))
                for i in range(max_len):
                    ip = ips[i] if i < len(ips) else ''
                    port = ports[i] if i < len(ports) else ''
                    # We don't use level per-server; logging level will be set globally
                    if ip:
                        if port:
                            cli_lines.append(f'logging host {ip} {port}')
                        else:
                            cli_lines.append(f'logging host {ip}')
                # Console logging
                if 'syslog_console_enable' in form_data:
                    console_lvl = get_single('syslog_console_level') or ''
                    if console_lvl:
                        cli_lines.append(f'logging console {console_lvl}')
                    else:
                        cli_lines.append('logging console')
                # Buffered logging
                if 'syslog_buffer_enable' in form_data:
                    buffer_lvl = get_single('syslog_buffer_level') or ''
                    buffer_size = get_single('syslog_buffer_size') or ''
                    if buffer_lvl and buffer_size:
                        cli_lines.append(f'logging buffered {buffer_lvl} {buffer_size}')
                    elif buffer_lvl:
                        cli_lines.append(f'logging buffered {buffer_lvl}')
                    elif buffer_size:
                        cli_lines.append(f'logging buffered {buffer_size}')
                    else:
                        cli_lines.append('logging buffered')
                # Monitor logging
                if 'syslog_monitor_enable' in form_data:
                    monitor_lvl = get_single('syslog_monitor_level') or ''
                    if monitor_lvl:
                        cli_lines.append(f'logging monitor {monitor_lvl}')
                    else:
                        cli_lines.append('logging monitor')
                if len(cli_lines) <= 1:
                    cli_lines.append('! no syslog entries provided')
                entry = "\n".join(cli_lines)
            else:
                # Default case: just dump form key/values
                kvs = [f"{k}={v}" for k, v in form_data.items()]
                entry += "; ".join(kvs)

            # Determine filename based on device if provided
            filename = 'generated_config'
            if device:
                # sanitise device name
                safe_device = device.lower().replace(' ', '_')
                filename = f"{safe_device}_config"
            file_path = os.path.join(data_dir, f"{filename}.txt")
            # Write to file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(entry + "\n")

            # Redirect back to GET view after adding, preserving device param
            return redirect(url_for('protocol_page', slug=slug, device=device))

        # GET: render template
        template_name = template_map.get(slug)
        if template_name:
            return render_template(template_name, slug=slug, device=device)
        # Fallback page if protocol not implemented
        return render_template('protocol_coming_soon.html', slug=slug, device=device)

    @app.route('/generated-config/<device>')
    def show_generated_config(device: str) -> str:
        """Display all configurations that have been added for the given device."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        # Determine filename based on device
        safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
        filename = f"{safe_device}_config.txt"
        file_path = os.path.join(data_dir, filename)
        # Read file if exists
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = ''
        return render_template('generated_config.html', content=content, device=device)

    @app.route('/clear-config/<device>', methods=['POST'])
    def clear_config(device: str) -> str:
        """Clear (empty) the generated configuration file for the given device."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
        file_path = os.path.join(data_dir, f"{safe_device}_config.txt")
        # Truncate the file if it exists
        try:
            with open(file_path, 'w', encoding='utf-8'):
                pass
        except Exception:
            # Ignore errors (file may not exist)
            pass
        return redirect(url_for('show_generated_config', device=device))

    @app.route('/download-config/<device>')
    def download_config(device: str):
        """Send the generated configuration file for the device as a downloadable attachment."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        safe_device = device.lower().replace(' ', '_') if device else 'generated_config'
        file_path = os.path.join(data_dir, f"{safe_device}_config.txt")
        # If file does not exist, create an empty one for download
        if not os.path.exists(file_path):
            open(file_path, 'w', encoding='utf-8').close()
        return send_file(file_path, as_attachment=True, download_name=f"{safe_device}_config.txt", mimetype='text/plain')

    @app.route('/troubleshoot/<slug>')
    def troubleshoot(slug: str) -> str:
        """
        Display troubleshooting commands for a given protocol slug.  The ``device``
        query parameter (if provided) is used for back navigation so the user can
        return to the protocol configuration page.  If no commands are defined
        for the slug, the template will display an informative message.
        """
        device = request.args.get('device', 'router')
        commands = troubleshoot_commands.get(slug)
        return render_template('protocol_troubleshoot.html', slug=slug, commands=commands, device=device)

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)