"""
Sample data generation script
Run this script to populate the database with sample data for testing
"""
import os
import sys
import random
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db, bcrypt
from app.models import User, Admin, Graduate, Company, JobPosting, Application
from config import Config

app = create_app(Config)

def generate_sample_data():
    """Generate sample data for testing"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Application.query.delete()
        JobPosting.query.delete()
        db.session.commit()
        
        # We'll keep any existing users but clear their relationships
        print("Keeping existing users...")
        
        # Create admin if not exists
        if not Admin.query.filter_by(email='admin@example.com').first():
            print("Creating admin user...")
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Admin(
                email='admin@example.com',
                password=hashed_password,
                name='System Admin'
            )
            db.session.add(admin)
            db.session.commit()
        
        # Create sample companies if we have fewer than 5
        companies = Company.query.all()
        if len(companies) < 5:
            print("Creating sample companies...")
            sample_companies = [
                {
                    'email': 'info@techinnovate.com',
                    'password': bcrypt.generate_password_hash('company123').decode('utf-8'),
                    'name': 'Tech Innovate',
                    'industry': 'Technology',
                    'description': 'A leading innovator in software development and IT solutions.',
                    'website': 'https://www.techinnovate.example.com'
                },
                {
                    'email': 'careers@financeplus.com',
                    'password': bcrypt.generate_password_hash('company123').decode('utf-8'),
                    'name': 'Finance Plus',
                    'industry': 'Finance',
                    'description': 'Financial services company providing banking and investment solutions.',
                    'website': 'https://www.financeplus.example.com'
                },
                {
                    'email': 'hr@edulearn.com',
                    'password': bcrypt.generate_password_hash('company123').decode('utf-8'),
                    'name': 'EduLearn',
                    'industry': 'Education',
                    'description': 'Educational technology company revolutionizing learning experiences.',
                    'website': 'https://www.edulearn.example.com'
                },
                {
                    'email': 'jobs@healthcorp.com',
                    'password': bcrypt.generate_password_hash('company123').decode('utf-8'),
                    'name': 'HealthCorp',
                    'industry': 'Healthcare',
                    'description': 'Healthcare provider focused on innovative medical solutions.',
                    'website': 'https://www.healthcorp.example.com'
                },
                {
                    'email': 'contact@mediaworks.com',
                    'password': bcrypt.generate_password_hash('company123').decode('utf-8'),
                    'name': 'Media Works',
                    'industry': 'Media',
                    'description': 'Creative agency specializing in digital marketing and media production.',
                    'website': 'https://www.mediaworks.example.com'
                }
            ]
            
            for company_data in sample_companies:
                if not Company.query.filter_by(email=company_data['email']).first():
                    company = Company(**company_data)
                    db.session.add(company)
            
            db.session.commit()
            companies = Company.query.all()
        
        # Create sample graduates if we have fewer than 5
        graduates = Graduate.query.all()
        if len(graduates) < 5:
            print("Creating sample graduates...")
            sample_graduates = [
                {
                    'email': 'ahmad@example.com',
                    'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                    'first_name': 'Ahmad',
                    'last_name': 'Rahman',
                    'skills': 'Python, JavaScript, React, Data Analysis',
                    'experience': 'Internship at Tech Company, Research Assistant',
                    'location_preference': 'Kuala Lumpur, Selangor',
                    'salary_preference': 'RM 3,000 - RM 4,500'
                },
                {
                    'email': 'sarah@example.com',
                    'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                    'first_name': 'Sarah',
                    'last_name': 'Abdullah',
                    'skills': 'Marketing, Social Media Management, Content Creation',
                    'experience': 'Marketing Intern, Event Organizer',
                    'location_preference': 'Kuala Lumpur, Penang',
                    'salary_preference': 'RM 2,800 - RM 4,000'
                },
                {
                    'email': 'mei@example.com',
                    'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                    'first_name': 'Mei Ling',
                    'last_name': 'Tan',
                    'skills': 'Accounting, Financial Analysis, Excel, QuickBooks',
                    'experience': 'Accounting Assistant (Part-time)',
                    'location_preference': 'Kuala Lumpur, Johor Bahru',
                    'salary_preference': 'RM 3,500 - RM 5,000'
                },
                {
                    'email': 'ali@example.com',
                    'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                    'first_name': 'Ali',
                    'last_name': 'Hassan',
                    'skills': 'Graphic Design, Adobe Creative Suite, UI/UX Design',
                    'experience': 'Freelance Designer, Student Project Lead',
                    'location_preference': 'Kuala Lumpur, Remote',
                    'salary_preference': 'RM 3,000 - RM 4,000'
                },
                {
                    'email': 'nurul@example.com',
                    'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                    'first_name': 'Nurul',
                    'last_name': 'Izzah',
                    'skills': 'Teaching, Curriculum Development, Communication, Public Speaking',
                    'experience': 'Teaching Assistant, Tutor',
                    'location_preference': 'Machang, Kota Bharu',
                    'salary_preference': 'RM 2,500 - RM 3,500'
                }
            ]
            
            for graduate_data in sample_graduates:
                if not Graduate.query.filter_by(email=graduate_data['email']).first():
                    graduate = Graduate(**graduate_data)
                    db.session.add(graduate)
            
            db.session.commit()
            graduates = Graduate.query.all()
        
        # Create sample job postings
        print("Creating sample job postings...")
        job_categories = ['Technology', 'Finance', 'Education', 'Healthcare', 'Media', 'Engineering', 'Sales', 'Customer Service']
        job_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Remote']
        locations = ['Kuala Lumpur', 'Selangor', 'Penang', 'Johor Bahru', 'Kota Bharu', 'Ipoh', 'Melaka', 'Kuching', 'Remote']
        
        # Sample job descriptions for different industries
        # Add these job templates to the existing templates in the file
        job_templates = {
            'Technology': [
                {
                    'title': 'Senior Software Engineer',
                    'description': 'Lead development of enterprise applications using modern technologies. Experience with cloud platforms and microservices architecture.',
                    'qualification': 'Bachelor\'s degree in Computer Science, 5+ years experience in software development.',
                    'role': 'Senior Developer',
                    'salary_min': 8000,
                    'salary_max': 15000
                },
                {
                    'title': 'Junior Developer',
                    'description': 'Join our development team to build web applications. Great opportunity for fresh graduates.',
                    'qualification': 'Bachelor\'s degree in Computer Science or related field. Knowledge of web technologies.',
                    'role': 'Junior Developer',
                    'salary_min': 3000,
                    'salary_max': 4500
                }
            ],
            'Finance': [
                {
                    'title': 'Investment Analyst',
                    'description': 'Analyze market trends and investment opportunities. Prepare financial models and reports.',
                    'qualification': 'Bachelor\'s degree in Finance or Economics. CFA certification is a plus.',
                    'role': 'Analyst',
                    'salary_min': 4500,
                    'salary_max': 7000
                },
                {
                    'title': 'Junior Accountant',
                    'description': 'Handle day-to-day accounting operations and financial reporting.',
                    'qualification': 'Bachelor\'s degree in Accounting. Knowledge of accounting software.',
                    'role': 'Junior Accountant',
                    'salary_min': 3200,
                    'salary_max': 4800
                }
            ]
        }
        
        # Add these graduate profiles
        sample_graduates.extend([
            {
                'email': 'zain@example.com',
                'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                'first_name': 'Zain',
                'last_name': 'Ibrahim',
                'skills': 'Java, Spring Boot, Microservices, AWS, System Design',
                'experience': 'Software Engineer Intern at Enterprise Tech Company',
                'location_preference': 'Kuala Lumpur, Remote',
                'salary_min': 4000,
                'salary_max': 6000
            },
            {
                'email': 'lisa@example.com',
                'password': bcrypt.generate_password_hash('graduate123').decode('utf-8'),
                'first_name': 'Lisa',
                'last_name': 'Wong',
                'skills': 'Financial Analysis, Investment Research, Bloomberg Terminal, Excel VBA',
                'experience': 'Investment Banking Intern',
                'location_preference': 'Kuala Lumpur',
                'salary_min': 4500,
                'salary_max': 7000
            }
        ])
        
        # Create 20-30 job postings
        num_jobs = random.randint(20, 30)
        for i in range(num_jobs):
            # Select a random company
            company = random.choice(companies)
            
            # Select industry based on company or random
            industry = company.industry if company.industry in job_templates else random.choice(list(job_templates.keys()))
            
            # Select a job template from the industry
            job_template = random.choice(job_templates.get(industry, job_templates['Technology']))
            
            # Create random posting date within the last 30 days
            days_ago = random.randint(0, 30)
            posting_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Randomly decide if job has a closing date
            has_closing_date = random.choice([True, False])
            closing_date = posting_date + timedelta(days=random.randint(14, 60)) if has_closing_date else None
            
            # Create the job posting
            job = JobPosting(
                company_id=company.id,
                title=job_template['title'] + (f' {i+1}' if i > 0 else ''),
                location=random.choice(locations),
                description=job_template['description'],
                category=industry,
                subcategory=random.choice(['Entry-level', 'Mid-level', 'Senior']),
                role=job_template['role'],
                salary=f'RM {random.randint(2500, 8000)} - RM {random.randint(8001, 12000)}',
                job_type=random.choice(job_types),
                qualification=job_template['qualification'],
                criteria=f'Additional criteria for {job_template["title"]}',
                posting_date=posting_date,
                closing_date=closing_date,
                is_active=random.choice([True, True, True, False])  # 75% chance of being active
            )
            
            db.session.add(job)
        
        db.session.commit()
        job_postings = JobPosting.query.all()
        
        # Create sample applications
        print("Creating sample applications...")
        # Each graduate applies to 2-5 random jobs
        for graduate in graduates:
            num_applications = random.randint(2, 5)
            # Get random jobs to apply for
            applied_jobs = random.sample(job_postings, min(num_applications, len(job_postings)))
            
            for job in applied_jobs:
                # Random application date between job posting date and now
                days_since_posting = (datetime.utcnow() - job.posting_date).days
                application_date = job.posting_date + timedelta(days=random.randint(1, max(1, days_since_posting)))
                
                # Create application with random status
                status = random.choice(['Pending', 'Pending', 'Accepted', 'Rejected'])  # Higher chance of pending
                
                application = Application(
                    graduate_id=graduate.id,
                    job_id=job.id,
                    application_date=application_date,
                    status=status
                )
                
                db.session.add(application)
        
        db.session.commit()
        print("Sample data generated successfully!")

if __name__ == '__main__':
    generate_sample_data()