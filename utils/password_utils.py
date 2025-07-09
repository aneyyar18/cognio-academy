"""
Password utility functions for TutorConnect application.
"""
import re
import secrets
import hashlib
from datetime import datetime, timedelta

def validate_password_strength(password):
    """
    Validate password strength and return errors if any.
    
    Args:
        password (str): The password to validate
        
    Returns:
        list: List of error messages, empty if password is valid
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '123456789', 'qwertyuiop', 'abc123456', 
        'password123', '12345678', 'admin123', 'welcome123'
    ]
    
    if password.lower() in weak_passwords:
        errors.append("This password is too common. Please choose a more unique password")
    
    return errors

def generate_reset_token():
    """
    Generate a secure random token for password reset.
    
    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(32)

def hash_reset_token(token):
    """
    Hash a reset token for secure storage.
    
    Args:
        token (str): The token to hash
        
    Returns:
        str: The hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()

def verify_reset_token(token, hashed_token):
    """
    Verify a reset token against its hash.
    
    Args:
        token (str): The token to verify
        hashed_token (str): The stored hash to verify against
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    return hashlib.sha256(token.encode()).hexdigest() == hashed_token

def get_password_requirements():
    """
    Get a list of password requirements for display to users.
    
    Returns:
        list: List of password requirements
    """
    return [
        "At least 8 characters long",
        "At least one uppercase letter (A-Z)",
        "At least one lowercase letter (a-z)",
        "At least one number (0-9)",
        "At least one special character (!@#$%^&*)",
        "Cannot be a common password"
    ]
