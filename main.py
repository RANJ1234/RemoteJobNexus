import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import datetime
import json
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Import models so that variables like Job and UserAccount are globally available
try:
    from models import UserAccount, Job, BlogPost, WebsiteContent, SiteVisit, JobApplication, NewsletterSubscriber
except ImportError:
    # These type placeholders help with type checking when models are unavailable.
    UserAccount = None
    Job = None

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"]pip install flask werkzeug python-dotenv = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
from db import db, init_app

# Initialize app with database and login manager
init_app(app)

# Admin credentials - change in production
ADMIN_USER = "admin"
ADMIN_PASSWORD = generate_password_hash("remotework_admin2025")

# Create database tables if they don't exist
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
            admin.set_password("remotework_admin2025")  # Using the set_password method instead of direct hash
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Admin user created successfully")
        
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {e}")

# Job categories and subcategories
JOB_CATEGORIES = {
    "technology": ["Software Development", "IT & Networking", "Data Science", "DevOps", "Cybersecurity", "Product Management"],
    "creative": ["Design", "Writing", "Marketing", "Video Production", "Animation", "Social Media"],
    "professional": ["Accounting", "Legal", "HR", "Customer Service", "Sales", "Consulting"],
    "healthcare": ["Telemedicine", "Medical Coding", "Health Coaching", "Mental Health", "Medical Writing"],
    "education": ["Online Teaching", "Curriculum Development", "Educational Consulting", "Tutoring", "Course Creation"],
    "skilled-trades": ["Remote Technician", "Project Management", "Quality Assurance", "Virtual Installation Support"]
}

# Sample data for jobs - replace with database in production
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
        "posted_date": datetime.datetime(2025, 3, 20),
        "is_active": True,
        "views": 245
    },
    {
        "id": 2,
        "title": "Remote Customer Support Specialist",
        "company": "SupportNow",
        "location": "Remote (US Only)",
        "category": "professional",
        "subcategory": "Customer Service",
        "job_type": "Full-time",
        "salary": "$45,000 - $55,000",
        "description": "Join our customer support team and help clients solve their technical issues.",
        "requirements": "2+ years in customer support, excellent communication skills.",
        "application_url": "https://example.com/apply",
        "posted_date": datetime.datetime(2025, 3, 22),
        "is_active": True,
        "views": 127
    },
    {
        "id": 3,
        "title": "Remote HVAC Technician Coordinator",
        "company": "CoolAir Systems",
        "location": "Remote with occasional travel",
        "category": "skilled-trades",
        "subcategory": "Project Management",
        "job_type": "Contract",
        "salary": "$35 - $45 per hour",
        "description": "Coordinate with our team of field technicians to optimize service delivery.",
        "requirements": "Experience in HVAC and team coordination.",
        "application_url": "https://example.com/apply",
        "posted_date": datetime.datetime(2025, 3, 15),
        "is_active": True,
        "views": 78
    },
    {
        "id": 4,
        "title": "Remote Graphic Designer",
        "company": "DesignHub",
        "location": "Remote (Worldwide)",
        "category": "creative",
        "subcategory": "Design",
        "job_type": "Part-time",
        "salary": "$30 - $50 per hour",
        "description": "Create engaging visual content for our marketing campaigns and products.",
        "requirements": "Proficiency in Adobe Creative Suite and 3+ years of design experience.",
        "application_url": "https://example.com/apply",
        "posted_date": datetime.datetime(2025, 3, 18),
        "is_active": True,
        "views": 156
    },
    {
        "id": 5,
        "title": "Online Math Tutor",
        "company": "LearnOnline",
        "location": "Remote (Worldwide)",
        "category": "education",
        "subcategory": "Tutoring",
        "job_type": "Flexible",
        "salary": "$25 - $40 per hour",
        "description": "Teach mathematics to students of all levels through our virtual classroom platform.",
        "requirements": "Degree in Mathematics or related field and previous teaching experience.",
        "application_url": "https://example.com/apply",
        "posted_date": datetime.datetime(2025, 3, 10),
        "is_active": True,
        "views": 93
    }
]

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
        app.logger.error(f"Error in index route: {e}")
        # Fallback to sample data in case of error
        return render_template('index.html', jobs=JOBS[:3])

@app.route('/jobs')
def jobs():
    """Job listings page with filters"""
    try:
        # Get filter parameters
        category = request.args.get('category', '')
        subcategory = request.args.get('subcategory', '')
        job_type = request.args.get('job_type', '')
        location = request.args.get('location', '')
        
        # Start with base query
        query = Job.query.filter_by(is_active=True)
        
        # Apply filters
        if category:
            query = query.filter(Job.category == category)
        
        if subcategory:
            query = query.filter(Job.subcategory == subcategory)
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        # Order by most recent
        filtered_jobs = query.order_by(Job.posted_date.desc()).all()
        
        # Convert SQLAlchemy models to dictionaries
        filtered_jobs = [job.to_dict() for job in filtered_jobs]
        
        # Use sample data if no jobs exist yet
        if not filtered_jobs and JOBS:
            filtered_jobs = JOBS
            if category:
                filtered_jobs = [job for job in filtered_jobs if job.get('category') == category]
            if subcategory:
                filtered_jobs = [job for job in filtered_jobs if job.get('subcategory') == subcategory]
            if job_type:
                filtered_jobs = [job for job in filtered_jobs if job.get('job_type') == job_type]
            if location:
                filtered_jobs = [job for job in filtered_jobs 
                               if location.lower() in job.get('location', '').lower()]
        
        return render_template('jobs.html', 
                            jobs=filtered_jobs, 
                            category=category,
                            subcategory=subcategory,
                            job_type=job_type,
                            location=location,
                            job_categories=JOB_CATEGORIES)
    except Exception as e:
        app.logger.error(f"Error in jobs route: {e}")
        # Fallback to sample data in case of error
        return render_template('jobs.html', 
                            jobs=JOBS, 
                            category=category,
                            subcategory=subcategory,
                            job_type=job_type,
                            location=location,
                            job_categories=JOB_CATEGORIES)

@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    try:
        # Get job from database
        job = Job.query.get(job_id)
        
        if not job:
            # Try to find job in sample data if not in database
            sample_job = next((j for j in JOBS if j['id'] == job_id), None)
            if sample_job:
                return render_template('job_detail.html', job=sample_job)
            
            flash('Job not found', 'error')
            return redirect(url_for('jobs'))
        
        # Increment view count
        job.views += 1
        db.session.commit()
        
        # Convert SQLAlchemy model to dictionary
        job_data = job.to_dict()
        
        return render_template('job_detail.html', job=job_data)
    except Exception as e:
        app.logger.error(f"Error in job_detail route: {e}")
        # Try to find job in sample data
        sample_job = next((j for j in JOBS if j['id'] == job_id), None)
        if sample_job:
            return render_template('job_detail.html', job=sample_job)
        
        flash('Error loading job details', 'error')
        return redirect(url_for('jobs'))

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    """Job submission form"""
    if request.method == 'POST':
        try:
            # Create new job from form data
            new_job = Job(
                title=request.form.get('title'),
                company=request.form.get('company'),
                location=request.form.get('location'),
                job_type=request.form.get('job_type'),
                category=request.form.get('category'),
                subcategory=request.form.get('subcategory'),
                salary=request.form.get('salary'),
                description=request.form.get('description'),
                requirements=request.form.get('requirements'),
                contact_email=request.form.get('contact_email'),
                application_url=request.form.get('application_url'),
                is_active=True
            )
            
            # Save to database
            db.session.add(new_job)
            db.session.commit()
            
            flash('Job posted successfully!', 'success')
            return redirect(url_for('job_detail', job_id=new_job.id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error posting job: {e}")
            flash(f'Error posting job: {str(e)}', 'error')
    
    return render_template('post_job.html', job_categories=JOB_CATEGORIES)

@app.route('/extract-job', methods=['POST'])
def extract_job():
    """Extract job details from URL (API endpoint)"""
    data = request.get_json() if request.is_json else None
    
    # Get URL from JSON body or fallback to form data
    url = data.get('url') if data else request.form.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
    
    # Import web scraping function
    from web_scraper import extract_job_details, is_valid_url
    
    if not is_valid_url(url):
        return jsonify({"success": False, "error": "Invalid URL format"}), 400
    
    try:
        # Extract job details from the URL
        result = extract_job_details(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"Error extracting job details: {str(e)}",
            "job": {}
        }), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Check for the user in the database
            user = UserAccount.query.filter_by(username=username).first()
            
            if user and user.is_admin() and user.check_password(password):
                session['admin_logged_in'] = True
                session['admin_user_id'] = user.id
                session['admin_username'] = user.username
                
                # Update last login
                user.last_login = datetime.datetime.now()
                db.session.commit()
                
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                # Fallback to environment admin credentials for development
                if username == ADMIN_USER and check_password_hash(ADMIN_PASSWORD, password):
                    session['admin_logged_in'] = True
                    session['admin_username'] = ADMIN_USER
                    flash('Login successful (using development credentials)!', 'success')
                    return redirect(url_for('admin_dashboard'))
                
                flash('Invalid credentials', 'error')
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            # Fallback to environment admin credentials
            if username == ADMIN_USER and check_password_hash(ADMIN_PASSWORD, password):
                session['admin_logged_in'] = True
                session['admin_username'] = ADMIN_USER
                flash('Login successful (using development credentials)!', 'success')
                return redirect(url_for('admin_dashboard'))
            
            flash('Error during login process', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Get stats from database
        job_count = Job.query.count()
        active_job_count = Job.query.filter_by(is_active=True).count()
        total_views = db.session.query(db.func.sum(Job.views)).scalar() or 0
        user_count = UserAccount.query.count()
        
        stats = {
            'total_jobs': job_count,
            'active_jobs': active_job_count,
            'total_views': total_views,
            'total_users': user_count
        }
        
        # If no data in database, use sample data
        if job_count == 0 and JOBS:
            stats = {
                'total_jobs': len(JOBS),
                'active_jobs': sum(1 for job in JOBS if job['is_active']),
                'total_views': sum(job['views'] for job in JOBS),
                'total_users': 1  # Admin only
            }
    except Exception as e:
        app.logger.error(f"Dashboard stats error: {e}")
        # Fallback to sample data
        stats = {
            'total_jobs': len(JOBS),
            'active_jobs': sum(1 for job in JOBS if job['is_active']),
            'total_views': sum(job['views'] for job in JOBS),
            'total_users': 1  # Admin only
        }
    
    return render_template('admin/dashboard.html', stats=stats, username=session.get('admin_username', 'Admin'))

@app.route('/admin/jobs')
def admin_jobs():
    """Admin job management"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Get jobs from database
        jobs_list = Job.query.order_by(Job.posted_date.desc()).all()
        
        # Convert to list of dictionaries
        jobs_data = [job.to_dict() for job in jobs_list]
        
        # Use sample data if no jobs in database
        if not jobs_data and JOBS:
            jobs_data = JOBS
    except Exception as e:
        app.logger.error(f"Admin jobs list error: {e}")
        # Fallback to sample data
        jobs_data = JOBS
    
    return render_template('admin/jobs.html', jobs=jobs_data)

@app.route('/admin/jobs/delete/<int:job_id>')
def admin_delete_job(job_id):
    """Delete a job"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Find and delete job from database
        job = Job.query.get(job_id)
        if job:
            db.session.delete(job)
            db.session.commit()
            flash('Job deleted successfully', 'success')
        else:
            # If not in database, try to remove from sample data
            old_length = len(JOBS)
            # Using a non-global approach to modify JOBS
            new_jobs = [job for job in JOBS if job['id'] != job_id]
            # Update the global list
            JOBS.clear()
            JOBS.extend(new_jobs)
            if len(JOBS) < old_length:
                flash('Job deleted from sample data', 'success')
            else:
                flash('Job not found', 'error')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting job: {e}")
        
        # Fallback to sample data
        old_length = len(JOBS)
        # Using a non-global approach to modify JOBS
        new_jobs = [job for job in JOBS if job['id'] != job_id]
        # Update the global list
        JOBS.clear()
        JOBS.extend(new_jobs)
        if len(JOBS) < old_length:
            flash('Job deleted from sample data', 'success')
        else:
            flash(f'Error deleting job: {str(e)}', 'error')
    
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/export')
def admin_export_jobs():
    """Export jobs as JSON"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Get jobs from database
        jobs_list = Job.query.order_by(Job.posted_date.desc()).all()
        
        # Convert to list of dictionaries
        export_jobs = [job.to_dict() for job in jobs_list]
        
        # If no jobs in database, use sample data
        if not export_jobs and JOBS:
            export_jobs = []
            for job in JOBS:
                job_copy = job.copy()
                job_copy['posted_date'] = format_date(job_copy['posted_date'])
                export_jobs.append(job_copy)
    except Exception as e:
        app.logger.error(f"Error exporting jobs: {e}")
        # Fallback to sample data
        export_jobs = []
        for job in JOBS:
            job_copy = job.copy()
            job_copy['posted_date'] = format_date(job_copy['posted_date'])
            export_jobs.append(job_copy)
    
    return jsonify(export_jobs)

@app.route('/admin/scrape-job', methods=['GET', 'POST'])
def admin_scrape_job():
    """Admin page for scraping jobs from URLs"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        url = request.form.get('job_url')
        save_to_db = request.form.get('save_to_db') == 'yes'
        
        if not url:
            flash('URL is required', 'error')
            return redirect(url_for('admin_scrape_job'))
            
        # Import web scraping function
        from web_scraper import extract_job_details, is_valid_url
        
        if not is_valid_url(url):
            flash('Invalid URL format', 'error')
            return redirect(url_for('admin_scrape_job'))
        
        try:
            # Extract job details from the URL
            result = extract_job_details(url)
            
            if result.get('success'):
                job_data = result.get('job', {})
                
                if save_to_db and job_data:
                    # Save to database
                    new_job = Job(
                        title=job_data.get('title', 'Untitled Job'),
                        company=job_data.get('company', 'Unknown Company'),
                        location=job_data.get('location', 'Remote'),
                        job_type=job_data.get('job_type', 'Full-time'),
                        category=job_data.get('category', 'technology'),
                        subcategory=job_data.get('subcategory', 'Software Development'),
                        salary=job_data.get('salary', ''),
                        description=job_data.get('description', ''),
                        requirements=job_data.get('requirements', ''),
                        application_url=url,
                        source_url=url,
                        is_active=True
                    )
                    
                    db.session.add(new_job)
                    db.session.commit()
                    
                    flash(f'Job "{new_job.title}" scraped and saved to database!', 'success')
                    return redirect(url_for('job_detail', job_id=new_job.id))
                else:
                    # Just preview the data
                    flash('Job details extracted successfully!', 'success')
                    return render_template('admin/scrape_job.html', job=job_data, preview=True)
            else:
                flash(f'Error: {result.get("error", "Unknown error")}', 'error')
        except Exception as e:
            app.logger.error(f"Error scraping job: {e}")
            flash(f'Error extracting job details: {str(e)}', 'error')
    
    return render_template('admin/scrape_job.html')

@app.route('/text-extractor')
def text_extractor():
    """Page for extracting text from websites"""
    return render_template('text_extractor.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

# Add jinja2 template filters
app.jinja_env.globals.update(format_date=format_date)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)