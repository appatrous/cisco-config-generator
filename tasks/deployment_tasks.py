"""
Celery tasks for device deployment
"""
from celery import Task
from celery_app import celery
from extensions import db, socketio
from models import Device, Deployment, Configuration, HealthCheck
from device_manager import DeviceManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SQLAlchemyTask(Task):
    """Base task class that handles SQLAlchemy session management"""
    _db = None

    @property
    def db_session(self):
        if self._db is None:
            from app_api import create_app
            app = create_app()
            app.app_context().push()
            self._db = db
        return self._db


@celery.task(base=SQLAlchemyTask, bind=True)
def deploy_configuration_task(self, deployment_id):
    """Deploy configuration to a device"""
    logger.info(f"Starting deployment task for deployment_id={deployment_id}")

    deployment = Deployment.query.get(deployment_id)
    if not deployment:
        logger.error(f"Deployment {deployment_id} not found")
        return {'error': 'Deployment not found'}

    device = deployment.device
    config = deployment.configuration

    # Update deployment status
    deployment.status = 'in_progress'
    deployment.started_at = datetime.utcnow()
    deployment.logs = f"Starting deployment to {device.hostname}\n"
    db.session.commit()

    # Emit WebSocket event
    socketio.emit('deployment_update', {
        'deployment_id': deployment_id,
        'status': 'in_progress',
        'message': f'Starting deployment to {device.hostname}'
    }, namespace='/deployments')

    try:
        # Initialize device manager
        manager = DeviceManager(device)

        # Test connectivity
        deployment.logs += "Testing connectivity...\n"
        db.session.commit()

        is_connected = manager.test_connectivity()
        if not is_connected:
            raise Exception("Device is unreachable")

        deployment.logs += "Device is reachable\n"

        # Backup current config
        deployment.logs += "Backing up current configuration...\n"
        db.session.commit()

        current_config = manager.pull_config_ssh(
            device.ip_address,
            device.credentials.username if device.credentials else 'admin',
            device.credentials.password if device.credentials else '',
            device.credentials.enable_secret if device.credentials else ''
        )

        # Save backup
        backup = Configuration(
            device_id=device.id,
            config_text=current_config.get('config', ''),
            config_type='backup',
            version=config.version if config else 1
        )
        db.session.add(backup)
        deployment.logs += f"Backup saved (version {backup.version})\n"

        # Deploy new configuration
        deployment.logs += "Deploying new configuration...\n"
        db.session.commit()

        socketio.emit('deployment_update', {
            'deployment_id': deployment_id,
            'status': 'deploying',
            'progress': 50,
            'message': 'Applying configuration'
        }, namespace='/deployments')

        result = manager.push_config_ssh(
            device.ip_address,
            device.credentials.username if device.credentials else 'admin',
            device.credentials.password if device.credentials else '',
            device.credentials.enable_secret if device.credentials else '',
            config.config_text if config else ''
        )

        deployment.logs += result.get('output', '')

        if result.get('success'):
            deployment.status = 'success'
            deployment.logs += "\nDeployment completed successfully\n"

            # Mark configuration as active
            if config:
                # Deactivate other configs
                Configuration.query.filter_by(device_id=device.id, is_active=True).update({'is_active': False})
                config.is_active = True

            # Update device status
            device.status = 'reachable'
            device.last_seen = datetime.utcnow()
        else:
            raise Exception(result.get('error', 'Deployment failed'))

    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        deployment.status = 'failed'
        deployment.error_message = str(e)
        deployment.logs += f"\n ERROR: {str(e)}\n"

        # Update device status
        device.status = 'unreachable'

    finally:
        deployment.completed_at = datetime.utcnow()
        db.session.commit()

        # Emit final WebSocket event
        socketio.emit('deployment_update', {
            'deployment_id': deployment_id,
            'status': deployment.status,
            'progress': 100,
            'message': 'Deployment complete' if deployment.status == 'success' else 'Deployment failed',
            'logs': deployment.logs
        }, namespace='/deployments')

    return deployment.to_dict()


@celery.task(base=SQLAlchemyTask)
def health_check_task(device_id):
    """Perform health check on a device"""
    logger.info(f"Health check for device_id={device_id}")

    device = Device.query.get(device_id)
    if not device:
        logger.error(f"Device {device_id} not found")
        return {'error': 'Device not found'}

    manager = DeviceManager(device)
    result = manager.test_connectivity()

    # Record health check
    health_check = HealthCheck(
        device_id=device.id,
        status='up' if result['alive'] else 'down',
        response_time_ms=result.get('response_time_ms')
    )
    db.session.add(health_check)

    # Update device status
    device.status = 'reachable' if result['alive'] else 'unreachable'
    if result['alive']:
        device.last_seen = datetime.utcnow()

    db.session.commit()

    # Emit WebSocket event
    socketio.emit('health_check_update', {
        'device_id': device_id,
        'status': device.status,
        'response_time_ms': result.get('response_time_ms')
    }, namespace='/devices')

    return result


@celery.task(base=SQLAlchemyTask)
def bulk_health_check_task():
    """Run health checks on all devices"""
    logger.info("Running bulk health check")

    devices = Device.query.filter(Device.status != 'archived').all()
    results = []

    for device in devices:
        result = health_check_task.delay(device.id)
        results.append({'device_id': device.id, 'task_id': result.id})

    return {'total': len(results), 'tasks': results}
