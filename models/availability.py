"""
Tutor availability model for TutorConnect application.
"""
from enum import Enum
from datetime import time, datetime
from db import db
from models.tutor import Tutor
import pytz

class DayOfWeek(Enum):
    """Enum for days of the week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class TutorAvailability(db.Model):
    """Model to store tutor availability for each day of the week."""
    __tablename__ = 'tutor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'), nullable=False)
    day_of_week = db.Column(db.Enum(DayOfWeek), nullable=False)
    start_time = db.Column(db.Time, nullable=False)  # Time in GMT
    end_time = db.Column(db.Time, nullable=False)    # Time in GMT
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to tutor
    tutor = db.relationship('Tutor', backref=db.backref('availability_slots', lazy=True))
    
    def __init__(self, tutor_id, day_of_week, start_time, end_time, is_available=True):
        """Initialize availability slot."""
        self.tutor_id = tutor_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available
    
    @classmethod
    def create_availability_slot(cls, tutor_id, day_of_week, start_time_str, end_time_str, 
                               tutor_timezone, is_available=True):
        """
        Create an availability slot converting from tutor's timezone to GMT.
        
        Args:
            tutor_id (int): The tutor's ID
            day_of_week (DayOfWeek): Day of the week
            start_time_str (str): Start time in 'HH:MM' format
            end_time_str (str): End time in 'HH:MM' format
            tutor_timezone (str): Tutor's timezone (e.g., 'US/Eastern')
            is_available (bool): Whether the slot is available
            
        Returns:
            TutorAvailability: The created availability slot
        """
        # Parse time strings
        start_hour, start_min = map(int, start_time_str.split(':'))
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        # Create time objects in tutor's timezone
        tutor_tz = pytz.timezone(tutor_timezone)
        
        # Create a dummy date to work with timezone conversion
        dummy_date = datetime.now().replace(hour=start_hour, minute=start_min, 
                                          second=0, microsecond=0)
        
        # Localize to tutor's timezone and convert to GMT
        localized_start = tutor_tz.localize(dummy_date)
        gmt_start = localized_start.astimezone(pytz.UTC)
        
        dummy_date_end = datetime.now().replace(hour=end_hour, minute=end_min, 
                                              second=0, microsecond=0)
        localized_end = tutor_tz.localize(dummy_date_end)
        gmt_end = localized_end.astimezone(pytz.UTC)
        
        # Extract time components
        start_time_gmt = time(gmt_start.hour, gmt_start.minute)
        end_time_gmt = time(gmt_end.hour, gmt_end.minute)
        
        availability = cls(
            tutor_id=tutor_id,
            day_of_week=day_of_week,
            start_time=start_time_gmt,
            end_time=end_time_gmt,
            is_available=is_available
        )
        
        db.session.add(availability)
        db.session.commit()
        return availability
    
    def get_local_times(self, tutor_timezone):
        """
        Convert GMT times back to tutor's local timezone.
        
        Args:
            tutor_timezone (str): Tutor's timezone
            
        Returns:
            tuple: (local_start_time, local_end_time) as time objects
        """
        tutor_tz = pytz.timezone(tutor_timezone)
        
        # Create datetime objects in GMT
        dummy_date = datetime.now().replace(hour=self.start_time.hour, 
                                          minute=self.start_time.minute)
        gmt_start = pytz.UTC.localize(dummy_date)
        local_start = gmt_start.astimezone(tutor_tz)
        
        dummy_date_end = datetime.now().replace(hour=self.end_time.hour, 
                                              minute=self.end_time.minute)
        gmt_end = pytz.UTC.localize(dummy_date_end)
        local_end = gmt_end.astimezone(tutor_tz)
        
        return (time(local_start.hour, local_start.minute), 
                time(local_end.hour, local_end.minute))
    
    @classmethod
    def get_tutor_availability(cls, tutor_id):
        """Get all availability slots for a tutor grouped by day."""
        slots = cls.query.filter_by(tutor_id=tutor_id).all()
        
        # Group by day of week
        availability_by_day = {}
        for slot in slots:
            day = slot.day_of_week
            if day not in availability_by_day:
                availability_by_day[day] = []
            availability_by_day[day].append(slot)
        
        return availability_by_day
    
    @classmethod
    def update_tutor_availability(cls, tutor_id, availability_data, tutor_timezone):
        """
        Update all availability slots for a tutor.
        
        Args:
            tutor_id (int): The tutor's ID
            availability_data (dict): Dictionary with day as key and list of time slots
            tutor_timezone (str): Tutor's timezone
        """
        # Delete existing availability
        cls.query.filter_by(tutor_id=tutor_id).delete()
        
        # Create new availability slots
        for day_name, slots in availability_data.items():
            if not slots:  # Skip if no slots for this day
                continue
                
            # Convert day name to enum
            day_enum = DayOfWeek[day_name.upper()]
            
            for slot in slots:
                if slot.get('is_available', False):
                    cls.create_availability_slot(
                        tutor_id=tutor_id,
                        day_of_week=day_enum,
                        start_time_str=slot['start_time'],
                        end_time_str=slot['end_time'],
                        tutor_timezone=tutor_timezone,
                        is_available=True
                    )
        
        db.session.commit()
    
    def to_dict(self, tutor_timezone=None):
        """Convert availability slot to dictionary."""
        result = {
            'id': self.id,
            'day_of_week': self.day_of_week.name.lower(),
            'start_time_gmt': self.start_time.strftime('%H:%M'),
            'end_time_gmt': self.end_time.strftime('%H:%M'),
            'is_available': self.is_available
        }
        
        if tutor_timezone:
            local_start, local_end = self.get_local_times(tutor_timezone)
            result['start_time_local'] = local_start.strftime('%H:%M')
            result['end_time_local'] = local_end.strftime('%H:%M')
        
        return result
    
    def __repr__(self):
        return f'<TutorAvailability {self.day_of_week.name} {self.start_time}-{self.end_time}>'