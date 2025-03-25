import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# Initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "remote_work_dev_key")

# Database configuration
DB_PATH = "jobs.db"

# Helper functions for database
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        job_type TEXT,
        category TEXT,
        salary TEXT,
        description TEXT NOT NULL,
        requirements TEXT,
        contact_email TEXT,
        application_url TEXT,
        posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        views INTEGER DEFAULT 0,
        source_url TEXT
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Add admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    if not admin:
        cursor.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            ("admin", "remotework_admin2025", "admin@remotework.com", "admin")
        )
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def index():
    """Homepage with featured jobs"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM jobs WHERE is_active = 1 ORDER BY posted_date DESC LIMIT 10"
    )
    featured_jobs = cursor.fetchall()
    conn.close()
    return render_template('index.html', featured_jobs=featured_jobs)

@app.route('/jobs')
def jobs():
    """Job listings page"""
    category = request.args.get('category', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE is_active = 1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if job_type:
        query += " AND job_type = ?"
        params.append(job_type)
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    
    query += " ORDER BY posted_date DESC"
    
    cursor.execute(query, params)
    all_jobs = cursor.fetchall()
    conn.close()
    
    return render_template('jobs.html', jobs=all_jobs, category=category, job_type=job_type, location=location)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Increment view count
    cursor.execute("UPDATE jobs SET views = views + 1 WHERE id = ?", (job_id,))
    conn.commit()
    
    # Get job details
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if job is None:
        flash('Job not found', 'error')
        return redirect(url_for('jobs'))
    
    return render_template('job_detail.html', job=job)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    """Job submission form"""
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        job_type = request.form.get('job_type')
        category = request.form.get('category')
        salary = request.form.get('salary')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        contact_email = request.form.get('contact_email')
        application_url = request.form.get('application_url')
        source_url = request.form.get('source_url', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs 
            (title, company, location, job_type, category, salary, description, 
             requirements, contact_email, application_url, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, company, location, job_type, category, salary, description,
             requirements, contact_email, application_url, source_url)
        )
        conn.commit()
        conn.close()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    
    return render_template('post_job.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user['password'] == password:  # Simple password check
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('logged_in') or session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    job_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE is_active = 1")
    active_jobs = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    conn.close()
    
    return render_template('admin/dashboard.html', 
                          job_count=job_count, 
                          active_jobs=active_jobs, 
                          user_count=user_count)

@app.route('/admin/jobs')
def admin_jobs():
    """Admin job management"""
    if not session.get('logged_in') or session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY posted_date DESC")
    all_jobs = cursor.fetchall()
    conn.close()
    
    return render_template('admin/jobs.html', jobs=all_jobs)

@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    """Delete a job"""
    if not session.get('logged_in') or session.get('role') != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    
    flash('Job deleted successfully', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/export-jobs')
def admin_export_jobs():
    """Export jobs as JSON"""
    if not session.get('logged_in') or session.get('role') != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    job_list = []
    for job in jobs:
        job_dict = {key: job[key] for key in job.keys()}
        job_list.append(job_dict)
    
    return jsonify(job_list)

@app.route('/extract-job', methods=['POST'])
def extract_job():
    """Extract job details from URL (API endpoint)"""
    url = request.form.get('url', '')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    # Simple job extraction (placeholder)
    # In a real app, you would use BeautifulSoup or similar
    job_details = {
        'title': 'Job extracted from ' + url,
        'company': 'Company',
        'location': 'Remote',
        'description': 'Job description would be extracted from the URL.'
    }
    
    return jsonify(job_details)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)