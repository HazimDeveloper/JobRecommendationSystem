# Database models
from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'graduate', 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }
    
    def __repr__(self):
        return f"User('{self.email}', '{self.user_type}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }
    
    def __repr__(self):
        return f"Admin('{self.name}', '{self.email}')"

class Graduate(User):
    __tablename__ = 'graduates'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    skills = db.Column(db.Text)
    salary_preference = db.Column(db.String(50))
    location_preference = db.Column(db.String(100))
    experience = db.Column(db.Text)
    resume_path = db.Column(db.String(255))
    applications = db.relationship('Application', backref='graduate', lazy=True)
    recommendations = db.relationship('Recommendation', backref='graduate', lazy=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'graduate',
    }
    
    def __repr__(self):
        return f"Graduate('{self.first_name} {self.last_name}', '{self.email}')"

class Company(User):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    job_postings = db.relationship('JobPosting', backref='company', lazy=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'company',
    }
    
    def __repr__(self):
        return f"Company('{self.name}', '{self.email}')"

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50))
    role = db.Column(db.String(50))
    salary_min = db.Column(db.Integer)  # Add this line
    salary_max = db.Column(db.Integer)  # Add this line
    salary = db.Column(db.String(50))   # Keep this for backward compatibility
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    qualification = db.Column(db.Text)
    criteria = db.Column(db.Text)
    posting_date = db.Column(db.DateTime, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    applications = db.relationship('Application', backref='job_posting', lazy=True)
    recommendations = db.relationship('Recommendation', backref='job_posting', lazy=True)
    
    def __repr__(self):
        return f"JobPosting('{self.title}', '{self.company.name}')"

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    
    def __repr__(self):
        return f"Application('{self.graduate.first_name} {self.graduate.last_name}', '{self.job_posting.title}')"

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Recommendation('{self.graduate.first_name} {self.graduate.last_name}', '{self.job_posting.title}', '{self.match_score}')"

class SUSEvaluation(db.Model):
    __tablename__ = 'sus_evaluations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    q1 = db.Column(db.Integer, nullable=False)  # SUS questions 1-10
    q2 = db.Column(db.Integer, nullable=False)
    q3 = db.Column(db.Integer, nullable=False)
    q4 = db.Column(db.Integer, nullable=False)
    q5 = db.Column(db.Integer, nullable=False)
    q6 = db.Column(db.Integer, nullable=False)
    q7 = db.Column(db.Integer, nullable=False)
    q8 = db.Column(db.Integer, nullable=False)
    q9 = db.Column(db.Integer, nullable=False)
    q10 = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='evaluations')
    
    def calculate_score(self):
        # SUS scoring algorithm
        # For odd questions (1,3,5,7,9), subtract 1 from the score
        # For even questions (2,4,6,8,10), subtract the score from 5
        # Multiply the sum by 2.5 to get the SUS score (0-100)
        odd_sum = (self.q1 - 1) + (self.q3 - 1) + (self.q5 - 1) + (self.q7 - 1) + (self.q9 - 1)
        even_sum = (5 - self.q2) + (5 - self.q4) + (5 - self.q6) + (5 - self.q8) + (5 - self.q10)
        return (odd_sum + even_sum) * 2.5
    
    def __repr__(self):
        return f"SUSEvaluation(User: '{self.user.email}', Score: '{self.calculate_score()}')"