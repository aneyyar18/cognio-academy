"""
Admin views for the TutorConnect application.
Contains routes for admin authentication, tutor verification, etc.
"""
from flask import (Blueprint, render_template, request, url_for, redirect, 
                  flash, current_app, session)
from sqlalchemy.exc import IntegrityError

from db import db
from models.admin import Admin
from models.tutor import Tutor, TutorStatus
from models.student import Student
from auth import login_user, login_required, role_required
from utils.file_handling import allowed_file, save_uploaded_file

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login')
def login_form():
    """Renders the admin login form."""
    return render_template('admin/login.html')

@admin_bp.route('/login', methods=['POST'])
def login_submit():
    """Handles admin login submission."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('admin.login_form'))
    
    # Find admin by email
    admin = Admin.query.filter_by(email=email).first()
    
    if admin and admin.verify_password(password):
        # Update last login and last action
        admin.update_last_login()
        admin.update_last_action()
        
        # Log the admin in
        login_user(admin.id, 'admin', admin.fullname)
        
        flash('Welcome to the admin panel!', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('admin.login_form'))

@admin_bp.route('/dashboard')
@login_required
@role_required(['admin'])
def dashboard():
    """Admin dashboard page."""
    # Get statistics
    pending_tutors_count = Tutor.query.filter_by(status=TutorStatus.PENDING).count()
    verified_tutors_count = Tutor.query.filter_by(status=TutorStatus.VERIFIED).count()
    denied_tutors_count = Tutor.query.filter_by(status=TutorStatus.DENIED).count()
    banned_tutors_count = Tutor.query.filter_by(status=TutorStatus.BANNED).count()
    total_students = Student.query.count()
    
    # Get recent tutor applications
    recent_applications = Tutor.query.filter_by(status=TutorStatus.PENDING)\
                                   .order_by(Tutor.created_at.desc())\
                                   .limit(5)\
                                   .all()
    
    stats = {
        'pending_tutors': pending_tutors_count,
        'verified_tutors': verified_tutors_count,
        'denied_tutors': denied_tutors_count,
        'banned_tutors': banned_tutors_count,
        'total_students': total_students,
        'total_tutors': pending_tutors_count + verified_tutors_count + denied_tutors_count + banned_tutors_count
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_applications=recent_applications)

@admin_bp.route('/tutors')
@login_required
@role_required(['admin'])
def tutors():
    """View all tutors with filtering options."""
    status_filter = request.args.get('status', 'all')
    
    query = Tutor.query
    
    if status_filter != 'all':
        try:
            status_enum = TutorStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            status_filter = 'all'
    
    tutors_list = query.order_by(Tutor.created_at.desc()).all()
    
    return render_template('admin/tutors.html', tutors=tutors_list, current_filter=status_filter)

@admin_bp.route('/tutor/<int:tutor_id>')
@login_required
@role_required(['admin'])
def tutor_detail(tutor_id):
    """View detailed information about a specific tutor."""
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template('admin/tutor_detail.html', tutor=tutor)

@admin_bp.route('/tutor/<int:tutor_id>/update_status', methods=['POST'])
@login_required
@role_required(['admin'])
def update_tutor_status(tutor_id):
    """Update tutor verification status."""
    tutor = Tutor.query.get_or_404(tutor_id)
    new_status = request.form.get('status')
    reason = request.form.get('reason', '')
    
    if not new_status:
        flash('Status is required.', 'error')
        return redirect(url_for('admin.tutor_detail', tutor_id=tutor_id))
    
    try:
        # Validate status
        status_enum = TutorStatus(new_status)
        old_status = tutor.status.value
        
        # Update tutor status
        admin_id = session.get('user_id')
        tutor.update_status(status_enum, admin_id)
        
        # Update admin's last action
        admin = Admin.query.get(admin_id)
        if admin:
            admin.update_last_action()
        
        # Log the action
        current_app.logger.info(f"Admin {admin_id} changed tutor {tutor_id} status from {old_status} to {new_status}")
        
        # Flash appropriate message
        if status_enum == TutorStatus.VERIFIED:
            flash(f'Tutor {tutor.fullname} has been verified and can now access the system.', 'success')
        elif status_enum == TutorStatus.DENIED:
            flash(f'Tutor {tutor.fullname} application has been denied.', 'info')
        elif status_enum == TutorStatus.BANNED:
            flash(f'Tutor {tutor.fullname} has been banned from the system.', 'warning')
        elif status_enum == TutorStatus.PENDING:
            flash(f'Tutor {tutor.fullname} status has been reset to pending.', 'info')
        
        # TODO: Send email notification to tutor about status change
        
    except ValueError:
        flash('Invalid status value.', 'error')
    except Exception as e:
        current_app.logger.error(f"Error updating tutor status: {str(e)}")
        flash('An error occurred while updating tutor status.', 'error')
    
    return redirect(url_for('admin.tutor_detail', tutor_id=tutor_id))

@admin_bp.route('/students')
@login_required
@role_required(['admin'])
def students():
    """View all students."""
    students_list = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students_list)

@admin_bp.route('/settings')
@login_required
@role_required(['admin'])
def settings():
    """Admin settings page."""
    admin_id = session.get('user_id')
    admin = Admin.query.get(admin_id)
    
    if not admin:
        flash('Admin profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('admin/settings.html', user=admin, active_section='profile')

@admin_bp.route('/settings/appearance')
@login_required
@role_required(['admin'])
def settings_appearance():
    """Admin settings page - Appearance section."""
    admin_id = session.get('user_id')
    admin = Admin.query.get(admin_id)
    
    if not admin:
        flash('Admin profile not found.', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('admin/settings.html', user=admin, active_section='appearance')

@admin_bp.route('/settings/profile/update', methods=['POST'])
@login_required
@role_required(['admin'])
def update_profile():
    """Update admin profile information."""
    admin_id = session.get('user_id')
    admin = Admin.query.get(admin_id)
    
    if not admin:
        flash('Admin profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    try:
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
                        admin.profile_pic = profile_pic_filename
                    else:
                        flash('Error saving profile picture', 'error')
                else:
                    flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating admin profile: {str(e)}")
        flash('An error occurred while updating your profile. Please try again.', 'error')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/logout')
@login_required
@role_required(['admin'])
def logout():
    """Admin logout."""
    # Clear session
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin.login_form'))