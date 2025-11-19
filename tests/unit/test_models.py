"""
Unit tests for database models.
"""
import pytest
from datetime import datetime
from models import Organization, User, Device, Configuration, Deployment, Credential


class TestOrganizationModel:
    """Tests for Organization model."""

    def test_create_organization(self, db):
        """Test creating an organization."""
        org = Organization(
            name="Test Org",
            slug="test-org",
            is_active=True
        )
        db.session.add(org)
        db.session.commit()

        assert org.id is not None
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.is_active is True
        assert org.created_at is not None

    def test_organization_to_dict(self, organization):
        """Test organization serialization."""
        data = organization.to_dict()

        assert data['id'] == organization.id
        assert data['name'] == organization.name
        assert data['slug'] == organization.slug
        assert data['is_active'] == organization.is_active


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, db, organization):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            organization_id=organization.id
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password_hash is not None
        assert user.password_hash != "password123"

    def test_password_hashing(self, user):
        """Test password hashing and verification."""
        assert user.check_password("testpassword123") is True
        assert user.check_password("wrongpassword") is False

    def test_user_to_dict(self, user):
        """Test user serialization."""
        data = user.to_dict()

        assert data['id'] == user.id
        assert data['email'] == user.email
        assert data['username'] == user.username
        assert 'password_hash' not in data  # Should not expose password

    def test_admin_user(self, admin_user):
        """Test admin user."""
        assert admin_user.is_admin is True
        assert admin_user.check_password("adminpassword123") is True


class TestDeviceModel:
    """Tests for Device model."""

    def test_create_device(self, db, organization, credential):
        """Test creating a device."""
        device = Device(
            hostname="router1",
            ip_address="192.168.1.1",
            platform="ios",
            device_type="router",
            organization_id=organization.id,
            credential_id=credential.id
        )
        db.session.add(device)
        db.session.commit()

        assert device.id is not None
        assert device.hostname == "router1"
        assert device.ip_address == "192.168.1.1"
        assert device.platform == "ios"

    def test_device_relationships(self, device, configuration):
        """Test device relationships."""
        assert len(device.configurations) == 1
        assert device.configurations[0].id == configuration.id

    def test_device_to_dict(self, device):
        """Test device serialization."""
        data = device.to_dict()

        assert data['id'] == device.id
        assert data['hostname'] == device.hostname
        assert data['ip_address'] == device.ip_address
        assert data['platform'] == device.platform


class TestConfigurationModel:
    """Tests for Configuration model."""

    def test_create_configuration(self, db, device):
        """Test creating a configuration."""
        config = Configuration(
            device_id=device.id,
            config_text="hostname test\n!",
            version=1,
            is_active=True,
            created_by="testuser"
        )
        db.session.add(config)
        db.session.commit()

        assert config.id is not None
        assert config.device_id == device.id
        assert config.version == 1
        assert config.is_active is True

    def test_configuration_checksum(self, configuration):
        """Test configuration checksum generation."""
        assert configuration.checksum is not None
        assert len(configuration.checksum) == 64  # SHA256 hex length

    def test_configuration_to_dict(self, configuration):
        """Test configuration serialization."""
        data = configuration.to_dict()

        assert data['id'] == configuration.id
        assert data['device_id'] == configuration.device_id
        assert data['version'] == configuration.version


class TestDeploymentModel:
    """Tests for Deployment model."""

    def test_create_deployment(self, db, device, configuration):
        """Test creating a deployment."""
        deploy = Deployment(
            device_id=device.id,
            configuration_id=configuration.id,
            deployed_by="testuser",
            status="pending"
        )
        db.session.add(deploy)
        db.session.commit()

        assert deploy.id is not None
        assert deploy.status == "pending"
        assert deploy.deployed_by == "testuser"

    def test_deployment_status_transition(self, deployment):
        """Test deployment status transitions."""
        assert deployment.status == "pending"

        deployment.status = "in_progress"
        deployment.started_at = datetime.utcnow()
        assert deployment.status == "in_progress"
        assert deployment.started_at is not None

        deployment.status = "success"
        deployment.completed_at = datetime.utcnow()
        assert deployment.status == "success"
        assert deployment.completed_at is not None

    def test_deployment_to_dict(self, deployment):
        """Test deployment serialization."""
        data = deployment.to_dict()

        assert data['id'] == deployment.id
        assert data['device_id'] == deployment.device_id
        assert data['status'] == deployment.status


class TestCredentialModel:
    """Tests for Credential model."""

    def test_create_credential(self, db, organization):
        """Test creating a credential."""
        cred = Credential(
            name="Test Creds",
            username="admin",
            organization_id=organization.id
        )
        cred.set_password("password123")
        cred.set_enable_password("enable123")
        db.session.add(cred)
        db.session.commit()

        assert cred.id is not None
        assert cred.username == "admin"
        assert cred.password_encrypted is not None

    def test_credential_password_encryption(self, credential):
        """Test credential password encryption/decryption."""
        password = credential.get_password()
        assert password == "cisco123"

        enable_password = credential.get_enable_password()
        assert enable_password == "enable123"

    def test_credential_to_dict(self, credential):
        """Test credential serialization."""
        data = credential.to_dict()

        assert data['id'] == credential.id
        assert data['username'] == credential.username
        assert 'password_encrypted' not in data  # Should not expose encrypted password
