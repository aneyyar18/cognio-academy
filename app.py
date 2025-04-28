from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import bcrypt

app = Flask(__name__)

def create_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            dob DATE NOT NULL,
            role TEXT CHECK(role IN ('student', 'educator')) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call create_table to ensure the table is created
create_table()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']

        name_error = email_error = password_error = dob_error = None

        # Basic validation
        if not first_name or not last_name:
            name_error = 'Both First Name and Last Name are required.'

        if not email:
            email_error = 'Email is required.'
        elif len(email) == 0:
            email_error = 'Invalid email format.'

        if not password:
            password_error = 'Password is required.'
        elif len(password) < 6:
            password_error = 'Password must be at least 6 characters long.'

        if not dob:
            dob_error = 'Date of Birth is required.'

        if name_error or email_error or password_error or dob_error:
            return render_template('signup.html', name_error=name_error, email_error=email_error, 
                                   password_error=password_error, dob_error=dob_error)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (first_name, last_name, email, password, dob, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, hashed_password, dob, 'student'))  # Default role
            conn.commit()
            return redirect(url_for('role_selection'))
        except sqlite3.IntegrityError:
            email_error = "Email already exists."
            return render_template('signup.html', email_error=email_error)
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT password FROM users WHERE email = ?
        ''', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            return redirect(url_for('home'))
        else:
            error_message = 'Invalid credentials or no account found.'
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/role-selection')
def role_selection():
    return render_template('role_selection.html')

@app.route('/home')
def home():
    return 'Welcome to the home page!'

if __name__ == '__main__':
    app.run(debug=True)
