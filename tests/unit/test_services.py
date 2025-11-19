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
