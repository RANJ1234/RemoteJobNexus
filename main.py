from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import os
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

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
    """Job listings page with filters"""
    # Get filter parameters
    category = request.args.get('category', '')
    subcategory = request.args.get('subcategory', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    # Filter jobs
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
                          location=location)

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

@app.route('/admin/scrape-job', methods=['GET', 'POST'])
def admin_scrape_job():
    """Admin page for scraping jobs from URLs"""
    if not session.get('admin_logged_in'):
        flash('Please log in first', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        url = request.form.get('job_url')
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
            job_details = extract_job_details(url)
            if job_details.get('success'):
                flash('Job details extracted successfully!', 'success')
                # Process the job data (in a real app, save to database)
                # For now, we're just redirecting back with a success message
            else:
                flash(f'Error: {job_details.get("error", "Unknown error")}', 'error')
        except Exception as e:
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