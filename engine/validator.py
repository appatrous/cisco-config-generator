"""
Network Configuration Validator
Validates configuration data before rendering
"""

import re
import ipaddress
from typing import Dict, Any, List, Tuple, Optional


class ValidationError(Exception):
    """Custom validation error exception"""
    pass


class ConfigValidator:
    """Validates network configuration data"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, config: Dict[str, Any],
                vendor: Optional[str] = None) -> Tuple[bool, List[str], List[str]]:
        """
        Validate configuration data

        Args:
            config: Configuration dictionary
            vendor: Target vendor (optional, for vendor-specific validation)

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Global validation
        if 'global' in config:
            self._validate_global(config['global'])

        # Layer 2 validation
        if 'l2' in config:
            self._validate_l2(config['l2'], vendor)

        # Layer 3 validation
        if 'l3' in config:
            self._validate_l3(config['l3'], vendor)

        # VXLAN validation
        if 'vxlan' in config:
            self._validate_vxlan(config['vxlan'], config.get('l3', {}))

        # Cross-validation (dependencies between sections)
        self._validate_cross_references(config)

        return (len(self.errors) == 0, self.errors, self.warnings)

    def _validate_global(self, global_config: Dict[str, Any]):
        """Validate global configuration"""
        # Hostname validation
        if 'hostname' not in global_config:
            self.errors.append("Global: hostname is required")
        elif not re.match(r'^[a-zA-Z0-9\-_.]+$', global_config['hostname']):
            self.errors.append(
                f"Global: Invalid hostname '{global_config['hostname']}' "
                "(only alphanumeric, dash, underscore, dot allowed)"
            )

        # NTP servers validation
        if 'ntp_servers' in global_config:
            for ntp in global_config['ntp_servers']:
                if not self._is_valid_ip_or_hostname(ntp):
                    self.errors.append(f"Global: Invalid NTP server '{ntp}'")

        # DNS servers validation
        if 'dns_servers' in global_config:
            for dns in global_config['dns_servers']:
                if not self._is_valid_ip(dns):
                    self.errors.append(f"Global: Invalid DNS server '{dns}'")

    def _validate_l2(self, l2_config: Dict[str, Any], vendor: Optional[str]):
        """Validate Layer 2 configuration"""
        vlan_ids = set()

        # VLAN validation
        if 'vlans' in l2_config:
            for vlan in l2_config['vlans']:
                vlan_id = vlan.get('id')
                if not vlan_id:
                    self.errors.append("L2: VLAN ID is required")
                    continue

                if not (1 <= vlan_id <= 4094):
                    self.errors.append(
                        f"L2: Invalid VLAN ID {vlan_id} (must be 1-4094)"
                    )

                if vlan_id in vlan_ids:
                    self.errors.append(f"L2: Duplicate VLAN ID {vlan_id}")
                vlan_ids.add(vlan_id)

                if not vlan.get('name'):
                    self.warnings.append(f"L2: VLAN {vlan_id} has no name")

                if 'mtu' in vlan:
                    mtu = vlan['mtu']
                    if not (1500 <= mtu <= 9216):
                        self.warnings.append(
                            f"L2: VLAN {vlan_id} MTU {mtu} outside typical range (1500-9216)"
                        )

        # Trunk validation
        if 'trunks' in l2_config:
            for trunk in l2_config['trunks']:
                if not trunk.get('interface'):
                    self.errors.append("L2: Trunk interface name is required")

                if 'allowed_vlans' in trunk:
                    allowed = trunk['allowed_vlans']
                    if isinstance(allowed, list):
                        for vlan_id in allowed:
                            if vlan_id not in vlan_ids and vlan_id != 1:
                                self.warnings.append(
                                    f"L2: Trunk references non-existent VLAN {vlan_id}"
                                )

                if 'native_vlan' in trunk:
                    native = trunk['native_vlan']
                    if native not in vlan_ids and native != 1:
                        self.warnings.append(
                            f"L2: Trunk native VLAN {native} not defined"
                        )

        # STP validation
        if 'stp' in l2_config:
            stp = l2_config['stp']
            if stp.get('mode') not in [None, 'pvst', 'rapid-pvst', 'mst', 'rstp', 'stp']:
                self.errors.append(f"L2: Invalid STP mode '{stp.get('mode')}'")

            if stp.get('mode') == 'mst':
                if 'mst_config' not in stp:
                    self.errors.append("L2: MST mode requires mst_config")
                else:
                    mst = stp['mst_config']
                    if not mst.get('name'):
                        self.warnings.append("L2: MST region name not set")
                    if 'instances' in mst:
                        for inst in mst['instances']:
                            if not (0 <= inst.get('id', -1) <= 15):
                                self.errors.append(
                                    f"L2: MST instance ID {inst.get('id')} "
                                    "must be 0-15"
                                )

            # Priority validation
            if 'root_priority' in stp:
                if 'global' in stp['root_priority']:
                    priority = stp['root_priority']['global']
                    if priority % 4096 != 0 or not (0 <= priority <= 61440):
                        self.errors.append(
                            f"L2: STP priority {priority} must be multiple of 4096 "
                            "and 0-61440"
                        )

        # LAG validation
        if 'lag' in l2_config:
            bundle_ids = set()
            for lag in l2_config['lag']:
                bundle_id = lag.get('bundle_id')
                if not bundle_id:
                    self.errors.append("L2: LAG bundle_id is required")
                    continue

                if bundle_id in bundle_ids:
                    self.errors.append(f"L2: Duplicate LAG bundle ID {bundle_id}")
                bundle_ids.add(bundle_id)

                if not lag.get('members'):
                    self.errors.append(f"L2: LAG {bundle_id} has no member interfaces")

                mode = lag.get('mode', 'active')
                if mode not in ['active', 'passive', 'on']:
                    self.errors.append(f"L2: Invalid LAG mode '{mode}'")

        # MLAG validation
        if 'mlag' in l2_config:
            mlag = l2_config['mlag']
            if mlag.get('enabled'):
                if vendor == 'ios':
                    self.warnings.append(
                        "L2: MLAG not natively supported on IOS "
                        "(use StackWise or VSS instead)"
                    )
                if not mlag.get('peer_link'):
                    self.errors.append("L2: MLAG peer_link is required")
                if not mlag.get('keepalive'):
                    self.errors.append("L2: MLAG keepalive configuration required")

        # Security validation
        if 'security' in l2_config:
            self._validate_l2_security(l2_config['security'])

    def _validate_l2_security(self, security: Dict[str, Any]):
        """Validate L2 security features"""
        # DHCP snooping validation
        if 'dhcp_snooping' in security:
            ds = security['dhcp_snooping']
            if ds.get('enabled'):
                if not ds.get('vlans'):
                    self.warnings.append(
                        "L2 Security: DHCP snooping enabled but no VLANs specified"
                    )
                if not ds.get('trusted_interfaces'):
                    self.warnings.append(
                        "L2 Security: No trusted interfaces for DHCP snooping"
                    )

        # DAI validation
        if 'dai' in security:
            dai = security['dai']
            if dai.get('enabled'):
                if not dai.get('vlans'):
                    self.warnings.append(
                        "L2 Security: DAI enabled but no VLANs specified"
                    )

        # 802.1X validation
        if 'dot1x' in security:
            dot1x = security['dot1x']
            if dot1x.get('enabled'):
                if not dot1x.get('system_auth_control'):
                    self.warnings.append(
                        "L2 Security: 802.1X enabled but system-auth-control not set"
                    )

    def _validate_l3(self, l3_config: Dict[str, Any], vendor: Optional[str]):
        """Validate Layer 3 configuration"""
        vrf_names = set()

        # VRF validation
        if 'vrfs' in l3_config:
            for vrf in l3_config['vrfs']:
                name = vrf.get('name')
                if not name:
                    self.errors.append("L3: VRF name is required")
                    continue

                if name in vrf_names:
                    self.errors.append(f"L3: Duplicate VRF name '{name}'")
                vrf_names.add(name)

                if 'rd' in vrf:
                    if not self._is_valid_rd(vrf['rd']):
                        self.errors.append(f"L3: Invalid RD '{vrf['rd']}' for VRF {name}")

                for rt_list in ['rt_import', 'rt_export']:
                    if rt_list in vrf:
                        for rt in vrf[rt_list]:
                            if not self._is_valid_rt(rt):
                                self.errors.append(
                                    f"L3: Invalid RT '{rt}' in VRF {name}"
                                )

        # Interface validation
        if 'interfaces' in l3_config:
            interface_names = set()
            for iface in l3_config['interfaces']:
                name = iface.get('interface')
                if not name:
                    self.errors.append("L3: Interface name is required")
                    continue

                if name in interface_names:
                    self.errors.append(f"L3: Duplicate interface '{name}'")
                interface_names.add(name)

                # VRF reference check
                if 'vrf' in iface:
                    if iface['vrf'] not in vrf_names:
                        self.warnings.append(
                            f"L3: Interface {name} references undefined VRF '{iface['vrf']}'"
                        )

                # IP address validation
                for ip_list in ['ipv4', 'ipv6']:
                    if ip_list in iface:
                        for ip_entry in iface[ip_list]:
                            addr = ip_entry.get('address')
                            if not addr:
                                continue
                            if not self._is_valid_cidr(addr):
                                self.errors.append(
                                    f"L3: Invalid IP address '{addr}' on {name}"
                                )

                # MTU validation
                if 'mtu' in iface:
                    mtu = iface['mtu']
                    if not (64 <= mtu <= 9216):
                        self.warnings.append(
                            f"L3: Interface {name} MTU {mtu} outside typical range"
                        )

        # Static routes validation
        if 'static_routes' in l3_config:
            for route in l3_config['static_routes']:
                if not route.get('prefix'):
                    self.errors.append("L3: Static route prefix is required")
                elif not self._is_valid_cidr(route['prefix']):
                    self.errors.append(
                        f"L3: Invalid route prefix '{route['prefix']}'"
                    )

                if not route.get('next_hop'):
                    self.errors.append("L3: Static route next_hop is required")

                if 'distance' in route:
                    dist = route['distance']
                    if not (1 <= dist <= 255):
                        self.errors.append(
                            f"L3: Invalid administrative distance {dist} (must be 1-255)"
                        )

        # OSPF validation
        if 'ospf' in l3_config:
            for ospf in l3_config['ospf']:
                if not ospf.get('process_id'):
                    self.errors.append("L3: OSPF process_id is required")

                if 'router_id' in ospf:
                    if not self._is_valid_ip(ospf['router_id']):
                        self.errors.append(
                            f"L3: Invalid OSPF router-id '{ospf['router_id']}'"
                        )

        # BGP validation
        if 'bgp' in l3_config:
            bgp = l3_config['bgp']
            if not bgp.get('asn'):
                self.errors.append("L3: BGP ASN is required")
            elif not (1 <= bgp['asn'] <= 4294967295):
                self.errors.append(
                    f"L3: Invalid BGP ASN {bgp['asn']} (must be 1-4294967295)"
                )

            if 'router_id' in bgp:
                if not self._is_valid_ip(bgp['router_id']):
                    self.errors.append(f"L3: Invalid BGP router-id '{bgp['router_id']}'")

            # Neighbor validation
            if 'neighbors' in bgp:
                for neighbor in bgp['neighbors']:
                    if not neighbor.get('ip'):
                        self.errors.append("L3: BGP neighbor IP is required")
                    elif not self._is_valid_ip(neighbor['ip']):
                        self.errors.append(
                            f"L3: Invalid BGP neighbor IP '{neighbor['ip']}'"
                        )

                    if not neighbor.get('remote_as'):
                        self.errors.append(
                            f"L3: BGP neighbor {neighbor.get('ip')} "
                            "missing remote-as"
                        )

    def _validate_vxlan(self, vxlan_config: Dict[str, Any],
                       l3_config: Dict[str, Any]):
        """Validate VXLAN configuration"""
        if not vxlan_config.get('enabled'):
            return

        if 'vtep' not in vxlan_config:
            self.errors.append("VXLAN: VTEP configuration is required")
        elif not vxlan_config['vtep'].get('source_interface'):
            self.errors.append("VXLAN: VTEP source_interface is required")

        # L2VNI validation
        vni_ids = set()
        if 'l2vnis' in vxlan_config:
            for l2vni in vxlan_config['l2vnis']:
                vni = l2vni.get('vni')
                if not vni:
                    self.errors.append("VXLAN: L2VNI vni is required")
                    continue

                if vni in vni_ids:
                    self.errors.append(f"VXLAN: Duplicate VNI {vni}")
                vni_ids.add(vni)

                if not (1 <= vni <= 16777215):
                    self.errors.append(f"VXLAN: Invalid VNI {vni} (1-16777215)")

        # L3VNI validation
        if 'l3vnis' in vxlan_config:
            vrf_names = {vrf['name'] for vrf in l3_config.get('vrfs', [])}
            for l3vni in vxlan_config['l3vnis']:
                vni = l3vni.get('vni')
                if not vni:
                    self.errors.append("VXLAN: L3VNI vni is required")
                    continue

                if vni in vni_ids:
                    self.errors.append(f"VXLAN: Duplicate VNI {vni}")
                vni_ids.add(vni)

                vrf = l3vni.get('vrf')
                if not vrf:
                    self.errors.append(f"VXLAN: L3VNI {vni} missing VRF")
                elif vrf not in vrf_names:
                    self.errors.append(
                        f"VXLAN: L3VNI {vni} references undefined VRF '{vrf}'"
                    )

    def _validate_cross_references(self, config: Dict[str, Any]):
        """Validate cross-references between configuration sections"""
        # Check that VRFs referenced in routing protocols are defined
        vrf_names = set()
        if 'l3' in config and 'vrfs' in config['l3']:
            vrf_names = {vrf['name'] for vrf in config['l3']['vrfs']}

        if 'l3' in config:
            # OSPF VRF references
            if 'ospf' in config['l3']:
                for ospf in config['l3']['ospf']:
                    if 'vrf' in ospf and ospf['vrf'] not in vrf_names:
                        self.warnings.append(
                            f"L3: OSPF references undefined VRF '{ospf['vrf']}'"
                        )

    # Helper validation methods
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is valid IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _is_valid_cidr(self, cidr: str) -> bool:
        """Check if string is valid CIDR notation"""
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False

    def _is_valid_ip_or_hostname(self, value: str) -> bool:
        """Check if string is valid IP or hostname"""
        if self._is_valid_ip(value):
            return True
        # Simple hostname validation
        return re.match(r'^[a-zA-Z0-9\-_.]+$', value) is not None

    def _is_valid_rd(self, rd: str) -> bool:
        """Validate Route Distinguisher format (ASN:nn or IP:nn)"""
        pattern = r'^(\d+:\d+|(\d{1,3}\.){3}\d{1,3}:\d+)$'
        return re.match(pattern, rd) is not None

    def _is_valid_rt(self, rt: str) -> bool:
        """Validate Route Target format"""
        return self._is_valid_rd(rt)
