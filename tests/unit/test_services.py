"""
Unit tests for service layer.
"""
import pytest
from services.protocol_service import ProtocolService


class TestProtocolService:
    """Tests for ProtocolService."""

    def test_get_template_name(self):
        """Test getting template name for protocol."""
        assert ProtocolService.get_template_name('ospf') == 'protocol_ospf.html'
        assert ProtocolService.get_template_name('static-routing') == 'protocol_static_routing.html'
        assert ProtocolService.get_template_name('vlan') == 'protocol_vlan.html'
        assert ProtocolService.get_template_name('unknown') is None

    def test_generate_static_routing(self):
        """Test static routing configuration generation."""
        form_data = {
            'static_dest_network': ['192.168.1.0'],
            'static_next_hop': ['10.0.0.1'],
            'static_distance': ['']
        }
        config = ProtocolService.generate_config('static-routing', form_data)

        assert '! Static routing' in config
        assert 'ip route 192.168.1.0 10.0.0.1' in config

    def test_generate_ospf(self):
        """Test OSPF configuration generation."""
        form_data = {
            'ospf_enable': True,
            'ospf_version': ['v2'],
            'ospf_process_id': ['1'],
            'ospf_router_id': ['1.1.1.1'],
            'ospf_network': ['10.0.0.0'],
            'ospf_area': ['0']
        }
        config = ProtocolService.generate_config('ospf', form_data)

        assert '! OSPF configuration' in config
        assert 'router ospf 1' in config
        assert 'router-id 1.1.1.1' in config
        assert 'network 10.0.0.0 area 0' in config

    def test_generate_vlan(self):
        """Test VLAN configuration generation."""
        form_data = {
            'vlan_id': ['10', '20'],
            'vlan_name': ['VLAN_10', 'VLAN_20']
        }
        config = ProtocolService.generate_config('vlan', form_data)

        assert '! VLAN configuration' in config
        assert 'vlan 10' in config
        assert 'name VLAN_10' in config
        assert 'vlan 20' in config
        assert 'name VLAN_20' in config

    def test_generate_eigrp(self):
        """Test EIGRP configuration generation."""
        form_data = {
            'eigrp_as_number': ['100'],
            'eigrp_router_id': ['2.2.2.2'],
            'eigrp_network': ['192.168.0.0'],
            'eigrp_wildcard': ['0.0.255.255']
        }
        config = ProtocolService.generate_config('eigrp', form_data)

        assert '! EIGRP configuration' in config
        assert 'router eigrp 100' in config
        assert 'eigrp router-id 2.2.2.2' in config
        assert 'network 192.168.0.0 0.0.255.255' in config

    def test_generate_nat(self):
        """Test NAT configuration generation."""
        form_data = {
            'inside_local_ip': ['192.168.1.10'],
            'inside_global_ip': ['203.0.113.10']
        }
        config = ProtocolService.generate_config('static-nat', form_data)

        assert '! Static NAT' in config
        assert 'ip nat inside source static 192.168.1.10 203.0.113.10' in config

    def test_generate_ntp(self):
        """Test NTP configuration generation."""
        form_data = {
            'ntp_server': ['pool.ntp.org', 'time.google.com'],
            'ntp_source': ['Loopback0']
        }
        config = ProtocolService.generate_config('ntp-ptp', form_data)

        assert '! NTP configuration' in config
        assert 'ntp server pool.ntp.org' in config
        assert 'ntp server time.google.com' in config
        assert 'ntp source Loopback0' in config

    def test_generate_vtp(self):
        """Test VTP configuration generation."""
        form_data = {
            'vtp_mode': ['server'],
            'vtp_domain': ['CISCO'],
            'vtp_password': ['cisco123'],
            'vtp_version': ['2']
        }
        config = ProtocolService.generate_config('vtp', form_data)

        assert '! VTP configuration' in config
        assert 'vtp mode server' in config
        assert 'vtp domain CISCO' in config
        assert 'vtp password cisco123' in config
        assert 'vtp version 2' in config

    def test_generate_vtp_minimal(self):
        """Test VTP with minimal configuration."""
        form_data = {
            'vtp_mode': ['client']
        }
        config = ProtocolService.generate_config('vtp', form_data)

        assert '! VTP configuration' in config
        assert 'vtp mode client' in config

    def test_generate_dhcp_snooping(self):
        """Test DHCP Snooping configuration generation."""
        form_data = {
            'dhcp_snoop_vlans': ['10,20,30'],
            'dhcp_snoop_trusted_interfaces': ['GigabitEthernet0/1, GigabitEthernet0/2'],
            'dhcp_snoop_rate_limit': ['100'],
            'dhcp_snoop_option82': True
        }
        config = ProtocolService.generate_config('dhcp-snooping', form_data)

        assert '! DHCP Snooping configuration' in config
        assert 'ip dhcp snooping' in config
        assert 'ip dhcp snooping vlan 10,20,30' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip dhcp snooping trust' in config
        assert 'interface GigabitEthernet0/2' in config
        assert 'ip dhcp snooping information option' in config
        assert 'ip dhcp snooping limit rate 100' in config

    def test_generate_dhcp_snooping_without_option82(self):
        """Test DHCP Snooping without Option 82."""
        form_data = {
            'dhcp_snoop_vlans': ['10'],
            'dhcp_snoop_trusted_interfaces': ['GigabitEthernet0/1']
        }
        config = ProtocolService.generate_config('dhcp-snooping', form_data)

        assert '! DHCP Snooping configuration' in config
        assert 'ip dhcp snooping' in config
        assert 'ip dhcp snooping information option' not in config

    def test_generate_dai(self):
        """Test Dynamic ARP Inspection configuration generation."""
        form_data = {
            'dai_vlans': ['10,20'],
            'dai_trusted_interfaces': ['GigabitEthernet0/1, GigabitEthernet0/2'],
            'dai_rate_limit': ['15'],
            'dai_validate': ['src-mac', 'dst-mac', 'ip']
        }
        config = ProtocolService.generate_config('dynamic-arp-inspection', form_data)

        assert '! Dynamic ARP Inspection configuration' in config
        assert 'ip arp inspection vlan 10,20' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip arp inspection trust' in config
        assert 'interface GigabitEthernet0/2' in config
        assert 'ip arp inspection limit rate 15' in config
        assert 'ip arp inspection validate src-mac dst-mac ip' in config

    def test_generate_dai_minimal(self):
        """Test DAI with minimal configuration."""
        form_data = {
            'dai_vlans': ['10']
        }
        config = ProtocolService.generate_config('dynamic-arp-inspection', form_data)

        assert '! Dynamic ARP Inspection configuration' in config
        assert 'ip arp inspection vlan 10' in config

    def test_generate_ip_source_guard(self):
        """Test IP Source Guard configuration generation."""
        form_data = {
            'ipsg_interfaces': ['GigabitEthernet0/1', 'GigabitEthernet0/2'],
            'ipsg_mode': ['ip-mac', 'ip']
        }
        config = ProtocolService.generate_config('ip-source-guard', form_data)

        assert '! IP Source Guard configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip verify source port-security' in config
        assert 'interface GigabitEthernet0/2' in config
        assert 'ip verify source' in config

    def test_generate_ip_source_guard_single_mode(self):
        """Test IP Source Guard with single interface."""
        form_data = {
            'ipsg_interfaces': ['GigabitEthernet0/1'],
            'ipsg_mode': ['ip']
        }
        config = ProtocolService.generate_config('ip-source-guard', form_data)

        assert '! IP Source Guard configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip verify source' in config
        assert 'port-security' not in config

    def test_generate_igmp_snooping(self):
        """Test IGMP Snooping configuration generation."""
        form_data = {
            'igmp_snoop_vlans': ['10,20'],
            'igmp_snoop_version': ['2'],
            'igmp_snoop_querier': ['querier'],
            'igmp_snoop_fast_leave': True
        }
        config = ProtocolService.generate_config('igmp-snooping', form_data)

        assert '! IGMP Snooping configuration' in config
        assert 'ip igmp snooping' in config
        assert 'ip igmp snooping vlan 10,20' in config
        assert 'ip igmp snooping vlan 10,20 querier' in config
        assert 'ip igmp snooping vlan 10,20 immediate-leave' in config

    def test_generate_igmp_snooping_minimal(self):
        """Test IGMP Snooping with minimal configuration."""
        form_data = {}
        config = ProtocolService.generate_config('igmp-snooping', form_data)

        assert '! IGMP Snooping configuration' in config
        assert 'ip igmp snooping' in config

    def test_generate_private_vlan(self):
        """Test Private VLAN configuration generation."""
        form_data = {
            'pvlan_primary': ['100', '100'],
            'pvlan_secondary': ['101', '102'],
            'pvlan_type': ['isolated', 'community']
        }
        config = ProtocolService.generate_config('private-vlan', form_data)

        assert '! Private VLAN configuration' in config
        assert 'vlan 100' in config
        assert 'private-vlan primary' in config
        assert 'vlan 101' in config
        assert 'private-vlan isolated' in config
        assert 'vlan 102' in config
        assert 'private-vlan community' in config
        assert 'private-vlan association 101,102' in config

    def test_generate_private_vlan_single(self):
        """Test Private VLAN with single secondary."""
        form_data = {
            'pvlan_primary': ['100'],
            'pvlan_secondary': ['101'],
            'pvlan_type': ['isolated']
        }
        config = ProtocolService.generate_config('private-vlan', form_data)

        assert '! Private VLAN configuration' in config
        assert 'vlan 100' in config
        assert 'private-vlan primary' in config
        assert 'vlan 101' in config
        assert 'private-vlan isolated' in config
        assert 'private-vlan association 101' in config

    def test_generate_voice_vlan(self):
        """Test Voice VLAN configuration generation."""
        form_data = {
            'voice_vlan_id': ['10'],
            'voice_vlan_interfaces': ['GigabitEthernet0/1, GigabitEthernet0/2'],
            'voice_vlan_qos_trust': ['cos'],
            'voice_vlan_auto_qos': True
        }
        config = ProtocolService.generate_config('voice-vlan', form_data)

        assert '! Voice VLAN configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'switchport voice vlan 10' in config
        assert 'mls qos trust cos' in config
        assert 'auto qos voip cisco-phone' in config
        assert 'interface GigabitEthernet0/2' in config

    def test_generate_voice_vlan_minimal(self):
        """Test Voice VLAN with minimal configuration."""
        form_data = {
            'voice_vlan_id': ['20'],
            'voice_vlan_interfaces': ['GigabitEthernet0/1']
        }
        config = ProtocolService.generate_config('voice-vlan', form_data)

        assert '! Voice VLAN configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'switchport voice vlan 20' in config
        assert 'auto qos' not in config

    def test_generate_bgp(self):
        """Test BGP configuration generation."""
        form_data = {
            'bgp_as_number': ['65000'],
            'bgp_router_id': ['1.1.1.1'],
            'bgp_neighbor': ['10.0.0.1', '10.0.0.2'],
            'bgp_remote_as': ['65001', '65002'],
            'bgp_network': ['192.168.1.0', '192.168.2.0'],
            'bgp_mask': ['255.255.255.0', '255.255.255.0']
        }
        config = ProtocolService.generate_config('bgp', form_data)

        assert '! BGP configuration' in config
        assert 'router bgp 65000' in config
        assert 'bgp router-id 1.1.1.1' in config
        assert 'neighbor 10.0.0.1 remote-as 65001' in config
        assert 'neighbor 10.0.0.1 activate' in config
        assert 'neighbor 10.0.0.2 remote-as 65002' in config
        assert 'network 192.168.1.0 mask 255.255.255.0' in config
        assert 'network 192.168.2.0 mask 255.255.255.0' in config

    def test_generate_bgp_minimal(self):
        """Test BGP with minimal configuration."""
        form_data = {
            'bgp_as_number': ['65000']
        }
        config = ProtocolService.generate_config('bgp', form_data)

        assert '! BGP configuration' in config
        assert 'router bgp 65000' in config

    def test_generate_acl(self):
        """Test ACL configuration generation."""
        form_data = {
            'acl_action': ['permit', 'deny'],
            'acl_protocol': ['tcp', 'ip'],
            'acl_src': ['192.168.1.0 0.0.0.255', 'any'],
            'acl_dst': ['any', '10.0.0.0 0.255.255.255']
        }
        config = ProtocolService.generate_config('acl', form_data)

        assert '! Access Control List' in config
        assert 'ip access-list extended ACL_1' in config
        assert '10 permit tcp 192.168.1.0 0.0.0.255 any' in config
        assert '20 deny ip any 10.0.0.0 0.255.255.255' in config

    def test_generate_acl_empty(self):
        """Test ACL with no entries."""
        form_data = {}
        config = ProtocolService.generate_config('acl', form_data)

        assert '! Access Control List' in config
        assert 'no ACL entries provided' in config

    def test_generate_aaa_tacacs(self):
        """Test AAA with TACACS+ configuration."""
        form_data = {
            'aaa_use_tacacs': True,
            'tacacs_server': ['10.0.0.10', '10.0.0.11'],
            'local_user_name': ['admin'],
            'local_user_password': ['cisco123'],
            'local_user_priv': ['15']
        }
        config = ProtocolService.generate_config('aaa', form_data)

        assert '! AAA configuration' in config
        assert 'aaa new-model' in config
        assert 'tacacs-server host 10.0.0.10' in config
        assert 'tacacs-server host 10.0.0.11' in config
        assert 'aaa authentication login default group tacacs+ local' in config
        assert 'username admin privilege 15 secret cisco123' in config

    def test_generate_aaa_radius(self):
        """Test AAA with RADIUS configuration."""
        form_data = {
            'aaa_use_radius': True,
            'radius_server': ['10.0.0.20']
        }
        config = ProtocolService.generate_config('aaa', form_data)

        assert '! AAA configuration' in config
        assert 'aaa new-model' in config
        assert 'radius-server host 10.0.0.20' in config
        assert 'aaa authentication login default group radius local' in config

    def test_generate_aaa_local_only(self):
        """Test AAA with local users only."""
        form_data = {
            'local_user_name': ['user1', 'user2'],
            'local_user_password': ['pass1', 'pass2'],
            'local_user_priv': ['10', '']
        }
        config = ProtocolService.generate_config('aaa', form_data)

        assert '! AAA configuration' in config
        assert 'aaa new-model' in config
        assert 'username user1 privilege 10 secret pass1' in config
        assert 'username user2 privilege 15 secret pass2' in config

    def test_generate_snmp_v2(self):
        """Test SNMP v2 configuration."""
        form_data = {
            'snmp_community': ['public', 'private'],
            'snmp_community_access': ['RO', 'RW'],
            'snmp_community_acl': ['10', '20'],
            'snmp_location': ['Data Center 1'],
            'snmp_contact': ['admin@example.com'],
            'snmp_trap_server': ['10.0.0.100']
        }
        config = ProtocolService.generate_config('snmp', form_data)

        assert '! SNMP configuration' in config
        assert 'snmp-server community public RO 10' in config
        assert 'snmp-server community private RW 20' in config
        assert 'snmp-server location Data Center 1' in config
        assert 'snmp-server contact admin@example.com' in config
        assert 'snmp-server host 10.0.0.100' in config

    def test_generate_snmp_v3(self):
        """Test SNMP v3 configuration."""
        form_data = {
            'snmp_v3_user': ['snmpuser'],
            'snmp_v3_auth': ['sha'],
            'snmp_v3_auth_pwd': ['authpass123'],
            'snmp_v3_priv': ['aes128'],
            'snmp_v3_priv_pwd': ['privpass123']
        }
        config = ProtocolService.generate_config('snmp', form_data)

        assert '! SNMP configuration' in config
        assert 'snmp-server group V3GROUP v3 priv' in config
        assert 'snmp-server user snmpuser V3GROUP v3 auth sha authpass123 priv aes128 privpass123' in config

    def test_generate_syslog(self):
        """Test Syslog configuration generation."""
        form_data = {
            'syslog_server_ip': ['10.0.0.50', '10.0.0.51'],
            'syslog_server_port': ['514', ''],
            'syslog_console_enable': True,
            'syslog_console_level': ['informational'],
            'syslog_buffer_enable': True,
            'syslog_buffer_level': ['debugging'],
            'syslog_buffer_size': ['8192']
        }
        config = ProtocolService.generate_config('syslog', form_data)

        assert '! Syslog configuration' in config
        assert 'logging host 10.0.0.50 514' in config
        assert 'logging host 10.0.0.51' in config
        assert 'logging console informational' in config
        assert 'logging buffered 8192 debugging' in config

    def test_generate_syslog_minimal(self):
        """Test Syslog with minimal configuration."""
        form_data = {
            'syslog_server_ip': ['10.0.0.50']
        }
        config = ProtocolService.generate_config('syslog', form_data)

        assert '! Syslog configuration' in config
        assert 'logging host 10.0.0.50' in config

    def test_generate_stp(self):
        """Test STP configuration generation."""
        form_data = {
            'stp_mode': ['rapid-pvst'],
            'stp_priority': ['4096']
        }
        config = ProtocolService.generate_config('stp', form_data)

        assert '! Spanning Tree configuration' in config
        assert 'spanning-tree mode rapid-pvst' in config
        assert 'spanning-tree priority 4096' in config

    def test_generate_stp_minimal(self):
        """Test STP with mode only."""
        form_data = {
            'stp_mode': ['pvst']
        }
        config = ProtocolService.generate_config('stp', form_data)

        assert '! Spanning Tree configuration' in config
        assert 'spanning-tree mode pvst' in config

    def test_generate_qos(self):
        """Test QoS configuration generation."""
        form_data = {
            'qos_class_name': ['VOICE', 'VIDEO', 'DATA'],
            'qos_bandwidth': ['', '2000', '1000'],
            'qos_priority': ['yes', '', ''],
            'qos_dscp': ['ef', 'af41', 'af21']
        }
        config = ProtocolService.generate_config('qos', form_data)

        assert '! QoS configuration' in config
        assert 'class-map match-any VOICE' in config
        assert 'match dscp ef' in config
        assert 'class-map match-any VIDEO' in config
        assert 'match dscp af41' in config
        assert 'policy-map QOS_POLICY' in config
        assert 'class VOICE' in config
        assert 'priority' in config
        assert 'class VIDEO' in config
        assert 'bandwidth 2000' in config
        assert 'set dscp af41' in config

    def test_generate_qos_minimal(self):
        """Test QoS with minimal configuration."""
        form_data = {
            'qos_class_name': ['VOICE'],
            'qos_dscp': ['ef']
        }
        config = ProtocolService.generate_config('qos', form_data)

        assert '! QoS configuration' in config
        assert 'class-map match-any VOICE' in config
        assert 'match dscp ef' in config

    def test_generate_vrf(self):
        """Test VRF configuration generation."""
        form_data = {
            'vrf_name': ['CUSTOMER_A', 'CUSTOMER_B'],
            'vrf_rd': ['100:1', '100:2'],
            'vrf_rt': ['100:1', '100:2']
        }
        config = ProtocolService.generate_config('vrf', form_data)

        assert '! VRF/MPLS configuration' in config
        assert 'ip vrf CUSTOMER_A' in config
        assert 'rd 100:1' in config
        assert 'route-target both 100:1' in config
        assert 'ip vrf CUSTOMER_B' in config
        assert 'rd 100:2' in config
        assert 'route-target both 100:2' in config

    def test_generate_vrf_minimal(self):
        """Test VRF with minimal configuration."""
        form_data = {
            'vrf_name': ['CUSTOMER_A']
        }
        config = ProtocolService.generate_config('vrf', form_data)

        assert '! VRF/MPLS configuration' in config
        assert 'ip vrf CUSTOMER_A' in config

    def test_generate_rip(self):
        """Test RIP configuration generation."""
        form_data = {
            'rip_version': ['2'],
            'rip_network': ['10.0.0.0', '192.168.1.0', '172.16.0.0']
        }
        config = ProtocolService.generate_config('rip', form_data)

        assert '! RIP configuration' in config
        assert 'router rip' in config
        assert 'version 2' in config
        assert 'network 10.0.0.0' in config
        assert 'network 192.168.1.0' in config
        assert 'network 172.16.0.0' in config
        assert 'no auto-summary' in config

    def test_generate_rip_minimal(self):
        """Test RIP with minimal configuration."""
        form_data = {
            'rip_network': ['10.0.0.0']
        }
        config = ProtocolService.generate_config('rip', form_data)

        assert '! RIP configuration' in config
        assert 'router rip' in config
        assert 'network 10.0.0.0' in config
        assert 'no auto-summary' in config

    def test_generate_igmp(self):
        """Test IGMP configuration generation."""
        form_data = {
            'igmp_interface': ['GigabitEthernet0/1', 'GigabitEthernet0/2'],
            'igmp_version': ['2', '3']
        }
        config = ProtocolService.generate_config('igmp', form_data)

        assert '! IGMP configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip igmp version 2' in config
        assert 'interface GigabitEthernet0/2' in config
        assert 'ip igmp version 3' in config

    def test_generate_igmp_without_version(self):
        """Test IGMP without version specification."""
        form_data = {
            'igmp_interface': ['GigabitEthernet0/1']
        }
        config = ProtocolService.generate_config('igmp', form_data)

        assert '! IGMP configuration' in config
        assert 'interface GigabitEthernet0/1' in config

    def test_generate_pim(self):
        """Test PIM configuration generation."""
        form_data = {
            'pim_mode': ['sparse'],
            'pim_interface': ['GigabitEthernet0/1', 'GigabitEthernet0/2'],
            'pim_rp_address': ['10.0.0.1'],
            'pim_group_range': ['224.0.0.0/4']
        }
        config = ProtocolService.generate_config('pim', form_data)

        assert '! PIM configuration' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip pim sparse-mode' in config
        assert 'interface GigabitEthernet0/2' in config
        assert 'ip pim rp-address 10.0.0.1 224.0.0.0/4' in config

    def test_generate_pim_rp_only(self):
        """Test PIM with RP address only."""
        form_data = {
            'pim_rp_address': ['10.0.0.1']
        }
        config = ProtocolService.generate_config('pim', form_data)

        assert '! PIM configuration' in config
        assert 'ip pim rp-address 10.0.0.1' in config

    def test_generate_multicast_routing(self):
        """Test Multicast Routing configuration generation."""
        form_data = {
            'multicast_enable': True,
            'multicast_ssm_range': ['232.0.0.0/8'],
            'multicast_rp_enable': True,
            'multicast_rp_address': ['10.0.0.1'],
            'multicast_bsr_enable': True
        }
        config = ProtocolService.generate_config('multicast-routing', form_data)

        assert '! Multicast Routing configuration' in config
        assert 'ip multicast-routing' in config
        assert 'ip pim ssm range 232.0.0.0/8' in config
        assert 'ip pim rp-address 10.0.0.1' in config
        assert 'BSR candidate configuration required' in config

    def test_generate_multicast_routing_minimal(self):
        """Test Multicast Routing with minimal configuration."""
        form_data = {
            'multicast_enable': True
        }
        config = ProtocolService.generate_config('multicast-routing', form_data)

        assert '! Multicast Routing configuration' in config
        assert 'ip multicast-routing' in config

    def test_generate_dhcp_server_relay(self):
        """Test DHCP Server/Relay configuration generation."""
        form_data = {
            'dhcp_pool_name': ['POOL1', 'POOL2'],
            'dhcp_pool_network': ['192.168.1.0 255.255.255.0', '192.168.2.0 255.255.255.0'],
            'dhcp_pool_router': ['192.168.1.1', '192.168.2.1'],
            'dhcp_pool_dns': ['8.8.8.8, 8.8.4.4', '1.1.1.1'],
            'dhcp_exclude_start': ['192.168.1.1', '192.168.2.1'],
            'dhcp_exclude_end': ['192.168.1.10', '192.168.2.10'],
            'dhcp_relay_interface': ['GigabitEthernet0/1'],
            'dhcp_relay_address': ['10.0.0.1']
        }
        config = ProtocolService.generate_config('dhcp-server-relay', form_data)

        assert '! DHCP Server/Relay configuration' in config
        assert 'ip dhcp excluded-address 192.168.1.1 192.168.1.10' in config
        assert 'ip dhcp pool POOL1' in config
        assert 'network 192.168.1.0 255.255.255.0' in config
        assert 'default-router 192.168.1.1' in config
        assert 'dns-server 8.8.8.8 8.8.4.4' in config
        assert 'ip dhcp pool POOL2' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip helper-address 10.0.0.1' in config

    def test_generate_dhcp_server_relay_minimal(self):
        """Test DHCP with minimal pool configuration."""
        form_data = {
            'dhcp_pool_name': ['POOL1'],
            'dhcp_pool_network': ['192.168.1.0 255.255.255.0']
        }
        config = ProtocolService.generate_config('dhcp-server-relay', form_data)

        assert '! DHCP Server/Relay configuration' in config
        assert 'ip dhcp pool POOL1' in config
        assert 'network 192.168.1.0 255.255.255.0' in config

    def test_generate_netflow(self):
        """Test NetFlow configuration generation."""
        form_data = {
            'netflow_collector_ip': ['10.0.0.100', '10.0.0.101'],
            'netflow_collector_port': ['9996', '9996'],
            'netflow_version': ['9', '9'],
            'netflow_interfaces': ['GigabitEthernet0/1, GigabitEthernet0/2']
        }
        config = ProtocolService.generate_config('netflow', form_data)

        assert '! NetFlow configuration' in config
        assert 'ip flow-export destination 10.0.0.100 9996' in config
        assert 'ip flow-export version 9' in config
        assert 'ip flow-export destination 10.0.0.101 9996' in config
        assert 'interface GigabitEthernet0/1' in config
        assert 'ip flow ingress' in config
        assert 'interface GigabitEthernet0/2' in config

    def test_generate_netflow_minimal(self):
        """Test NetFlow with minimal configuration."""
        form_data = {
            'netflow_collector_ip': ['10.0.0.100'],
            'netflow_collector_port': ['9996']
        }
        config = ProtocolService.generate_config('netflow', form_data)

        assert '! NetFlow configuration' in config
        assert 'ip flow-export destination 10.0.0.100 9996' in config

    def test_generate_gnoc(self):
        """Test GNOC configuration generation."""
        form_data = {
            'gnoc_param1': ['value1'],
            'gnoc_param2': ['value2']
        }
        config = ProtocolService.generate_config('gnoc', form_data)

        assert '! GNOC configuration' in config
        assert '! param1: value1' in config
        assert '! param2: value2' in config

    def test_generate_gnoc_minimal(self):
        """Test GNOC with no parameters."""
        form_data = {}
        config = ProtocolService.generate_config('gnoc', form_data)

        assert '! GNOC configuration' in config
        assert '! param1:' in config
        assert '! param2:' in config

    def test_generate_gre(self):
        """Test GRE tunnel configuration generation."""
        form_data = {
            'gre_tunnel_id': ['1', '2'],
            'gre_source': ['GigabitEthernet0/0', '10.0.0.1'],
            'gre_destination': ['203.0.113.1', '203.0.113.2'],
            'gre_tunnel_ip': ['192.168.1.1 255.255.255.252', '192.168.1.5 255.255.255.252']
        }
        config = ProtocolService.generate_config('gre', form_data)

        assert '! GRE tunnel configuration' in config
        assert 'interface Tunnel1' in config
        assert 'ip address 192.168.1.1 255.255.255.252' in config
        assert 'tunnel source GigabitEthernet0/0' in config
        assert 'tunnel destination 203.0.113.1' in config
        assert 'interface Tunnel2' in config
        assert 'ip address 192.168.1.5 255.255.255.252' in config
        assert 'tunnel source 10.0.0.1' in config
        assert 'tunnel destination 203.0.113.2' in config

    def test_generate_gre_minimal(self):
        """Test GRE with minimal configuration."""
        form_data = {
            'gre_destination': ['203.0.113.1']
        }
        config = ProtocolService.generate_config('gre', form_data)

        assert '! GRE tunnel configuration' in config
        assert 'interface Tunnel0' in config
        assert 'tunnel destination 203.0.113.1' in config

    def test_generate_ssl_vpn(self):
        """Test SSL VPN configuration generation."""
        form_data = {
            'ssl_public_ip': ['203.0.113.10'],
            'ssl_port': ['443'],
            'ssl_tunnel_group': ['SSL_VPN_GROUP'],
            'ssl_auth_method': ['RADIUS']
        }
        config = ProtocolService.generate_config('ssl-vpn', form_data)

        assert '! SSL VPN configuration' in config
        assert 'webvpn' in config
        assert 'port 443' in config
        assert 'tunnel-group SSL_VPN_GROUP type remote-access' in config
        assert 'tunnel-group SSL_VPN_GROUP general-attributes' in config
        assert 'authentication-server-group RADIUS' in config
        assert '! public IP for SSL VPN: 203.0.113.10' in config

    def test_generate_ssl_vpn_minimal(self):
        """Test SSL VPN with minimal configuration."""
        form_data = {
            'ssl_port': ['443']
        }
        config = ProtocolService.generate_config('ssl-vpn', form_data)

        assert '! SSL VPN configuration' in config
        assert 'webvpn' in config
        assert 'port 443' in config

    def test_generate_anyconnect(self):
        """Test AnyConnect VPN configuration generation."""
        form_data = {
            'anyconnect_portal_address': ['vpn.example.com'],
            'anyconnect_group_policy': ['ANYCONNECT_POLICY'],
            'anyconnect_protocol': ['ssl-client']
        }
        config = ProtocolService.generate_config('anyconnect', form_data)

        assert '! AnyConnect configuration' in config
        assert 'webvpn' in config
        assert 'url-listen vpn.example.com' in config
        assert 'anyconnect enable' in config
        assert 'group-policy ANYCONNECT_POLICY internal' in config
        assert 'group-policy ANYCONNECT_POLICY attributes' in config
        assert 'vpn-tunnel-protocol ssl-client' in config
        assert 'tunnel-group ANYCONNECT_POLICY type remote-access' in config
        assert 'tunnel-group ANYCONNECT_POLICY general-attributes' in config
        assert 'default-group-policy ANYCONNECT_POLICY' in config

    def test_generate_anyconnect_minimal(self):
        """Test AnyConnect with minimal configuration."""
        form_data = {
            'anyconnect_portal_address': ['vpn.example.com']
        }
        config = ProtocolService.generate_config('anyconnect', form_data)

        assert '! AnyConnect configuration' in config
        assert 'webvpn' in config
        assert 'url-listen vpn.example.com' in config
        assert 'anyconnect enable' in config


class TestTroubleshootUtils:
    """Tests for troubleshoot utilities."""

    def test_get_troubleshoot_commands(self):
        """Test getting troubleshoot commands."""
        from utils.troubleshoot import get_troubleshoot_commands

        # Test known protocol
        commands = get_troubleshoot_commands('ospf')
        assert 'show ip ospf' in commands
        assert 'show ip ospf neighbor' in commands

        # Test unknown protocol (should return default commands)
        commands = get_troubleshoot_commands('unknown_protocol')
        assert 'show running-config' in commands
        assert 'show version' in commands
