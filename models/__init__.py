"""
Database models for network configuration management
"""
from datetime import datetime
from extensions import db
from sqlalchemy import Index
from werkzeug.security import generate_password_hash, check_password_hash
import json


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Organization(db.Model, TimestampMixin):
    """Organization/Tenant model for multi-tenancy"""
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    settings = db.Column(db.JSON, default={})

    # Relationships
    users = db.relationship('User', back_populates='organization', lazy='dynamic')
    devices = db.relationship('Device', back_populates='organization', lazy='dynamic')

    def __repr__(self):
        return f'<Organization {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class User(db.Model, TimestampMixin):
    """User model with authentication and authorization"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Multi-tenancy
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    organization = db.relationship('Organization', back_populates='users')

    # Relationships
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='dynamic')
    deployments = db.relationship('Deployment', back_populates='deployed_by_user', lazy='dynamic')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'organization_id': self.organization_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data


class Credential(db.Model, TimestampMixin):
    """Credentials for device access"""
    __tablename__ = 'credentials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Should be encrypted
    enable_secret = db.Column(db.String(255))  # Should be encrypted
    ssh_key = db.Column(db.Text)

    # Multi-tenancy
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)

    # Relationships
    devices = db.relationship('Device', back_populates='credentials', lazy='dynamic')

    def __repr__(self):
        return f'<Credential {self.name}>'


class Device(db.Model, TimestampMixin):
    """Network device model"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)  # IPv6 support
    platform = db.Column(db.String(50), nullable=False, index=True)  # ios, nxos, asa, eos, junos
    device_type = db.Column(db.String(50), default='router')  # router, switch, firewall
    location = db.Column(db.String(255))
    status = db.Column(db.String(20), default='unknown', index=True)  # reachable, unreachable, unknown
    last_seen = db.Column(db.DateTime)
    metadata = db.Column(db.JSON, default={})

    # Multi-tenancy
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    organization = db.relationship('Organization', back_populates='devices')

    # Credentials
    credentials_id = db.Column(db.Integer, db.ForeignKey('credentials.id'))
    credentials = db.relationship('Credential', back_populates='devices')

    # Relationships
    configurations = db.relationship('Configuration', back_populates='device', lazy='dynamic', cascade='all, delete-orphan')
    deployments = db.relationship('Deployment', back_populates='device', lazy='dynamic')
    health_checks = db.relationship('HealthCheck', back_populates='device', lazy='dynamic', cascade='all, delete-orphan')

    # Indexes
    __table_args__ = (
        Index('idx_device_org_status', 'organization_id', 'status'),
        Index('idx_device_platform', 'platform'),
    )

    def __repr__(self):
        return f'<Device {self.hostname} ({self.ip_address})>'

    def to_dict(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'platform': self.platform,
            'device_type': self.device_type,
            'location': self.location,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'organization_id': self.organization_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Configuration(db.Model, TimestampMixin):
    """Configuration version storage"""
    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    config_text = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(50), default='generated')  # running, startup, generated
    version = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    checksum = db.Column(db.String(64))  # SHA-256 hash

    # Relationships
    device = db.relationship('Device', back_populates='configurations')
    deployments = db.relationship('Deployment', back_populates='configuration', lazy='dynamic')

    # Indexes
    __table_args__ = (
        Index('idx_config_device_version', 'device_id', 'version'),
    )

    def __repr__(self):
        return f'<Configuration v{self.version} for Device {self.device_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'config_type': self.config_type,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Deployment(db.Model, TimestampMixin):
    """Deployment history and tracking"""
    __tablename__ = 'deployments'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    configuration_id = db.Column(db.Integer, db.ForeignKey('configurations.id'))
    status = db.Column(db.String(50), default='pending', index=True)  # pending, in_progress, success, failed, rolled_back
    method = db.Column(db.String(50), default='ssh')  # ssh, api, manual
    logs = db.Column(db.Text)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # User tracking
    deployed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deployed_by_user = db.relationship('User', back_populates='deployments')

    # Celery task
    task_id = db.Column(db.String(255), index=True)

    # Relationships
    device = db.relationship('Device', back_populates='deployments')
    configuration = db.relationship('Configuration', back_populates='deployments')

    # Indexes
    __table_args__ = (
        Index('idx_deployment_status_date', 'status', 'created_at'),
    )

    def __repr__(self):
        return f'<Deployment {self.id} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'configuration_id': self.configuration_id,
            'status': self.status,
            'method': self.method,
            'logs': self.logs,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'deployed_by': self.deployed_by,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class HealthCheck(db.Model):
    """Device health check history"""
    __tablename__ = 'health_checks'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # up, down
    response_time_ms = db.Column(db.Integer)
    checked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    device = db.relationship('Device', back_populates='health_checks')

    # Indexes
    __table_args__ = (
        Index('idx_health_check_device_date', 'device_id', 'checked_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'status': self.status,
            'response_time_ms': self.response_time_ms,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None,
        }


class AuditLog(db.Model):
    """Audit trail for all actions"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # create_device, deploy_config, etc.
    target_type = db.Column(db.String(50))  # device, configuration, deployment
    target_id = db.Column(db.Integer)
    details = db.Column(db.JSON, default={})
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Multi-tenancy
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='audit_logs')

    # Indexes
    __table_args__ = (
        Index('idx_audit_org_date', 'organization_id', 'created_at'),
        Index('idx_audit_user_action', 'user_id', 'action'),
    )

    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
