# Main routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.models import JobPosting, Company
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route"""
    # Get recent job postings to display on the home page
    recent_jobs = JobPosting.query.filter_by(is_active=True) \
                   .order_by(JobPosting.posting_date.desc()).limit(6).all()
    
    # Get some top companies
    top_companies = Company.query.limit(4).all()
    
    return render_template('index.html', 
                          recent_jobs=recent_jobs, 
                          top_companies=top_companies)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/jobs')
def jobs():
    """View all job listings"""
    page = request.args.get('page', 1, type=int)
    
    # Base query - only active jobs
    query = JobPosting.query.filter_by(is_active=True)
    
    # Get filter options from query parameters
    category = request.args.get('category')
    location = request.args.get('location')
    job_type = request.args.get('type')
    
    # Apply filters if provided
    if category:
        query = query.filter_by(category=category)
    if location:
        query = query.filter(JobPosting.location.like(f'%{location}%'))
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    # Order by posting date (newest first)
    query = query.order_by(JobPosting.posting_date.desc())
    
    # Pagination handling with fallback
    try:
        # First try Flask-SQLAlchemy 3.x style
        jobs = query.paginate(page=page, per_page=10)
    except TypeError:
        try:
            # Then try Flask-SQLAlchemy 2.x style
            jobs = query.paginate(page, 10, False)
        except Exception as e:
            # If all else fails, manually paginate
            print(f"Pagination error: {e}")
            all_jobs = query.all()
            total = len(all_jobs)
            start = (page - 1) * 10
            end = min(start + 10, total)
            
            # Create a simple object that mimics the pagination interface
            class SimplePagination:
                def __init__(self, items, page, per_page, total):
                    self.items = items
                    self.page = page
                    self.per_page = per_page
                    self.total = total
                    self.pages = (total + per_page - 1) // per_page
                    self.has_prev = page > 1
                    self.has_next = end < total
                    self.prev_num = page - 1
                    self.next_num = page + 1
            
            jobs = SimplePagination(all_jobs[start:end], page, 10, total)
    
    # Get all categories and locations for filter dropdowns
    categories = db.session.query(JobPosting.category).distinct().all()
    locations = db.session.query(JobPosting.location).distinct().all()
    job_types = db.session.query(JobPosting.job_type).distinct().all()
    
    # Use the regular template
    return render_template('jobs.html', 
                          jobs=jobs,
                          categories=categories,
                          locations=locations,
                          job_types=job_types)

@main_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    """View details of a specific job"""
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if job is active
    if not job.is_active and not current_user.is_authenticated:
        flash('This job posting is no longer active.', 'info')
        return redirect(url_for('main.jobs'))
    
    # Get similar jobs
    similar_jobs = JobPosting.query.filter_by(
        category=job.category, 
        is_active=True
    ).filter(JobPosting.id != job_id).limit(3).all()
    
    return render_template('job_detail.html', job=job, similar_jobs=similar_jobs)

@main_bp.route('/search')
def search():
    """Search for jobs"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('main.jobs'))
    
    # Search in job title, description, and company name
    jobs = JobPosting.query.join(Company).filter(
        (JobPosting.title.contains(query) |
         JobPosting.description.contains(query) |
         Company.name.contains(query)) &
        JobPosting.is_active
    ).all()
    
    return render_template('search_results.html', jobs=jobs, query=query)

@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500