"""
Main views for the TutorConnect application.
Contains routes for the homepage, about page, features page, etc.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app
from auth import authenticate_user, login_user
from db import db

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


@main_bp.route('/tutorsearch')
def tutorsearch():
    """Renders the tutor search page for finding tutors."""
    from models.tutor import Tutor
    from models.availability import TutorAvailability, DayOfWeek
    from datetime import time
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    subject_filter = request.args.get('subject', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    min_rating = request.args.get('min_rating', type=float)
    availability_day = request.args.get('availability_day', '')
    availability_start = request.args.get('availability_start', '')
    availability_end = request.args.get('availability_end', '')
    
    # Build query for tutors
    query = Tutor.query.filter(Tutor.is_active == True)
    
    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                Tutor.fullname.ilike(f'%{search}%'),
                Tutor.subjects_taught.ilike(f'%{search}%'),
                Tutor.bio.ilike(f'%{search}%')
            )
        )
    
    # Apply subject filter
    if subject_filter and subject_filter not in ['', 'All Subjects']:
        query = query.filter(Tutor.subjects_taught.ilike(f'%{subject_filter}%'))
    
    # Apply price filter
    if min_price is not None:
        query = query.filter(Tutor.hourly_rate >= min_price)
    if max_price is not None:
        query = query.filter(Tutor.hourly_rate <= max_price)
    
    # Apply rating filter
    if min_rating is not None:
        query = query.filter(Tutor.rating >= min_rating)
    
    # Apply availability filter
    if availability_day and availability_start and availability_end:
        try:
            # Convert day to enum
            day_enum = DayOfWeek[availability_day.upper()]
            start_hour, start_min = map(int, availability_start.split(':'))
            end_hour, end_min = map(int, availability_end.split(':'))
            start_time_obj = time(start_hour, start_min)
            end_time_obj = time(end_hour, end_min)
            
            # Find tutors with availability that overlaps the requested time
            available_tutor_ids = db.session.query(TutorAvailability.tutor_id).filter(
                TutorAvailability.day_of_week == day_enum,
                TutorAvailability.start_time <= start_time_obj,
                TutorAvailability.end_time >= end_time_obj,
                TutorAvailability.is_available == True
            ).distinct().all()
            
            if available_tutor_ids:
                tutor_ids = [tid[0] for tid in available_tutor_ids]
                query = query.filter(Tutor.id.in_(tutor_ids))
            else:
                # No tutors available at this time
                query = query.filter(db.false())
                
        except (ValueError, KeyError):
            # Invalid time format or day, ignore availability filter
            pass
    
    # Get all tutors ordered by rating (desc) then creation date (newest first)
    tutors = query.order_by(Tutor.rating.desc(), Tutor.created_at.desc()).all()
    
    # Get predefined subjects list for dropdown
    predefined_subjects = [
        'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English',
        'History', 'Geography', 'Computer Science', 'Economics',
        'Psychology', 'Statistics', 'Calculus', 'Algebra', 'Geometry',
        'French', 'Spanish', 'German', 'Art', 'Music', 'Philosophy'
    ]
    
    # Get unique subjects from current tutors to add to predefined list
    all_tutors = Tutor.query.filter(Tutor.is_active == True).all()
    current_subjects = set()
    for tutor in all_tutors:
        if tutor.subjects_taught:
            for subject in tutor.subjects_taught.split(','):
                current_subjects.add(subject.strip())
    
    # Combine and sort all subjects
    all_subjects = sorted(list(set(predefined_subjects + list(current_subjects))))
    
    return render_template('tutorsearch.html', tutors=tutors, subjects=all_subjects,
                         current_search=search, current_subject=subject_filter,
                         current_min_price=min_price, current_max_price=max_price,
                         current_min_rating=min_rating, current_availability_day=availability_day,
                         current_availability_start=availability_start, current_availability_end=availability_end)


@main_bp.route('/tutor/<int:tutor_id>')
def tutor_detail(tutor_id):
    """Display detailed information about a specific tutor."""
    from models.tutor import Tutor
    from models.availability import TutorAvailability

    tutor = Tutor.query.get_or_404(tutor_id)

    # Check if tutor is active
    if not tutor.is_active:
        flash('This tutor profile is not available.', 'error')
        return redirect(url_for('main.tutorsearch'))

    # Get tutor availability and convert to local timezone
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

    return render_template('tutor_detail.html', tutor=tutor, availability=availability)


@main_bp.route('/send_message', methods=['POST'])
def send_message():
    """Handle sending messages from students to tutors."""
    from models.message import Message
    from models.tutor import Tutor
    from auth import login_required, role_required
    
    # Check if user is logged in and is a student
    if 'user_id' not in session or session.get('user_role') != 'student':
        flash('You must be logged in as a student to send messages.', 'error')
        return redirect(url_for('main.login'))
    
    tutor_id = request.form.get('tutor_id')
    subject = request.form.get('subject')
    message_content = request.form.get('message')
    
    # Validation
    if not all([tutor_id, subject, message_content]):
        flash('All fields are required.', 'error')
        return redirect(request.referrer or url_for('main.tutorsearch'))
    
    # Verify tutor exists and is active
    tutor = Tutor.query.get(tutor_id)
    if not tutor or not tutor.is_active:
        flash('Tutor not found or not available.', 'error')
        return redirect(url_for('main.tutorsearch'))
    
    try:
        # Create the message
        message = Message.create(
            sender_id=session['user_id'],
            receiver_id=tutor_id,
            subject=subject.strip(),
            message=message_content.strip()
        )
        
        # Log success
        current_app.logger.info(f"Message sent from student {session['user_id']} to tutor {tutor_id}")
        
        flash(f'Your message has been sent to {tutor.fullname}!', 'success')
        return redirect(url_for('main.tutor_detail', tutor_id=tutor_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending message: {str(e)}")
        flash('An error occurred while sending your message. Please try again.', 'error')
        return redirect(url_for('main.tutor_detail', tutor_id=tutor_id))


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
        elif session['user_role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
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

        if user == 'unverified_tutor':
            # Special case for unverified tutors
            flash('Your tutor account is pending admin verification. Please wait for approval before logging in.', 'warning')
            current_app.logger.info(f"Unverified tutor attempted login: {email}")
            return render_template('login.html')
        elif user:
            # Log the user in
            login_user(user.id, user.role.value, user.fullname)
            
            # Update last login for the user
            user.update_last_login()
            
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
            elif user.role.value == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            # Log failed login attempt
            current_app.logger.warning(f"Failed login attempt for: {email}")
            flash('Invalid email or password.', 'error')

    # Render login form for GET requests and failed POST requests
    return render_template('login.html')