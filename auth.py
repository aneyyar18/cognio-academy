"""
Authentication utilities for TutorConnect application.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, current_app, request
from models.student import Student
from models.tutor import Tutor, TutorStatus
from models.admin import Admin
from models.user import UserRole

def login_user(user_id, role, fullname):
    """
    Log in a user by storing their data in the session.
    
    Args:
        user_id (int): User ID
        role (str): User role
        fullname (str): User's full name
    """
    # Store user info in session
    session['user_id'] = user_id
    session['user_role'] = role
    session['user_name'] = fullname
    
    # Set session to expire after the configured time
    session.permanent = True
    
def logout_user():
    """Log out the current user by clearing their session data."""
    session.clear()

def get_current_user():
    """
    Get the currently logged in user.
    
    Returns:
        User or None: The current user or None if no user is logged in
    """
    if 'user_id' not in session or 'user_role' not in session:
        return None
        
    user_id = session['user_id']
    role = session['user_role']
    
    if role == UserRole.STUDENT.value:
        return Student.query.get(user_id)
    elif role == UserRole.TUTOR.value:
        return Tutor.query.get(user_id)
    elif role == UserRole.ADMIN.value:
        return Admin.query.get(user_id)
    else:
        return None

def authenticate_user(email, password):
    """
    Authenticate a user with email and password.
    
    Args:
        email (str): The user's email
        password (str): The user's password
        
    Returns:
        User or None: The authenticated user or None if authentication failed
    """
    # Try to find the user as a student first
    user = Student.query.filter_by(email=email).first()
    
    # If not found, try as a tutor
    if not user:
        user = Tutor.query.filter_by(email=email).first()
        # Check if tutor is verified before allowing login
        if user and user.status != TutorStatus.VERIFIED:
            # Return a special indicator for unverified tutors
            return 'unverified_tutor'
    
    # If still not found, try as admin (admin login should use separate function)
    if not user:
        user = Admin.query.filter_by(email=email).first()
        
    # Verify password if user was found
    if user and user.verify_password(password):
        return user
        
    return None

def authenticate_admin(email, password):
    """
    Authenticate an admin user with email and password.
    
    Args:
        email (str): The admin's email
        password (str): The admin's password
        
    Returns:
        Admin or None: The authenticated admin or None if authentication failed
    """
    admin = Admin.query.filter_by(email=email).first()
    
    if admin and admin.verify_password(password):
        return admin
        
    return None

def login_required(f):
    """
    Decorator to require login for a view.
    
    Args:
        f (function): The view function to protect
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            next_url = request.url if request.url else None
            return redirect(url_for('main.login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """
    Decorator to require specific role(s) for a view.
    
    Args:
        roles (list): List of allowed roles
        
    Returns:
        function: The decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator