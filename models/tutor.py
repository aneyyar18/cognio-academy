"""
Tutor model for TutorConnect application.
"""
import decimal
from db import db
from models.user import User, UserRole

class Tutor(User):
    """Tutor user model extending the base User model."""
    __tablename__ = 'tutors'
    
    # Override role to set it as TUTOR
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.TUTOR)
    
    # Tutor-specific fields
    qualification = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Float, nullable=False)  # Years of experience
    subjects_taught = db.Column(db.String(255), nullable=False)  # Comma-separated list
    bio = db.Column(db.Text, nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)  # Decimal field for currency
    profile_pic = db.Column(db.String(255), nullable=True)  # Path to profile picture
    
    @classmethod
    def create(cls, email, fullname, password, timezone, qualification, experience, subjects_taught, bio,
               phone=None, hourly_rate=None, profile_pic=None):
        """
        Create a new tutor user.
        
        Args:
            email (str): Email address
            fullname (str): Full name
            password (str): Password (will be hashed)
            timezone (str): Timezone
            qualification (str): Highest qualification
            experience (float): Years of experience
            subjects_taught (list): List of subjects taught
            bio (str): Bio/introduction
            phone (str, optional): Phone number
            hourly_rate (float, optional): Hourly rate
            profile_pic (str, optional): Path to profile picture
            
        Returns:
            Tutor: The newly created tutor object
        """
        tutor = cls(
            email=email,
            fullname=fullname,
            timezone=timezone,
            phone=phone,
            qualification=qualification,
            experience=float(experience),
            subjects_taught=','.join(subjects_taught) if isinstance(subjects_taught, list) else subjects_taught,
            bio=bio,
            hourly_rate=decimal.Decimal(str(hourly_rate)) if hourly_rate else None,
            profile_pic=profile_pic
        )
        tutor.password = password  # This will hash the password
        
        db.session.add(tutor)
        db.session.commit()
        
        return tutor
    
    def to_dict(self):
        """Convert the tutor object to a dictionary."""
        base_dict = super().to_dict()
        tutor_dict = {
            'qualification': self.qualification,
            'experience': self.experience,
            'subjects_taught': self.subjects_taught.split(',') if self.subjects_taught else [],
            'bio': self.bio,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'profile_pic': self.profile_pic
        }
        return {**base_dict, **tutor_dict}