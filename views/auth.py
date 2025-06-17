"""
Authentication views for TutorConnect application.
Handles OAuth login, password reset, and authentication flows.
"""
import requests
import secrets
from urllib.parse import urlencode
from flask import Blueprint, request, redirect, url_for, flash, session, current_app, render_template
from models.student import Student
from models.tutor import Tutor
from models.password_reset import PasswordReset
from utils.email_utils import send_password_reset_email
from utils.password_utils import validate_password_strength
from auth import login_user, logout_user
from db import db

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login."""
    if not current_app.config.get('GOOGLE_CLIENT_ID'):
        flash('Google login is not configured.', 'error')
        return redirect(url_for('main.login'))
    
    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Google OAuth 2.0 authorization URL
    google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    
    params = {
        'client_id': current_app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': url_for('auth.google_callback', _external=True),
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state
    }
    
    auth_url = f"{google_auth_url}?{urlencode(params)}"
    return redirect(auth_url)


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    # Verify state to prevent CSRF attacks
    if request.args.get('state') != session.get('oauth_state'):
        flash('Authentication failed: Invalid state parameter.', 'error')
        return redirect(url_for('main.login'))
    
    # Clear the state from session
    session.pop('oauth_state', None)
    
    # Handle error from Google
    if request.args.get('error'):
        flash('Authentication cancelled.', 'info')
        return redirect(url_for('main.login'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Authentication failed: No authorization code received.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Exchange code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('auth.google_callback', _external=True)
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        access_token = token_json.get('access_token')
        if not access_token:
            flash('Authentication failed: No access token received.', 'error')
            return redirect(url_for('main.login'))
        
        # Get user info from Google
        userinfo_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        userinfo_response = requests.get(userinfo_url)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()
        
        email = user_data.get('email')
        name = user_data.get('name')
        
        if not email:
            flash('Authentication failed: No email received from Google.', 'error')
            return redirect(url_for('main.login'))
        
        # Check if user exists
        user = Student.query.filter_by(email=email).first() or Tutor.query.filter_by(email=email).first()
        
        if user:
            # User exists, log them in
            login_user(user)
            flash(f'Welcome back, {user.fullname}!', 'success')
            
            # Redirect based on role
            if user.role.value == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role.value == 'tutor':
                return redirect(url_for('tutor.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            # New user, redirect to role selection with pre-filled data
            session['oauth_user_data'] = {
                'email': email,
                'name': name,
                'provider': 'google'
            }
            flash(f'Welcome {name}! Please complete your registration by selecting your role.', 'info')
            return redirect(url_for('main.role_selection'))
    
    except requests.RequestException as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        flash('Authentication failed: Unable to connect to Google.', 'error')
        return redirect(url_for('main.login'))
    except Exception as e:
        current_app.logger.error(f"Google OAuth unexpected error: {str(e)}")
        flash('Authentication failed: An unexpected error occurred.', 'error')
        return redirect(url_for('main.login'))


@auth_bp.route('/microsoft')
def microsoft_login():
    """Initiate Microsoft OAuth login."""
    if not current_app.config.get('MICROSOFT_CLIENT_ID'):
        flash('Microsoft login is not configured.', 'error')
        return redirect(url_for('main.login'))
    
    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Microsoft OAuth 2.0 authorization URL
    microsoft_auth_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    
    params = {
        'client_id': current_app.config['MICROSOFT_CLIENT_ID'],
        'redirect_uri': url_for('auth.microsoft_callback', _external=True),
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state
    }
    
    auth_url = f"{microsoft_auth_url}?{urlencode(params)}"
    return redirect(auth_url)


@auth_bp.route('/microsoft/callback')
def microsoft_callback():
    """Handle Microsoft OAuth callback."""
    # Verify state to prevent CSRF attacks
    if request.args.get('state') != session.get('oauth_state'):
        flash('Authentication failed: Invalid state parameter.', 'error')
        return redirect(url_for('main.login'))
    
    # Clear the state from session
    session.pop('oauth_state', None)
    
    # Handle error from Microsoft
    if request.args.get('error'):
        flash('Authentication cancelled.', 'info')
        return redirect(url_for('main.login'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Authentication failed: No authorization code received.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Exchange code for access token
        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        token_data = {
            'client_id': current_app.config['MICROSOFT_CLIENT_ID'],
            'client_secret': current_app.config['MICROSOFT_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('auth.microsoft_callback', _external=True)
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        access_token = token_json.get('access_token')
        if not access_token:
            flash('Authentication failed: No access token received.', 'error')
            return redirect(url_for('main.login'))
        
        # Get user info from Microsoft Graph
        userinfo_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()
        
        email = user_data.get('mail') or user_data.get('userPrincipalName')
        name = user_data.get('displayName')
        
        if not email:
            flash('Authentication failed: No email received from Microsoft.', 'error')
            return redirect(url_for('main.login'))
        
        # Check if user exists
        user = Student.query.filter_by(email=email).first() or Tutor.query.filter_by(email=email).first()
        
        if user:
            # User exists, log them in
            login_user(user)
            flash(f'Welcome back, {user.fullname}!', 'success')
            
            # Redirect based on role
            if user.role.value == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role.value == 'tutor':
                return redirect(url_for('tutor.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            # New user, redirect to role selection with pre-filled data
            session['oauth_user_data'] = {
                'email': email,
                'name': name,
                'provider': 'microsoft'
            }
            flash(f'Welcome {name}! Please complete your registration by selecting your role.', 'info')
            return redirect(url_for('main.role_selection'))
    
    except requests.RequestException as e:
        current_app.logger.error(f"Microsoft OAuth error: {str(e)}")
        flash('Authentication failed: Unable to connect to Microsoft.', 'error')
        return redirect(url_for('main.login'))
    except Exception as e:
        current_app.logger.error(f"Microsoft OAuth unexpected error: {str(e)}")
        flash('Authentication failed: An unexpected error occurred.', 'error')
        return redirect(url_for('main.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')
        
        # Check if user exists (in either student or tutor table)
        user = Student.query.filter_by(email=email).first() or Tutor.query.filter_by(email=email).first()
        
        if user:
            try:
                # Create password reset token
                reset_record, plain_token = PasswordReset.create_reset_token(email)
                
                # Send reset email
                if send_password_reset_email(email, plain_token):
                    flash('Password reset instructions have been sent to your email address.', 'success')
                    current_app.logger.info(f"Password reset email sent to {email}")
                else:
                    flash('Failed to send reset email. Please try again later.', 'error')
                    current_app.logger.error(f"Failed to send password reset email to {email}")
            except Exception as e:
                current_app.logger.error(f"Error creating password reset for {email}: {str(e)}")
                flash('An error occurred. Please try again later.', 'error')
        else:
            # For security, don't reveal if email exists or not
            flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    # Verify the token
    reset_record = PasswordReset.verify_token(token)
    
    if not reset_record:
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate passwords
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Validate password strength
        password_errors = validate_password_strength(password)
        if password_errors:
            for error in password_errors:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        try:
            # Find the user and update their password
            user = Student.query.filter_by(email=reset_record.email).first() or \
                   Tutor.query.filter_by(email=reset_record.email).first()
            
            if user:
                user.password = password  # This will hash the password
                reset_record.mark_as_used()
                
                flash('Your password has been successfully updated. You can now log in with your new password.', 'success')
                current_app.logger.info(f"Password reset completed for {reset_record.email}")
                return redirect(url_for('main.login'))
            else:
                flash('User account not found.', 'error')
                return redirect(url_for('auth.forgot_password'))
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error resetting password for {reset_record.email}: {str(e)}")
            flash('An error occurred while resetting your password. Please try again.', 'error')
            return render_template('reset_password.html', token=token)
    
    return render_template('reset_password.html', token=token)


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