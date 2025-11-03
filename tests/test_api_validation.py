"""Tests for API payload validation helpers."""

import os
import sys

# Ensure project root is on sys.path for module imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest

from utils.payload_validation import validate_api_payload


class TestApiValidation(unittest.TestCase):
    """Ensure payloads are normalised and validated."""

    def test_valid_payload_is_sanitised(self) -> None:
        payload = {
            'platform': 'IOS',
            'static_routes': [
                {'destination': '10.0.0.0/24', 'next_hop': '192.0.2.1', 'distance': '5'}
            ],
            'vlans': [{'id': '10', 'name': 'Users'}],
            'ntp_servers': ['198.51.100.2'],
            'ospf': {
                'version': 'v2',
                'process_id': '100',
                'router_id': '1.1.1.1',
                'networks': [{'network': '10.0.0.0/24', 'area': '0'}],
            },
            'aaa': {
                'use_tacacs': True,
                'tacacs_servers': ['203.0.113.5'],
                'use_radius': 'false',
                'radius_servers': [],
                'local_users': [
                    {'username': 'ops', 'password': 'cisco123', 'privilege': '15'}
                ],
            },
        }
        sanitised, errors = validate_api_payload(payload)
        self.assertFalse(errors)
        self.assertEqual(sanitised['platform'], 'ios')
        self.assertEqual(sanitised['static_routes'][0]['distance'], 5)
        self.assertEqual(sanitised['vlans'][0]['id'], 10)
        self.assertEqual(sanitised['aaa']['local_users'][0]['privilege'], 15)

    def test_invalid_payload_reports_errors(self) -> None:
        payload = {
            'platform': 'unknown',
            'static_routes': [{'destination': 'bad', 'next_hop': '10.0.0.1'}],
            'vlans': [{'id': 5000}],
            'ntp_servers': ['not-an-ip'],
            'ospf': {
                'version': 'v4',
                'process_id': 0,
                'router_id': '999.999.999.999',
                'networks': [{'network': 'foo', 'area': 'bar'}],
            },
            'aaa': {
                'use_tacacs': True,
                'tacacs_servers': [],
                'use_radius': True,
                'radius_servers': ['bad-ip'],
                'local_users': [{'username': '', 'password': ''}],
            },
        }
        sanitised, errors = validate_api_payload(payload)
        self.assertTrue(errors)
        self.assertIsInstance(errors, list)
        self.assertIn('platform', errors[0].lower())
        self.assertEqual(sanitised['static_routes'], [])


if __name__ == '__main__':
    unittest.main()
