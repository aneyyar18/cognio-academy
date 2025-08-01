"""
Tutor views for the TutorConnect application.
Contains routes for tutor registration, profile management, etc.
"""
from flask import (Blueprint, render_template, request, url_for, redirect, 
                  flash, current_app, session)
from flask_moment import Moment

from sqlalchemy.exc import IntegrityError

from db import db
from models.tutor import Tutor
from auth import login_user, login_required, role_required
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
            return redirect(url_for('tutor.signup_form'))

        try:
            # Create the tutor record
            tutor = Tutor.create(
                email=email,
                fullname=fullname,
                password=password,
                timezone=timezone,
                qualification=qualification,
                experience=experience_str,
                subjects_taught=subjects,
                bio=bio,
                phone=phone,
                hourly_rate=hourly_rate_str if hourly_rate_str else None,
                profile_pic=profile_pic_filename
            )
            
            # Log success
            current_app.logger.info(f"Tutor account created: {fullname}, {email}")
            
            # Flash success message and redirect to login
            flash('Tutor account created successfully! Your account is pending admin verification. You will be notified once approved.', 'success')
            return redirect(url_for('main.login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An account with that email already exists.', 'error')
            return redirect(url_for('tutor.signup_form'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating tutor account: {str(e)}")
            flash('An error occurred while creating your account. Please try again.', 'error')
            return redirect(url_for('tutor.signup_form'))
        
    # If method is not POST
    return redirect(url_for('tutor.signup_form'))


@tutor_bp.route('/dashboard')
@login_required
@role_required(['tutor'])
def dashboard():
    """Tutor dashboard page."""
    from models.message import Message
    
    # Get recent messages for this tutor
    tutor_id = session.get('user_id')
    recent_messages = Message.query.filter_by(receiver_id=tutor_id)\
                                  .order_by(Message.created_at.desc())\
                                  .limit(5)\
                                  .all()
    
    # Count unread messages
    unread_count = Message.query.filter_by(receiver_id=tutor_id, is_read=False).count()
    
    return render_template('tutor/dashboard.html', 
                         recent_messages=recent_messages, 
                         unread_count=unread_count)


@tutor_bp.route('/profile')
@login_required
@role_required(['tutor'])
def profile():
    """Tutor profile page."""
    # Get the current tutor from the database
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/profile.html', tutor=tutor)


@tutor_bp.route('/settings')
@login_required
@role_required(['tutor'])
def settings():
    """Tutor settings page - Profile section."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/settings.html', user=tutor, active_section='profile')


@tutor_bp.route('/settings/appearance')
@login_required
@role_required(['tutor'])
def settings_appearance():
    """Tutor settings page - Appearance section."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/settings.html', user=tutor, active_section='appearance')


@tutor_bp.route('/settings/notifications')
@login_required
@role_required(['tutor'])
def settings_notifications():
    """Tutor settings page - Notifications section."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/settings.html', user=tutor, active_section='notifications')


@tutor_bp.route('/settings/privacy')
@login_required
@role_required(['tutor'])
def settings_privacy():
    """Tutor settings page - Privacy section."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/settings.html', user=tutor, active_section='privacy')


@tutor_bp.route('/profile/edit')
@login_required
@role_required(['tutor'])
def edit_profile():
    """Show tutor profile edit form."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('tutor/edit_profile.html', tutor=tutor)


@tutor_bp.route('/profile/edit/submit', methods=['POST'])
@login_required
@role_required(['tutor'])
def edit_profile_submit():
    """Update tutor profile information."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Basic validation
    errors = []
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    bio = request.form.get('bio')
    qualification = request.form.get('qualification')
    experience_str = request.form.get('experience')
    subjects = request.form.getlist('subjects[]')
    timezone = request.form.get('timezone')
    
    if not fullname:
        errors.append("Full name is required.")
    if not email:
        errors.append("Email is required.")
    if not bio:
        errors.append("Bio is required.")
    if not qualification:
        errors.append("Qualification is required.")
    if not experience_str:
        errors.append("Experience is required.")
    elif not experience_str.replace('.', '').isdigit():
        errors.append("Experience must be a number.")
    if not subjects:
        errors.append("At least one subject is required.")
    if not timezone:
        errors.append("Timezone is required.")
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('tutor.edit_profile'))
    
    try:
        # Update profile fields
        tutor.fullname = fullname
        tutor.email = email
        tutor.phone = request.form.get('phone')
        tutor.timezone = timezone
        tutor.bio = bio
        tutor.qualification = qualification
        tutor.experience = float(experience_str)
        tutor.subjects_taught = ','.join(subjects)
        
        # Handle hourly rate if provided
        hourly_rate_str = request.form.get('hourly_rate')
        if hourly_rate_str:
            try:
                tutor.hourly_rate = float(hourly_rate_str)
            except ValueError:
                flash('Invalid hourly rate format.', 'error')
                return redirect(url_for('tutor.edit_profile'))
        
        # Handle profile picture upload if provided
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                if allowed_file(file.filename):
                    profile_pic_filename = save_uploaded_file(
                        file, 
                        current_app.config['UPLOAD_FOLDER']
                    )
                    if profile_pic_filename:
                        tutor.profile_pic = profile_pic_filename
                    else:
                        flash('Error saving profile picture', 'error')
                else:
                    flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('tutor.profile'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating tutor profile: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('tutor.edit_profile'))


@tutor_bp.route('/settings/profile/update', methods=['POST'])
@login_required
@role_required(['tutor'])
def update_profile():
    """Update tutor profile information from settings page."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Update profile fields
        tutor.fullname = request.form.get('fullname', tutor.fullname)
        tutor.email = request.form.get('email', tutor.email)
        tutor.phone = request.form.get('phone', tutor.phone)
        tutor.timezone = request.form.get('timezone', tutor.timezone)
        tutor.bio = request.form.get('bio', tutor.bio)
        tutor.qualification = request.form.get('qualification', tutor.qualification)
        
        # Handle experience
        experience_str = request.form.get('experience')
        if experience_str:
            try:
                tutor.experience = float(experience_str)
            except ValueError:
                pass  # Keep existing value if invalid
        
        # Handle subjects
        subjects = request.form.getlist('subjects[]')
        if subjects:
            tutor.subjects_taught = ','.join(subjects)
        
        # Handle hourly rate if provided
        hourly_rate_str = request.form.get('hourly_rate')
        if hourly_rate_str:
            try:
                tutor.hourly_rate = float(hourly_rate_str)
            except ValueError:
                pass  # Keep existing rate if invalid input
        
        # Handle profile picture upload if provided
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                if allowed_file(file.filename):
                    profile_pic_filename = save_uploaded_file(
                        file, 
                        current_app.config['UPLOAD_FOLDER']
                    )
                    if profile_pic_filename:
                        tutor.profile_pic = profile_pic_filename
                    else:
                        flash('Error saving profile picture', 'error')
                else:
                    flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating tutor profile: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('tutor.settings'))


@tutor_bp.route('/messages')
@login_required
@role_required(['tutor'])
def messages():
    """View all messages received by the tutor."""
    from models.message import Message
    
    tutor_id = session.get('user_id')
    
    # Get all messages for this tutor, ordered by creation date (newest first)
    all_messages = Message.query.filter_by(receiver_id=tutor_id)\
                                .order_by(Message.created_at.desc())\
                                .all()
    
    # Count unread messages
    unread_count = Message.query.filter_by(receiver_id=tutor_id, is_read=False).count()
    
    return render_template('tutor/messages.html', 
                         messages=all_messages, 
                         unread_count=unread_count)


@tutor_bp.route('/message/<int:message_id>')
@login_required
@role_required(['tutor'])
def view_message(message_id):
    """View a specific message and mark it as read."""
    from models.message import Message
    
    tutor_id = session.get('user_id')
    
    # Get the message and verify it belongs to this tutor
    message = Message.query.filter_by(id=message_id, receiver_id=tutor_id).first_or_404()
    
    # Mark as read if not already read
    if not message.is_read:
        message.mark_as_read()
    
    return render_template('tutor/message_detail.html', message=message)