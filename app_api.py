"""
Main Flask application with complete REST API, WebSockets, and authentication
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException
import logging

# Local imports
from config_enhanced import get_config
from extensions import db, migrate, jwt, socketio, cors, init_app
from models import (
    User, Organization, Device, Configuration, Deployment,
    HealthCheck, AuditLog, Credential
)
from auth import get_current_user, get_current_organization, admin_required, organization_required, filter_by_organization
from tasks.deployment_tasks import deploy_configuration_task, health_check_task, bulk_health_check_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app.config.from_object(get_config(config_name))

    # Initialize extensions
    init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Register routes
    register_routes(app)

    # Register WebSocket events
    register_socketio_events(app)

    return app


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors"""
        return jsonify({
            'error': e.name,
            'message': e.description,
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle uncaught exceptions"""
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e) if app.debug else 'An unexpected error occurred'
        }), 500


def register_routes(app):
    """Register all API routes"""

    # ========== AUTHENTICATION ==========

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
            return jsonify({'error': 'User already exists'}), 409

        # Create organization if multi-tenant
        org = None
        if app.config.get('MULTI_TENANT_ENABLED') and 'organization_name' in data:
            org = Organization(
                name=data['organization_name'],
                slug=data['organization_name'].lower().replace(' ', '-')
            )
            db.session.add(org)
            db.session.flush()

        # Create user
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            organization_id=org.id if org else None
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(include_email=True)
        }), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login and get JWT tokens"""
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'error': 'User account is disabled'}), 403

        # Create tokens with additional claims
        additional_claims = {
            'is_admin': user.is_admin,
            'organization_id': user.organization_id
        }

        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.id)

        # Log audit
        audit = AuditLog(
            user_id=user.id,
            action='login',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            organization_id=user.organization_id
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_email=True)
        }), 200

    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Refresh access token"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404

        additional_claims = {
            'is_admin': user.is_admin,
            'organization_id': user.organization_id
        }

        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )

        return jsonify({'access_token': access_token}), 200

    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_current_user_info():
        """Get current user information"""
        user = get_current_user()
        return jsonify(user.to_dict(include_email=True)), 200

    # ========== DEVICES ==========

    @app.route('/api/devices', methods=['GET'])
    @jwt_required()
    def get_devices():
        """Get all devices (filtered by organization)"""
        query = Device.query
        query = filter_by_organization(query, Device)

        # Filters
        platform = request.args.get('platform')
        status = request.args.get('status')
        search = request.args.get('search')

        if platform:
            query = query.filter(Device.platform == platform)
        if status:
            query = query.filter(Device.status == status)
        if search:
            query = query.filter(
                (Device.hostname.ilike(f'%{search}%')) |
                (Device.ip_address.ilike(f'%{search}%')) |
                (Device.location.ilike(f'%{search}%'))
            )

        devices = query.order_by(Device.hostname).all()
        return jsonify([d.to_dict() for d in devices]), 200

    @app.route('/api/devices', methods=['POST'])
    @jwt_required()
    def create_device():
        """Create a new device"""
        data = request.get_json()
        org = get_current_organization()

        device = Device(
            hostname=data['hostname'],
            ip_address=data['ip_address'],
            platform=data.get('platform', 'ios'),
            device_type=data.get('device_type', 'router'),
            location=data.get('location'),
            organization_id=org.id if org else None
        )

        db.session.add(device)

        # Log audit
        user = get_current_user()
        audit = AuditLog(
            user_id=user.id,
            action='create_device',
            target_type='device',
            target_id=device.id,
            details={'hostname': device.hostname},
            ip_address=request.remote_addr,
            organization_id=org.id if org else None
        )
        db.session.add(audit)

        db.session.commit()

        return jsonify(device.to_dict()), 201

    @app.route('/api/devices/<int:device_id>', methods=['GET'])
    @jwt_required()
    def get_device(device_id):
        """Get a specific device"""
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        return jsonify(device.to_dict()), 200

    @app.route('/api/devices/<int:device_id>', methods=['PUT'])
    @jwt_required()
    def update_device(device_id):
        """Update a device"""
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        data = request.get_json()

        # Update fields
        for field in ['hostname', 'ip_address', 'platform', 'device_type', 'location']:
            if field in data:
                setattr(device, field, data[field])

        # Log audit
        user = get_current_user()
        org = get_current_organization()
        audit = AuditLog(
            user_id=user.id,
            action='update_device',
            target_type='device',
            target_id=device.id,
            details=data,
            ip_address=request.remote_addr,
            organization_id=org.id if org else None
        )
        db.session.add(audit)

        db.session.commit()

        return jsonify(device.to_dict()), 200

    @app.route('/api/devices/<int:device_id>', methods=['DELETE'])
    @jwt_required()
    def delete_device(device_id):
        """Delete a device"""
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        # Log audit before deletion
        user = get_current_user()
        org = get_current_organization()
        audit = AuditLog(
            user_id=user.id,
            action='delete_device',
            target_type='device',
            target_id=device.id,
            details={'hostname': device.hostname},
            ip_address=request.remote_addr,
            organization_id=org.id if org else None
        )
        db.session.add(audit)

        db.session.delete(device)
        db.session.commit()

        return '', 204

    @app.route('/api/devices/bulk-import', methods=['POST'])
    @jwt_required()
    def bulk_import_devices():
        """Bulk import devices from CSV"""
        import csv
        from io import StringIO

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))

        org = get_current_organization()
        devices_created = []
        errors = []

        for row in csv_reader:
            try:
                device = Device(
                    hostname=row['hostname'],
                    ip_address=row['ip_address'],
                    platform=row.get('platform', 'ios'),
                    device_type=row.get('device_type', 'router'),
                    location=row.get('location'),
                    organization_id=org.id if org else None
                )
                db.session.add(device)
                devices_created.append(device.hostname)
            except Exception as e:
                errors.append({
                    'hostname': row.get('hostname'),
                    'error': str(e)
                })

        db.session.commit()

        return jsonify({
            'created': len(devices_created),
            'devices': devices_created,
            'errors': errors
        }), 201

    @app.route('/api/devices/<int:device_id>/ping', methods=['POST'])
    @jwt_required()
    def ping_device(device_id):
        """Test device connectivity"""
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        # Trigger health check task
        task = health_check_task.delay(device.id)

        return jsonify({
            'message': 'Health check initiated',
            'task_id': task.id
        }), 202

    # ========== CONFIGURATIONS ==========

    @app.route('/api/devices/<int:device_id>/configs', methods=['GET'])
    @jwt_required()
    def get_device_configs(device_id):
        """Get configuration history for a device"""
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        configs = Configuration.query.filter_by(device_id=device.id)\
            .order_by(Configuration.version.desc()).all()

        return jsonify([c.to_dict() for c in configs]), 200

    @app.route('/api/configs/<int:config_id>', methods=['GET'])
    @jwt_required()
    def get_config(config_id):
        """Get a specific configuration"""
        config = Configuration.query.get_or_404(config_id)

        # Check organization access
        device_query = Device.query.filter_by(id=config.device_id)
        device_query = filter_by_organization(device_query, Device)
        device_query.first_or_404()  # Verify access

        return jsonify({
            **config.to_dict(),
            'config_text': config.config_text
        }), 200

    @app.route('/api/configs', methods=['POST'])
    @jwt_required()
    def create_config():
        """Create a new configuration version"""
        data = request.get_json()

        # Verify device access
        device_query = Device.query.filter_by(id=data['device_id'])
        device_query = filter_by_organization(device_query, Device)
        device = device_query.first_or_404()

        # Get next version number
        last_config = Configuration.query.filter_by(device_id=device.id)\
            .order_by(Configuration.version.desc()).first()

        next_version = (last_config.version + 1) if last_config else 1

        config = Configuration(
            device_id=device.id,
            config_text=data['config_text'],
            config_type=data.get('config_type', 'generated'),
            version=next_version
        )

        db.session.add(config)
        db.session.commit()

        return jsonify(config.to_dict()), 201

    @app.route('/api/configs/compare-detailed', methods=['POST'])
    @jwt_required()
    def compare_configs():
        """Compare two configurations"""
        from config_comparison import ConfigComparator

        data = request.get_json()
        config1 = Configuration.query.get_or_404(data['config_id_1'])
        config2 = Configuration.query.get_or_404(data['config_id_2'])

        comparator = ConfigComparator()
        result = comparator.compare_configs_detailed(
            config1.config_text,
            config2.config_text
        )

        return jsonify(result), 200

    # ========== DEPLOYMENT ==========

    @app.route('/api/deploy', methods=['POST'])
    @jwt_required()
    def deploy_config():
        """Deploy configuration to devices"""
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        config_id = data.get('config_id')
        dry_run = data.get('dry_run', False)

        user = get_current_user()
        org = get_current_organization()

        # Verify device access
        devices_query = Device.query.filter(Device.id.in_(device_ids))
        devices_query = filter_by_organization(devices_query, Device)
        devices = devices_query.all()

        if len(devices) != len(device_ids):
            return jsonify({'error': 'Some devices not found or access denied'}), 404

        deployments = []

        for device in devices:
            deployment = Deployment(
                device_id=device.id,
                configuration_id=config_id,
                status='pending',
                deployed_by=user.id
            )
            db.session.add(deployment)
            db.session.flush()

            # Queue deployment task
            if not dry_run:
                task = deploy_configuration_task.delay(deployment.id)
                deployment.task_id = task.id

            deployments.append(deployment)

        db.session.commit()

        return jsonify({
            'message': f'Deployment {"simulated" if dry_run else "initiated"} for {len(deployments)} device(s)',
            'deployments': [d.to_dict() for d in deployments]
        }), 202

    @app.route('/api/deploy/history', methods=['GET'])
    @jwt_required()
    def get_deployment_history():
        """Get deployment history"""
        org = get_current_organization()

        query = db.session.query(Deployment)\
            .join(Device)\
            .filter(Device.organization_id == (org.id if org else None))

        # Filters
        device_id = request.args.get('device_id', type=int)
        status = request.args.get('status')

        if device_id:
            query = query.filter(Deployment.device_id == device_id)
        if status:
            query = query.filter(Deployment.status == status)

        deployments = query.order_by(Deployment.created_at.desc()).limit(100).all()

        return jsonify([d.to_dict() for d in deployments]), 200

    # ========== VALIDATION ==========

    @app.route('/api/validate/config', methods=['POST'])
    @jwt_required()
    def validate_config():
        """Validate a configuration"""
        from config_validator import ConfigValidator

        data = request.get_json()
        config = data.get('config')
        vendor = data.get('vendor', 'cisco')

        validator = ConfigValidator()
        result = validator.validate_config(config, vendor)

        return jsonify(result), 200

    @app.route('/api/validate/compliance', methods=['POST'])
    @jwt_required()
    def check_compliance():
        """Check configuration compliance"""
        from config_validator import ComplianceChecker

        data = request.get_json()
        config = data.get('config')
        standards = data.get('standards', ['pci_dss', 'hipaa'])

        checker = ComplianceChecker()
        result = checker.check_compliance(config, standards)

        return jsonify(result), 200

    # ========== AUDIT & HISTORY ==========

    @app.route('/api/changes/history', methods=['GET'])
    @jwt_required()
    def get_audit_history():
        """Get audit history"""
        org = get_current_organization()

        query = AuditLog.query
        if org:
            query = query.filter_by(organization_id=org.id)

        # Filters
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if user_id:
            query = query.filter_by(user_id=user_id)
        if action:
            query = query.filter_by(action=action)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        logs = query.order_by(AuditLog.created_at.desc()).limit(500).all()

        return jsonify([log.to_dict() for log in logs]), 200

    @app.route('/api/changes/history/<int:device_id>', methods=['GET'])
    @jwt_required()
    def get_device_audit_history(device_id):
        """Get audit history for a specific device"""
        # Verify device access
        query = Device.query.filter_by(id=device_id)
        query = filter_by_organization(query, Device)
        device = query.first_or_404()

        logs = AuditLog.query.filter_by(target_type='device', target_id=device_id)\
            .order_by(AuditLog.created_at.desc()).limit(100).all()

        return jsonify([log.to_dict() for log in logs]), 200

    # ========== HEALTH ==========

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # ========== FRONTEND ==========

    @app.route('/')
    def serve_frontend():
        """Serve React frontend"""
        return send_from_directory('static/dist', 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files"""
        if os.path.exists(os.path.join('static/dist', path)):
            return send_from_directory('static/dist', path)
        return send_from_directory('static/dist', 'index.html')


def register_socketio_events(app):
    """Register WebSocket event handlers"""

    @socketio.on('connect', namespace='/deployments')
    def handle_deployment_connect():
        logger.info('Client connected to deployments namespace')

    @socketio.on('disconnect', namespace='/deployments')
    def handle_deployment_disconnect():
        logger.info('Client disconnected from deployments namespace')

    @socketio.on('connect', namespace='/devices')
    def handle_devices_connect():
        logger.info('Client connected to devices namespace')

    @socketio.on('disconnect', namespace='/devices')
    def handle_devices_disconnect():
        logger.info('Client disconnected from devices namespace')


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
