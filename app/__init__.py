# Application factory pattern
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import Config

# Configure PyMySQL to be used with SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.company import company_bp
    from app.routes.graduate import graduate_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(graduate_bp, url_prefix='/graduate')
    
    # Register main routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Add after creating the app
    import os
    
    # Create upload directories if they don't exist
    upload_dirs = [
        os.path.join(app.static_folder, 'uploads'),
        os.path.join(app.static_folder, 'uploads', 'resumes')
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Make datetime available in templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow}
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

# Import models to ensure they are registered with SQLAlchemy
from app import models

# Import routes module at the end to avoid circular imports
from app.routes import main_bp