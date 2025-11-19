"""
Protocol configuration service.

Handles protocol-specific configuration generation logic.
"""
from typing import Dict, Any, List, Optional
from flask import Request


class ProtocolService:
    """Service for handling protocol-specific configuration."""

    # Mapping of protocol slugs to template filenames
    TEMPLATE_MAP = {
        'static-routing': 'protocol_static_routing.html',
        'ospf': 'protocol_ospf.html',
        'static-nat': 'protocol_static_nat.html',
        'dynamic-nat': 'protocol_dynamic_nat.html',
        'pat': 'protocol_pat.html',
        'vlan': 'protocol_vlan.html',
        'eigrp': 'protocol_eigrp.html',
        'vrrp': 'protocol_vrrp.html',
        'hsrp': 'protocol_hsrp.html',
        'glbp': 'protocol_glbp.html',
        'ntp-ptp': 'protocol_ntp.html',
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
    }

    @staticmethod
    def get_template_name(slug: str) -> Optional[str]:
        """Get the template name for a protocol slug."""
        return ProtocolService.TEMPLATE_MAP.get(slug)

    @staticmethod
    def generate_config(slug: str, form_data: Dict[str, Any]) -> str:
        """
        Generate CLI configuration for a specific protocol.

        Args:
            slug: Protocol identifier
            form_data: Form data dictionary

        Returns:
            Generated CLI configuration string
        """
        def get_single(name: str) -> Optional[str]:
            """Extract single value from form data."""
            value = form_data.get(name)
            if not value:
                return None
            return value[0] if isinstance(value, list) else value

        # Route to appropriate protocol handler
        if slug == 'static-routing':
            return ProtocolService._generate_static_routing(form_data)
        elif slug == 'ospf':
            return ProtocolService._generate_ospf(form_data, get_single)
        elif slug == 'static-nat':
            return ProtocolService._generate_static_nat(form_data, get_single)
        elif slug == 'dynamic-nat':
            return ProtocolService._generate_dynamic_nat(form_data, get_single)
        elif slug == 'pat':
            return ProtocolService._generate_pat(form_data, get_single)
        elif slug == 'vlan':
            return ProtocolService._generate_vlan(form_data)
        elif slug == 'eigrp':
            return ProtocolService._generate_eigrp(form_data, get_single)
        elif slug in ['vrrp', 'hsrp', 'glbp']:
            return ProtocolService._generate_fhrp(slug, form_data)
        elif slug == 'ntp-ptp':
            return ProtocolService._generate_ntp(form_data, get_single)
        else:
            return f"{slug}: configuration submitted"

    @staticmethod
    def _generate_static_routing(form_data: Dict[str, Any]) -> str:
        """Generate static routing configuration."""
        dests = form_data.get('static_dest_network', [])
        nhs = form_data.get('static_next_hop', [])
        dists = form_data.get('static_distance', [])

        cli_lines = ['! Static routing']
        for d, nh, dist in zip(dests, nhs, dists):
            if d and nh:
                line = f'ip route {d} {nh}'
                if dist:
                    line += f' {dist}'
                cli_lines.append(line)

        if len(cli_lines) <= 1:
            cli_lines.append('! no static routes provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_ospf(form_data: Dict[str, Any], get_single) -> str:
        """Generate OSPF configuration."""
        enabled = 'ospf_enable' in form_data
        if not enabled:
            return '! OSPF disabled'

        version = get_single('ospf_version') or 'v2'
        pid = get_single('ospf_process_id') or '1'
        rid = get_single('ospf_router_id') or ''
        nets = form_data.get('ospf_network', [])
        areas = form_data.get('ospf_area', [])

        cli_lines = ['! OSPF configuration']
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
        return "\n".join(cli_lines)

    @staticmethod
    def _generate_static_nat(form_data: Dict[str, Any], get_single) -> str:
        """Generate static NAT configuration."""
        local = get_single('inside_local_ip') or ''
        global_ip = get_single('inside_global_ip') or ''

        cli_lines = ['! Static NAT']
        if local and global_ip:
            cli_lines.append(f'ip nat inside source static {local} {global_ip}')
        else:
            cli_lines.append('! no static NAT entry provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_dynamic_nat(form_data: Dict[str, Any], get_single) -> str:
        """Generate dynamic NAT configuration."""
        inside_net = get_single('inside_network') or ''
        start_ip = get_single('pool_start_ip') or ''
        end_ip = get_single('pool_end_ip') or ''
        mask = get_single('subnet_mask') or ''

        cli_lines = ['! Dynamic NAT']
        if inside_net and start_ip and end_ip and mask:
            cli_lines.append(f'ip nat pool DYN_POOL {start_ip} {end_ip} netmask {mask}')
            cli_lines.append(f'access-list NAT_ACL permit ip {inside_net} any')
            cli_lines.append('ip nat inside source list NAT_ACL pool DYN_POOL')
        else:
            cli_lines.append('! incomplete dynamic NAT parameters provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_pat(form_data: Dict[str, Any], get_single) -> str:
        """Generate PAT configuration."""
        local_ip = get_single('inside_local_ip') or ''
        local_port = get_single('inside_local_port') or ''
        global_ip = get_single('inside_global_ip') or ''
        global_port = get_single('inside_global_port') or ''

        cli_lines = ['! Port Address Translation']
        if local_ip and local_port and global_ip and global_port:
            cli_lines.append(
                f'ip nat inside source static tcp {local_ip} {local_port} '
                f'{global_ip} {global_port}'
            )
        else:
            cli_lines.append('! incomplete PAT parameters provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_vlan(form_data: Dict[str, Any]) -> str:
        """Generate VLAN configuration."""
        vlan_ids = form_data.get('vlan_id', [])
        vlan_names = form_data.get('vlan_name', [])

        cli_lines = ['! VLAN configuration']
        for vid, name in zip(vlan_ids, vlan_names):
            if vid:
                cli_lines.append(f'vlan {vid}')
                if name:
                    cli_lines.append(f' name {name}')
                cli_lines.append(' exit')

        if not any(vlan_ids):
            cli_lines.append('! no VLANs provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_eigrp(form_data: Dict[str, Any], get_single) -> str:
        """Generate EIGRP configuration."""
        as_num = get_single('eigrp_as_number') or ''
        rid = get_single('eigrp_router_id') or ''
        variance = get_single('eigrp_variance') or ''
        passive = get_single('eigrp_passive_interfaces') or ''
        nets = form_data.get('eigrp_network', [])
        wilds = form_data.get('eigrp_wildcard', [])

        cli_lines = ['! EIGRP configuration']
        if as_num:
            cli_lines.append(f'router eigrp {as_num}')
            if rid:
                cli_lines.append(f' eigrp router-id {rid}')
            if variance:
                cli_lines.append(f' variance {variance}')
            if passive:
                for iface in [i.strip() for i in passive.split(',') if i.strip()]:
                    cli_lines.append(f' passive-interface {iface}')

            for net, wc in zip(nets, wilds):
                if net:
                    if wc:
                        cli_lines.append(f' network {net} {wc}')
                    else:
                        cli_lines.append(f' network {net}')
            cli_lines.append(' exit')
        else:
            cli_lines.append('! no EIGRP AS number provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_fhrp(protocol: str, form_data: Dict[str, Any]) -> str:
        """Generate FHRP (VRRP/HSRP/GLBP) configuration."""
        protocol_map = {
            'vrrp': ('vrrp', 'VRRP'),
            'hsrp': ('standby', 'HSRP'),
            'glbp': ('glbp', 'GLBP')
        }

        cmd, name = protocol_map.get(protocol, ('vrrp', 'FHRP'))

        gids = form_data.get(f'{protocol}_group_id', [])
        vips = form_data.get(f'{protocol}_virtual_ip', [])
        prios = form_data.get(f'{protocol}_priority', [])
        preempts = form_data.get(f'{protocol}_preempt', [])

        cli_lines = [f'! {name} configuration']
        max_len = max(len(gids), len(vips), len(prios), len(preempts))
        added = False

        for i in range(max_len):
            gid = gids[i] if i < len(gids) else ''
            vip = vips[i] if i < len(vips) else ''
            prio = prios[i] if i < len(prios) else ''
            pre = preempts[i] if i < len(preempts) else ''

            if gid and vip:
                added = True
                cli_lines.append(f'{cmd} {gid} ip {vip}')
                if prio:
                    cli_lines.append(f'{cmd} {gid} priority {prio}')
                if pre:
                    cli_lines.append(f'{cmd} {gid} preempt')

        if not added:
            cli_lines.append(f'! no {name} groups provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_ntp(form_data: Dict[str, Any], get_single) -> str:
        """Generate NTP configuration."""
        servers = form_data.get('ntp_server', [])
        source = get_single('ntp_source') or ''

        cli_lines = ['! NTP configuration']
        for srv in servers:
            if srv:
                cli_lines.append(f'ntp server {srv}')

        if source:
            cli_lines.append(f'ntp source {source}')

        if len(cli_lines) <= 1:
            cli_lines.append('! no NTP servers provided')

        return "\n".join(cli_lines)
