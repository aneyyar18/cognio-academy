"""
Student views for the TutorConnect application.
Contains routes for student registration, profile management, etc.
"""
from flask import (Blueprint, render_template, request, url_for, redirect, 
                  flash, current_app, session)
from sqlalchemy.exc import IntegrityError

from db import db
from models.student import Student
from auth import login_user, login_required, role_required

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
        phone = request.form.get('phone')
        study_level = request.form.get('study-level')
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
        if confirm_password != password:
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

        try:
            # Create the student record
            student = Student.create(
                email=email,
                fullname=fullname,
                password=password,
                timezone=timezone,
                dob=dob,
                phone=phone,
                study_level=study_level,
                subjects_interested=subjects,
                learning_goals=learning_goals
            )
            
            # Log success
            current_app.logger.info(f"Student account created: {fullname}, {email}")
            
            # Flash success message and redirect to login
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('main.login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('student.signup_form'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating student account: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'error')
            return redirect(url_for('student.signup_form'))

    # If method is not POST (shouldn't happen with route definition)
    return redirect(url_for('student.signup_form'))


@student_bp.route('/dashboard')
@login_required
@role_required(['student'])
def dashboard():
    """Student dashboard page."""
    return render_template('student/dashboard.html')


@student_bp.route('/profile')
@login_required
@role_required(['student'])
def profile():
    """Student profile page."""
    # Get the current student from the database
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/profile.html', student=student)


@student_bp.route('/settings')
@login_required
@role_required(['student'])
def settings():
    """Student settings page - Profile section."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/settings.html', user=student, active_section='profile')


@student_bp.route('/settings/appearance')
@login_required
@role_required(['student'])
def settings_appearance():
    """Student settings page - Appearance section."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/settings.html', user=student, active_section='appearance')


@student_bp.route('/settings/notifications')
@login_required
@role_required(['student'])
def settings_notifications():
    """Student settings page - Notifications section."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/settings.html', user=student, active_section='notifications')


@student_bp.route('/settings/privacy')
@login_required
@role_required(['student'])
def settings_privacy():
    """Student settings page - Privacy section."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/settings.html', user=student, active_section='privacy')


@student_bp.route('/profile/edit')
@login_required
@role_required(['student'])
def edit_profile():
    """Show student profile edit form."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('student/edit_profile.html', student=student)


@student_bp.route('/profile/edit/submit', methods=['POST'])
@login_required
@role_required(['student'])
def edit_profile_submit():
    """Update student profile information."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Basic validation
    errors = []
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    dob = request.form.get('dob')
    timezone = request.form.get('timezone')
    
    if not fullname:
        errors.append("Full name is required.")
    if not email:
        errors.append("Email is required.")
    if not dob:
        errors.append("Date of birth is required.")
    if not timezone:
        errors.append("Timezone is required.")
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('student.edit_profile'))
    
    try:
        # Update profile fields
        student.fullname = fullname
        student.email = email
        student.phone = request.form.get('phone')
        student.timezone = timezone
        student.study_level = request.form.get('study_level')
        student.learning_goals = request.form.get('learning_goals')
        
        # Handle subjects interested
        subjects = request.form.getlist('subjects[]')
        if subjects:
            student.subjects_interested = ','.join(subjects)
        
        # Handle date of birth
        if dob:
            from datetime import datetime
            try:
                student.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth.', 'error')
                return redirect(url_for('student.edit_profile'))
        
        # Handle profile picture upload if provided
        from utils.file_handling import allowed_file, save_uploaded_file
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                if allowed_file(file.filename):
                    profile_pic_filename = save_uploaded_file(
                        file, 
                        current_app.config['UPLOAD_FOLDER']
                    )
                    if profile_pic_filename:
                        student.profile_pic = profile_pic_filename
                    else:
                        flash('Error saving profile picture', 'error')
                else:
                    flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating student profile: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('student.edit_profile'))


@student_bp.route('/settings/profile/update', methods=['POST'])
@login_required
@role_required(['student'])
def update_profile():
    """Update student profile information from settings page."""
    student_id = session.get('user_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Update profile fields
        student.fullname = request.form.get('fullname', student.fullname)
        student.email = request.form.get('email', student.email)
        student.phone = request.form.get('phone', student.phone)
        student.timezone = request.form.get('timezone', student.timezone)
        student.study_level = request.form.get('study_level', student.study_level)
        student.learning_goals = request.form.get('learning_goals', student.learning_goals)
        
        # Handle subjects interested
        subjects = request.form.getlist('subjects[]')
        if subjects:
            student.subjects_interested = ','.join(subjects)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating student profile: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('student.settings'))