"""
Admin model for TutorConnect application.
"""
import datetime
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
    
    @classmethod
    def create(cls, email, fullname, password, timezone, phone=None, admin_level='standard', permissions=None):
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
            
        Returns:
            Admin: The newly created admin object
        """
        admin = cls(
            email=email,
            fullname=fullname,
            timezone=timezone,
            phone=phone,
            admin_level=admin_level,
            permissions=permissions
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