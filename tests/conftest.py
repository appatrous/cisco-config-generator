"""
Pytest configuration and fixtures.

This module provides common fixtures and configuration for all tests.
"""
import pytest
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_api import create_app
from extensions import db as _db
from models import Organization, User, Device, Configuration, Deployment, Credential


@pytest.fixture(scope='session')
def app():
    """
    Create application for testing.

    Yields:
        Flask: Test application instance
    """
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    # Create app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    # Create application context
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """
    Create database for testing.

    Args:
        app: Flask application

    Yields:
        SQLAlchemy: Database instance
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """
    Create test client.

    Args:
        app: Flask application
        db: Database instance

    Yields:
        FlaskClient: Test client
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def organization(db):
    """
    Create test organization.

    Args:
        db: Database instance

    Returns:
        Organization: Test organization
    """
    org = Organization(
        name="Test Organization",
        slug="test-org",
        is_active=True
    )
    db.session.add(org)
    db.session.commit()
    return org


@pytest.fixture(scope='function')
def user(db, organization):
    """
    Create test user.

    Args:
        db: Database instance
        organization: Test organization

    Returns:
        User: Test user
    """
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        is_admin=False,
        is_active=True,
        organization_id=organization.id
    )
    user.set_password("testpassword123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db, organization):
    """
    Create test admin user.

    Args:
        db: Database instance
        organization: Test organization

    Returns:
        User: Test admin user
    """
    admin = User(
        email="admin@example.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        is_admin=True,
        is_active=True,
        organization_id=organization.id
    )
    admin.set_password("adminpassword123")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture(scope='function')
def auth_headers(client, user):
    """
    Get authentication headers for test user.

    Args:
        client: Test client
        user: Test user

    Returns:
        dict: Headers with JWT token
    """
    response = client.post('/api/auth/login', json={
        'username': user.username,
        'password': 'testpassword123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def admin_headers(client, admin_user):
    """
    Get authentication headers for admin user.

    Args:
        client: Test client
        admin_user: Admin user

    Returns:
        dict: Headers with JWT token
    """
    response = client.post('/api/auth/login', json={
        'username': admin_user.username,
        'password': 'adminpassword123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def credential(db, organization):
    """
    Create test credential.

    Args:
        db: Database instance
        organization: Test organization

    Returns:
        Credential: Test credential
    """
    cred = Credential(
        name="Test Credentials",
        username="cisco",
        organization_id=organization.id
    )
    cred.set_password("cisco123")
    cred.set_enable_password("enable123")
    db.session.add(cred)
    db.session.commit()
    return cred


@pytest.fixture(scope='function')
def device(db, organization, credential):
    """
    Create test device.

    Args:
        db: Database instance
        organization: Test organization
        credential: Test credential

    Returns:
        Device: Test device
    """
    device = Device(
        hostname="test-router-1",
        ip_address="192.168.1.1",
        platform="ios",
        device_type="router",
        location="Test Lab",
        status="unknown",
        organization_id=organization.id,
        credential_id=credential.id
    )
    db.session.add(device)
    db.session.commit()
    return device


@pytest.fixture(scope='function')
def configuration(db, device):
    """
    Create test configuration.

    Args:
        db: Database instance
        device: Test device

    Returns:
        Configuration: Test configuration
    """
    config = Configuration(
        device_id=device.id,
        config_text="hostname test-router-1\n!\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n!",
        version=1,
        is_active=True,
        created_by="testuser"
    )
    db.session.add(config)
    db.session.commit()
    return config


@pytest.fixture(scope='function')
def deployment(db, device, configuration):
    """
    Create test deployment.

    Args:
        db: Database instance
        device: Test device
        configuration: Test configuration

    Returns:
        Deployment: Test deployment
    """
    deploy = Deployment(
        device_id=device.id,
        configuration_id=configuration.id,
        deployed_by="testuser",
        status="pending"
    )
    db.session.add(deploy)
    db.session.commit()
    return deploy


@pytest.fixture(scope='function')
def sample_config_data():
    """
    Sample configuration data for testing.

    Returns:
        dict: Sample configuration data
    """
    return {
        'platform': 'ios',
        'hostname': 'test-router',
        'domain_name': 'example.com',
        'static_routes': [
            {
                'network': '192.168.1.0',
                'mask': '255.255.255.0',
                'next_hop': '10.0.0.1'
            }
        ],
        'vlans': [
            {
                'vlan_id': 10,
                'name': 'VLAN_10'
            },
            {
                'vlan_id': 20,
                'name': 'VLAN_20'
            }
        ],
        'ospf': {
            'process_id': 1,
            'router_id': '1.1.1.1',
            'networks': [
                {
                    'network': '10.0.0.0',
                    'wildcard': '0.0.0.255',
                    'area': 0
                }
            ]
        }
    }
