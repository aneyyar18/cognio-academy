"""
Authentication utilities for TutorConnect application.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, current_app, request
from models.student import Student
from models.tutor import Tutor
from models.user import UserRole

def login_user(user):
    """
    Log in a user by storing their data in the session.
    
    Args:
        user (User): The user object to log in
    """
    # Update last login time
    user.update_last_login()
    
    # Store user info in session
    session['user_id'] = user.id
    session['user_role'] = user.role.value
    session['user_email'] = user.email
    session['user_name'] = user.fullname
    
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
        
    # Verify password if user was found
    if user and user.verify_password(password):
        return user
        
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