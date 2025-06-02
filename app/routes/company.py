# Company routes
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, Company, JobPosting, Application

company_bp = Blueprint('company', __name__)

# Check if the user is a company
def company_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.user_type != 'company':
            flash('Access denied. You must be logged in as a company.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    
    # Preserve the metadata of the original function
    decorated_view.__name__ = func.__name__
    decorated_view.__module__ = func.__module__
    
    return decorated_view

@company_bp.route('/dashboard')
@company_required
def dashboard():
    """Company dashboard"""
    company = Company.query.get(current_user.id)
    
    # Get active job postings
    active_jobs = JobPosting.query.filter_by(company_id=company.id, is_active=True).all()
    
    # Get recent applications
    recent_applications = db.session.query(Application, JobPosting) \
                         .join(JobPosting) \
                         .filter(JobPosting.company_id == company.id) \
                         .order_by(Application.application_date.desc()) \
                         .limit(5).all()
    
    # Count statistics
    active_job_count = JobPosting.query.filter_by(company_id=company.id, is_active=True).count()
    inactive_job_count = JobPosting.query.filter_by(company_id=company.id, is_active=False).count()
    
    pending_application_count = db.session.query(Application) \
                              .join(JobPosting) \
                              .filter(JobPosting.company_id == company.id) \
                              .filter(Application.status == 'Pending') \
                              .count()
    
    return render_template('company/dashboard.html',
                          company=company,
                          active_jobs=active_jobs,
                          recent_applications=recent_applications,
                          active_job_count=active_job_count,
                          inactive_job_count=inactive_job_count,
                          pending_application_count=pending_application_count)

@company_bp.route('/profile', methods=['GET', 'POST'])
@company_required
def profile():
    """Company profile page"""
    company = Company.query.get(current_user.id)
    
    if request.method == 'POST':
        # Update profile information
        company.name = request.form.get('name')
        company.industry = request.form.get('industry')
        company.description = request.form.get('description')
        company.website = request.form.get('website')
        
        # Handle logo upload
        if 'logo' in request.files and request.files['logo'].filename:
            logo_file = request.files['logo']
            filename = secure_filename(logo_file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', filename)
            os.makedirs(os.path.dirname(logo_path), exist_ok=True)
            logo_file.save(logo_path)
            
            company.logo_path = os.path.join('logos', filename)
        
        # Update database
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('company.profile'))
    
    return render_template('company/profile.html', company=company)

@company_bp.route('/job/create', methods=['GET', 'POST'])
@company_required
def create_job():
    """Create a new job posting"""
    company = Company.query.get(current_user.id)
    
    if request.method == 'POST':
        # Create new job posting
        new_job = JobPosting(
            company_id=company.id,
            title=request.form.get('title'),
            location=request.form.get('location'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            subcategory=request.form.get('subcategory'),
            role=request.form.get('role'),
            salary=request.form.get('salary'),
            job_type=request.form.get('job_type'),
            qualification=request.form.get('qualification'),
            criteria=request.form.get('criteria'),
            is_active=True
        )
        
        # Parse and set closing date if provided
        closing_date = request.form.get('closing_date')
        if closing_date:
            new_job.closing_date = datetime.strptime(closing_date, '%Y-%m-%d')
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posting created successfully', 'success')
        return redirect(url_for('company.jobs'))
    
    return render_template('company/create_job.html')

@company_bp.route('/jobs')
@company_required
def jobs():
    """View all job postings"""
    company = Company.query.get(current_user.id)
    
    # Get filter parameters
    status = request.args.get('status', 'active')
    
    # Query job postings
    if status == 'active':
        jobs = JobPosting.query.filter_by(company_id=company.id, is_active=True) \
              .order_by(JobPosting.posting_date.desc()).all()
    elif status == 'inactive':
        jobs = JobPosting.query.filter_by(company_id=company.id, is_active=False) \
              .order_by(JobPosting.posting_date.desc()).all()
    else:
        jobs = JobPosting.query.filter_by(company_id=company.id) \
              .order_by(JobPosting.posting_date.desc()).all()
    
    return render_template('company/jobs.html', jobs=jobs, current_status=status)

@company_bp.route('/job/edit/<int:job_id>', methods=['GET', 'POST'])
@company_required
def edit_job(job_id):
    """Edit a job posting"""
    company = Company.query.get(current_user.id)
    job = JobPosting.query.get_or_404(job_id)
    
    # Ensure the job belongs to this company
    if job.company_id != company.id:
        flash('You do not have permission to edit this job posting.', 'danger')
        return redirect(url_for('company.jobs'))
    
    if request.method == 'POST':
        # Update job posting
        job.title = request.form.get('title')
        job.location = request.form.get('location')
        job.description = request.form.get('description')
        job.category = request.form.get('category')
        job.subcategory = request.form.get('subcategory')
        job.role = request.form.get('role')
        job.salary = request.form.get('salary')
        job.job_type = request.form.get('job_type')
        job.qualification = request.form.get('qualification')
        job.criteria = request.form.get('criteria')
        
        # Parse and set closing date if provided
        closing_date = request.form.get('closing_date')
        if closing_date:
            job.closing_date = datetime.strptime(closing_date, '%Y-%m-%d')
        
        db.session.commit()
        
        flash('Job posting updated successfully', 'success')
        return redirect(url_for('company.jobs'))
    
    return render_template('company/edit_job.html', job=job)

@company_bp.route('/job/toggle/<int:job_id>')
@company_required
def toggle_job(job_id):
    """Toggle job posting active status"""
    company = Company.query.get(current_user.id)
    job = JobPosting.query.get_or_404(job_id)
    
    # Ensure the job belongs to this company
    if job.company_id != company.id:
        flash('You do not have permission to modify this job posting.', 'danger')
        return redirect(url_for('company.jobs'))
    
    # Toggle active status
    job.is_active = not job.is_active
    db.session.commit()
    
    if job.is_active:
        flash('Job posting activated successfully', 'success')
    else:
        flash('Job posting deactivated successfully', 'success')
    
    return redirect(url_for('company.jobs'))

@company_bp.route('/change-password', methods=['POST'])
@company_required
def change_password():
    """Change company password"""
    company = Company.query.get(current_user.id)
    
    # Get form data
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Check if current password is correct
    if not bcrypt.check_password_hash(company.password, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('company.profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('company.profile'))
    
    # Update password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    company.password = hashed_password
    db.session.commit()
    
    flash('Password changed successfully.', 'success')
    return redirect(url_for('company.profile'))

@company_bp.route('/applications')
@company_required
def applications():
    """View all applications for company jobs"""
    company = Company.query.get(current_user.id)
    
    # Get filter parameters
    job_id = request.args.get('job_id', type=int)
    status = request.args.get('status')
    
    # Base query - join Application with JobPosting
    query = db.session.query(Application, JobPosting, Graduate) \
            .join(JobPosting, Application.job_id == JobPosting.id) \
            .join(Graduate, Application.graduate_id == Graduate.id) \
            .filter(JobPosting.company_id == company.id)
    
    # Apply filters
    if job_id:
        query = query.filter(JobPosting.id == job_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    # Execute query
    applications = query.order_by(Application.application_date.desc()).all()
    
    # Get all company jobs for filter dropdown
    jobs = JobPosting.query.filter_by(company_id=company.id).all()
    
    return render_template('company/applications.html', 
                          applications=applications,
                          jobs=jobs,
                          selected_job_id=job_id,
                          selected_status=status)

@company_bp.route('/application/<int:application_id>')
def application_detail(application_id):
    application = Application.query.get_or_404(application_id)
    return render_template('company/application_detail.html', application=application)

@company_bp.route('/application/update/<int:application_id>', methods=['POST'])
@company_required
def update_application(application_id):
    """Update application status"""
    company = Company.query.get(current_user.id)
    application = Application.query.get_or_404(application_id)
    
    # Ensure the application is for a job owned by this company
    job = JobPosting.query.get(application.job_id)
    if job.company_id != company.id:
        flash('You do not have permission to update this application.', 'danger')
        return redirect(url_for('company.applications'))
    
    # Update status
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Accepted', 'Rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated successfully', 'success')
    else:
        flash('Invalid status value', 'danger')
    
    return redirect(url_for('company.applications'))