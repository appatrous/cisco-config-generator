"""Unit tests for configuration generation."""

import os
import sys

# Ensure project root is on sys.path for module imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest

from utils.config_export import render_cli_config, serialize_config


class TestConfigGeneration(unittest.TestCase):
    """Validate CLI rendering and serialisation helpers."""

    def test_ios_static_route(self) -> None:
        data = {
            'platform': 'ios',
            'static_routes': [
                {'destination': '192.168.1.0/24', 'next_hop': '10.0.0.1', 'distance': None}
            ],
            'vlans': [],
            'ospf': None,
            'ntp_servers': [],
            'aaa': None,
        }
        cli = render_cli_config('ios', data)
        self.assertIn('ip route 192.168.1.0/24 10.0.0.1', cli)
        self.assertNotIn('router ospf', cli)

    def test_nxos_vlan_and_ospf(self) -> None:
        data = {
            'platform': 'nxos',
            'static_routes': [],
            'vlans': [{'id': 10, 'name': 'Users'}],
            'ospf': {
                'version': 'v2',
                'process_id': 100,
                'router_id': '1.1.1.1',
                'networks': [{'network': '10.0.0.0/24', 'area': '0'}],
            },
            'ntp_servers': ['192.0.2.10'],
            'aaa': None,
        }
        cli = render_cli_config('nxos', data)
        self.assertIn('feature vlan', cli)
        self.assertIn('vlan 10', cli)
        self.assertIn('router ospf 100', cli)
        self.assertIn('ntp server 192.0.2.10', cli)

    def test_asa_aaa_and_ntp(self) -> None:
        data = {
            'platform': 'asa',
            'static_routes': [],
            'vlans': [],
            'ospf': None,
            'ntp_servers': ['198.51.100.20'],
            'aaa': {
                'use_tacacs': True,
                'tacacs_servers': ['203.0.113.5'],
                'use_radius': False,
                'radius_servers': [],
                'local_users': [
                    {'username': 'admin', 'password': 'cisco', 'privilege': 15}
                ],
            },
        }
        cli = render_cli_config('asa', data)
        self.assertIn('ntp server 198.51.100.20', cli)
        self.assertIn('aaa-server TAC1 protocol tacacs+', cli)
        self.assertIn('username admin password cisco privilege 15', cli)

    def test_serialize_config_outputs(self) -> None:
        data = {
            'platform': 'ios',
            'static_routes': [],
            'vlans': [{'id': 20, 'name': None}],
            'ospf': None,
            'ntp_servers': [],
            'aaa': None,
        }
        json_output, yaml_output = serialize_config(data)
        self.assertIn('"platform": "ios"', json_output)
        self.assertIn('platform: ios', yaml_output)


if __name__ == '__main__':
    unittest.main()
