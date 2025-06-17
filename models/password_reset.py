"""
Password Reset model for TutorConnect application.
"""
import datetime
from db import db
from utils.password_utils import generate_reset_token, hash_reset_token

class PasswordReset(db.Model):
    """Password reset token model."""
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    
    @classmethod
    def create_reset_token(cls, email):
        """
        Create a new password reset token for an email.
        
        Args:
            email (str): The email address to create a reset token for
            
        Returns:
            tuple: (PasswordReset object, plain_token)
        """
        # Generate a secure token
        plain_token = generate_reset_token()
        token_hash = hash_reset_token(plain_token)
        
        # Set expiration time (1 hour from now)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        
        # Create the reset record
        reset = cls(
            email=email.lower(),
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        # Remove any existing unused tokens for this email
        cls.query.filter_by(email=email.lower(), used=False).delete()
        
        db.session.add(reset)
        db.session.commit()
        
        return reset, plain_token
    
    @classmethod
    def verify_token(cls, token):
        """
        Verify a reset token and return the associated reset record.
        
        Args:
            token (str): The plain token to verify
            
        Returns:
            PasswordReset or None: The reset record if valid, None otherwise
        """
        from utils.password_utils import hash_reset_token
        
        token_hash = hash_reset_token(token)
        
        # Find the reset record
        reset = cls.query.filter_by(token_hash=token_hash, used=False).first()
        
        if not reset:
            return None
        
        # Check if token has expired
        if datetime.datetime.utcnow() > reset.expires_at:
            return None
        
        return reset
    
    def mark_as_used(self):
        """Mark this reset token as used."""
        self.used = True
        db.session.commit()
    
    @classmethod
    def cleanup_expired_tokens(cls):
        """Remove expired password reset tokens."""
        expired_tokens = cls.query.filter(
            cls.expires_at < datetime.datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.session.delete(token)
        
        db.session.commit()
        return len(expired_tokens)
    
    def __repr__(self):
        return f'<PasswordReset {self.email} at {self.created_at}>'