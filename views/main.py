"""
Main views for the TutorConnect application.
Contains routes for the homepage, about page, features page, etc.
"""
from flask import Blueprint, render_template

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


@main_bp.route('/login')
def login():
    """Renders the login page."""
    return render_template('login.html')