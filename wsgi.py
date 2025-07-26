"""
Main application entry point for TutorConnect.
"""
from factory import create_app
# wsgi.py
import sys
import os

# Add your project directory to the Python path
# If your Flask app is in a package, adjust this.
# Example: if app.py is directly in /var/www/your_flask_app_name
sys.path.insert(0, '/opt/cognio')
# Create the application
app = create_app()

# Run the application
if __name__ == '__main__':
    # Debug=True allows auto-reloading and provides detailed error pages
    # Turn off debug mode in production!
    app.run( port=5001)