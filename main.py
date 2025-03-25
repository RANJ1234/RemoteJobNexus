import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "remote_work_dev_key")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Models
class UserAccount(db.Model, UserMixin):
    __tablename__ = 'user_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # admin, employer, user
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_employer(self):
        return self.role == 'employer'

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100))
    job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
    category = db.Column(db.String(50))  # white-collar, blue-collar, grey-collar
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    contact_email = db.Column(db.String(100))
    application_url = db.Column(db.String(255))
    posted_date = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    source_url = db.Column(db.String(255))  # If scraped from another site
    
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=True)
    user = db.relationship('UserAccount', backref=db.backref('jobs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type,
            'category': self.category,
            'description': self.description,
            'requirements': self.requirements,
            'posted_date': self.posted_date.strftime('%Y-%m-%d'),
            'is_active': self.is_active
        }

class WebsiteContent(db.Model):
    __tablename__ = 'website_content'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)  # JSON content stored as text
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))

# Create all tables
with app.app_context():
    db.create_all()
    
    # Create admin user if none exists
    admin = UserAccount.query.filter_by(username='admin').first()
    if not admin:
        admin = UserAccount(
            username='admin',
            email='admin@remotework.com',
            full_name='Site Administrator',
            role='admin'
        )
        admin.set_password('remotework_admin2025')
        db.session.add(admin)
        db.session.commit()

# Basic routes
@app.route('/')
def index():
    featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(10).all()
    return render_template('index.html', featured_jobs=featured_jobs)

@app.route('/jobs')
def jobs():
    category = request.args.get('category', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    query = Job.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if job_type:
        query = query.filter_by(job_type=job_type)
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    all_jobs = query.order_by(Job.posted_date.desc()).all()
    return render_template('jobs.html', jobs=all_jobs, category=category, job_type=job_type, location=location)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    job.views += 1
    db.session.commit()
    return render_template('job_detail.html', job=job)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        job = Job(
            title=request.form.get('title'),
            company=request.form.get('company'),
            location=request.form.get('location'),
            salary=request.form.get('salary'),
            job_type=request.form.get('job_type'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            requirements=request.form.get('requirements'),
            contact_email=request.form.get('contact_email'),
            application_url=request.form.get('application_url'),
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    return render_template('post_job.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = UserAccount.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.now()
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('index'))
    
    job_count = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    user_count = UserAccount.query.count()
    
    return render_template('admin/dashboard.html', 
                           job_count=job_count, 
                           active_jobs=active_jobs, 
                           user_count=user_count)

@app.route('/admin/jobs')
@login_required
def admin_jobs():
    if not current_user.is_admin():
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('index'))
    
    all_jobs = Job.query.order_by(Job.posted_date.desc()).all()
    return render_template('admin/jobs.html', jobs=all_jobs)

@app.route('/admin/delete-job/<int:job_id>')
@login_required
def admin_delete_job(job_id):
    if not current_user.is_admin():
        flash('Access denied: Admin privileges required', 'danger')
        return redirect(url_for('index'))
    
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/export-jobs')
@login_required
def admin_export_jobs():
    if not current_user.is_admin():
        return jsonify({"error": "Access denied"}), 403
    
    jobs = Job.query.all()
    job_data = [job.to_dict() for job in jobs]
    return jsonify(job_data)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Application is running"})

# Start the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)