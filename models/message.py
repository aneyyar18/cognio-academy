"""
Message model for TutorConnect application.
Handles messaging between students and tutors.
"""
import datetime
from db import db

class Message(db.Model):
    """Message model for communication between students and tutors."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sender and receiver information
    sender_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('tutors.id', ondelete='CASCADE'), nullable=False)
    
    # Message content
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Message status
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sender = db.relationship('Student', backref='sent_messages', foreign_keys=[sender_id])
    receiver = db.relationship('Tutor', backref='received_messages', foreign_keys=[receiver_id])
    
    @classmethod
    def create(cls, sender_id, receiver_id, subject, message):
        """
        Create a new message.
        
        Args:
            sender_id (int): ID of the student sending the message
            receiver_id (int): ID of the tutor receiving the message
            subject (str): Message subject
            message (str): Message content
            
        Returns:
            Message: The newly created message object
        """
        new_message = cls(
            sender_id=sender_id,
            receiver_id=receiver_id,
            subject=subject,
            message=message
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return new_message
    
    def mark_as_read(self):
        """Mark the message as read and set read timestamp."""
        self.is_read = True
        self.read_at = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert the message object to a dictionary."""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'sender_name': self.sender.fullname if self.sender else 'Unknown',
            'receiver_name': self.receiver.fullname if self.receiver else 'Unknown',
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id}: {self.subject[:50]}...>'