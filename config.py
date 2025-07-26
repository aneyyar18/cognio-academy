import os

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Secret key for session management (change this in production!)
SECRET_KEY = 'change_this_later'

# Database configuration
#SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "SqliteDb/TutorConnect.db")}'
DB_USER = os.environ.get('DB_USER', 'cognio_admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin18') 
DB_INSTANCE = os.environ.get('DB_INSTANCE', 'cognio-db')
SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_INSTANCE}/cognio-db'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+mysqlconnector://cognio_admin:admin18@localhost:3306/cognio')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = True

# Authentication settings
AUTH_TOKEN_EXPIRY = 86400  # 24 hours in seconds

# OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')

# Email Configuration for Password Reset
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

# Password Reset Settings
RESET_TOKEN_EXPIRY = 3600  # 1 hour in seconds