"""
Student views for the TutorConnect application.
Contains routes for student registration, profile management, etc.
"""
from flask import (Blueprint, render_template, request, url_for, redirect, 
                  flash, current_app)

# Create a Blueprint for student routes
student_bp = Blueprint('student', __name__)


@student_bp.route('/signup')
def signup_form():
    """Renders the student signup form."""
    return render_template('student_signup.html')


@student_bp.route('/signup/submit', methods=['POST'])
def signup_submit():
    """Handles the submission of the student signup form."""
    if request.method == 'POST':
        # Extract form data
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        dob = request.form.get('dob')
        timezone = request.form.get('timezone')
        subjects = request.form.getlist('subjects[]')
        learning_goals = request.form.get('learning-goals')
        terms = request.form.get('terms')

        # Basic server-side validation
        errors = []
        if not fullname:
            errors.append("Full Name is required.")
        if not email:
            errors.append("Email is required.")
        if not password or len(password) < 8:
            errors.append("Password is required and must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not dob:
            errors.append("Date of Birth is required.")
        if not timezone:
            errors.append("Timezone is required.")
        if not terms:
            errors.append("You must agree to the Terms of Service and Privacy Policy.")

        if errors:
            # If there are errors, flash them and re-render the form
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('student.signup_form'))

        # If validation passes
        # TODO: Securely hash the password before storing
        # hashed_password = generate_password_hash(password)

        # TODO: Store the user data in your database
        current_app.logger.info(f"Student signup: {fullname}, {email}")
        
        # Log form data for development purposes
        if current_app.debug:
            print("--- Form Data Received ---")
            print(f"Full Name: {fullname}")
            print(f"Email: {email}")
            print(f"DOB: {dob}")
            print(f"Timezone: {timezone}")
            print(f"Subjects: {subjects}")
            print(f"Goals: {learning_goals}")
            print(f"Terms Agreed: {terms}")
            print("--- End Form Data ---")

        # Redirect to success page or login page
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))

    # If method is not POST (shouldn't happen with route definition)
    return redirect(url_for('student.signup_form'))