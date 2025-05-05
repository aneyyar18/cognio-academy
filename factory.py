"""
Application factory for TutorConnect.
"""
import os
from flask import Flask


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
    
    # Ensure the upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads/profile_pics'),
                exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
    return app


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
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(tutor_bp, url_prefix='/tutor')