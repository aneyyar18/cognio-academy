# app.py
from flask import Flask, render_template, request, url_for, redirect, flash
import os

from werkzeug.utils import secure_filename  # For secure file handling

# from werkzeug.security import generate_password_hash # Import if using password hashing

# Initialize the Flask application
app = Flask(__name__)
# Secret key is needed for flashing messages
app.secret_key = 'your_very_secret_key'  # Change this in production!
app.config.from_object('config')


# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Route for the homepage (index.html)
@app.route('/')
def index():
    """Renders the homepage."""
    print("Serving homepage (index.html).")
    # Make sure you have an 'index.html' file in your 'templates' folder
    # This should be the homepage UI created earlier.
    return render_template('index.html')  # Changed from redirect


# Route to display the student signup page
@app.route('/signup/student')
def signup_student_form():
    """Renders the student signup form."""
    print("Serving signup form page.")
    return render_template('student_signup.html')


# Route to handle the form submission
@app.route('/signup/student/submit', methods=['POST'])
def signup_student_submit():
    """Handles the submission of the student signup form."""
    if request.method == 'POST':
        # Extract form data (add more fields as needed)
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        dob = request.form.get('dob')
        timezone = request.form.get('timezone')
        subjects = request.form.getlist('subjects[]')  # Get list for checkboxes
        learning_goals = request.form.get('learning-goals')
        terms = request.form.get('terms')

        # --- Basic Server-Side Validation (Example) ---
        errors = []
        if not fullname:
            errors.append("Full Name is required.")
        if not email:
            errors.append("Email is required.")
        if not password or len(password) < 8:
            errors.append("Password is required and must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not dob:
            errors.append("Date of Birth is required.")
        if not timezone:
            errors.append("Timezone is required.")
        if not terms:
            errors.append("You must agree to the Terms of Service and Privacy Policy.")

        if errors:
            # If there are errors, flash them and re-render the form
            for error in errors:
                flash(error, 'error')  # Use 'error' category for styling if desired
            # Re-populate form with previous data (optional, good UX)
            # For simplicity, just re-rendering the blank form here
            return redirect(url_for('signup_student_form'))

        # --- If Validation Passes ---
        # 1. TODO: Securely hash the password before storing
        # hashed_password = generate_password_hash(password) # Example using Werkzeug

        # 2. TODO: Store the user data in your database
        print("--- Form Data Received ---")
        print(f"Full Name: {fullname}")
        print(f"Email: {email}")
        print(f"DOB: {dob}")
        print(f"Timezone: {timezone}")
        print(f"Subjects: {subjects}")
        print(f"Goals: {learning_goals}")
        print(f"Terms Agreed: {terms}")
        print("--- End Form Data ---")
        # Never print passwords!

        # 3. Redirect to a success page or login page
        flash('Account created successfully! Please log in.', 'success')
        # return redirect(url_for('login_page')) # Redirect to login after success
        return redirect(url_for('signup_student_form'))  # Or redirect back for now

    # If method is not POST (shouldn't happen with route definition)
    return redirect(url_for('signup_student_form'))


# --- Tutor Signup Routes ---

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/signup/tutor')
def signup_tutor_form():
    """Renders the tutor signup form."""
    print("Serving tutor signup form page.")
    return render_template('tutor_signup.html')


@app.route('/signup/tutor/submit', methods=['POST'])
def signup_tutor_submit():
    """Handles the submission of the tutor signup form."""
    if request.method == 'POST':
        # Extract basic info
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        phone = request.form.get('phone')  # Optional
        timezone = request.form.get('timezone')
        terms = request.form.get('terms')

        # Extract tutor profile info
        qualification = request.form.get('qualification')
        experience_str = request.form.get('experience')
        subjects = request.form.getlist('subjects[]')
        bio = request.form.get('bio')
        hourly_rate_str = request.form.get('hourly_rate')  # Optional

        # Handle file upload
        profile_pic_filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file and file.filename and allowed_file(file.filename):
            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(file.filename)
            # TODO: Consider renaming files to avoid conflicts (e.g., using user ID or UUID)
            # Example: filename = f"{user_id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_pic_filename = filename  # Store filename to save in DB
            print(f"Profile picture saved: {profile_pic_filename}")
        elif file and file.filename and not allowed_file(file.filename):
            flash('Invalid file type for profile picture. Allowed: png, jpg, jpeg', 'error')
            # Decide if this is a critical error or just ignore the upload
            # return redirect(url_for('signup_tutor_form')) # Option: halt signup

        # --- Basic Server-Side Validation ---
        errors = []
        if not fullname: errors.append("Full Name is required.")
        if not email: errors.append("Email is required.")
        # TODO: Add email format validation / check if email exists
        if not password or len(password) < 8: errors.append("Password is required (min 8 chars).")
        if password != confirm_password: errors.append("Passwords do not match.")
        if not timezone: errors.append("Timezone is required.")
        if not qualification: errors.append("Highest Qualification is required.")
        if not experience_str:
            errors.append("Years of Experience is required.")
        else:
            try:
                experience = float(experience_str)
                if experience < 0: errors.append("Experience cannot be negative.")
            except ValueError:
                errors.append("Invalid number for Years of Experience.")
        if not subjects: errors.append("Please select at least one subject you can teach.")
        if not bio: errors.append("Bio/Introduction is required.")
        if hourly_rate_str:  # Validate only if provided
            try:
                hourly_rate = float(hourly_rate_str)
                if hourly_rate < 0: errors.append("Hourly rate cannot be negative.")
            except ValueError:
                errors.append("Invalid number for Hourly Rate.")
        if not terms: errors.append("You must agree to the Tutor Terms of Service.")

        if errors:
            for error in errors: flash(error, 'error')
        # TODO: Re-populate form with previous data for better UX
        return redirect(url_for('signup_tutor_form'))

        # --- If Validation Passes ---
        # TODO: Hash password: hashed_password = generate_password_hash(password)
        # TODO: Store tutor data in DB, including profile_pic_filename if available
        print("--- Tutor Form Data Received ---")
        print(f"Tutor Full Name: {fullname}")
        print(f"Tutor Email: {email}")
        print(f"Timezone: {timezone}")
        print(f"Qualification: {qualification}")
        print(f"Experience: {experience_str}")
        print(f"Subjects: {subjects}")
        print(f"Bio: {bio[:50]}...")  # Print start of bio
        print(f"Hourly Rate: {hourly_rate_str}")
        print(f"Profile Pic Filename: {profile_pic_filename}")
        print(f"Terms Agreed: {terms}")
        print("--- End Tutor Form Data ---")

        flash('Tutor account created successfully! Your profile may be subject to review.', 'success')
        return redirect(url_for('index'))  # Or tutor dashboard/login page
    # If method is not POST
    return redirect(url_for('signup_tutor_form'))


# Run the Flask app
if __name__ == '__main__':
    # Debug=True allows auto-reloading and provides detailed error pages
    # Turn off debug mode in production!
    app.run(debug=True)
