"""
Database models for the Cisco Configuration Generator.

This module defines SQLAlchemy models for users, configurations,
configuration history, compliance checks, and more.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import text
import json

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='engineer')  # admin, engineer, viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    configurations = db.relationship('Configuration', backref='author', lazy='dynamic',
                                      cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_permission(self, action):
        """Check if user has permission for action."""
        permissions = {
            'admin': ['read', 'write', 'delete', 'admin'],
            'engineer': ['read', 'write'],
            'viewer': ['read']
        }
        return action in permissions.get(self.role, [])

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Configuration(db.Model):
    """Configuration model for storing device configurations."""

    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    platform = db.Column(db.String(20), nullable=False, index=True)  # ios, nxos, asa
    device_type = db.Column(db.String(20), index=True)  # router, switch, firewall
    config_data = db.Column(db.Text, nullable=False)  # JSON string
    cli_output = db.Column(db.Text)  # Generated CLI commands
    version = db.Column(db.Integer, default=1)
    is_template = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255))  # Comma-separated tags

    # Metadata
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    history = db.relationship('ConfigHistory', backref='configuration', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='ConfigHistory.version.desc()')
    compliance_checks = db.relationship('ComplianceCheck', backref='configuration',
                                       lazy='dynamic', cascade='all, delete-orphan')

    def get_config_data(self):
        """Parse JSON config data."""
        try:
            return json.loads(self.config_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_config_data(self, data):
        """Set config data from dictionary."""
        self.config_data = json.dumps(data, indent=2)

    def create_history_snapshot(self):
        """Create a history snapshot of current configuration."""
        history = ConfigHistory(
            configuration_id=self.id,
            version=self.version,
            config_data=self.config_data,
            cli_output=self.cli_output,
            changed_by_id=self.user_id
        )
        db.session.add(history)
        self.version += 1
        return history

    def get_tag_list(self):
        """Get tags as list."""
        return [tag.strip() for tag in (self.tags or '').split(',') if tag.strip()]

    def set_tag_list(self, tags):
        """Set tags from list."""
        self.tags = ','.join(tags) if tags else ''

    def to_dict(self, include_config=False):
        """Convert configuration to dictionary."""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'platform': self.platform,
            'device_type': self.device_type,
            'version': self.version,
            'is_template': self.is_template,
            'is_public': self.is_public,
            'tags': self.get_tag_list(),
            'author': self.author.username if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_config:
            result['config_data'] = self.get_config_data()
            result['cli_output'] = self.cli_output
        return result

    def __repr__(self):
        return f'<Configuration {self.name} v{self.version}>'


class ConfigHistory(db.Model):
    """Configuration version history."""

    __tablename__ = 'config_history'

    id = db.Column(db.Integer, primary_key=True)
    configuration_id = db.Column(db.Integer, db.ForeignKey('configurations.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    config_data = db.Column(db.Text, nullable=False)
    cli_output = db.Column(db.Text)
    change_description = db.Column(db.Text)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    changed_by = db.relationship('User', backref='config_changes')

    def get_config_data(self):
        """Parse JSON config data."""
        try:
            return json.loads(self.config_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def to_dict(self):
        """Convert history record to dictionary."""
        return {
            'id': self.id,
            'version': self.version,
            'change_description': self.change_description,
            'changed_by': self.changed_by.username if self.changed_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ConfigHistory Config:{self.configuration_id} v{self.version}>'


class ComplianceCheck(db.Model):
    """Compliance check results for configurations."""

    __tablename__ = 'compliance_checks'

    id = db.Column(db.Integer, primary_key=True)
    configuration_id = db.Column(db.Integer, db.ForeignKey('configurations.id'), nullable=False)
    standard = db.Column(db.String(50), nullable=False)  # PCI-DSS, NIST, CIS, etc.
    status = db.Column(db.String(20), default='pending')  # pending, passed, failed, warning
    score = db.Column(db.Float)  # Compliance score (0-100)
    results = db.Column(db.Text)  # JSON string with detailed results
    recommendations = db.Column(db.Text)  # JSON string with recommendations
    checked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def get_results(self):
        """Parse JSON results."""
        try:
            return json.loads(self.results) if self.results else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_results(self, results):
        """Set results from list/dict."""
        self.results = json.dumps(results, indent=2)

    def get_recommendations(self):
        """Parse JSON recommendations."""
        try:
            return json.loads(self.recommendations) if self.recommendations else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_recommendations(self, recommendations):
        """Set recommendations from list/dict."""
        self.recommendations = json.dumps(recommendations, indent=2)

    def to_dict(self):
        """Convert compliance check to dictionary."""
        return {
            'id': self.id,
            'configuration_id': self.configuration_id,
            'standard': self.standard,
            'status': self.status,
            'score': self.score,
            'results': self.get_results(),
            'recommendations': self.get_recommendations(),
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }

    def __repr__(self):
        return f'<ComplianceCheck {self.standard} - {self.status}>'


class NetworkTopology(db.Model):
    """Network topology for visualization."""

    __tablename__ = 'network_topologies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    topology_data = db.Column(db.Text, nullable=False)  # JSON with nodes and edges
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='topologies')

    def get_topology_data(self):
        """Parse JSON topology data."""
        try:
            return json.loads(self.topology_data)
        except (json.JSONDecodeError, TypeError):
            return {'nodes': [], 'edges': []}

    def set_topology_data(self, data):
        """Set topology data from dictionary."""
        self.topology_data = json.dumps(data, indent=2)

    def to_dict(self):
        """Convert topology to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'topology_data': self.get_topology_data(),
            'user': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<NetworkTopology {self.name}>'


class APIKey(db.Model):
    """API keys for programmatic access."""

    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def is_valid(self):
        """Check if API key is valid and not expired."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def to_dict(self):
        """Convert API key to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key[:8] + '...',  # Only show first 8 chars
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    def __repr__(self):
        return f'<APIKey {self.name}>'
