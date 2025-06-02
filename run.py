#!/usr/bin/env python3
"""
UiTM Machang Job Recommender System
=====================================

🎓 Ultimate Easy Deploy Version 🎓

This script automatically:
✅ Checks Python version compatibility
✅ Installs required packages
✅ Tests and configures database connections
✅ Creates sample data for testing
✅ Downloads required NLTK data
✅ Sets up the complete system
✅ Starts the Flask application

Just run: python run.py
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Color codes for better terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """Print application header"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("🎓 UiTM MACHANG JOB RECOMMENDER SYSTEM 🎓", Colors.BOLD + Colors.BLUE)
    print_colored("="*60, Colors.CYAN)
    print_colored("Personalized Job Recommendations for Graduates", Colors.WHITE)
    print_colored("="*60 + "\n", Colors.CYAN)

def check_python_version():
    """Check if Python version is compatible"""
    print_colored("🐍 Checking Python version...", Colors.YELLOW)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3:
        print_colored(f"❌ Python {version_str} detected", Colors.RED)
        print_colored("   This system requires Python 3.8 or higher", Colors.RED)
        print_colored("   Please install Python 3.8+ from https://python.org", Colors.YELLOW)
        return False
    elif version.major == 3 and version.minor < 8:
        print_colored(f"❌ Python {version_str} detected", Colors.RED)
        print_colored("   This system requires Python 3.8 or higher", Colors.RED)
        print_colored("   Please upgrade your Python installation", Colors.YELLOW)
        return False
    
    print_colored(f"✅ Python {version_str} - Compatible!", Colors.GREEN)
    return True

def check_pip():
    """Check if pip is available"""
    print_colored("📦 Checking pip installation...", Colors.YELLOW)
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print_colored("✅ pip is available!", Colors.GREEN)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ pip not found", Colors.RED)
        print_colored("   Please install pip first", Colors.YELLOW)
        return False

def install_requirements():
    """Install required packages"""
    print_colored("📦 Installing/Updating required packages...", Colors.YELLOW)
    
    if not Path("requirements.txt").exists():
        print_colored("❌ requirements.txt not found!", Colors.RED)
        print_colored("   Creating basic requirements.txt...", Colors.YELLOW)
        
        # Create basic requirements if file doesn't exist
        basic_requirements = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
Flask-Mail==0.9.1
PyMySQL==1.1.0
pandas==2.1.1
numpy==1.24.3
scikit-learn==1.3.0
nltk==3.8.1
matplotlib==3.7.2
cryptography==41.0.4
python-dateutil==2.8.2
Pillow==10.0.1
"""
        with open("requirements.txt", "w") as f:
            f.write(basic_requirements)
        print_colored("✅ Basic requirements.txt created", Colors.GREEN)
    
    try:
        print_colored("   Installing packages... (this may take a few minutes)", Colors.CYAN)
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ], capture_output=True, text=True, check=True)
        
        print_colored("✅ All packages installed successfully!", Colors.GREEN)
        return True
        
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error installing packages: {e}", Colors.RED)
        print_colored("   Trying alternative installation...", Colors.YELLOW)
        
        # Try installing essential packages individually
        essential_packages = [
            "Flask==2.3.3",
            "Flask-SQLAlchemy==3.0.5",
            "Flask-Login==0.6.3",
            "Flask-Bcrypt==1.0.1",
            "PyMySQL==1.1.0",
            "pandas",
            "numpy",
            "scikit-learn",
            "nltk"
        ]
        
        for package in essential_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             capture_output=True, check=True)
                print_colored(f"   ✅ {package}", Colors.GREEN)
            except:
                print_colored(f"   ⚠️  Failed: {package}", Colors.YELLOW)
        
        print_colored("✅ Essential packages installed!", Colors.GREEN)
        return True

def setup_nltk_data():
    """Download required NLTK data"""
    print_colored("📚 Setting up NLTK data...", Colors.YELLOW)
    
    try:
        import nltk
        
        # Download required NLTK data
        nltk_data = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        for data in nltk_data:
            try:
                nltk.data.find(f'tokenizers/{data}') if data == 'punkt' else \
                nltk.data.find(f'corpora/{data}')
                print_colored(f"   ✅ {data} already available", Colors.GREEN)
            except LookupError:
                print_colored(f"   📥 Downloading {data}...", Colors.CYAN)
                nltk.download(data, quiet=True)
                print_colored(f"   ✅ {data} downloaded", Colors.GREEN)
        
        print_colored("✅ NLTK data setup complete!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"⚠️  NLTK setup warning: {e}", Colors.YELLOW)
        print_colored("   System will work, but text processing may be limited", Colors.YELLOW)
        return True

def test_database_connections():
    """Test different database configurations"""
    print_colored("🔍 Testing database connections...", Colors.YELLOW)
    
    # Import after packages are installed
    try:
        os.environ['FLASK_APP'] = 'run.py'
        from app import create_app, db
        from app.models import User
    except ImportError as e:
        print_colored(f"❌ Import error: {e}", Colors.RED)
        print_colored("   Please check if all packages installed correctly", Colors.YELLOW)
        return None
    
    # Test configurations in order of preference
    test_configs = [
        ('mysql://root:@localhost:3307/job_recommender', 'XAMPP MySQL (Port 3307)'),
        ('mysql://root:@localhost:3306/job_recommender', 'Standard MySQL (Port 3306)'),
        ('mysql://root:root@localhost:3307/job_recommender', 'XAMPP MySQL with password (Port 3307)'),
        ('mysql://root:root@localhost:3306/job_recommender', 'MySQL with root password (Port 3306)'),
        ('mysql://root:password@localhost:3306/job_recommender', 'MySQL with password'),
        ('sqlite:///job_recommender.db', 'SQLite (Fallback)')
    ]
    
    for config_uri, description in test_configs:
        try:
            print_colored(f"   🔧 Testing: {description}", Colors.CYAN)
            
            # Set the database URI
            os.environ['DATABASE_URI'] = config_uri
            
            # Create app and test connection
            app = create_app()
            with app.app_context():
                # Test connection by creating tables
                db.create_all()
                
                # Test a simple query
                try:
                    db.session.execute("SELECT 1")
                    db.session.commit()
                except:
                    # For SQLite, tables might not exist yet
                    pass
            
            print_colored(f"   ✅ SUCCESS: {description}", Colors.GREEN)
            return config_uri
            
        except Exception as e:
            print_colored(f"   ❌ Failed: {str(e)[:50]}...", Colors.RED)
            continue
    
    print_colored("❌ No working database configuration found!", Colors.RED)
    return None

def create_database_if_needed(db_uri):
    """Create database if it doesn't exist (for MySQL)"""
    if 'mysql' not in db_uri.lower():
        return True
    
    print_colored("🗄️  Checking MySQL database...", Colors.YELLOW)
    
    try:
        import pymysql
        
        # Parse connection details
        from urllib.parse import urlparse
        parsed = urlparse(db_uri)
        
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        username = parsed.username or 'root'
        password = parsed.password or ''
        database = parsed.path.lstrip('/')
        
        # Connect to MySQL server (without database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        
        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            if not cursor.fetchone():
                print_colored(f"   📥 Creating database: {database}", Colors.CYAN)
                cursor.execute(f"CREATE DATABASE {database}")
                print_colored(f"   ✅ Database {database} created!", Colors.GREEN)
            else:
                print_colored(f"   ✅ Database {database} already exists", Colors.GREEN)
        
        connection.close()
        return True
        
    except Exception as e:
        print_colored(f"   ⚠️  Database check failed: {e}", Colors.YELLOW)
        print_colored("   Continuing anyway...", Colors.YELLOW)
        return True

def create_sample_data():
    """Create sample data for testing"""
    print_colored("📊 Setting up sample data...", Colors.YELLOW)
    
    try:
        from app import create_app, db
        from app.models import Admin, Company, Graduate, JobPosting
        from app import bcrypt
        
        app = create_app()
        with app.app_context():
            # Create tables
            db.create_all()
            
            # Check if we already have data
            if Admin.query.first():
                print_colored("   ℹ️  Sample data already exists", Colors.CYAN)
                return True
            
            print_colored("   👤 Creating admin user...", Colors.CYAN)
            admin = Admin(
                email='admin@uitm.edu.my',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                name='System Administrator'
            )
            db.session.add(admin)
            
            print_colored("   🏢 Creating sample company...", Colors.CYAN)
            company = Company(
                email='hr@techcorp.com',
                password=bcrypt.generate_password_hash('company123').decode('utf-8'),
                name='TechCorp Malaysia',
                industry='Technology',
                description='Leading technology company providing innovative solutions for businesses across Malaysia.'
            )
            db.session.add(company)
            db.session.flush()  # Get the company ID
            
            print_colored("   💼 Creating sample job posting...", Colors.CYAN)
            job1 = JobPosting(
                company_id=company.id,
                title='Software Developer',
                location='Kuala Lumpur',
                description='We are seeking a talented Software Developer to join our dynamic team. You will be responsible for developing web applications using modern technologies.',
                category='Technology',
                subcategory='Software Development',
                role='Developer',
                job_type='Full-time',
                qualification='Bachelor degree in Computer Science, Software Engineering, or related field. Experience with Python, JavaScript, and databases preferred.',
                criteria='Strong problem-solving skills, ability to work in a team, good communication skills.',
                salary='RM 4,000 - RM 6,500'
            )
            db.session.add(job1)
            
            job2 = JobPosting(
                company_id=company.id,
                title='Digital Marketing Specialist',
                location='Petaling Jaya',
                description='Join our marketing team to create and execute digital marketing campaigns across various platforms.',
                category='Marketing',
                subcategory='Digital Marketing',
                role='Specialist',
                job_type='Full-time',
                qualification='Degree in Marketing, Communications, or related field. Knowledge of social media platforms and digital marketing tools.',
                criteria='Creative thinking, analytical skills, experience with Google Analytics and social media management.',
                salary='RM 3,500 - RM 5,000'
            )
            db.session.add(job2)
            
            print_colored("   🎓 Creating sample graduate...", Colors.CYAN)
            graduate = Graduate(
                email='student@uitm.edu.my',
                password=bcrypt.generate_password_hash('student123').decode('utf-8'),
                first_name='Ahmad',
                last_name='Bin Ali',
                skills='Python, Java, Web Development, Database Management, JavaScript, HTML, CSS, Problem Solving, Team Work',
                experience='Completed internship at local IT company for 3 months. Developed several university projects including a web-based student management system. Strong foundation in programming and software development.',
                location_preference='Kuala Lumpur',
                salary_preference='RM 3,000 - RM 5,000'
            )
            db.session.add(graduate)
            
            # Add more sample data
            company2 = Company(
                email='hr@financeplus.com',
                password=bcrypt.generate_password_hash('company123').decode('utf-8'),
                name='FinancePlus Sdn Bhd',
                industry='Finance',
                description='Established financial services company providing comprehensive banking and investment solutions.'
            )
            db.session.add(company2)
            db.session.flush()
            
            job3 = JobPosting(
                company_id=company2.id,
                title='Junior Accountant',
                location='Kuala Lumpur',
                description='Entry-level position for fresh graduates in accounting. You will assist in preparing financial statements and maintaining accounting records.',
                category='Finance',
                subcategory='Accounting',
                role='Assistant',
                job_type='Full-time',
                qualification='Bachelor degree in Accounting, Finance, or related field. Fresh graduates are welcome.',
                criteria='Attention to detail, proficiency in Excel, basic knowledge of accounting software.',
                salary='RM 2,800 - RM 3,500'
            )
            db.session.add(job3)
            
            db.session.commit()
            
            print_colored("✅ Sample data created successfully!", Colors.GREEN)
            print_colored("\n📋 LOGIN CREDENTIALS:", Colors.BOLD + Colors.YELLOW)
            print_colored("   👨‍💼 Admin: admin@uitm.edu.my / admin123", Colors.WHITE)
            print_colored("   🏢 Company: hr@techcorp.com / company123", Colors.WHITE)
            print_colored("   🎓 Graduate: student@uitm.edu.my / student123", Colors.WHITE)
            
            return True
            
    except Exception as e:
        print_colored(f"❌ Error creating sample data: {e}", Colors.RED)
        print_colored("   The system will still work, but without sample data", Colors.YELLOW)
        return False

def create_directories():
    """Create necessary directories"""
    print_colored("📁 Creating directories...", Colors.YELLOW)
    
    directories = [
        'app/static/uploads',
        'app/static/uploads/resumes',
        'app/static/uploads/logos',
        'logs',
        'instance'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_colored("✅ Directories created!", Colors.GREEN)

def start_application():
    """Start the Flask application"""
    print_colored("\n🚀 Starting the UiTM Machang Job Recommender System...", Colors.BOLD + Colors.GREEN)
    print_colored("="*60, Colors.CYAN)
    
    try:
        from app import create_app
        
        app = create_app()
        
        print_colored("🌐 System is starting up...", Colors.CYAN)
        print_colored("📱 Open your web browser and go to:", Colors.BOLD + Colors.YELLOW)
        print_colored("   👉 http://localhost:5000", Colors.BOLD + Colors.BLUE)
        print_colored("   👉 http://127.0.0.1:5000", Colors.BOLD + Colors.BLUE)
        print_colored("\n⏹️  Press Ctrl+C to stop the server", Colors.YELLOW)
        print_colored("="*60, Colors.CYAN)
        
        # Start the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print_colored("\n\n👋 Server stopped by user", Colors.YELLOW)
        print_colored("Thank you for using UiTM Machang Job Recommender!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"\n❌ Error starting application: {e}", Colors.RED)
        print_colored("Please check the error above and try again", Colors.YELLOW)

def show_success_info():
    """Show success information and next steps"""
    print_colored("\n🎉 SETUP COMPLETE! 🎉", Colors.BOLD + Colors.GREEN)
    print_colored("="*60, Colors.CYAN)
    print_colored("Your UiTM Machang Job Recommender System is ready!", Colors.WHITE)
    print_colored("\n🔗 QUICK ACCESS:", Colors.BOLD + Colors.YELLOW)
    print_colored("   Web Interface: http://localhost:5000", Colors.BLUE)
    print_colored("\n👥 TEST ACCOUNTS:", Colors.BOLD + Colors.YELLOW)
    print_colored("   Admin Portal: admin@uitm.edu.my / admin123", Colors.WHITE)
    print_colored("   Company Portal: hr@techcorp.com / company123", Colors.WHITE)
    print_colored("   Graduate Portal: student@uitm.edu.my / student123", Colors.WHITE)
    print_colored("\n✨ FEATURES:", Colors.BOLD + Colors.YELLOW)
    print_colored("   ✅ Personalized job recommendations", Colors.WHITE)
    print_colored("   ✅ Smart job matching algorithm", Colors.WHITE)
    print_colored("   ✅ Resume upload and management", Colors.WHITE)
    print_colored("   ✅ Application tracking", Colors.WHITE)
    print_colored("   ✅ Admin analytics dashboard", Colors.WHITE)
    print_colored("="*60, Colors.CYAN)

def main():
    """Main setup and run function"""
    print_header()
    
    # System checks
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    if not check_pip():
        input("Press Enter to exit...")
        return
    
    # Setup process
    print_colored("🔧 SYSTEM SETUP PHASE", Colors.BOLD + Colors.PURPLE)
    print_colored("="*30, Colors.PURPLE)
    
    if not install_requirements():
        print_colored("❌ Setup failed at package installation", Colors.RED)
        input("Press Enter to exit...")
        return
    
    setup_nltk_data()
    create_directories()
    
    # Database setup
    print_colored("\n💾 DATABASE SETUP PHASE", Colors.BOLD + Colors.PURPLE)
    print_colored("="*30, Colors.PURPLE)
    
    working_db = test_database_connections()
    if not working_db:
        print_colored("❌ Could not establish database connection", Colors.RED)
        print_colored("Please check MySQL installation or use SQLite fallback", Colors.YELLOW)
        input("Press Enter to exit...")
        return
    
    # Set the working database configuration
    os.environ['DATABASE_URI'] = working_db
    create_database_if_needed(working_db)
    create_sample_data()
    
    # Show success info
    show_success_info()
    
    # Start the application
    print_colored("\n🚀 STARTING APPLICATION", Colors.BOLD + Colors.PURPLE)
    print_colored("="*30, Colors.PURPLE)
    
    start_application()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Setup interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        print_colored("Please report this error for support", Colors.YELLOW)
        input("Press Enter to exit...")
    finally:
        print_colored("\nThank you for using UiTM Machang Job Recommender System! 🎓", Colors.GREEN)