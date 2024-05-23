from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, logout_user,current_user
from . import auth
from app.models.models import User, db, LoginHistory
from datetime import datetime
import re


# Function to verify email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@auth.route('/')
def index():
    return render_template('introduction.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            # Record the login time
            login_time = datetime.now()
            login_history = LoginHistory(username=username, login_time=login_time,user_id = user.id)
            db.session.add(login_history)
            db.session.commit()
            
            # Redirect to the main page after successful login
            return redirect(url_for("pr.view_post"))  # Adjust the redirect as needed
        
        else:
            # Flash an error message if login fails
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))
    # Render the login page template
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        # Get username, password, and email from the registration form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Validate email format
        if not is_valid_email(email):
            flash("Invalid email format", "warning")
            return redirect(url_for("auth.register"))
        
        # Check if the username already exists in the database
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "warning")
            return redirect(url_for("auth.register"))
        
        # Hash the password and create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Flash a success message and redirect to the login page
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    # Render the registration page template
    return render_template('auth/register.html')

# Route for user logout
@auth.route('/logout')
@login_required
def logout():
    """Handle user logout and record logout time."""
    if current_user.is_authenticated:
        # Query for the most recent login entry for the user
        login_history = LoginHistory.query.filter_by(user_id=current_user.id, logout_time=None).order_by(LoginHistory.id.desc()).first()

        # Update the logout time for the most recent login entry
        if login_history:
            # Update the logout time for the most recent login entry
            login_history.logout_time = datetime.now()
            db.session.commit()

     # logout the user
    logout_user()

    # Clear chat history from session
    session.pop('chat_history', None)
    
    # Redirect to the home page
    return redirect(url_for("auth.index"))






