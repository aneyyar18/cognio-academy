"""
Main views for the TutorConnect application.
Contains routes for the homepage, about page, features page, etc.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from auth import authenticate_user, login_user

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')


@main_bp.route('/features')
def features():
    """Renders the features page."""
    return render_template('features.html')


@main_bp.route('/discover')
def discover():
    """Renders the discover page for finding tutors."""
    return render_template('discover.html')


@main_bp.route('/role-selection')
def role_selection():
    """Renders the role selection page."""
    return render_template('role-selection.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page and handles login attempts."""
    # If user is already logged in, redirect to appropriate dashboard
    if 'user_id' in session:
        if session['user_role'] == 'student':
            return redirect(url_for('student.dashboard'))
        elif session['user_role'] == 'tutor':
            return redirect(url_for('tutor.dashboard'))
        return redirect(url_for('main.index'))

    # Handle form submission
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')

        # Attempt to authenticate the user
        user = authenticate_user(email, password)

        if user:
            # Log the user in
            login_user(user)
            
            # Set session permanency based on remember checkbox
            session.permanent = remember
            
            # Log successful login
            current_app.logger.info(f"User logged in: {email}")
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role.value == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role.value == 'tutor':
                return redirect(url_for('tutor.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            # Log failed login attempt
            current_app.logger.warning(f"Failed login attempt for: {email}")
            flash('Invalid email or password.', 'error')

    # Render login form for GET requests and failed POST requests
    return render_template('login.html')