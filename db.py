from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create a SQLAlchemy instance
db = SQLAlchemy()

# Create a LoginManager instance
login_manager = LoginManager()
login_manager.login_view = 'admin_login'

def init_app(app):
    """Initialize database and login manager with the Flask app"""
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models import UserAccount
    
    @login_manager.user_loader
    def load_user(user_id):
        return UserAccount.query.get(int(user_id))