# Admin routes
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Admin, Graduate, Company, JobPosting, Application, SUSEvaluation, Recommendation, User
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

# Check if the user is an admin
def admin_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.user_type != 'admin':
            flash('Access denied. You must be logged in as an admin.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    
    # Preserve the metadata of the original function
    decorated_view.__name__ = func.__name__
    decorated_view.__module__ = func.__module__
    
    return decorated_view

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get counts for dashboard
    graduate_count = Graduate.query.count()
    company_count = Company.query.count()
    job_count = JobPosting.query.count()
    application_count = Application.query.count()
    
    # Get recent job postings
    recent_jobs = JobPosting.query.order_by(JobPosting.posting_date.desc()).limit(5).all()
    
    # Get recent applications
    recent_applications = Application.query.order_by(Application.application_date.desc()).limit(5).all()
    
    # Generate chart for SUS evaluation
    sus_chart = generate_sus_chart()
    
    # Generate chart for applications over time
    app_chart = generate_application_chart()
    
    return render_template('admin/dashboard.html',
                          graduate_count=graduate_count,
                          company_count=company_count,
                          job_count=job_count,
                          application_count=application_count,
                          recent_jobs=recent_jobs,
                          recent_applications=recent_applications,
                          sus_chart=sus_chart,
                          app_chart=app_chart)

@admin_bp.route('/graduates')
@admin_required
def graduates():
    """View all graduates"""
    graduates = Graduate.query.all()
    return render_template('admin/graduates.html', graduates=graduates)

@admin_bp.route('/companies')
@admin_required
def companies():
    """View all companies"""
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@admin_bp.route('/jobs')
@admin_required
def jobs():
    """View all job postings"""
    # Get filter parameters
    company_id = request.args.get('company_id', type=int)
    is_active = request.args.get('is_active')
    
    # Base query
    query = JobPosting.query
    
    # Apply filters
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    if is_active == 'true':
        query = query.filter_by(is_active=True)
    elif is_active == 'false':
        query = query.filter_by(is_active=False)
    
    # Execute query
    jobs = query.order_by(JobPosting.posting_date.desc()).all()
    
    # Get all companies for filter
    companies = Company.query.all()
    
    return render_template('admin/jobs.html', 
                          jobs=jobs, 
                          companies=companies,
                          selected_company_id=company_id,
                          selected_is_active=is_active)

@admin_bp.route('/job/<int:job_id>')
@admin_required
def job_detail(job_id):
    """View detail of a job posting"""
    job = JobPosting.query.get_or_404(job_id)
    
    # Get applications for this job
    applications = Application.query.filter_by(job_id=job.id).all()
    
    return render_template('admin/job_detail.html', job=job, applications=applications)

@admin_bp.route('/job/toggle/<int:job_id>')
@admin_required
def toggle_job(job_id):
    """Toggle job posting active status"""
    job = JobPosting.query.get_or_404(job_id)
    
    # Toggle active status
    job.is_active = not job.is_active
    db.session.commit()
    
    if job.is_active:
        flash('Job posting activated successfully', 'success')
    else:
        flash('Job posting deactivated successfully', 'success')
    
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/applications')
@admin_required
def applications():
    """View all applications"""
    # Get filter parameters
    status = request.args.get('status')
    company_id = request.args.get('company_id', type=int)
    
    # Base query - join Application with JobPosting and Graduate
    query = db.session.query(Application, JobPosting, Graduate) \
            .join(JobPosting, Application.job_id == JobPosting.id) \
            .join(Graduate, Application.graduate_id == Graduate.id)
    
    # Apply filters
    if status:
        query = query.filter(Application.status == status)
    
    if company_id:
        query = query.filter(JobPosting.company_id == company_id)
    
    # Execute query
    applications = query.order_by(Application.application_date.desc()).all()
    
    # Get all companies for filter
    companies = Company.query.all()
    
    return render_template('admin/applications.html', 
                          applications=applications,
                          companies=companies,
                          selected_status=status,
                          selected_company_id=company_id)

@admin_bp.route('/application/update/<int:application_id>', methods=['POST'])
@admin_required
def update_application(application_id):
    """Update application status"""
    application = Application.query.get_or_404(application_id)
    
    # Update status
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Accepted', 'Rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated successfully', 'success')
    else:
        flash('Invalid status value', 'danger')
    
    return redirect(url_for('admin.applications'))

@admin_bp.route('/evaluations')
@admin_required
def evaluations():
    """View all SUS evaluations"""
    evaluations = db.session.query(SUSEvaluation, User) \
                .join(User, SUSEvaluation.user_id == User.id) \
                .all()
    
    # Calculate overall average SUS score
    if evaluations:
        avg_score = sum(eval[0].calculate_score() for eval in evaluations) / len(evaluations)
    else:
        avg_score = 0
    
    return render_template('admin/evaluations.html', 
                          evaluations=evaluations,
                          avg_score=avg_score)

@admin_bp.route('/evaluation/<int:evaluation_id>')
@admin_required
def evaluation_detail(evaluation_id):
    """View detail of a SUS evaluation"""
    evaluation = SUSEvaluation.query.get_or_404(evaluation_id)
    user = User.query.get(evaluation.user_id)
    
    return render_template('admin/evaluation_detail.html', 
                          evaluation=evaluation,
                          user=user)

@admin_bp.route('/reports')
@admin_required
def reports():
    """View system reports"""
    return render_template('admin/reports.html')

@admin_bp.route('/generate-report', methods=['POST'])
@admin_required
def generate_report():
    """Generate various reports"""
    report_type = request.form.get('report_type')
    
    if report_type == 'graduates':
        # Generate graduate report
        graduates = Graduate.query.all()
        return render_template('admin/reports/graduates.html', graduates=graduates)
    
    elif report_type == 'companies':
        # Generate company report
        companies = Company.query.all()
        return render_template('admin/reports/companies.html', companies=companies)
    
    elif report_type == 'jobs':
        # Generate jobs report
        jobs = JobPosting.query.all()
        return render_template('admin/reports/jobs.html', jobs=jobs)
    
    elif report_type == 'applications':
        # Generate applications report
        applications = db.session.query(Application, JobPosting, Graduate) \
                     .join(JobPosting, Application.job_id == JobPosting.id) \
                     .join(Graduate, Application.graduate_id == Graduate.id) \
                     .all()
        return render_template('admin/reports/applications.html', applications=applications)
    
    elif report_type == 'evaluations':
        # Generate SUS evaluations report
        evaluations = SUSEvaluation.query.all()
        avg_score = sum(eval.calculate_score() for eval in evaluations) / len(evaluations) if evaluations else 0
        return render_template('admin/reports/evaluations.html', 
                             evaluations=evaluations,
                             avg_score=avg_score)
    
    flash('Invalid report type', 'danger')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    """Create a new admin user"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists', 'danger')
            return render_template('admin/create_admin.html')
        
        # Create new admin
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_admin = Admin(
            email=email,
            password=hashed_password,
            name=name
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('New admin user created successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_admin.html')

def generate_sus_chart():
    """Generate chart for SUS evaluations"""
    evaluations = SUSEvaluation.query.all()
    
    if not evaluations:
        return None
    
    scores = [eval.calculate_score() for eval in evaluations]
    
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=10, range=(0, 100), edgecolor='black')
    plt.title('Distribution of SUS Scores')
    plt.xlabel('SUS Score')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    
    # Add mean line
    mean_score = sum(scores) / len(scores)
    plt.axvline(x=mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.2f}')
    plt.legend()
    
    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert plot to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    return img_str

def generate_application_chart():
    """Generate chart for applications over time"""
    # Get application data
    applications = Application.query.all()
    
    if not applications:
        return None
    
    # Convert to pandas dataframe for easier manipulation
    app_data = pd.DataFrame([
        {'date': app.application_date.date(), 'status': app.status}
        for app in applications
    ])
    
    # Group by date and count
    daily_counts = app_data.groupby('date').size().reset_index(name='count')
    
    # Sort by date
    daily_counts = daily_counts.sort_values('date')
    
    # Generate plot
    plt.figure(figsize=(10, 6))
    plt.plot(daily_counts['date'], daily_counts['count'], marker='o')
    plt.title('Applications Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Applications')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert plot to base64 string
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    return img_str