# Graduate routes
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, Graduate, JobPosting, Application, Recommendation, SUSEvaluation
from app.recommender import JobRecommender
from app import bcrypt  # Add this import

graduate_bp = Blueprint('graduate', __name__)

# Check if the user is a graduate
def graduate_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.user_type != 'graduate':
            flash('Access denied. You must be logged in as a graduate.', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    
    # Preserve the metadata of the original function
    decorated_view.__name__ = func.__name__
    decorated_view.__module__ = func.__module__
    
    return decorated_view

# Add allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@graduate_bp.route('/dashboard')
@graduate_required
def dashboard():
    """Graduate dashboard"""
    # Get graduate profile
    graduate = Graduate.query.get(current_user.id)
    
    # Get recent applications
    recent_applications = Application.query.filter_by(graduate_id=graduate.id) \
                         .order_by(Application.application_date.desc()).limit(5).all()
    
    # Get job recommendations
    recommendations = Recommendation.query.filter_by(graduate_id=graduate.id) \
                     .order_by(Recommendation.match_score.desc()).limit(6).all()
    
    # If no recommendations exist and profile is complete enough, generate them
    if not recommendations and graduate.skills and graduate.experience:
        try:
            generate_recommendations(graduate.id)
            recommendations = Recommendation.query.filter_by(graduate_id=graduate.id) \
                           .order_by(Recommendation.match_score.desc()).limit(6).all()
        except Exception as e:
            print(f"Error generating recommendations: {e}")
    
    # Count applications by status
    pending_count = Application.query.filter_by(graduate_id=graduate.id, status='Pending').count()
    accepted_count = Application.query.filter_by(graduate_id=graduate.id, status='Accepted').count()
    rejected_count = Application.query.filter_by(graduate_id=graduate.id, status='Rejected').count()
    
    return render_template('graduate/dashboard.html', 
                          graduate=graduate,
                          recent_applications=recent_applications,
                          recommendations=recommendations,
                          pending_count=pending_count,
                          accepted_count=accepted_count,
                          rejected_count=rejected_count)

@graduate_bp.route('/profile', methods=['GET', 'POST'])
@graduate_required
def profile():
    """Graduate profile page"""
    graduate = Graduate.query.get(current_user.id)
    
    if request.method == 'POST':
        # Update profile information
        graduate.first_name = request.form.get('first_name')
        graduate.last_name = request.form.get('last_name')
        graduate.skills = request.form.get('skills')
        graduate.salary_preference = request.form.get('salary_preference')
        graduate.location_preference = request.form.get('location_preference')
        graduate.experience = request.form.get('experience')
        
        # Handle resume upload
        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file and resume_file.filename != '':
                if allowed_file(resume_file.filename):
                    # Delete old resume if it exists
                    if graduate.resume_path:
                        old_resume_path = os.path.join(current_app.root_path, 'static', graduate.resume_path)
                        if os.path.exists(old_resume_path):
                            os.remove(old_resume_path)
                    
                    filename = secure_filename(resume_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"{current_user.id}_{timestamp}_{filename}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'resumes')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save the file
                    resume_path = os.path.join('uploads', 'resumes', filename)
                    full_path = os.path.join(current_app.root_path, 'static', resume_path)
                    resume_file.save(full_path)
                    
                    # Update database
                    graduate.resume_path = resume_path
                    flash('Resume uploaded successfully!', 'success')
                else:
                    flash('Invalid file type. Please upload a PDF or Word document.', 'danger')
        
        # Save changes
        db.session.commit()
        
        # Regenerate recommendations after profile update
        recommendations = generate_recommendations(graduate.id)
        if recommendations:
            flash('Profile updated and recommendations refreshed!', 'success')
        else:
            flash('Profile updated! Add more skills and experience to get job recommendations.', 'info')
        
        return redirect(url_for('graduate.profile'))
    
    return render_template('graduate/profile.html', graduate=graduate)

@graduate_bp.route('/applications')
@graduate_required
def applications():
    """View all applications"""
    graduate = Graduate.query.get(current_user.id)
    
    # Get filter parameters
    status = request.args.get('status')
    
    # Query applications
    query = Application.query.filter_by(graduate_id=graduate.id)
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    # Sort by date descending
    applications = query.order_by(Application.application_date.desc()).all()
    
    return render_template('graduate/applications.html', applications=applications)

@graduate_bp.route('/recommendations')
@graduate_required
def recommendations():
    """View job recommendations"""
    graduate = Graduate.query.get(current_user.id)
    
    # Get recommendations
    recommendations = Recommendation.query.filter_by(graduate_id=graduate.id) \
                     .order_by(Recommendation.match_score.desc()).all()
    
    return render_template('graduate/recommendations.html', recommendations=recommendations)

@graduate_bp.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@graduate_required
def apply_job(job_id):
    """Apply for a job"""
    job = JobPosting.query.get_or_404(job_id)
    graduate = Graduate.query.get(current_user.id)
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        graduate_id=graduate.id,
        job_id=job.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('main.job_detail', job_id=job.id))
    
    if request.method == 'POST':
        # Check if resume is uploaded
        if not graduate.resume_path:
            flash('Please upload your resume before applying for jobs.', 'warning')
            return redirect(url_for('graduate.profile'))
        
        # Create new application
        application = Application(
            graduate_id=graduate.id,
            job_id=job.id,
            status='Pending'
        )
        
        try:
            db.session.add(application)
            db.session.commit()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('graduate.applications'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting application. Please try again.', 'danger')
            print(f"Application error: {e}")
    
    return render_template('graduate/apply.html', job=job, graduate=graduate)

@graduate_bp.route('/change-password', methods=['POST'])
@graduate_required
def change_password():
    """Change graduate password"""
    graduate = Graduate.query.get(current_user.id)
    
    # Get form data
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Check if current password is correct
    if not bcrypt.check_password_hash(graduate.password, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('graduate.profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('graduate.profile'))
    
    # Update password
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    graduate.password = hashed_password
    
    try:
        db.session.commit()
        flash('Password changed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing password. Please try again.', 'danger')
        print(f"Password change error: {e}")
    
    return redirect(url_for('graduate.profile'))

@graduate_bp.route('/regenerate-recommendations', methods=['POST'])
@graduate_required
def regenerate_recommendations():
    """Regenerate job recommendations for the current graduate"""
    graduate = Graduate.query.get(current_user.id)
    
    # Check if profile is complete enough
    if not graduate.skills or not graduate.experience:
        flash('Please complete your profile (skills and experience) before generating recommendations.', 'warning')
        return redirect(url_for('graduate.profile'))
    
    try:
        # Generate recommendations
        recommendations = generate_recommendations(graduate.id)
        
        if recommendations and len(recommendations) > 0:
            flash('Job recommendations have been refreshed successfully!', 'success')
        else:
            flash('No suitable job recommendations found. Please try updating your profile or check back later.', 'info')
    except Exception as e:
        flash('Error generating recommendations. Please try again later.', 'danger')
        print(f"Recommendation generation error: {e}")
    
    return redirect(url_for('graduate.recommendations'))

@graduate_bp.route('/evaluation', methods=['GET', 'POST'])
@graduate_required
def evaluation():
    """System usability scale evaluation"""
    # Check if user has already submitted an evaluation
    existing_evaluation = SUSEvaluation.query.filter_by(user_id=current_user.id).first()
    
    if existing_evaluation:
        flash('You have already submitted an evaluation. Thank you for your feedback!', 'info')
        return redirect(url_for('graduate.dashboard'))
    
    if request.method == 'POST':
        # Create new evaluation
        evaluation = SUSEvaluation(
            user_id=current_user.id,
            q1=int(request.form.get('q1')),
            q2=int(request.form.get('q2')),
            q3=int(request.form.get('q3')),
            q4=int(request.form.get('q4')),
            q5=int(request.form.get('q5')),
            q6=int(request.form.get('q6')),
            q7=int(request.form.get('q7')),
            q8=int(request.form.get('q8')),
            q9=int(request.form.get('q9')),
            q10=int(request.form.get('q10')),
            comments=request.form.get('comments')
        )
        
        try:
            db.session.add(evaluation)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('graduate.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting evaluation. Please try again.', 'danger')
            print(f"Evaluation error: {e}")
    
    return render_template('graduate/evaluation.html')

def generate_recommendations(graduate_id):
    """Generate job recommendations for a graduate"""
    try:
        graduate = Graduate.query.get(graduate_id)
        
        if not graduate:
            print(f"Graduate with ID {graduate_id} not found")
            return []
        
        # Check if graduate has sufficient profile information
        if not graduate.skills and not graduate.experience:
            print(f"Graduate {graduate_id} has insufficient profile information")
            return []
        
        # Get active job postings
        active_jobs = JobPosting.query.filter_by(is_active=True).all()
        
        if not active_jobs:
            print("No active job postings found")
            return []
        
        print(f"Found {len(active_jobs)} active jobs for matching")
        
        # Initialize recommender
        recommender = JobRecommender()
        recommender.fit(active_jobs)
        
        # Get recommendations
        recommendations = recommender.get_recommendations_for_graduate(graduate, top_n=10)
        
        print(f"Generated {len(recommendations)} recommendations")
        
        # Clear existing recommendations
        Recommendation.query.filter_by(graduate_id=graduate.id).delete()
        
        # Create new recommendation records
        for rec in recommendations:
            # Ensure match score is reasonable (between 0 and 1)
            match_score = max(0.0, min(1.0, rec['similarity_score']))
            
            # Only save recommendations with a meaningful score
            if match_score > 0.01:  # At least 1% match
                recommendation = Recommendation(
                    graduate_id=graduate.id,
                    job_id=rec['job_id'],
                    match_score=match_score
                )
                db.session.add(recommendation)
        
        db.session.commit()
        print(f"Saved recommendations for graduate {graduate_id}")
        
        return recommendations
        
    except Exception as e:
        print(f"Error in generate_recommendations: {e}")
        db.session.rollback()
        return []