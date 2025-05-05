import os

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Secret key for session management (change this in production!)
SECRET_KEY = 'change_this_later'

# Database configuration
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "SqliteDb/TutorConnect.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Authentication settings
AUTH_TOKEN_EXPIRY = 86400  # 24 hours in seconds