"""
Unit tests for validation helpers.

These tests ensure that IP address and VLAN ID validators behave as
expected.
"""

import unittest
from utils.validators import is_valid_ipv4, is_valid_vlan_id


class TestValidators(unittest.TestCase):
    def test_ipv4_validator(self):
        self.assertTrue(is_valid_ipv4('192.168.0.1'))
        self.assertFalse(is_valid_ipv4('999.999.999.999'))

    def test_vlan_id(self):
        self.assertTrue(is_valid_vlan_id(100))
        self.assertFalse(is_valid_vlan_id(5000))


if __name__ == '__main__':
    unittest.main()