# debug_connection.py
import pymysql
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_mysql_service():
    """Test if MySQL service is accessible"""
    print("=" * 50)
    print("1. Testing MySQL Service Connection")
    print("=" * 50)
    
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            connect_timeout=10
        )
        print("✅ MySQL service is running and accessible")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL service error: {e}")
        print("   → Check if XAMPP MySQL is running")
        print("   → Verify port 3307 is correct")
        return False

def test_database_exists():
    """Test if the database exists"""
    print("\n" + "=" * 50)
    print("2. Testing Database Existence")
    print("=" * 50)
    
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password=''
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        print(f"Available databases: {databases}")
        
        if 'job_recommender' in databases:
            print("✅ Database 'job_recommender' exists")
            connection.close()
            return True
        else:
            print("❌ Database 'job_recommender' does not exist")
            print("   → Creating database...")
            cursor.execute("CREATE DATABASE job_recommender")
            print("✅ Database 'job_recommender' created successfully")
            connection.close()
            return True
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n" + "=" * 50)
    print("3. Testing SQLAlchemy Connection")
    print("=" * 50)
    
    connection_strings = [
        'mysql+pymysql://root:@localhost:3307/job_recommender',
        'mysql+pymysql://root@localhost:3307/job_recommender',
        'mysql://root@localhost:3307/job_recommender'
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\nTrying connection string {i}: {conn_str}")
        try:
            engine = create_engine(
                conn_str,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={'connect_timeout': 60}
            )
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                print(f"✅ SQLAlchemy connection {i} successful!")
                return conn_str
                
        except Exception as e:
            print(f"❌ SQLAlchemy connection {i} failed: {e}")
    
    return None

def test_flask_app_config():
    """Test Flask app configuration"""
    print("\n" + "=" * 50)
    print("4. Testing Flask App Configuration")
    print("=" * 50)
    
    try:
        # Import your config
        sys.path.append('.')
        from config import Config
        
        print(f"Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
        print(f"Track modifications: {Config.SQLALCHEMY_TRACK_MODIFICATIONS}")
        
        if hasattr(Config, 'SQLALCHEMY_ENGINE_OPTIONS'):
            print(f"Engine options: {Config.SQLALCHEMY_ENGINE_OPTIONS}")
        
        print("✅ Config file loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_models_import():
    """Test if models can be imported"""
    print("\n" + "=" * 50)
    print("5. Testing Models Import")
    print("=" * 50)
    
    try:
        sys.path.append('.')
        from app.models import User, Graduate, Company, JobPosting
        print("✅ Models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Models import error: {e}")
        return False

def run_all_tests():
    """Run all diagnostic tests"""
    print("DIAGNOSTIC REPORT FOR JOB RECOMMENDER SYSTEM")
    print("=" * 60)
    
    tests = [
        ("MySQL Service", test_mysql_service),
        ("Database Existence", test_database_exists),
        ("SQLAlchemy Connection", test_sqlalchemy_connection),
        ("Flask Config", test_flask_app_config),
        ("Models Import", test_models_import)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! You can now run the application.")
        print("Next step: python run.py")
    else:
        print("❌ SOME TESTS FAILED. Please fix the issues above.")
        print("Common fixes:")
        print("1. Start XAMPP MySQL service")
        print("2. Create database manually")
        print("3. Check config.py database URL")
        print("4. Install missing packages")

if __name__ == "__main__":
    run_all_tests()