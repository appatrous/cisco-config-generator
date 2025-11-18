"""
Database extensions and initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')
cors = CORS()

def init_app(app):
    """Initialize all extensions with the Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    cors.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
