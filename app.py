"""
Kinesis AI - Flask Application Factory
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'kinesis-dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kinesis.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    # Initialize extensions
    from models import db
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    from sports_routes import sports_bp
    app.register_blueprint(sports_bp)

    from api_routes import api_bp
    app.register_blueprint(api_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
