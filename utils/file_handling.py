"""
Utilities for file handling in the TutorConnect application.
"""
import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions=None):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): The name of the file to check
        allowed_extensions (set, optional): Set of allowed extensions. 
            If None, uses the app config's ALLOWED_EXTENSIONS.
    
    Returns:
        bool: True if file is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder=None, custom_filename=None):
    """
    Save an uploaded file with a secure filename.
    
    Args:
        file: The file from request.files
        upload_folder (str, optional): The folder to save to.
            If None, uses the app config's UPLOAD_FOLDER.
        custom_filename (str, optional): Custom filename to use.
            If None, uses the original filename.
    
    Returns:
        str or None: The saved filename or None if saving failed
    """
    if not file or not file.filename:
        return None
        
    if upload_folder is None:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Create secure filename
    if custom_filename:
        filename = secure_filename(custom_filename)
    else:
        filename = secure_filename(file.filename)
        
    try:
        file.save(os.path.join(upload_folder, filename))
        return filename
    except Exception as e:
        current_app.logger.error(f"File save error: {str(e)}")
        return None