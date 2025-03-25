"""
Delayed loader for database and models.
This module is imported by the main Flask application after it has started.
It handles database initialization and model loading in the background.
"""
import logging
import threading
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database reference
db = None

def init_database(app):
    """Initialize database and models in the background"""
    logger.info("Starting delayed database initialization")
    
    try:
        # Configure database connection
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        
        # Import and initialize database
        from flask_sqlalchemy import SQLAlchemy
        from sqlalchemy.orm import DeclarativeBase
        
        class Base(DeclarativeBase):
            pass
        
        global db
        db = SQLAlchemy(model_class=Base)
        db.init_app(app)
        
        # We need to push an application context to work with the database
        with app.app_context():
            # Import models - we need to do it here inside the app context
            import models

            # Set the db in models
            models.db = db
            
            # Create tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Try to create admin user if it doesn't exist
            from models import UserAccount
            try:
                admin = UserAccount.query.filter_by(username='admin').first()
                if not admin:
                    admin = UserAccount(
                        username='admin',
                        email='admin@remoteworkjobboard.com',
                        full_name='Admin User',
                        role='admin'
                    )
                    admin.set_password('remotework_admin2025')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("Admin user created successfully")
            except Exception as e:
                logger.error(f"Error creating admin user: {e}")
                db.session.rollback()
                    
    except Exception as e:
        logger.error(f"Error in delayed database initialization: {e}")

def start_delayed_loading(app):
    """Start the delayed loading process in a separate thread"""
    thread = threading.Thread(target=init_database, args=(app,))
    thread.daemon = True
    thread.start()
    return thread