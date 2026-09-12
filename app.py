import os
import logging
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Automatically check and start Ollama for local model execution
def check_and_start_ollama():
    try:
        import requests
    except ImportError:
        logging.warning("requests module not found. Cannot auto-check Ollama status.")
        return

    import subprocess
    import sys
    import time

    def is_ollama_running():
        try:
            r = requests.get("http://localhost:11434", timeout=1)
            return r.status_code == 200
        except Exception:
            return False

    if is_ollama_running():
        logging.info("Ollama is already running.")
        return

    logging.info("Ollama is not running. Starting Ollama...")
    try:
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        logging.info("Waiting for Ollama to start...")
        for _ in range(15):  # Wait up to 15 seconds
            if is_ollama_running():
                logging.info("Ollama started successfully.")
                return
            time.sleep(1)
        logging.warning("Timed out waiting for Ollama to start.")
    except FileNotFoundError:
        logging.warning("Ollama executable ('ollama') was not found in the PATH. "
                        "Please install Ollama (https://ollama.com) to run local models.")
    except Exception as e:
        logging.warning(f"Failed to start Ollama: {e}")

check_and_start_ollama()

# Import extensions
from extensions import db, login_manager

def create_app():
    # Create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure the database
    # Handle potential "postgres://" URLs from Railway
    database_url = os.environ.get("DATABASE_URL", "sqlite:///kinesis.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)

    # Configure Sessions.
    #
    # This used to be SESSION_TYPE = "filesystem" — session files written
    # to disk. That breaks on any host with an ephemeral or non-shared
    # filesystem (Render, Heroku, multi-instance deploys): every restart
    # or redeploy wipes the folder and every logged-in user gets silently
    # signed out / loses in-progress state (same failure class as the
    # earlier stale voice-session bug, just triggered by a restart
    # instead of a stale cookie).
    #
    # Switched to the SQLAlchemy backend instead: sessions are rows in
    # the same Postgres database everything else already uses, so they
    # survive restarts/redeploys and work correctly even if this app
    # ever runs as more than one instance. Kept SESSION_TYPE off
    # "cookie" (the zero-infra default) specifically because OAuth
    # tokens (Google Fit) can be too large for the ~4KB signed-cookie
    # limit — this comment is the reason a plain cookie switch wasn't
    # used instead.
    app.config["SESSION_TYPE"] = "sqlalchemy"
    app.config["SESSION_SQLALCHEMY"] = db
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    Session(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Firebase Auth (admin SDK verifies tokens; web config goes to templates)
    from firebase_init import init_firebase, get_web_config
    init_firebase()

    @app.context_processor
    def inject_firebase_config():
        return {"firebase_config": get_web_config()}

    @app.after_request
    def _allow_auth_popups(response):
        # Without this, Chrome's default Cross-Origin-Opener-Policy blocks the
        # postMessage handshake signInWithPopup needs, and the Google popup
        # closes instantly without completing sign-in.
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        return response

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    with app.app_context():
        # Import models first
        import models

        # Create all tables
        db.create_all()

    return app

# Create the app instance
app = create_app()

# Import and register routes after app creation
# We need to import routes here to avoid circular imports
import routes

# Register all routes with the Flask app instance
routes.register_routes(app)

if __name__ == '__main__':
    # Use environment variables for host and port with fallbacks
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)