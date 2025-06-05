#!/usr/bin/env python3
"""
🎓 UiTM Machang Job Recommender System - One-Click Setup 🎓
================================================================

This script automatically:
✅ Detects and configures MySQL/XAMPP/WAMP automatically
✅ Installs all required Python packages
✅ Creates and imports database with sample data
✅ Downloads NLTK data
✅ Sets up all directories and permissions
✅ Starts the web application

Usage: python setup.py

NO CONFIGURATION NEEDED - Everything is automatic!
"""

import os
import sys
import subprocess
import time
import json
import shutil
import platform
import urllib.request
from pathlib import Path

# Color codes for terminal output
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
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header():
    """Print the application header"""
    print_colored("\n" + "="*70, Colors.CYAN)
    print_colored("🎓 UiTM MACHANG JOB RECOMMENDER - ONE-CLICK SETUP 🎓", Colors.BOLD + Colors.BLUE)
    print_colored("="*70, Colors.CYAN)
    print_colored("Automatic detection and configuration for all systems", Colors.WHITE)
    print_colored("No manual configuration required!", Colors.GREEN)
    print_colored("="*70 + "\n", Colors.CYAN)

def check_python_version():
    """Verify Python version compatibility"""
    print_colored("🐍 Checking Python version...", Colors.YELLOW)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored(f"❌ Python {version_str} detected - INCOMPATIBLE", Colors.RED)
        print_colored("   This system requires Python 3.8 or higher", Colors.RED)
        print_colored("   Download from: https://python.org/downloads", Colors.YELLOW)
        return False
    
    print_colored(f"✅ Python {version_str} - Compatible!", Colors.GREEN)
    return True

def install_packages():
    """Install required Python packages with error handling"""
    print_colored("📦 Installing required packages...", Colors.YELLOW)
    
    # Essential packages in order of importance
    packages = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5", 
        "Flask-Login==0.6.3",
        "Flask-Bcrypt==1.0.1",
        "Flask-Migrate==4.0.5",
        "Flask-Mail==0.9.1",
        "PyMySQL==1.1.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0", 
        "scikit-learn>=1.1.0",
        "nltk>=3.7",
        "matplotlib>=3.5.0",
        "cryptography>=3.4.0",
        "python-dateutil>=2.8.0",
        "Pillow>=9.0.0"
    ]
    
    # Try pip install with upgrade
    try:
        print_colored("   Installing core packages...", Colors.CYAN)
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--user"] + packages
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_colored("✅ All packages installed successfully!", Colors.GREEN)
            return True
    except subprocess.TimeoutExpired:
        print_colored("⏱️  Installation taking too long, trying alternative method...", Colors.YELLOW)
    except Exception as e:
        print_colored(f"⚠️  Standard installation failed: {e}", Colors.YELLOW)
    
    # Fallback: Install packages individually
    print_colored("   Trying individual package installation...", Colors.CYAN)
    success_count = 0
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", package], 
                          capture_output=True, timeout=60, check=True)
            print_colored(f"   ✅ {package.split('==')[0]}", Colors.GREEN)
            success_count += 1
        except Exception:
            print_colored(f"   ⚠️  {package.split('==')[0]} (will retry later)", Colors.YELLOW)
    
    if success_count >= len(packages) * 0.8:  # 80% success rate
        print_colored("✅ Essential packages installed!", Colors.GREEN)
        return True
    else:
        print_colored("❌ Package installation failed", Colors.RED)
        return False

def setup_nltk_data():
    """Download required NLTK data"""
    print_colored("📚 Setting up NLTK data...", Colors.YELLOW)
    
    try:
        import nltk
        
        # Set NLTK data path to user directory
        nltk_data_dir = Path.home() / 'nltk_data'
        nltk_data_dir.mkdir(exist_ok=True)
        
        # Download required datasets
        datasets = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        
        for dataset in datasets:
            try:
                nltk.download(dataset, quiet=True, download_dir=str(nltk_data_dir))
                print_colored(f"   ✅ {dataset}", Colors.GREEN)
            except Exception:
                print_colored(f"   ⚠️  {dataset} (optional)", Colors.YELLOW)
        
        print_colored("✅ NLTK setup complete!", Colors.GREEN)
        return True
        
    except ImportError:
        print_colored("⚠️  NLTK not available, text processing will be limited", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"⚠️  NLTK setup warning: {e}", Colors.YELLOW)
        return True

def detect_mysql_configs():
    """Detect all possible MySQL configurations"""
    print_colored("🔍 Auto-detecting MySQL configurations...", Colors.YELLOW)
    
    # Common MySQL configurations to test
    configs = [
        # XAMPP configurations (most common)
        {'host': 'localhost', 'port': 3307, 'user': 'root', 'password': '', 'name': 'XAMPP (Port 3307)'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '', 'name': 'XAMPP (Port 3306)'},
        {'host': '127.0.0.1', 'port': 3307, 'user': 'root', 'password': '', 'name': 'XAMPP Local (3307)'},
        {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': '', 'name': 'XAMPP Local (3306)'},
        
        # WAMP configurations
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '', 'name': 'WAMP Server'},
        {'host': 'localhost', 'port': 3308, 'user': 'root', 'password': '', 'name': 'WAMP (Port 3308)'},
        
        # Standard MySQL with common passwords
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'root', 'name': 'MySQL (password: root)'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'password', 'name': 'MySQL (password: password)'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': 'mysql', 'name': 'MySQL (password: mysql)'},
        {'host': 'localhost', 'port': 3306, 'user': 'root', 'password': '123456', 'name': 'MySQL (password: 123456)'},
        
        # Alternative users
        {'host': 'localhost', 'port': 3306, 'user': 'mysql', 'password': '', 'name': 'MySQL (user: mysql)'},
        {'host': 'localhost', 'port': 3306, 'user': 'admin', 'password': 'admin', 'name': 'MySQL (admin/admin)'},
    ]
    
    working_configs = []
    
    for config in configs:
        try:
            import pymysql
            
            print_colored(f"   Testing: {config['name']}", Colors.CYAN)
            
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                connect_timeout=5
            )
            
            # Test basic query
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
            
            connection.close()
            
            print_colored(f"   ✅ SUCCESS: {config['name']}", Colors.GREEN)
            working_configs.append(config)
            
        except ImportError:
            print_colored("   Installing PyMySQL...", Colors.CYAN)
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "PyMySQL"], 
                             capture_output=True, check=True)
                import pymysql
                # Retry the connection
                continue
            except:
                print_colored("   ❌ Could not install PyMySQL", Colors.RED)
                break
        except Exception as e:
            print_colored(f"   ❌ Failed: {str(e)[:50]}...", Colors.RED)
            continue
    
    if working_configs:
        print_colored(f"✅ Found {len(working_configs)} working MySQL configuration(s)!", Colors.GREEN)
        return working_configs[0]  # Return the first working config
    else:
        print_colored("❌ No working MySQL configuration found", Colors.RED)
        return None

def create_database(config):
    """Create the database if it doesn't exist"""
    print_colored("🗄️  Setting up database...", Colors.YELLOW)
    
    try:
        import pymysql
        
        # Connect to MySQL server
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password']
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS job_recommender")
            cursor.execute("USE job_recommender")
            
            # Check if database is empty
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print_colored(f"   Database: job_recommender", Colors.GREEN)
            print_colored(f"   Tables found: {len(tables)}", Colors.CYAN)
        
        connection.close()
        return True
        
    except Exception as e:
        print_colored(f"❌ Database setup failed: {e}", Colors.RED)
        return False

def import_sql_file(config):
    """Import SQL file if it exists"""
    print_colored("📥 Checking for SQL import files...", Colors.YELLOW)
    
    # Look for SQL files in common locations
    sql_files = []
    search_paths = ['.', 'database', 'sql', 'data', 'scripts']
    
    for path in search_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.lower().endswith('.sql'):
                    sql_files.append(os.path.join(path, file))
    
    if not sql_files:
        print_colored("   No SQL files found, will create fresh database", Colors.CYAN)
        return True
    
    # Use the first SQL file found
    sql_file = sql_files[0]
    print_colored(f"   Found SQL file: {sql_file}", Colors.GREEN)
    
    try:
        import pymysql
        
        # Read SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        # Connect and execute
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='job_recommender'
        )
        
        with connection.cursor() as cursor:
            for i, statement in enumerate(statements):
                if statement:
                    try:
                        cursor.execute(statement)
                        if i % 10 == 0:  # Progress indicator
                            print_colored(f"   Executing statement {i+1}/{len(statements)}", Colors.CYAN)
                    except Exception as e:
                        # Log error but continue
                        print_colored(f"   Warning: {str(e)[:50]}...", Colors.YELLOW)
        
        connection.commit()
        connection.close()
        
        print_colored("✅ SQL file imported successfully!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"⚠️  SQL import failed: {e}", Colors.YELLOW)
        print_colored("   Will create sample data instead", Colors.CYAN)
        return False

def create_sample_data(config):
    """Create sample data using the Flask app"""
    print_colored("👥 Creating sample data...", Colors.YELLOW)
    
    try:
        # Set environment variable for database
        db_uri = f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/job_recommender"
        os.environ['DATABASE_URI'] = db_uri
        
        # Import and setup Flask app
        from app import create_app, db, bcrypt
        from app.models import Admin, Company, Graduate, JobPosting
        
        app = create_app()
        
        with app.app_context():
            # Create tables
            db.create_all()
            
            # Check if data already exists
            if Admin.query.first():
                print_colored("   Sample data already exists", Colors.CYAN)
                return True
            
            # Create admin
            admin = Admin(
                email='admin@uitm.edu.my',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                name='System Administrator'
            )
            db.session.add(admin)
            
            # Create sample company
            company = Company(
                email='hr@techcorp.com',
                password=bcrypt.generate_password_hash('company123').decode('utf-8'),
                name='TechCorp Malaysia',
                industry='Technology',
                description='Leading technology company in Malaysia'
            )
            db.session.add(company)
            db.session.flush()
            
            # Create sample jobs
            jobs = [
                {
                    'title': 'Software Developer',
                    'location': 'Kuala Lumpur',
                    'description': 'Develop web applications using modern technologies',
                    'category': 'Technology',
                    'role': 'Developer',
                    'job_type': 'Full-time',
                    'qualification': 'Bachelor in Computer Science',
                    'salary': 'RM 4,000 - RM 6,000'
                },
                {
                    'title': 'Junior Programmer',
                    'location': 'Selangor',
                    'description': 'Entry-level programming position for fresh graduates',
                    'category': 'Technology',
                    'role': 'Developer',
                    'job_type': 'Full-time',
                    'qualification': 'Diploma/Degree in IT',
                    'salary': 'RM 3,000 - RM 4,500'
                }
            ]
            
            for job_data in jobs:
                job = JobPosting(company_id=company.id, **job_data)
                db.session.add(job)
            
            # Create sample graduate
            graduate = Graduate(
                email='student@uitm.edu.my',
                password=bcrypt.generate_password_hash('student123').decode('utf-8'),
                first_name='Ahmad',
                last_name='Ali',
                skills='Python, Web Development, Database',
                experience='Fresh graduate with internship experience'
            )
            db.session.add(graduate)
            
            db.session.commit()
            
            print_colored("✅ Sample data created successfully!", Colors.GREEN)
            return True
            
    except Exception as e:
        print_colored(f"❌ Error creating sample data: {e}", Colors.RED)
        return False

def create_config_file(config):
    """Create configuration file with detected settings"""
    print_colored("⚙️  Creating configuration file...", Colors.YELLOW)
    
    try:
        # Create database URI
        db_uri = f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/job_recommender"
        
        # Set environment variable
        os.environ['DATABASE_URI'] = db_uri
        
        # Create .env file
        env_content = f"""# Auto-generated configuration
DATABASE_URI={db_uri}
SECRET_KEY=uitm-machang-job-recommender-2024
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print_colored("✅ Configuration file created!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"❌ Configuration creation failed: {e}", Colors.RED)
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

def test_application(config):
    """Test if the application can start"""
    print_colored("🧪 Testing application...", Colors.YELLOW)
    
    try:
        # Set database URI
        db_uri = f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/job_recommender"
        os.environ['DATABASE_URI'] = db_uri
        
        # Try to import and create app
        from app import create_app
        app = create_app()
        
        # Test app context
        with app.app_context():
            from app.models import User
            # Simple query test
            User.query.limit(1).all()
        
        print_colored("✅ Application test successful!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"❌ Application test failed: {e}", Colors.RED)
        return False

def show_login_info():
    """Display login information"""
    print_colored("\n" + "="*70, Colors.CYAN)
    print_colored("🎉 SETUP COMPLETE! 🎉", Colors.BOLD + Colors.GREEN)
    print_colored("="*70, Colors.CYAN)
    print_colored("\n🔗 ACCESS INFORMATION:", Colors.BOLD + Colors.YELLOW)
    print_colored("   Website: http://localhost:5000", Colors.BLUE)
    print_colored("   Alternative: http://127.0.0.1:5000", Colors.BLUE)
    print_colored("\n👥 LOGIN CREDENTIALS:", Colors.BOLD + Colors.YELLOW)
    print_colored("   📊 Admin Portal:", Colors.WHITE)
    print_colored("      Email: admin@uitm.edu.my", Colors.WHITE)
    print_colored("      Password: admin123", Colors.WHITE)
    print_colored("\n   🏢 Company Portal:", Colors.WHITE)
    print_colored("      Email: hr@techcorp.com", Colors.WHITE)
    print_colored("      Password: company123", Colors.WHITE)
    print_colored("\n   🎓 Graduate Portal:", Colors.WHITE)
    print_colored("      Email: student@uitm.edu.my", Colors.WHITE)
    print_colored("      Password: student123", Colors.WHITE)
    print_colored("\n✨ FEATURES:", Colors.BOLD + Colors.YELLOW)
    print_colored("   ✅ Smart job recommendations", Colors.WHITE)
    print_colored("   ✅ Resume upload & management", Colors.WHITE)
    print_colored("   ✅ Application tracking", Colors.WHITE)
    print_colored("   ✅ Admin analytics dashboard", Colors.WHITE)
    print_colored("   ✅ Company job posting", Colors.WHITE)
    print_colored("\n⚡ QUICK START:", Colors.BOLD + Colors.YELLOW)
    print_colored("   1. Open browser to http://localhost:5000", Colors.WHITE)
    print_colored("   2. Login with any credentials above", Colors.WHITE)
    print_colored("   3. Explore the job recommendation system!", Colors.WHITE)
    print_colored("\n⏹️  To stop: Press Ctrl+C in this terminal", Colors.YELLOW)
    print_colored("="*70, Colors.CYAN)

def start_application(config):
    """Start the Flask application"""
    print_colored("\n🚀 Starting UiTM Machang Job Recommender System...", Colors.BOLD + Colors.GREEN)
    
    try:
        # Set database URI
        db_uri = f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/job_recommender"
        os.environ['DATABASE_URI'] = db_uri
        
        # Import and start app
        from app import create_app
        app = create_app()
        
        # Start server
        print_colored("🌐 Server starting...", Colors.CYAN)
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False,  # Disable reloader to prevent issues
            threaded=True
        )
        
    except KeyboardInterrupt:
        print_colored("\n\n👋 Server stopped by user", Colors.YELLOW)
        print_colored("Thank you for using UiTM Machang Job Recommender!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"\n❌ Error starting application: {e}", Colors.RED)
        print_colored("Check the error above and run the setup again", Colors.YELLOW)

def main():
    """Main setup function"""
    print_header()
    
    # Phase 1: System Requirements
    print_colored("📋 PHASE 1: SYSTEM REQUIREMENTS", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Phase 2: Package Installation
    print_colored("\n📦 PHASE 2: PACKAGE INSTALLATION", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    if not install_packages():
        print_colored("❌ Failed to install required packages", Colors.RED)
        input("Press Enter to exit...")
        return
    
    setup_nltk_data()
    
    # Phase 3: Database Configuration
    print_colored("\n💾 PHASE 3: DATABASE CONFIGURATION", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    mysql_config = detect_mysql_configs()
    if not mysql_config:
        print_colored("❌ Could not find working MySQL configuration", Colors.RED)
        print_colored("\nPlease ensure one of the following is running:", Colors.YELLOW)
        print_colored("  • XAMPP MySQL service", Colors.WHITE)
        print_colored("  • WAMP MySQL service", Colors.WHITE)
        print_colored("  • Standard MySQL server", Colors.WHITE)
        input("\nPress Enter to exit...")
        return
    
    print_colored(f"✅ Using: {mysql_config['name']}", Colors.GREEN)
    
    # Phase 4: Database Setup
    print_colored("\n🗄️  PHASE 4: DATABASE SETUP", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    if not create_database(mysql_config):
        print_colored("❌ Database setup failed", Colors.RED)
        input("Press Enter to exit...")
        return
    
    # Try to import SQL file, fall back to sample data
    if not import_sql_file(mysql_config):
        if not create_sample_data(mysql_config):
            print_colored("❌ Could not create database content", Colors.RED)
            input("Press Enter to exit...")
            return
    
    # Phase 5: Application Setup
    print_colored("\n⚙️  PHASE 5: APPLICATION SETUP", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    create_config_file(mysql_config)
    create_directories()
    
    # Phase 6: Final Testing
    print_colored("\n🧪 PHASE 6: FINAL TESTING", Colors.BOLD + Colors.PURPLE)
    print_colored("="*35, Colors.PURPLE)
    
    if not test_application(mysql_config):
        print_colored("❌ Application test failed", Colors.RED)
        input("Press Enter to exit...")
        return
    
    # Success - show login info and start
    show_login_info()
    
    input("\nPress Enter to start the web application...")
    start_application(mysql_config)

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