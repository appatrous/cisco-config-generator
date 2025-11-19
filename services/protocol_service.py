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
        # Layer 2 Security & Management
        elif slug == 'vtp':
            return ProtocolService._generate_vtp(form_data, get_single)
        elif slug == 'dhcp-snooping':
            return ProtocolService._generate_dhcp_snooping(form_data, get_single)
        elif slug == 'dynamic-arp-inspection':
            return ProtocolService._generate_dai(form_data, get_single)
        elif slug == 'ip-source-guard':
            return ProtocolService._generate_ip_source_guard(form_data)
        elif slug == 'igmp-snooping':
            return ProtocolService._generate_igmp_snooping(form_data, get_single)
        elif slug == 'private-vlan':
            return ProtocolService._generate_private_vlan(form_data)
        elif slug == 'voice-vlan':
            return ProtocolService._generate_voice_vlan(form_data)
        # Phase 2 - High Priority Protocols
        elif slug in ('bgp', 'bgp4-plus'):
            return ProtocolService._generate_bgp(form_data, get_single)
        elif slug == 'acl':
            return ProtocolService._generate_acl(form_data)
        elif slug == 'aaa':
            return ProtocolService._generate_aaa(form_data, get_single)
        elif slug == 'snmp':
            return ProtocolService._generate_snmp(form_data, get_single)
        elif slug == 'syslog':
            return ProtocolService._generate_syslog(form_data, get_single)
        elif slug in ('stp', 'pvst-plus'):
            return ProtocolService._generate_stp(form_data, get_single)
        elif slug == 'qos':
            return ProtocolService._generate_qos(form_data)
        elif slug in ('vrf', 'mpls'):
            return ProtocolService._generate_vrf(form_data)
        # Layer 3 - Multicast & Routing Protocols
        elif slug == 'rip':
            return ProtocolService._generate_rip(form_data, get_single)
        elif slug == 'igmp':
            return ProtocolService._generate_igmp(form_data)
        elif slug == 'pim':
            return ProtocolService._generate_pim(form_data, get_single)
        elif slug == 'multicast-routing':
            return ProtocolService._generate_multicast_routing(form_data, get_single)
        # Services - Network Management
        elif slug == 'dhcp-server-relay':
            return ProtocolService._generate_dhcp_server_relay(form_data, get_single)
        elif slug == 'netflow':
            return ProtocolService._generate_netflow(form_data, get_single)
        elif slug == 'gnoc':
            return ProtocolService._generate_gnoc(form_data, get_single)
        # VPN & Tunnels
        elif slug == 'gre':
            return ProtocolService._generate_gre(form_data)
        elif slug == 'ssl-vpn':
            return ProtocolService._generate_ssl_vpn(form_data, get_single)
        elif slug == 'anyconnect':
            return ProtocolService._generate_anyconnect(form_data, get_single)
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

    # ========================================================================
    # Layer 2 Security & Management Protocols
    # ========================================================================

    @staticmethod
    def _generate_vtp(form_data: Dict[str, Any], get_single) -> str:
        """Generate VTP (VLAN Trunking Protocol) configuration."""
        mode = get_single('vtp_mode') or ''
        domain = get_single('vtp_domain') or ''
        password = get_single('vtp_password') or ''
        version = get_single('vtp_version') or ''

        cli_lines = ['! VTP configuration']
        if mode:
            cli_lines.append(f'vtp mode {mode}')
        if domain:
            cli_lines.append(f'vtp domain {domain}')
        if password:
            cli_lines.append(f'vtp password {password}')
        if version:
            cli_lines.append(f'vtp version {version}')

        if len(cli_lines) <= 1:
            cli_lines.append('! no VTP configuration provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_dhcp_snooping(form_data: Dict[str, Any], get_single) -> str:
        """Generate DHCP Snooping configuration."""
        vlans = get_single('dhcp_snoop_vlans') or ''
        trusted = get_single('dhcp_snoop_trusted_interfaces') or ''
        rate = get_single('dhcp_snoop_rate_limit') or ''
        option82 = 'dhcp_snoop_option82' in form_data

        cli_lines = ['! DHCP Snooping configuration']
        cli_lines.append('ip dhcp snooping')

        if vlans:
            cli_lines.append(f'ip dhcp snooping vlan {vlans}')

        if option82:
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_dai(form_data: Dict[str, Any], get_single) -> str:
        """Generate Dynamic ARP Inspection configuration."""
        vlans = get_single('dai_vlans') or ''
        trusted = get_single('dai_trusted_interfaces') or ''
        rate = get_single('dai_rate_limit') or ''
        validate = 'dai_validate' in form_data

        cli_lines = ['! Dynamic ARP Inspection configuration']

        if vlans:
            cli_lines.append(f'ip arp inspection vlan {vlans}')

        if validate:
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_ip_source_guard(form_data: Dict[str, Any]) -> str:
        """Generate IP Source Guard configuration."""
        interfaces = form_data.get('ipsg_interface', [])
        modes = form_data.get('ipsg_mode', [])

        cli_lines = ['! IP Source Guard configuration']
        max_len = max(len(interfaces), len(modes))

        for i in range(max_len):
            iface = interfaces[i] if i < len(interfaces) else ''
            mode = modes[i] if i < len(modes) else ''

            if iface:
                cli_lines.append(f'interface {iface}')
                # Determine verification based on mode
                if mode == 'mac':
                    cli_lines.append(' ip verify source port-security')
                elif mode == 'ip-mac':
                    cli_lines.append(' ip verify source port-security')
                else:
                    cli_lines.append(' ip verify source')
                cli_lines.append(' exit')

        if len(cli_lines) <= 1:
            cli_lines.append('! no IP Source Guard entries provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_igmp_snooping(form_data: Dict[str, Any], get_single) -> str:
        """Generate IGMP Snooping configuration."""
        vlans = get_single('igmp_snoop_vlans') or ''
        version = get_single('igmp_snoop_version') or ''
        querier = 'igmp_snoop_querier' in form_data
        fast_leave = 'igmp_snoop_fast_leave' in form_data

        cli_lines = ['! IGMP Snooping configuration']
        cli_lines.append('ip igmp snooping')

        if vlans:
            cli_lines.append(f'ip igmp snooping vlan {vlans}')

            if querier:
                cli_lines.append(f'ip igmp snooping vlan {vlans} querier')

            if fast_leave:
                cli_lines.append(f'ip igmp snooping vlan {vlans} immediate-leave')

        if version:
            cli_lines.append(f'ip igmp snooping version {version}')

        # Best practice: set last-member query interval
        cli_lines.append('ip igmp snooping last-member-query-interval 1000')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_private_vlan(form_data: Dict[str, Any]) -> str:
        """Generate Private VLAN configuration."""
        primaries = form_data.get('pvlan_primary', [])
        secondaries = form_data.get('pvlan_secondary', [])
        types = form_data.get('pvlan_type', [])

        cli_lines = ['! Private VLAN configuration']

        # Build a dictionary of primary VLAN to list of (secondary, type)
        pvlan_dict = {}
        max_len = max(len(primaries), len(secondaries), len(types))

        for i in range(max_len):
            prim = primaries[i] if i < len(primaries) else ''
            sec = secondaries[i] if i < len(secondaries) else ''
            pvlan_type = types[i] if i < len(types) else ''

            if prim and sec:
                pvlan_dict.setdefault(prim, []).append((sec, pvlan_type))

        for prim, sec_list in pvlan_dict.items():
            # Define primary VLAN
            cli_lines.append(f'vlan {prim}')
            cli_lines.append(' private-vlan primary')
            cli_lines.append(' exit')

            # Define each secondary VLAN and type
            for sec, pvlan_type in sec_list:
                cli_lines.append(f'vlan {sec}')
                if pvlan_type and pvlan_type.lower() == 'community':
                    cli_lines.append(' private-vlan community')
                else:
                    cli_lines.append(' private-vlan isolated')
                cli_lines.append(' exit')

            # Associate secondary VLANs with primary
            cli_lines.append(f'vlan {prim}')
            sec_ids = ','.join([sec for sec, _ in sec_list])
            cli_lines.append(f' private-vlan association {sec_ids}')
            cli_lines.append(' exit')

        if len(cli_lines) <= 1:
            cli_lines.append('! no Private VLANs provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_voice_vlan(form_data: Dict[str, Any]) -> str:
        """Generate Voice VLAN configuration."""
        interfaces = form_data.get('voice_interface', [])
        vlans = form_data.get('voice_vlan_id', [])
        qos = form_data.get('voice_qos_trust', [])

        cli_lines = ['! Voice VLAN configuration']
        max_len = max(len(interfaces), len(vlans), len(qos))

        for i in range(max_len):
            iface = interfaces[i] if i < len(interfaces) else ''
            vlan_id = vlans[i] if i < len(vlans) else ''
            qos_trust = qos[i] if i < len(qos) else ''

            if iface and vlan_id:
                cli_lines.append(f'interface {iface}')
                cli_lines.append(' switchport mode access')
                cli_lines.append(f' switchport voice vlan {vlan_id}')

                # QoS trust if specified
                if qos_trust:
                    cli_lines.append(f' mls qos trust {qos_trust}')

                # Auto QoS voice for best practice
                cli_lines.append(' auto qos voip cisco-phone')
                cli_lines.append(' exit')

        if len(cli_lines) <= 1:
            cli_lines.append('! no voice VLANs provided')

        return "\n".join(cli_lines)

    # ========================================================================
    # Phase 2 - High Priority Protocols
    # ========================================================================

    @staticmethod
    def _generate_bgp(form_data: Dict[str, Any], get_single) -> str:
        """Generate BGP (Border Gateway Protocol) configuration."""
        as_number = get_single('bgp_as_number') or ''
        router_id = get_single('bgp_router_id') or ''
        neighbors = form_data.get('bgp_neighbor', [])
        remote_as = form_data.get('bgp_remote_as', [])
        networks = form_data.get('bgp_network', [])
        masks = form_data.get('bgp_mask', [])

        cli_lines = ['! BGP configuration']

        if as_number:
            cli_lines.append(f'router bgp {as_number}')

            if router_id:
                cli_lines.append(f' bgp router-id {router_id}')

            # Add BGP neighbors
            max_neighbors = max(len(neighbors), len(remote_as))
            for i in range(max_neighbors):
                neighbor = neighbors[i] if i < len(neighbors) else ''
                r_as = remote_as[i] if i < len(remote_as) else ''
                if neighbor and r_as:
                    cli_lines.append(f' neighbor {neighbor} remote-as {r_as}')
                    cli_lines.append(f' neighbor {neighbor} activate')

            # Add BGP networks
            max_networks = max(len(networks), len(masks))
            for i in range(max_networks):
                network = networks[i] if i < len(networks) else ''
                mask = masks[i] if i < len(masks) else ''
                if network and mask:
                    cli_lines.append(f' network {network} mask {mask}')

            cli_lines.append(' exit')
        else:
            cli_lines.append('! no BGP AS number provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_acl(form_data: Dict[str, Any]) -> str:
        """Generate Access Control List configuration."""
        actions = form_data.get('acl_action', [])
        protocols = form_data.get('acl_protocol', [])
        srcs = form_data.get('acl_src', [])
        dsts = form_data.get('acl_dst', [])

        cli_lines = ['! Access Control List']
        cli_lines.append('ip access-list extended ACL_1')

        seq = 10
        added = False
        max_len = max(len(actions), len(protocols), len(srcs), len(dsts))

        for i in range(max_len):
            act = actions[i] if i < len(actions) else ''
            proto = protocols[i] if i < len(protocols) else ''
            src = srcs[i] if i < len(srcs) else ''
            dst = dsts[i] if i < len(dsts) else ''

            if src and dst:
                added = True
                line = f' {seq} {act.lower()} {proto.lower()} '
                line += f'{src} {dst}'
                cli_lines.append(line)
                seq += 10

        cli_lines.append(' exit')

        if not added:
            cli_lines.append('! no ACL entries provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_aaa(form_data: Dict[str, Any], get_single) -> str:
        """Generate AAA (Authentication, Authorization, Accounting) configuration."""
        use_tacacs = 'aaa_use_tacacs' in form_data
        tacacs_servers = [s for s in form_data.get('tacacs_server', []) if s]
        use_radius = 'aaa_use_radius' in form_data
        radius_servers = [s for s in form_data.get('radius_server', []) if s]
        user_names = form_data.get('local_user_name', [])
        user_pwds = form_data.get('local_user_password', [])
        user_privs = form_data.get('local_user_priv', [])

        cli_lines = ['! AAA configuration']

        # Enable AAA if any method is configured
        if use_tacacs or use_radius or any(u for u in user_names):
            cli_lines.append('aaa new-model')

        # TACACS+ servers and method list
        if use_tacacs and tacacs_servers:
            for ip in tacacs_servers:
                cli_lines.append(f'tacacs-server host {ip}')
            cli_lines.append('aaa authentication login default group tacacs+ local')

        # RADIUS servers and method list
        if use_radius and radius_servers:
            for ip in radius_servers:
                cli_lines.append(f'radius-server host {ip}')
            cli_lines.append('aaa authentication login default group radius local')

        # Local user accounts
        max_len = max(len(user_names), len(user_pwds), len(user_privs))
        for i in range(max_len):
            name = user_names[i] if i < len(user_names) else ''
            pwd = user_pwds[i] if i < len(user_pwds) else ''
            priv = user_privs[i] if i < len(user_privs) else ''

            if name and pwd:
                priv_val = priv or '15'
                cli_lines.append(f'username {name} privilege {priv_val} secret {pwd}')

        if len(cli_lines) <= 1:
            cli_lines.append('! no AAA entries provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_snmp(form_data: Dict[str, Any], get_single) -> str:
        """Generate SNMP (Simple Network Management Protocol) configuration."""
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

        cli_lines = ['! SNMP configuration']

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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_syslog(form_data: Dict[str, Any], get_single) -> str:
        """Generate Syslog configuration."""
        ips = form_data.get('syslog_server_ip', [])
        ports = form_data.get('syslog_server_port', [])
        console_enable = 'syslog_console_enable' in form_data
        console_lvl = get_single('syslog_console_level') or ''
        buffer_enable = 'syslog_buffer_enable' in form_data
        buffer_lvl = get_single('syslog_buffer_level') or ''
        buffer_size = get_single('syslog_buffer_size') or ''

        cli_lines = ['! Syslog configuration']

        # Syslog servers
        max_len = max(len(ips), len(ports))
        for i in range(max_len):
            ip = ips[i] if i < len(ips) else ''
            port = ports[i] if i < len(ports) else ''

            if ip:
                if port:
                    cli_lines.append(f'logging host {ip} {port}')
                else:
                    cli_lines.append(f'logging host {ip}')

        # Console logging
        if console_enable:
            if console_lvl:
                cli_lines.append(f'logging console {console_lvl}')
            else:
                cli_lines.append('logging console')

        # Buffered logging
        if buffer_enable:
            if buffer_lvl and buffer_size:
                cli_lines.append(f'logging buffered {buffer_size} {buffer_lvl}')
            elif buffer_lvl:
                cli_lines.append(f'logging buffered {buffer_lvl}')
            else:
                cli_lines.append('logging buffered')

        if len(cli_lines) <= 1:
            cli_lines.append('! no Syslog entries provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_stp(form_data: Dict[str, Any], get_single) -> str:
        """Generate STP (Spanning Tree Protocol) configuration."""
        mode = get_single('stp_mode') or ''
        priority = get_single('stp_priority') or ''

        cli_lines = ['! Spanning Tree configuration']

        if mode:
            cli_lines.append(f'spanning-tree mode {mode}')

        if priority:
            cli_lines.append(f'spanning-tree priority {priority}')

        if len(cli_lines) <= 1:
            cli_lines.append('! no STP configuration provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_qos(form_data: Dict[str, Any]) -> str:
        """Generate QoS (Quality of Service) configuration."""
        class_names = form_data.get('qos_class_name', [])
        bws = form_data.get('qos_bandwidth', [])
        prios = form_data.get('qos_priority', [])
        dscps = form_data.get('qos_dscp', [])

        cli_lines = ['! QoS configuration']
        policy_name = 'QOS_POLICY'
        added = False

        max_len = max(len(class_names), len(bws), len(prios), len(dscps))

        # Create class-maps
        for i in range(max_len):
            cn = class_names[i] if i < len(class_names) else ''
            dc = dscps[i] if i < len(dscps) else ''

            if cn:
                added = True
                cli_lines.append(f'class-map match-any {cn}')
                if dc:
                    cli_lines.append(f' match dscp {dc}')
                cli_lines.append(' exit')

        # Create policy-map
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_vrf(form_data: Dict[str, Any]) -> str:
        """Generate VRF (Virtual Routing and Forwarding) configuration."""
        names = form_data.get('vrf_name', [])
        rds = form_data.get('vrf_rd', [])
        rts = form_data.get('vrf_rt', [])

        cli_lines = ['! VRF/MPLS configuration']
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
                    cli_lines.append(f' route-target both {rt}')
                cli_lines.append(' exit')

        if not added:
            cli_lines.append('! no VRFs provided')

        return "\n".join(cli_lines)

    # ========================================================================
    # Layer 3 - Multicast & Routing Protocols
    # ========================================================================

    @staticmethod
    def _generate_rip(form_data: Dict[str, Any], get_single) -> str:
        """Generate RIP (Routing Information Protocol) configuration."""
        version = get_single('rip_version') or ''
        networks = [n for n in form_data.get('rip_network', []) if n]

        cli_lines = ['! RIP configuration']
        cli_lines.append('router rip')

        if version:
            cli_lines.append(f' version {version}')

        for net in networks:
            cli_lines.append(f' network {net}')

        cli_lines.append(' no auto-summary')
        cli_lines.append(' exit')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_igmp(form_data: Dict[str, Any]) -> str:
        """Generate IGMP (Internet Group Management Protocol) configuration."""
        interfaces = form_data.get('igmp_interface', [])
        versions = form_data.get('igmp_version', [])

        cli_lines = ['! IGMP configuration']
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_pim(form_data: Dict[str, Any], get_single) -> str:
        """Generate PIM (Protocol Independent Multicast) configuration."""
        mode = get_single('pim_mode') or ''
        interfaces = form_data.get('pim_interface', [])
        rp = get_single('pim_rp_address') or ''
        grp = get_single('pim_group_range') or ''

        cli_lines = ['! PIM configuration']
        added = False

        # Configure PIM on interfaces
        for iface in interfaces:
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_multicast_routing(form_data: Dict[str, Any], get_single) -> str:
        """Generate Multicast Routing configuration."""
        enable = 'multicast_enable' in form_data
        ssm = get_single('multicast_ssm_range') or ''
        rp_enable = 'multicast_rp_enable' in form_data
        rp_addr = get_single('multicast_rp_address') or ''
        bsr = 'multicast_bsr_enable' in form_data

        cli_lines = ['! Multicast Routing configuration']

        if enable:
            cli_lines.append('ip multicast-routing')

        if ssm:
            cli_lines.append(f'ip pim ssm range {ssm}')

        if rp_enable and rp_addr:
            cli_lines.append(f'ip pim rp-address {rp_addr}')

        if bsr:
            cli_lines.append('! BSR candidate configuration required')

        if len(cli_lines) <= 1:
            cli_lines.append('! no multicast routing entries provided')

        return "\n".join(cli_lines)

    # ========================================================================
    # Services - Network Management
    # ========================================================================

    @staticmethod
    def _generate_dhcp_server_relay(form_data: Dict[str, Any], get_single) -> str:
        """Generate DHCP Server and Relay configuration."""
        pool_names = form_data.get('dhcp_pool_name', [])
        pool_networks = form_data.get('dhcp_pool_network', [])
        pool_routers = form_data.get('dhcp_pool_router', [])
        pool_dns = form_data.get('dhcp_pool_dns', [])
        pool_excl_start = form_data.get('dhcp_exclude_start', [])
        pool_excl_end = form_data.get('dhcp_exclude_end', [])
        rel_ifaces = form_data.get('dhcp_relay_interface', [])
        rel_addrs = form_data.get('dhcp_relay_address', [])

        cli_lines = ['! DHCP Server/Relay configuration']

        # DHCP Pools
        max_len = max(len(pool_names), len(pool_networks), len(pool_routers),
                      len(pool_dns), len(pool_excl_start), len(pool_excl_end))
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

        # DHCP Relays
        relays_added = False
        for iface, addr in zip(rel_ifaces, rel_addrs):
            if iface and addr:
                relays_added = True
                cli_lines.append(f'interface {iface}')
                cli_lines.append(f' ip helper-address {addr}')
                cli_lines.append(' exit')

        if not pools_added and not relays_added:
            cli_lines.append('! no DHCP pools or relays provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_netflow(form_data: Dict[str, Any], get_single) -> str:
        """Generate NetFlow configuration."""
        collector_ips = form_data.get('netflow_collector_ip', [])
        collector_ports = form_data.get('netflow_collector_port', [])
        versions = form_data.get('netflow_version', [])
        interfaces = get_single('netflow_interfaces') or ''

        cli_lines = ['! NetFlow configuration']
        max_len = max(len(collector_ips), len(collector_ports), len(versions))
        added = False

        # NetFlow export destinations
        for i in range(max_len):
            ip = collector_ips[i] if i < len(collector_ips) else ''
            port = collector_ports[i] if i < len(collector_ports) else ''
            ver = versions[i] if i < len(versions) else ''

            if ip:
                added = True
                cli_lines.append(f'ip flow-export destination {ip} {port}')
                if ver:
                    cli_lines.append(f'ip flow-export version {ver}')

        # Enable NetFlow on interfaces
        if interfaces:
            added = True
            # Interfaces may be comma-separated
            for iface in [x.strip() for x in interfaces.split(',') if x.strip()]:
                cli_lines.append(f'interface {iface}')
                cli_lines.append(' ip flow ingress')
                cli_lines.append(' exit')

        if not added:
            cli_lines.append('! no NetFlow entries provided')

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_gnoc(form_data: Dict[str, Any], get_single) -> str:
        """Generate GNOC (Generic Network Operations Center) configuration."""
        p1 = get_single('gnoc_param1') or ''
        p2 = get_single('gnoc_param2') or ''

        cli_lines = ['! GNOC configuration']
        # Document parameters as comments since specifics are unknown
        cli_lines.append(f'! param1: {p1}')
        cli_lines.append(f'! param2: {p2}')

        return "\n".join(cli_lines)

    # ========================================================================
    # VPN & Tunnels
    # ========================================================================

    @staticmethod
    def _generate_gre(form_data: Dict[str, Any]) -> str:
        """Generate GRE (Generic Routing Encapsulation) tunnel configuration."""
        ids = form_data.get('gre_tunnel_id', [])
        srcs = form_data.get('gre_source', [])
        dests = form_data.get('gre_destination', [])
        ips = form_data.get('gre_tunnel_ip', [])

        cli_lines = ['! GRE tunnel configuration']
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_ssl_vpn(form_data: Dict[str, Any], get_single) -> str:
        """Generate SSL VPN configuration (ASA style)."""
        ip_addr = get_single('ssl_public_ip') or ''
        port = get_single('ssl_port') or ''
        tg = get_single('ssl_tunnel_group') or ''
        auth = get_single('ssl_auth_method') or ''

        cli_lines = ['! SSL VPN configuration']

        # WebVPN port configuration
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

        return "\n".join(cli_lines)

    @staticmethod
    def _generate_anyconnect(form_data: Dict[str, Any], get_single) -> str:
        """Generate AnyConnect VPN configuration (ASA style)."""
        portal = get_single('anyconnect_portal_address') or ''
        gp = get_single('anyconnect_group_policy') or ''
        proto = get_single('anyconnect_protocol') or ''

        cli_lines = ['! AnyConnect configuration']

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

        return "\n".join(cli_lines)
