"""
Integration tests for configuration validation API.
"""
import pytest


class TestValidationAPI:
    """Tests for validation endpoints."""

    def test_validate_config_success(self, client, auth_headers):
        """Test validating valid configuration."""
        response = client.post('/api/validate/config', headers=auth_headers, json={
            'platform': 'ios',
            'config_text': 'hostname router1\n!\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n!',
            'validation_level': 'basic'
        })

        assert response.status_code == 200
        data = response.json
        assert 'valid' in data
        assert 'syntax_errors' in data
        assert 'warnings' in data

    def test_validate_config_with_errors(self, client, auth_headers):
        """Test validating invalid configuration."""
        response = client.post('/api/validate/config', headers=auth_headers, json={
            'platform': 'ios',
            'config_text': 'invalid command here\n',
            'validation_level': 'strict'
        })

        assert response.status_code == 200
        data = response.json
        # Validation returns success but with errors in the response
        assert 'syntax_errors' in data

    def test_compare_configs(self, client, auth_headers):
        """Test configuration comparison."""
        response = client.post('/api/configs/compare-detailed', headers=auth_headers, json={
            'config1': 'hostname router1\n!\nvlan 10\n name VLAN_10\n!',
            'config2': 'hostname router2\n!\nvlan 10\n name VLAN_TEN\n!\nvlan 20\n name VLAN_20\n!',
            'comparison_type': 'unified'
        })

        assert response.status_code == 200
        data = response.json
        assert 'has_changes' in data
        assert 'additions' in data
        assert 'deletions' in data
        assert 'statistics' in data
