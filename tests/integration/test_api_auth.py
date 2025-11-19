"""
Integration tests for authentication API.
"""
import pytest


class TestAuthAPI:
    """Tests for authentication endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'healthy'

    def test_register_user(self, client, organization):
        """Test user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'organization_name': organization.name
        })

        assert response.status_code == 201
        data = response.json
        assert data['user']['email'] == 'newuser@example.com'
        assert data['user']['username'] == 'newuser'
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_register_duplicate_email(self, client, user):
        """Test registration with duplicate email."""
        response = client.post('/api/auth/register', json={
            'email': user.email,
            'username': 'differentuser',
            'password': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User',
            'organization_name': 'Test Org'
        })

        assert response.status_code == 400
        assert 'already exists' in response.json['error'].lower()

    def test_login_success(self, client, user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'username': user.username,
            'password': 'testpassword123'
        })

        assert response.status_code == 200
        data = response.json
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == user.username

    def test_login_invalid_credentials(self, client, user):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'username': user.username,
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        assert 'invalid' in response.json['error'].lower()

    def test_get_current_user(self, client, user, auth_headers):
        """Test getting current user info."""
        response = client.get('/api/auth/me', headers=auth_headers)

        assert response.status_code == 200
        data = response.json
        assert data['username'] == user.username
        assert data['email'] == user.email

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401

    def test_refresh_token(self, client, user):
        """Test token refresh."""
        # Login to get refresh token
        login_response = client.post('/api/auth/login', json={
            'username': user.username,
            'password': 'testpassword123'
        })
        refresh_token = login_response.json['refresh_token']

        # Refresh token
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })

        assert response.status_code == 200
        assert 'access_token' in response.json
