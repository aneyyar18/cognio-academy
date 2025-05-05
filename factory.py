"""
Application factory for TutorConnect.
"""
import os
import datetime
from flask import Flask, session

def create_app(config_filename=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_filename (str, optional): Path to config file.
        If None, uses the default config.py.
        
    Returns:
        Flask: The configured Flask application
    """
    # Create the Flask application
    app = Flask(__name__)
    
    # Load the default configuration
    app.config.from_object('config')
    
    # Load the configuration from the instance folder
    if config_filename:
        app.config.from_pyfile(config_filename)
        
    # Set secret key from config
    app.secret_key = app.config.get('SECRET_KEY', 'default_key')
    
    # Configure session to expire after a specified time
    app.permanent_session_lifetime = datetime.timedelta(seconds=app.config.get('AUTH_TOKEN_EXPIRY', 86400))
    
    # Ensure the upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads/profile_pics'),
                exist_ok=True)
    
    # Initialize the database
    init_database(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def init_database(app):
    """
    Initialize the database for the application.
    
    Args:
        app (Flask): The Flask application
    """
    from db import init_db
    init_db(app)

def register_blueprints(app):
    """
    Register all blueprints for the application.
    
    Args:
        app (Flask): The Flask application
    """
    # Import blueprints
    from views.main import main_bp
    from views.student import student_bp
    from views.tutor import tutor_bp
    from views.auth import auth_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(tutor_bp, url_prefix='/tutor')
    app.register_blueprint(auth_bp, url_prefix='/auth')