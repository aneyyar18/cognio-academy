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
from models.availability import TutorAvailability, DayOfWeek
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
    from models.booking import Booking, BookingStatus
    from datetime import date, timedelta

    # Get recent messages for this tutor
    tutor_id = session.get('user_id')
    recent_messages = Message.query.filter_by(receiver_id=tutor_id)\
                                  .order_by(Message.created_at.desc())\
                                  .limit(5)\
                                  .all()

    # Count unread messages
    unread_count = Message.query.filter_by(receiver_id=tutor_id, is_read=False).count()

    # Get upcoming bookings (next 14 days)
    today = date.today()
    end_date = today + timedelta(days=14)
    upcoming_bookings = Booking.get_tutor_bookings_for_date_range(tutor_id, today, end_date)

    # Sort by date and time
    upcoming_bookings.sort(key=lambda x: (x.booking_date, x.start_time))

    # Get counts by status
    pending_count = sum(1 for b in upcoming_bookings if b.status == BookingStatus.PENDING)
    confirmed_count = sum(1 for b in upcoming_bookings if b.status == BookingStatus.CONFIRMED)

    return render_template('tutor/dashboard.html',
                         recent_messages=recent_messages,
                         unread_count=unread_count,
                         upcoming_bookings=upcoming_bookings[:3],  # Show only 3 in dashboard
                         pending_count=pending_count,
                         confirmed_count=confirmed_count,
                         total_upcoming=len(upcoming_bookings))


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


@tutor_bp.route('/settings/availability')
@login_required
@role_required(['tutor'])
def settings_availability():
    """Tutor settings page - Availability section."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get current availability and convert to local timezone
    availability_slots = TutorAvailability.get_tutor_availability(tutor_id)
    availability = {}
    
    if availability_slots and tutor.timezone:
        for day, slots in availability_slots.items():
            day_name = day.name.lower()
            availability[day_name] = []
            for slot in slots:
                local_start, local_end = slot.get_local_times(tutor.timezone)
                availability[day_name].append({
                    'start_time_local': local_start.strftime('%H:%M'),
                    'end_time_local': local_end.strftime('%H:%M'),
                    'is_available': slot.is_available
                })
        
    return render_template('tutor/settings.html', 
                         user=tutor, 
                         active_section='availability',
                         availability=availability)


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


@tutor_bp.route('/settings/availability/update', methods=['POST'])
@login_required
@role_required(['tutor'])
def update_availability():
    """Update tutor availability settings."""
    tutor_id = session.get('user_id')
    tutor = Tutor.query.get(tutor_id)
    
    if not tutor:
        flash('Tutor profile not found.', 'error')
        return redirect(url_for('main.index'))
    
    if not tutor.timezone:
        flash('Please set your timezone in profile settings before setting availability.', 'error')
        return redirect(url_for('tutor.settings_availability'))
    
    try:
        # Parse availability data from form
        availability_data = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            enabled_key = f'{day}-enabled'
            if enabled_key in request.form:  # Day is enabled
                start_times = request.form.getlist(f'{day}-start-time[]')
                end_times = request.form.getlist(f'{day}-end-time[]')
                
                if start_times and end_times and len(start_times) == len(end_times):
                    availability_data[day] = []
                    for start_time, end_time in zip(start_times, end_times):
                        # Validate time format and logic
                        if start_time and end_time and start_time < end_time:
                            availability_data[day].append({
                                'start_time': start_time,
                                'end_time': end_time,
                                'is_available': True
                            })
        
        # Update availability using the model method
        TutorAvailability.update_tutor_availability(
            tutor_id=tutor_id,
            availability_data=availability_data,
            tutor_timezone=tutor.timezone
        )
        
        flash('Availability updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating availability: {str(e)}")
        flash('An error occurred while updating your availability. Please try again.', 'error')
    
    return redirect(url_for('tutor.settings_availability'))


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


@tutor_bp.route('/bookings')
@login_required
@role_required(['tutor'])
def bookings():
    """View all bookings for the tutor with pagination."""
    from models.booking import Booking, BookingStatus

    tutor_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Get paginated bookings for this tutor, ordered by date (newest first)
    pagination_obj = Booking.query.filter_by(tutor_id=tutor_id)\
                                   .order_by(Booking.booking_date.desc(),
                                            Booking.start_time.desc())\
                                   .paginate(page=page, per_page=per_page, error_out=False)

    # Get all bookings for status counts
    all_bookings = Booking.query.filter_by(tutor_id=tutor_id).all()
    pending_count = sum(1 for b in all_bookings if b.status == BookingStatus.PENDING)
    confirmed_count = sum(1 for b in all_bookings if b.status == BookingStatus.CONFIRMED)
    completed_count = sum(1 for b in all_bookings if b.status == BookingStatus.COMPLETED)

    # Create pagination info
    pagination = {
        'page': page,
        'pages': pagination_obj.pages,
        'total': pagination_obj.total,
        'has_prev': pagination_obj.has_prev,
        'has_next': pagination_obj.has_next,
        'prev_num': pagination_obj.prev_num,
        'next_num': pagination_obj.next_num,
        'start_index': (page - 1) * per_page + 1 if pagination_obj.items else 0,
        'end_index': min(page * per_page, pagination_obj.total),
        'iter_pages': lambda **kwargs: pagination_obj.iter_pages(**kwargs)
    }

    return render_template('tutor/bookings.html',
                         bookings=pagination_obj.items,
                         pagination=pagination,
                         total_bookings=len(all_bookings),
                         pending_count=pending_count,
                         confirmed_count=confirmed_count,
                         completed_count=completed_count)


@tutor_bp.route('/booking/<int:booking_id>')
@login_required
@role_required(['tutor'])
def booking_detail(booking_id):
    """View details of a specific booking."""
    from models.booking import Booking
    from datetime import date, timedelta

    tutor_id = session.get('user_id')

    # Get the booking and verify it belongs to this tutor
    booking = Booking.query.filter_by(id=booking_id, tutor_id=tutor_id).first_or_404()

    # Calculate duration
    from datetime import datetime
    start_datetime = datetime.combine(booking.booking_date, booking.start_time)
    end_datetime = datetime.combine(booking.booking_date, booking.end_time)
    duration = int((end_datetime - start_datetime).total_seconds() / 60)

    # Calculate min and max dates for rescheduling (1-14 days from today)
    today = date.today()
    min_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    max_date = (today + timedelta(days=14)).strftime('%Y-%m-%d')

    return render_template('tutor/booking_detail.html',
                         booking=booking,
                         duration=duration,
                         min_date=min_date,
                         max_date=max_date)


@tutor_bp.route('/booking/<int:booking_id>/confirm', methods=['POST'])
@login_required
@role_required(['tutor'])
def confirm_booking(booking_id):
    """Confirm a booking."""
    from models.booking import Booking

    tutor_id = session.get('user_id')

    # Get the booking and verify it belongs to this tutor
    booking = Booking.query.filter_by(id=booking_id, tutor_id=tutor_id).first_or_404()

    try:
        booking.confirm()
        flash('Booking confirmed successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"Error confirming booking: {str(e)}")
        flash('An error occurred while confirming the booking.', 'error')

    return redirect(url_for('tutor.booking_detail', booking_id=booking_id))


@tutor_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required(['tutor'])
def cancel_booking(booking_id):
    """Cancel a booking."""
    from models.booking import Booking

    tutor_id = session.get('user_id')

    # Get the booking and verify it belongs to this tutor
    booking = Booking.query.filter_by(id=booking_id, tutor_id=tutor_id).first_or_404()

    try:
        booking.cancel()
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error cancelling booking: {str(e)}")
        flash('An error occurred while cancelling the booking.', 'error')

    return redirect(url_for('tutor.bookings'))


@tutor_bp.route('/booking/<int:booking_id>/reschedule', methods=['POST'])
@login_required
@role_required(['tutor'])
def reschedule_booking(booking_id):
    """Reschedule a booking."""
    from models.booking import Booking
    from datetime import datetime, date, timedelta

    tutor_id = session.get('user_id')

    # Get the booking and verify it belongs to this tutor
    booking = Booking.query.filter_by(id=booking_id, tutor_id=tutor_id).first_or_404()

    try:
        # Get new date and times from form
        new_date_str = request.form.get('new_date')
        new_start_time_str = request.form.get('new_start_time')
        new_end_time_str = request.form.get('new_end_time')

        if not all([new_date_str, new_start_time_str, new_end_time_str]):
            flash('Please provide all date and time fields.', 'error')
            return redirect(url_for('tutor.booking_detail', booking_id=booking_id))

        # Parse new date
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()

        # Validate new date (1-14 days from today)
        today = date.today()
        min_date = today + timedelta(days=1)
        max_date = today + timedelta(days=14)

        if new_date < min_date:
            flash('Cannot reschedule within 24 hours. Please select a future date.', 'error')
            return redirect(url_for('tutor.booking_detail', booking_id=booking_id))

        if new_date > max_date:
            flash('Cannot reschedule more than 14 days in advance.', 'error')
            return redirect(url_for('tutor.booking_detail', booking_id=booking_id))

        # Parse new times
        new_start_hour, new_start_min = map(int, new_start_time_str.split(':'))
        new_end_hour, new_end_min = map(int, new_end_time_str.split(':'))
        from datetime import time
        new_start_time = time(new_start_hour, new_start_min)
        new_end_time = time(new_end_hour, new_end_min)

        if new_start_time >= new_end_time:
            flash('End time must be after start time.', 'error')
            return redirect(url_for('tutor.booking_detail', booking_id=booking_id))

        # Check for conflicts with other bookings
        from sqlalchemy import and_
        from models.booking import BookingStatus

        conflict = Booking.query.filter(
            and_(
                Booking.tutor_id == tutor_id,
                Booking.id != booking_id,  # Exclude current booking
                Booking.booking_date == new_date,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                and_(
                    Booking.start_time < new_end_time,
                    Booking.end_time > new_start_time
                )
            )
        ).first()

        if conflict:
            flash('This time slot conflicts with another booking.', 'error')
            return redirect(url_for('tutor.booking_detail', booking_id=booking_id))

        # Update the booking
        booking.booking_date = new_date
        booking.start_time = new_start_time
        booking.end_time = new_end_time
        booking.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Booking rescheduled successfully!', 'success')

    except ValueError as e:
        flash('Invalid date or time format.', 'error')
        current_app.logger.error(f"Error parsing reschedule data: {str(e)}")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rescheduling booking: {str(e)}")
        flash('An error occurred while rescheduling the booking.', 'error')

    return redirect(url_for('tutor.booking_detail', booking_id=booking_id))