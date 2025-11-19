"""
Flask blueprints for organizing application routes.
"""
from flask import Blueprint

# Import all blueprints
from routes.main import main_bp
from routes.devices import devices_bp
from routes.protocols import protocols_bp
from routes.configs import configs_bp
from routes.troubleshoot import troubleshoot_bp


__all__ = [
    'main_bp',
    'devices_bp',
    'protocols_bp',
    'configs_bp',
    'troubleshoot_bp',
]


def register_blueprints(app):
    """
    Register all blueprints with the Flask application.

    Args:
        app: Flask application instance
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(protocols_bp)
    app.register_blueprint(configs_bp)
    app.register_blueprint(troubleshoot_bp)
