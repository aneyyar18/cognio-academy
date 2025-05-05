"""
Base User model for TutorConnect application.
"""
import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declared_attr

from db import db

class UserRole(Enum):
    """Enum for user roles in the system."""
    STUDENT = 'student'
    TUTOR = 'tutor'
    ADMIN = 'admin'
    
class User(db.Model):
    """Base User model for all user types."""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    _password_hash = db.Column(db.String(200), nullable=False)
    
    timezone = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # This allows children classes to set their own role
    @declared_attr
    def role(cls):
        return db.Column(db.Enum(UserRole), nullable=False)
    
    @property
    def password(self):
        """Password property - prevents direct access to the password."""
        raise AttributeError('Password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        """Password setter - securely hashes the password."""
        self._password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        """Verify that the provided password matches the stored hash."""
        return check_password_hash(self._password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp for the user."""
        self.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
    def to_dict(self):
        """Convert the user object to a dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'fullname': self.fullname,
            'timezone': self.timezone,
            'phone': self.phone,
            'role': self.role.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }