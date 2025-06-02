# Flask application configuration file
# UiTM Machang Job Recommender System

import os
from datetime import timedelta

class Config:
    """
    Configuration class for the Flask application
    This configuration automatically handles different environments and database setups
    """
    
    # =================================================================
    # SECURITY CONFIGURATION
    # =================================================================
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uitm-machang-job-recommender-2024-secure-key'
    
    # =================================================================
    # DATABASE CONFIGURATION  
    # =================================================================
    
    # Database URI - tries multiple configurations automatically
    if os.environ.get('DATABASE_URI'):
        # If explicitly set in environment
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    elif os.environ.get('MYSQL_HOST'):
        # If MySQL connection details are provided separately
        mysql_user = os.environ.get('MYSQL_USER', 'root')
        mysql_password = os.environ.get('MYSQL_PASSWORD', '')
        mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
        mysql_port = os.environ.get('MYSQL_PORT', '3306')
        mysql_db = os.environ.get('MYSQL_DATABASE', 'job_recommender')
        
        if mysql_password:
            SQLALCHEMY_DATABASE_URI = f'mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}'
        else:
            SQLALCHEMY_DATABASE_URI = f'mysql://{mysql_user}@{mysql_host}:{mysql_port}/{mysql_db}'
    else:
        # Default: Try common MySQL configurations, fallback to SQLite
        # Most common XAMPP configurations
        SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3307/job_recommender'
        
        # Alternative configurations (uncomment if needed):
        # SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3306/job_recommender'      # XAMPP default port
        # SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost:3306/job_recommender'  # Password: root
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///job_recommender.db'                      # SQLite fallback
    
    # Database configuration options
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,           # Recycle connections every hour
        'pool_pre_ping': True,          # Validate connections before use
        'pool_timeout': 20,             # Connection timeout
        'max_overflow': 0               # Don't allow overflow connections
    }
    
    # =================================================================
    # SESSION CONFIGURATION
    # =================================================================
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Users stay logged in for 7 days
    SESSION_COOKIE_SECURE = False                    # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True                   # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'                  # CSRF protection
    
    # =================================================================
    # FILE UPLOAD CONFIGURATION
    # =================================================================
    
    # Upload folder for resumes, logos, etc.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'resume': {'pdf', 'doc', 'docx'},
        'logo': {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    }
    
    # =================================================================
    # EMAIL CONFIGURATION
    # =================================================================
    
    # Email settings (for notifications, password reset, etc.)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@uitm-jobs.edu.my'
    
    # =================================================================
    # APPLICATION CONFIGURATION
    # =================================================================
    
    # Flask application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', 'on', '1']
    TESTING = False
    
    # Timezone
    TIMEZONE = 'Asia/Kuala_Lumpur'
    
    # Pagination settings
    JOBS_PER_PAGE = 10
    APPLICATIONS_PER_PAGE = 15
    RECOMMENDATIONS_PER_PAGE = 6
    
    # =================================================================
    # RECOMMENDATION SYSTEM CONFIGURATION
    # =================================================================
    
    # Job recommendation settings
    DEFAULT_RECOMMENDATIONS_COUNT = 5
    MAX_RECOMMENDATIONS_COUNT = 10
    MIN_MATCH_SCORE = 0.1  # Minimum similarity score to show recommendation
    
    # Content-based filtering parameters
    TFIDF_MAX_FEATURES = 10000
    TFIDF_NGRAM_RANGE = (1, 2)
    TFIDF_MIN_DF = 1
    TFIDF_MAX_DF = 0.85
    
    # =================================================================
    # SECURITY SETTINGS
    # =================================================================
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 6
    REQUIRE_PASSWORD_UPPERCASE = False
    REQUIRE_PASSWORD_NUMBERS = False
    REQUIRE_PASSWORD_SPECIAL_CHARS = False
    
    # Rate limiting (basic protection)
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # =================================================================
    # DEVELOPMENT SETTINGS
    # =================================================================
    
    # Useful for development
    EXPLAIN_TEMPLATE_LOADING = False
    SEND_FILE_MAX_AGE_DEFAULT = 0 if DEBUG else 43200  # No caching in debug mode
    
    # =================================================================
    # LOGGING CONFIGURATION
    # =================================================================
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    
    # =================================================================
    # ENVIRONMENT-SPECIFIC CONFIGURATIONS
    # =================================================================
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        
        # Create upload directories if they don't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'resumes'), exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'logos'), exist_ok=True)
        
        # Set up logging
        if not app.debug and not app.testing:
            import logging
            from logging.handlers import RotatingFileHandler
            
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/job_recommender.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Job Recommender System startup')


# =================================================================
# PRODUCTION CONFIGURATION (Optional)
# =================================================================

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Use more secure session settings in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Use environment variables for sensitive data in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'please-change-this-in-production'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


# =================================================================
# DEVELOPMENT CONFIGURATION (Optional)  
# =================================================================

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    # SQLite for easy development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///job_recommender_dev.db'


# =================================================================
# TESTING CONFIGURATION (Optional)
# =================================================================

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# =================================================================
# CONFIGURATION SELECTOR
# =================================================================

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': Config
}