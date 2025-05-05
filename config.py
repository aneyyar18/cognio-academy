import os

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/profile_pics'  # Create this folder structure
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Secret key for session management (change this!)
SECRET_KEY = 'change_this_later'