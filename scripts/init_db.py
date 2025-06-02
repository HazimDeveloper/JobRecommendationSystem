"""
Database initialization script
Run this script to create all the necessary database tables
"""
import os
import sys

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from config import Config
from app.models import User, Admin, Graduate, Company

app = create_app(Config)

def init_db():
    """Initialize the database tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin user exists
        if not Admin.query.filter_by(email='admin@example.com').first():
            # Create a default admin user
            from app import bcrypt
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Admin(
                email='admin@example.com',
                password=hashed_password,
                name='System Admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@example.com / admin123")
        
        print("Database initialization complete!")

if __name__ == '__main__':
    init_db()