"""Unit tests for validation helpers."""

import os
import sys

# Ensure project root is on sys.path for module imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from utils.validators import is_valid_ipv4, is_valid_vlan_id


class TestValidators(unittest.TestCase):
    def test_ipv4_validator(self) -> None:
        self.assertTrue(is_valid_ipv4('192.168.0.1'))
        self.assertFalse(is_valid_ipv4('999.999.999.999'))

    def test_vlan_id(self) -> None:
        self.assertTrue(is_valid_vlan_id(100))
        self.assertFalse(is_valid_vlan_id(5000))


if __name__ == '__main__':
    unittest.main()
