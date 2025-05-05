"""
Authentication routes for TutorConnect application.
"""
from flask import Blueprint, redirect, url_for, flash, current_app, session
from auth import logout_user

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/logout')
def logout():
    """Log out the current user and redirect to homepage."""
    # Get user details for logging before clearing session
    user_email = session.get('user_email', 'Unknown user')
    
    # Log the logout action
    current_app.logger.info(f"User logged out: {user_email}")
    
    # Clear the session
    logout_user()
    
    # Flash message and redirect
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))