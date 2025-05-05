"""
Tutor views for the TutorConnect application.
Contains routes for tutor registration, profile management, etc.
"""
from flask import (Blueprint, render_template, request, url_for, redirect, 
                  flash, current_app)

from utils.file_handling import allowed_file, save_uploaded_file

# Create a Blueprint for tutor routes
tutor_bp = Blueprint('tutor', __name__)


@tutor_bp.route('/signup')
def signup_form():
    """Renders the tutor signup form."""
    return render_template('tutor_signup.html')


@tutor_bp.route('/signup/submit', methods=['POST'])
def signup_submit():
    """Handles the submission of the tutor signup form."""
    if request.method == 'POST':
        # Extract basic info
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        phone = request.form.get('phone')  # Optional
        timezone = request.form.get('timezone')
        terms = request.form.get('terms')

        # Extract tutor profile info
        qualification = request.form.get('qualification')
        experience_str = request.form.get('experience')
        subjects = request.form.getlist('subjects[]')
        bio = request.form.get('bio')
        hourly_rate_str = request.form.get('hourly_rate')  # Optional

        # Handle file upload
        profile_pic_filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                if allowed_file(file.filename):
                    # Save file with secure name
                    profile_pic_filename = save_uploaded_file(
                        file, 
                        current_app.config['UPLOAD_FOLDER']
                    )
                    if not profile_pic_filename:
                        flash('Error saving profile picture', 'error')
                else:
                    flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')

        # Basic server-side validation
        errors = []
        if not fullname: 
            errors.append("Full Name is required.")
        if not email: 
            errors.append("Email is required.")
        # TODO: Add email format validation / check if email exists
        if not password or len(password) < 8: 
            errors.append("Password is required (min 8 chars).")
        if password != confirm_password: 
            errors.append("Passwords do not match.")
        if not timezone: 
            errors.append("Timezone is required.")
        if not qualification: 
            errors.append("Highest Qualification is required.")
        if not experience_str:
            errors.append("Years of Experience is required.")
        else:
            try:
                experience = float(experience_str)
                if experience < 0: 
                    errors.append("Experience cannot be negative.")
            except ValueError:
                errors.append("Invalid number for Years of Experience.")
        if not subjects: 
            errors.append("Please select at least one subject you can teach.")
        if not bio: 
            errors.append("Bio/Introduction is required.")
        if hourly_rate_str:  # Validate only if provided
            try:
                hourly_rate = float(hourly_rate_str)
                if hourly_rate < 0: 
                    errors.append("Hourly rate cannot be negative.")
            except ValueError:
                errors.append("Invalid number for Hourly Rate.")
        if not terms: 
            errors.append("You must agree to the Tutor Terms of Service.")

        if errors:
            for error in errors: 
                flash(error, 'error')
            # TODO: Re-populate form with previous data for better UX
            return redirect(url_for('tutor.signup_form'))

        # If validation passes
        # TODO: Hash password: hashed_password = generate_password_hash(password)
        # TODO: Store tutor data in DB, including profile_pic_filename if available
        
        # Log form data for development purposes
        if current_app.debug:
            print("--- Tutor Form Data Received ---")
            print(f"Tutor Full Name: {fullname}")
            print(f"Tutor Email: {email}")
            print(f"Timezone: {timezone}")
            print(f"Qualification: {qualification}")
            print(f"Experience: {experience_str}")
            print(f"Subjects: {subjects}")
            print(f"Bio: {bio[:50]}...")  # Print start of bio
            print(f"Hourly Rate: {hourly_rate_str}")
            print(f"Profile Pic Filename: {profile_pic_filename}")
            print(f"Terms Agreed: {terms}")
            print("--- End Tutor Form Data ---")

        flash('Tutor account created successfully! Your profile may be subject to review.', 'success')
        return redirect(url_for('main.index'))  # Or tutor dashboard/login page
        
    # If method is not POST
    return redirect(url_for('tutor.signup_form'))