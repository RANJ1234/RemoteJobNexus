from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import os
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Sample data for jobs - replace with database in production
JOBS = [
    {
        "id": 1,
        "title": "Remote Software Engineer",
        "company": "TechCorp",
        "location": "Remote (Worldwide)",
        "category": "white-collar",
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
        "category": "grey-collar",
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
        "category": "blue-collar",
        "job_type": "Contract",
        "salary": "$35 - $45 per hour",
        "description": "Coordinate with our team of field technicians to optimize service delivery.",
        "requirements": "Experience in HVAC and team coordination.",
        "application_url": "https://example.com/apply",
        "posted_date": datetime.datetime(2025, 3, 15),
        "is_active": True,
        "views": 78
    }
]

# Admin credentials - change in production
ADMIN_USER = "admin"
ADMIN_PASSWORD = generate_password_hash("remotework_admin2025")

def format_date(date):
    """Format date for display"""
    if isinstance(date, datetime.datetime):
        return date.strftime("%B %d, %Y")
    return date

@app.route('/')
def index():
    """Homepage with featured jobs"""
    featured_jobs = JOBS[:3]  # Display top 3 jobs on homepage
    return render_template('index.html', jobs=featured_jobs)

@app.route('/jobs')
def jobs():
    """Job listings page"""
    return render_template('jobs.html', jobs=JOBS)

@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    job = next((j for j in JOBS if j['id'] == job_id), None)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs'))
    
    # Increment view count
    job['views'] += 1
    return render_template('job_detail.html', job=job)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    """Job submission form"""
    if request.method == 'POST':
        # In a real app, validate and save to database
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    return render_template('post_job.html')

@app.route('/api/extract-job', methods=['POST'])
def extract_job():
    """Extract job details from URL (API endpoint)"""
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    # Placeholder for job extraction logic
    # In a real app, use web scraping to extract job details
    job_details = {
        "title": "Extracted Job Title",
        "company": "Company Name",
        "location": "Remote",
        "description": "Job description would be extracted from the provided URL."
    }
    
    return jsonify({"success": True, "job": job_details})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and check_password_hash(ADMIN_PASSWORD, password):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    stats = {
        'total_jobs': len(JOBS),
        'active_jobs': sum(1 for job in JOBS if job['is_active']),
        'total_views': sum(job['views'] for job in JOBS)
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/jobs')
def admin_jobs():
    """Admin job management"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/jobs.html', jobs=JOBS)

@app.route('/admin/jobs/delete/<int:job_id>')
def admin_delete_job(job_id):
    """Delete a job"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    global JOBS
    JOBS = [job for job in JOBS if job['id'] != job_id]
    flash('Job deleted successfully', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/export')
def admin_export_jobs():
    """Export jobs as JSON"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    # Convert datetime objects to strings for JSON serialization
    export_jobs = []
    for job in JOBS:
        job_copy = job.copy()
        job_copy['posted_date'] = format_date(job_copy['posted_date'])
        export_jobs.append(job_copy)
    
    return jsonify(export_jobs)

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