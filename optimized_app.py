"""
Optimized entry point for the Remote Work Job Board application.
"""
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create a simple route that loads quickly
@app.route('/startup-check')
def startup_check():
    """Quick health check for startup"""
    return jsonify({"status": "ok"})

# Import the rest of the application after defining the quick health check
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize database
from db import db, init_app
init_app(app)

# Define some constants
ADMIN_USER = "admin"
ADMIN_PASSWORD = generate_password_hash("remotework_admin2025")

# Job categories
JOB_CATEGORIES = {
    "technology": ["Software Development", "IT & Networking", "Data Science", "DevOps", "Cybersecurity", "Product Management"],
    "creative": ["Design", "Writing", "Marketing", "Video Production", "Animation", "Social Media"],
    "professional": ["Accounting", "Legal", "HR", "Customer Service", "Sales", "Consulting"],
    "healthcare": ["Telemedicine", "Medical Coding", "Health Coaching", "Mental Health", "Medical Writing"],
    "education": ["Online Teaching", "Curriculum Development", "Educational Consulting", "Tutoring", "Course Creation"],
    "skilled-trades": ["Remote Technician", "Project Management", "Quality Assurance", "Virtual Installation Support"]
}

# Sample data for jobs
JOBS = [
    {
        "id": 1,
        "title": "Remote Software Engineer",
        "company": "TechCorp",
        "location": "Remote (Worldwide)",
        "category": "technology",
        "subcategory": "Software Development",
        "job_type": "Full-time",
        "salary": "$90,000 - $120,000",
        "description": "We're looking for an experienced software engineer to join our remote team.",
        "requirements": "5+ years experience with Python, JavaScript, and cloud platforms.",
        "application_url": "https://example.com/apply",
        "posted_date": "2025-03-20",
        "is_active": True,
        "views": 245
    },
    # More sample jobs would go here
]

# Create database tables after startup check is defined
with app.app_context():
    try:
        # Import models here to ensure they're registered before creating tables
        from models import UserAccount, Job, BlogPost, WebsiteContent, SiteVisit, JobApplication, NewsletterSubscriber
        
        # Create all tables
        db.create_all()
        
        # Check if admin user exists, create if not
        admin = UserAccount.query.filter_by(username=ADMIN_USER).first()
        if not admin:
            admin = UserAccount(
                username=ADMIN_USER,
                email="admin@remoteworkjobs.com",
                role="admin",
                is_active=True
            )
            admin.set_password("remotework_admin2025")
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created successfully")
        
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def format_date(date):
    """Format date for display"""
    if isinstance(date, datetime.datetime):
        return date.strftime("%B %d, %Y")
    return date

@app.route('/')
def index():
    """Homepage with featured jobs"""
    try:
        # Get featured jobs from database
        featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(3).all()
        
        # Convert SQLAlchemy models to dictionaries
        featured_jobs = [job.to_dict() for job in featured_jobs]
        
        # Use sample data if no jobs exist yet
        if not featured_jobs and JOBS:
            featured_jobs = JOBS[:3]
            
        return render_template('index.html', jobs=featured_jobs)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        # Return a simple response during startup or if there's an error
        return "Remote Work Job Board is starting up. Please refresh in a moment."

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Remote Work Job Board API is running"})

# Add template filters
app.jinja_env.globals.update(format_date=format_date)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)