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
