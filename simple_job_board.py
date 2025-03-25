import os
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("SESSION_SECRET") or "remotework_secret_key_2025"

# Simplified in-memory storage
jobs = []
admin_user = {
    "username": "admin",
    "password": "remotework_admin2025"
}

# Initialize with some sample data
def initialize_data():
    if not jobs:
        jobs.append({
            "id": 1,
            "title": "Remote Software Developer",
            "company": "Tech Innovations",
            "location": "Remote, Worldwide",
            "category": "white-collar",
            "job_type": "Full-time",
            "salary": "$70,000 - $120,000",
            "description": "We're looking for an experienced software developer to join our remote team. You will work on cutting-edge technologies and contribute to various projects.",
            "requirements": "5+ years of experience in software development. Proficiency in JavaScript, Python, and cloud technologies. Good communication skills.",
            "application_url": "https://example.com/apply",
            "posted_date": datetime.datetime.now() - datetime.timedelta(days=5),
            "is_active": True,
            "views": 42
        })
        
        jobs.append({
            "id": 2,
            "title": "Remote HVAC Technician Consultant",
            "company": "Climate Solutions",
            "location": "Remote, US-based",
            "category": "blue-collar",
            "job_type": "Contract",
            "salary": "$45 - $60 per hour",
            "description": "Provide remote consultation and troubleshooting for HVAC systems. You will guide on-site technicians through complex repairs via video calls.",
            "requirements": "5+ years as an HVAC technician. Certification required. Excellent communication skills.",
            "application_url": "https://example.com/apply-hvac",
            "posted_date": datetime.datetime.now() - datetime.timedelta(days=2),
            "is_active": True,
            "views": 18
        })
        
        jobs.append({
            "id": 3,
            "title": "Remote Healthcare Data Analyst",
            "company": "MediData Inc.",
            "location": "Remote, US",
            "category": "grey-collar",
            "job_type": "Full-time",
            "salary": "$60,000 - $85,000",
            "description": "Analyze healthcare data to improve patient outcomes and operational efficiency. Work with healthcare providers to implement data-driven solutions.",
            "requirements": "Experience in healthcare and data analysis. Knowledge of HIPAA compliance. Proficiency in Excel, SQL, and data visualization tools.",
            "application_url": "https://example.com/apply-analyst",
            "posted_date": datetime.datetime.now() - datetime.timedelta(days=7),
            "is_active": True,
            "views": 36
        })
        
        logger.info(f"Initialized with {len(jobs)} sample jobs")

# Context processor to make functions available in templates
@app.context_processor
def utility_processor():
    def format_date(date):
        return date.strftime('%B %d, %Y') if date else ''
    
    now = datetime.datetime.now()
    
    return dict(format_date=format_date, now=now)

# Homepage route
@app.route('/')
def index():
    # Get featured jobs (most recent active jobs)
    featured_jobs = [job for job in jobs if job["is_active"]]
    featured_jobs.sort(key=lambda x: x["posted_date"], reverse=True)
    featured_jobs = featured_jobs[:6]  # Limit to 6 featured jobs
    
    return render_template('index.html', featured_jobs=featured_jobs)

# Jobs listing page
@app.route('/jobs')
def jobs_list():
    # Get filter parameters
    category = request.args.get('category', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    # Filter jobs
    filtered_jobs = [job for job in jobs if job["is_active"]]
    
    if category:
        filtered_jobs = [job for job in filtered_jobs if job["category"] == category]
    
    if job_type:
        filtered_jobs = [job for job in filtered_jobs if job["job_type"] == job_type]
    
    if location:
        location = location.lower()
        filtered_jobs = [job for job in filtered_jobs if location in job["location"].lower()]
    
    # Sort by date (newest first)
    filtered_jobs.sort(key=lambda x: x["posted_date"], reverse=True)
    
    return render_template('jobs.html', jobs=filtered_jobs, 
                          category=category, job_type=job_type, location=location)

# Job detail page
@app.route('/job/<int:job_id>')
def job_detail(job_id):
    # Find job by ID
    job = next((job for job in jobs if job["id"] == job_id), None)
    
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('jobs_list'))
    
    # Increment view count
    job["views"] += 1
    
    # Get similar jobs (same category)
    similar_jobs = [j for j in jobs if j["category"] == job["category"] and j["id"] != job["id"] and j["is_active"]]
    similar_jobs = similar_jobs[:3]  # Limit to 3 similar jobs
    
    return render_template('job_detail.html', job=job, similar_jobs=similar_jobs)

# Post a new job
@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        # Get next ID
        new_id = max([job["id"] for job in jobs], default=0) + 1
        
        # Create new job from form data
        new_job = {
            "id": new_id,
            "title": request.form.get('title'),
            "company": request.form.get('company'),
            "location": request.form.get('location'),
            "category": request.form.get('category'),
            "job_type": request.form.get('job_type'),
            "salary": request.form.get('salary'),
            "description": request.form.get('description'),
            "requirements": request.form.get('requirements'),
            "application_url": request.form.get('application_url'),
            "contact_email": request.form.get('contact_email'),
            "posted_date": datetime.datetime.now(),
            "is_active": True,
            "views": 0
        }
        
        jobs.append(new_job)
        flash('Job posted successfully!', 'success')
        return redirect(url_for('job_detail', job_id=new_id))
    
    return render_template('post_job.html')

# Simple job extraction from URL (placeholder for now)
@app.route('/extract-job', methods=['POST'])
def extract_job():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Placeholder response - would normally use web scraping
    sample_data = {
        'title': 'Software Developer',
        'company': 'Example Tech',
        'location': 'Remote, Worldwide',
        'description': 'This is a sample job description extracted from the URL. In a real application, this would contain actual content from the provided job posting URL.',
        'job_type': 'Full-time'
    }
    
    return jsonify(sample_data)

# ------- Admin Routes -------

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == admin_user["username"] and password == admin_user["password"]:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('admin/login.html')

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'danger')
        return redirect(url_for('admin_login'))
    
    # Basic stats
    job_count = len(jobs)
    active_jobs = len([job for job in jobs if job["is_active"]])
    user_count = 1  # Just the admin user in this simple version
    
    return render_template('admin/dashboard.html', 
                          job_count=job_count, 
                          active_jobs=active_jobs,
                          user_count=user_count)

# Admin job management
@app.route('/admin/jobs')
def admin_jobs():
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'danger')
        return redirect(url_for('admin_login'))
    
    # Sort by date (newest first)
    all_jobs = sorted(jobs, key=lambda x: x["posted_date"], reverse=True)
    
    return render_template('admin/jobs.html', jobs=all_jobs)

# Admin job deletion
@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'danger')
        return redirect(url_for('admin_login'))
    
    # Find job by ID
    job_index = next((i for i, job in enumerate(jobs) if job["id"] == job_id), None)
    
    if job_index is not None:
        del jobs[job_index]
        flash('Job deleted successfully', 'success')
    else:
        flash('Job not found', 'danger')
    
    return redirect(url_for('admin_jobs'))

# Export jobs as JSON
@app.route('/admin/export-jobs')
def admin_export_jobs():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Convert datetime objects to strings for JSON serialization
    exportable_jobs = []
    for job in jobs:
        job_copy = job.copy()
        job_copy["posted_date"] = job_copy["posted_date"].strftime('%Y-%m-%d')
        exportable_jobs.append(job_copy)
    
    return jsonify(exportable_jobs)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Initialize data on startup
initialize_data()

# Main app entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)