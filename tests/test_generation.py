"""
Unit tests for configuration generation.

These tests verify that the CLI templates render correctly given
various input data.  Use pytest or unittest to execute.  The tests
here are minimal and provided as examples; extend them to cover all
features.
"""

import unittest
from utils.config_export import render_cli_config


class TestConfigGeneration(unittest.TestCase):
    def test_ios_static_route(self):
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


if __name__ == '__main__':
    unittest.main()