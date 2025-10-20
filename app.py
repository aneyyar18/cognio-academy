"""
Main application entry point for TutorConnect.
"""
from factory import create_app
from dotenv import load_dotenv
import os
load_dotenv()

# Create the application
app = create_app()

# Run the application
if __name__ == '__main__':
    # Debug=True allows auto-reloading and provides detailed error pages
    # Turn off debug mode in production!
    DEBUG = os.getenv("DEBUG", "False")
    app.run(debug=DEBUG, port=5001)