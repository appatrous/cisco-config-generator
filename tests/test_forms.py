"""
Unit tests for form data classes and WTForms (if used).

These tests are placeholders demonstrating where form-related
validation and behaviour tests would reside once WTForms or another
form library is integrated.
"""

import os
import sys

# Ensure project root is on sys.path for module imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest
from forms.main_form import MainFormData, StaticRoute


class TestForms(unittest.TestCase):
    def test_main_form_dataclass(self):
        form = MainFormData(platform='ios')
        form.static_routes.append(StaticRoute(destination='10.1.1.0/24', next_hop='10.0.0.1'))
        self.assertEqual(form.platform, 'ios')
        self.assertEqual(len(form.static_routes), 1)


if __name__ == '__main__':
    unittest.main()