# app.py
from flask import Flask, render_template, request, url_for, redirect, flash

# Initialize the Flask application
app = Flask(__name__)
# Secret key is needed for flashing messages
app.secret_key = 'your_very_secret_key' # Change this in production!

# Route for the homepage (index.html)
@app.route('/')
def index():
    """Renders the homepage."""
    print("Serving homepage (index.html).")
    # Make sure you have an 'index.html' file in your 'templates' folder
    # This should be the homepage UI created earlier.
    return render_template('index.html') # Changed from redirect


# Route to display the student signup page
@app.route('/signup/student')
def signup_student_form():
    """Renders the student signup form."""
    print("Serving signup form page.")
    return render_template('register.html')

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
        subjects = request.form.getlist('subjects[]') # Get list for checkboxes
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
                flash(error, 'error') # Use 'error' category for styling if desired
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
        return redirect(url_for('signup_student_form')) # Or redirect back for now

    # If method is not POST (shouldn't happen with route definition)
    return redirect(url_for('signup_student_form'))




# Run the Flask app
if __name__ == '__main__':
    # Debug=True allows auto-reloading and provides detailed error pages
    # Turn off debug mode in production!
    app.run(debug=True)
    