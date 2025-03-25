"""
Database configuration module for the Remote Work Job Board.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create a SQLAlchemy instance - this will be initialized later
db = None

# Create a LoginManager instance
login_manager = LoginManager()
login_manager.login_view = 'admin_login'

def init_app(app):
    """Initialize database and login manager with the Flask app"""
    global db
    
    # Only initialize if db is not already set
    if db is None:
        from models import db as models_db
        db = models_db
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models import UserAccount
    
    @login_manager.user_loader
    def load_user(user_id):
        return UserAccount.query.get(int(user_id))