"""
Booking model for TutorConnect application.
Handles appointment bookings between students and tutors.
"""
from datetime import datetime, timedelta
from enum import Enum
from db import db
from sqlalchemy import and_


class BookingStatus(Enum):
    """Enum for booking status."""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'


class Booking(db.Model):
    """Model to store appointment bookings between students and tutors."""
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)  # Date of the appointment
    start_time = db.Column(db.Time, nullable=False)    # Start time in GMT
    end_time = db.Column(db.Time, nullable=False)      # End time in GMT
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    subject = db.Column(db.String(100), nullable=True)  # Subject for the session
    notes = db.Column(db.Text, nullable=True)           # Additional notes from student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('bookings', lazy=True))
    tutor = db.relationship('Tutor', backref=db.backref('tutor_bookings', lazy=True))

    def __init__(self, student_id, tutor_id, booking_date, start_time, end_time,
                 subject=None, notes=None, status=BookingStatus.PENDING):
        """Initialize a booking."""
        self.student_id = student_id
        self.tutor_id = tutor_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.notes = notes
        self.status = status

    @classmethod
    def create_booking(cls, student_id, tutor_id, booking_date, start_time_str,
                      end_time_str, subject=None, notes=None):
        """
        Create a new booking with validation.

        Args:
            student_id (int): Student's ID
            tutor_id (int): Tutor's ID
            booking_date (date): Date of appointment
            start_time_str (str): Start time in 'HH:MM' format
            end_time_str (str): End time in 'HH:MM' format
            subject (str): Subject for the session
            notes (str): Additional notes

        Returns:
            tuple: (booking, error_message) - booking is None if validation fails
        """
        from datetime import time, date

        # Validate booking date
        today = date.today()
        min_booking_date = today + timedelta(days=1)  # Cannot book within 24 hours
        max_booking_date = today + timedelta(days=14)  # Maximum 14 days in advance

        if booking_date < min_booking_date:
            return None, "Cannot book appointments within 24 hours. Please select a future date."

        if booking_date > max_booking_date:
            return None, "Cannot book appointments more than 14 days in advance."

        # Parse time strings
        try:
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            start_time = time(start_hour, start_min)
            end_time = time(end_hour, end_min)
        except ValueError:
            return None, "Invalid time format."

        if start_time >= end_time:
            return None, "End time must be after start time."

        # Check for existing bookings (no double booking)
        existing_booking = cls.query.filter(
            and_(
                cls.tutor_id == tutor_id,
                cls.booking_date == booking_date,
                cls.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                # Check for time overlap
                and_(
                    cls.start_time < end_time,
                    cls.end_time > start_time
                )
            )
        ).first()

        if existing_booking:
            return None, "This time slot is already booked."

        # Create the booking
        booking = cls(
            student_id=student_id,
            tutor_id=tutor_id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            subject=subject,
            notes=notes
        )

        try:
            db.session.add(booking)
            db.session.commit()
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating booking: {str(e)}"

    @classmethod
    def get_tutor_bookings_for_date_range(cls, tutor_id, start_date, end_date):
        """Get all bookings for a tutor within a date range."""
        return cls.query.filter(
            and_(
                cls.tutor_id == tutor_id,
                cls.booking_date >= start_date,
                cls.booking_date <= end_date,
                cls.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        ).all()

    @classmethod
    def get_student_bookings(cls, student_id):
        """Get all bookings for a student."""
        return cls.query.filter_by(student_id=student_id)\
                        .order_by(cls.booking_date.desc(), cls.start_time.desc())\
                        .all()

    def get_local_times(self, timezone_str):
        """
        Convert GMT times to local timezone.

        Args:
            timezone_str (str): Timezone string

        Returns:
            tuple: (local_start_time, local_end_time)
        """
        import pytz
        from datetime import datetime, time

        tz = pytz.timezone(timezone_str)

        # Create datetime objects in GMT
        dummy_date = datetime.now().replace(hour=self.start_time.hour,
                                          minute=self.start_time.minute)
        gmt_start = pytz.UTC.localize(dummy_date)
        local_start = gmt_start.astimezone(tz)

        dummy_date_end = datetime.now().replace(hour=self.end_time.hour,
                                              minute=self.end_time.minute)
        gmt_end = pytz.UTC.localize(dummy_date_end)
        local_end = gmt_end.astimezone(tz)

        return (time(local_start.hour, local_start.minute),
                time(local_end.hour, local_end.minute))

    def cancel(self):
        """Cancel this booking."""
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def confirm(self):
        """Confirm this booking."""
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self, include_timezone=None):
        """Convert booking to dictionary."""
        result = {
            'id': self.id,
            'student_id': self.student_id,
            'tutor_id': self.tutor_id,
            'booking_date': self.booking_date.strftime('%Y-%m-%d'),
            'start_time_gmt': self.start_time.strftime('%H:%M'),
            'end_time_gmt': self.end_time.strftime('%H:%M'),
            'status': self.status.value,
            'subject': self.subject,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_timezone:
            local_start, local_end = self.get_local_times(include_timezone)
            result['start_time_local'] = local_start.strftime('%H:%M')
            result['end_time_local'] = local_end.strftime('%H:%M')

        return result

    def __repr__(self):
        return f'<Booking {self.id} - {self.booking_date} {self.start_time}-{self.end_time}>'