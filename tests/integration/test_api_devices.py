"""
Integration tests for device API.
"""
import pytest


class TestDeviceAPI:
    """Tests for device endpoints."""

    def test_get_devices(self, client, auth_headers, device):
        """Test getting all devices."""
        response = client.get('/api/devices', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert len(data) == 1
        assert data[0]['hostname'] == device.hostname

    def test_get_devices_unauthorized(self, client, device):
        """Test getting devices without auth."""
        response = client.get('/api/devices')
        assert response.status_code == 401

    def test_get_device_by_id(self, client, auth_headers, device):
        """Test getting specific device."""
        response = client.get(f'/api/devices/{device.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert data['id'] == device.id
        assert data['hostname'] == device.hostname

    def test_create_device(self, client, auth_headers):
        """Test creating a new device."""
        response = client.post('/api/devices', headers=auth_headers, json={
            'hostname': 'new-router',
            'ip_address': '10.0.0.1',
            'platform': 'ios',
            'device_type': 'router',
            'location': 'Data Center 1'
        })

        assert response.status_code == 201
        data = response.json
        assert data['hostname'] == 'new-router'
        assert data['ip_address'] == '10.0.0.1'

    def test_create_device_invalid_data(self, client, auth_headers):
        """Test creating device with invalid data."""
        response = client.post('/api/devices', headers=auth_headers, json={
            'hostname': 'router1',
            'ip_address': 'invalid-ip',  # Invalid IP
            'platform': 'ios',
            'device_type': 'router'
        })

        assert response.status_code == 400

    def test_update_device(self, client, auth_headers, device):
        """Test updating a device."""
        response = client.put(f'/api/devices/{device.id}', headers=auth_headers, json={
            'location': 'Updated Location',
            'model': 'Cisco ISR 4451'
        })

        assert response.status_code == 200
        data = response.json
        assert data['location'] == 'Updated Location'
        assert data['model'] == 'Cisco ISR 4451'

    def test_delete_device(self, client, auth_headers, device):
        """Test deleting a device."""
        response = client.delete(f'/api/devices/{device.id}', headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f'/api/devices/{device.id}', headers=auth_headers)
        assert response.status_code == 404

    def test_filter_devices_by_platform(self, client, auth_headers, device):
        """Test filtering devices by platform."""
        response = client.get('/api/devices?platform=ios', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert len(data) >= 1
        assert all(d['platform'] == 'ios' for d in data)

    def test_search_devices(self, client, auth_headers, device):
        """Test searching devices."""
        response = client.get(f'/api/devices?search={device.hostname}', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert len(data) >= 1
        assert data[0]['hostname'] == device.hostname


class TestDeviceConfigAPI:
    """Tests for device configuration endpoints."""

    def test_get_device_configs(self, client, auth_headers, device, configuration):
        """Test getting device configurations."""
        response = client.get(f'/api/devices/{device.id}/configs', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert len(data) >= 1
        assert data[0]['device_id'] == device.id

    def test_create_config_version(self, client, auth_headers, device):
        """Test creating a new config version."""
        response = client.post('/api/configs', headers=auth_headers, json={
            'device_id': device.id,
            'config_text': 'hostname updated-router\n!\ninterface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n!',
            'description': 'Updated configuration'
        })

        assert response.status_code == 201
        data = response.json
        assert data['device_id'] == device.id
        assert 'hostname updated-router' in data['config_text']

    def test_get_config_by_id(self, client, auth_headers, configuration):
        """Test getting specific configuration."""
        response = client.get(f'/api/configs/{configuration.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert data['id'] == configuration.id
        assert data['device_id'] == configuration.device_id


class TestDeviceHealthCheck:
    """Tests for device health check endpoints."""

    def test_ping_device(self, client, auth_headers, device):
        """Test device ping."""
        response = client.post(f'/api/devices/{device.id}/ping', headers=auth_headers, json={
            'timeout': 5,
            'count': 4
        })

        assert response.status_code == 200
        data = response.json
        assert 'success' in data
        assert 'reachable' in data

    def test_health_check_device(self, client, auth_headers, device):
        """Test device health check."""
        response = client.post(f'/api/devices/{device.id}/health-check', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert 'device_id' in data
        assert 'status' in data
