"""
Refactored Flask application entry point for the Cisco Configuration Generator.

This is a clean, modular version of the original app.py, using blueprints
for route organization and services for business logic.

Architecture:
    - routes/: Flask blueprints for organizing routes
    - services/: Business logic layer
    - schemas/: Pydantic models for validation
    - utils/: Helper functions and utilities
"""
from flask import Flask
import config as app_config
from routes import register_blueprints


def create_app() -> Flask:
    """
    Factory to create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Load configuration
    app.config.from_object(app_config)
    app.secret_key = app_config.SECRET_KEY

    # Register all blueprints
    register_blueprints(app)

    # Register API blueprint if available (for backwards compatibility)
    try:
        from extensions.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        pass  # API may not be implemented yet

    # Optional: Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        from flask import render_template
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(
        debug=app_config.DEBUG if hasattr(app_config, 'DEBUG') else True,
        host='0.0.0.0',
        port=5000
    )
