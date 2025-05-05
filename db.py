"""
Database initialization and configuration for TutorConnect.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Create SQLAlchemy db instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask application."""
    db.init_app(app)
    
    with app.app_context():
        try:
            # Import models to ensure they are registered with SQLAlchemy
            from models.user import User
            from models.student import Student
            from models.tutor import Tutor
            
            # Create all tables if they don't exist
            db.create_all()
            app.logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            app.logger.error(f"Error initializing database: {str(e)}")
            raise