"""
Student model for TutorConnect application.
"""
import datetime
from flask import url_for, current_app
from db import db
from models.user import User, UserRole

class Student(User):
    """Student user model extending the base User model."""
    __tablename__ = 'students'
    
    # Override role to set it as STUDENT
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # Student-specific fields
    dob = db.Column(db.Date, nullable=False)
    study_level = db.Column(db.String(50), nullable=True)
    subjects_interested = db.Column(db.String(255), nullable=True)  # Comma-separated list
    learning_goals = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)  # Path to profile picture
    
    @property
    def profile_picture_url(self):
        """Generate the full URL for the profile picture using config directory."""
        if self.profile_pic:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads/profile_pics')
            return url_for('static', filename=f'{upload_folder.replace("static/", "")}/{self.profile_pic}')
        return None
    
    @classmethod
    def create(cls, email, fullname, password, timezone, dob, 
              phone=None, study_level=None, subjects_interested=None, learning_goals=None):
        """
        Create a new student user.
        
        Args:
            email (str): Email address
            fullname (str): Full name
            password (str): Password (will be hashed)
            timezone (str): Timezone
            dob (str): Date of birth (YYYY-MM-DD)
            phone (str, optional): Phone number
            study_level (str, optional): Current study level
            subjects_interested (list, optional): List of subjects interested in
            learning_goals (str, optional): Learning goals
            
        Returns:
            Student: The newly created student object
        """
        student = cls(
            email=email,
            fullname=fullname,
            timezone=timezone,
            phone=phone,
            dob=datetime.datetime.strptime(dob, '%Y-%m-%d').date() if isinstance(dob, str) else dob,
            study_level=study_level,
            subjects_interested=','.join(subjects_interested) if subjects_interested else None,
            learning_goals=learning_goals
        )
        student.password = password  # This will hash the password
        
        db.session.add(student)
        db.session.commit()
        
        return student
    
    def to_dict(self):
        """Convert the student object to a dictionary."""
        base_dict = super().to_dict()
        student_dict = {
            'dob': self.dob.isoformat() if self.dob else None,
            'study_level': self.study_level,
            'subjects_interested': self.subjects_interested.split(',') if self.subjects_interested else [],
            'learning_goals': self.learning_goals
        }
        return {**base_dict, **student_dict}