"""
Admin model for TutorConnect application.
"""
import datetime
from flask import url_for, current_app
from db import db
from models.user import User, UserRole

class Admin(User):
    """Admin user model extending the base User model."""
    __tablename__ = 'admins'
    
    # Override role to set it as ADMIN
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.ADMIN)
    
    # Admin-specific fields
    admin_level = db.Column(db.String(20), nullable=False, default='standard')  # standard, super
    permissions = db.Column(db.String(500), nullable=True)  # JSON string of permissions
    last_action = db.Column(db.DateTime, nullable=True)  # Track last admin action
    profile_pic = db.Column(db.String(255), nullable=True)  # Path to profile picture
    
    @property
    def profile_picture_url(self):
        """Generate the full URL for the profile picture using config directory."""
        if self.profile_pic:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads/profile_pics')
            return url_for('static', filename=f'{upload_folder.replace("static/", "")}/{self.profile_pic}')
        return None
    
    @classmethod
    def create(cls, email, fullname, password, timezone, phone=None, admin_level='standard', permissions=None, profile_pic=None):
        """
        Create a new admin user.
        
        Args:
            email (str): Email address
            fullname (str): Full name
            password (str): Password (will be hashed)
            timezone (str): Timezone
            phone (str, optional): Phone number
            admin_level (str): Admin level (standard, super)
            permissions (str, optional): JSON string of permissions
            profile_pic (str, optional): Path to profile picture
            
        Returns:
            Admin: The newly created admin object
        """
        admin = cls(
            email=email,
            fullname=fullname,
            timezone=timezone,
            phone=phone,
            admin_level=admin_level,
            permissions=permissions,
            profile_pic=profile_pic
        )
        admin.password = password  # This will hash the password
        
        db.session.add(admin)
        db.session.commit()
        
        return admin
    
    def update_last_action(self):
        """Update the last action timestamp for the admin."""
        self.last_action = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert the admin object to a dictionary."""
        base_dict = super().to_dict()
        admin_dict = {
            'admin_level': self.admin_level,
            'permissions': self.permissions,
            'last_action': self.last_action.isoformat() if self.last_action else None
        }
        return {**base_dict, **admin_dict}