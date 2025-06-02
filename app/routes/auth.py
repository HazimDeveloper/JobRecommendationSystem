# Authentication routes
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Graduate, Company, Admin
from app import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    # If user is already logged in, redirect to home
    if current_user.is_authenticated:
        if current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.user_type == 'graduate':
            return redirect(url_for('graduate.dashboard'))
        elif current_user.user_type == 'company':
            return redirect(url_for('company.dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')
        
        # Log in the user
        login_user(user, remember=remember)
        
        # Redirect to the appropriate dashboard
        if user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.user_type == 'graduate':
            return redirect(url_for('graduate.dashboard'))
        elif user.user_type == 'company':
            return redirect(url_for('company.dashboard'))
        
        # Default redirect
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Choose registration type"""
    return render_template('auth/register_choice.html')

@auth_bp.route('/register/graduate', methods=['GET', 'POST'])
def register_graduate():
    """Graduate registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return render_template('auth/register_graduate.html')
        
        # Create a new graduate user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_graduate = Graduate(
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Add to database
        db.session.add(new_graduate)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_graduate.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    """Company registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return render_template('auth/register_company.html')
        
        # Create a new company user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_company = Company(
            email=email,
            password=hashed_password,
            name=company_name,
            industry=industry
        )
        
        # Add to database
        db.session.add(new_company)
        db.session.commit()
        
        flash('Registration successful! Your account will be reviewed by an admin.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_company.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Logic to send password reset email would go here
            # For this example, we'll just flash a message
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        else:
            # We don't want to reveal that an email doesn't exist for security reasons
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')