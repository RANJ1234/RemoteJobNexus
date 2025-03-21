from flask import render_template, request, redirect, url_for, flash, jsonify, session, Response
import datetime
import logging
import csv
import io
import json
from functools import wraps
from app import app, job_store, content_store, user_store
from functools import wraps
from scraper import extract_job_details, is_valid_url, fallback_extraction

@app.route('/')
def index():
    """Homepage with featured jobs and search bar."""
    # Get the most recent 3 jobs for the featured section
    featured_jobs = job_store.get_all_jobs()[:3]
    return render_template('index.html', featured_jobs=featured_jobs)

@app.route('/jobs')
def jobs():
    """Job listings page with all available jobs."""
    search_query = request.args.get('q', '')
    if search_query:
        jobs_list = job_store.search_jobs(search_query)
    else:
        jobs_list = job_store.get_all_jobs()
    
    return render_template('jobs.html', jobs=jobs_list, search_query=search_query)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'admin' not in user_store.get_user_roles(session['username']):
            flash('Admin access required', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_users():
    return render_template('admin/users.html', users=user_store.users)

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    roles = request.form.getlist('roles')
    
    if user_store.add_user(username, password, roles):
        flash('User added successfully', 'success')
    else:
        flash('Username already exists', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<username>')
@admin_required
def admin_delete_user(username):
    if user_store.delete_user(username):
        flash('User deleted successfully', 'success')
    else:
        flash('Cannot delete user', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/change-password', methods=['POST'])
def admin_change_password():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin_login'))
        
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    if user_store.verify_password(session['username'], current_password):
        if user_store.change_password(session['username'], new_password):
            flash('Password changed successfully', 'success')
        else:
            flash('Failed to change password', 'error')
    else:
        flash('Current password is incorrect', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        token = user_store.generate_reset_token(username)
        if token:
            # In production, send this via email
            flash(f'Reset token: {token}', 'success')
        else:
            flash('User not found', 'error')
        return redirect(url_for('admin_login'))
    return render_template('admin/forgot_password.html')

@app.route('/admin/reset-password', methods=['GET', 'POST'])
def admin_reset_password():
    if request.method == 'POST':
        token = request.form.get('token')
        new_password = request.form.get('new_password')
        if user_store.reset_password_with_token(token, new_password):
            flash('Password reset successfully', 'success')
            return redirect(url_for('admin_login'))
        flash('Invalid or expired token', 'error')
    return render_template('admin/reset_password.html')

def jobs():
    """Job listings page with all available jobs."""
    search_query = request.args.get('q', '')
    if search_query:
        jobs_list = job_store.search_jobs(search_query)
    else:
        jobs_list = job_store.get_all_jobs()
    
    return render_template('jobs.html', jobs=jobs_list, search_query=search_query)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job detail page with full information."""
    job = job_store.get_job(job_id)
    if not job:
        flash("Job not found", "error")
        return redirect(url_for('jobs'))
    
    return render_template('job_detail.html', job=job)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    """Job submission form for employers."""
    if request.method == 'POST':
        # Handle manual job posting
        job_data = {
            'title': request.form.get('title', ''),
            'company': request.form.get('company', ''),
            'location': request.form.get('location', 'Remote'),
            'description': request.form.get('description', ''),
            'requirements': request.form.get('requirements', ''),
            'salary_range': request.form.get('salary_range', ''),
            'application_url': request.form.get('application_url', ''),
            'contact_email': request.form.get('contact_email', ''),
            'job_type': request.form.get('job_type', 'Full-time'),
            'job_category': request.form.get('job_category', 'White-collar'),
            'source_url': request.form.get('source_url', '')
        }
        
        # Validate required fields
        if not job_data['title'] or not job_data['company'] or not job_data['description']:
            flash("Please fill in all required fields", "error")
            return render_template('post_job.html', job_data=job_data)
        
        # Add job to the store
        job_id = job_store.add_job(job_data)
        flash("Job posted successfully!", "success")
        return redirect(url_for('job_detail', job_id=job_id))
    
    # Prefill from URL parameter if provided
    prefill_url = request.args.get('url', '')
    job_data = {}
    
    if prefill_url:
        if is_valid_url(prefill_url):
            try:
                job_data = extract_job_details(prefill_url)
                if "error" in job_data:
                    # Try fallback extraction method
                    job_data = fallback_extraction(prefill_url)
                    flash("Limited job details extracted. Please complete the missing information.", "warning")
            except Exception as e:
                logging.error(f"Error during job extraction: {str(e)}")
                flash(f"Could not extract job details: {str(e)}", "error")
                job_data = {}
        else:
            flash("Invalid URL provided", "error")
    
    return render_template('post_job.html', job_data=job_data)

@app.route('/api/extract-job', methods=['POST'])
def api_extract_job():
    """API endpoint for URL-based job detail extraction."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400
    
    url = data['url']
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL format"}), 400
    
    try:
        job_data = extract_job_details(url)
        if "error" in job_data:
            # Try fallback extraction
            job_data = fallback_extraction(url)
            job_data["_extraction_note"] = "Limited details extracted. Please verify and complete."
        
        return jsonify(job_data)
    except Exception as e:
        logging.error(f"Error during API job extraction: {str(e)}")
        return jsonify({"error": f"Could not extract job details: {str(e)}"}), 500

@app.context_processor
def utility_processor():
    """Add utility functions to the template context."""
    def format_date(date):
        if isinstance(date, datetime.datetime):
            return date.strftime("%B %d, %Y")
        return date
    
    return dict(format_date=format_date)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('base.html', error_message="Internal server error"), 500

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_authenticated' not in session or not session['admin_authenticated']:
            flash('Please log in to access the admin panel', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login page for both admin and employees"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if user_store.verify_password(username, password):
            session['username'] = username
            if 'admin' in user_store.get_user_roles(username):
                flash('Successfully logged in to admin panel', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Successfully logged in', 'success')
                return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout route"""
    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard page"""
    jobs_count = len(job_store.get_all_jobs())
    # Record last login time
    session['admin_last_login'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('admin/dashboard.html', jobs_count=jobs_count, now=datetime.datetime.now())

@app.route('/admin/content')
@admin_required
def admin_content():
    """Content management page"""
    return render_template('admin/content.html', content=content_store.content)

@app.route('/admin/content/update', methods=['POST'])
@admin_required
def admin_update_content():
    """Update website content"""
    section = request.form.get('section')
    if not section:
        flash('No section specified', 'error')
        return redirect(url_for('admin_content'))
    
    # Process form data for this section
    content_data = {}
    for key, value in request.form.items():
        if key.startswith(f"{section}_"):
            field_name = key.replace(f"{section}_", "")
            content_data[field_name] = value
    
    # Update content
    if content_store.update_section(section, content_data):
        flash(f'Content updated successfully for {section}', 'success')
    else:
        flash(f'Failed to update content for {section}', 'error')
    
    return redirect(url_for('admin_content'))

@app.route('/admin/carousel')
@admin_required
def admin_carousel():
    """Carousel management page"""
    return render_template('admin/carousel.html', carousel=content_store.get_section('carousel'))

@app.route('/admin/carousel/add', methods=['POST'])
@admin_required
def admin_add_carousel():
    """Add a carousel item"""
    item_data = {
        'image_url': request.form.get('image_url', ''),
        'title': request.form.get('title', ''),
        'description': request.form.get('description', '')
    }
    
    if content_store.add_carousel_item(item_data):
        flash('Carousel item added successfully', 'success')
    else:
        flash('Failed to add carousel item', 'error')
    
    return redirect(url_for('admin_carousel'))

@app.route('/admin/carousel/update/<int:index>', methods=['POST'])
@admin_required
def admin_update_carousel(index):
    """Update a carousel item"""
    item_data = {
        'image_url': request.form.get('image_url', ''),
        'title': request.form.get('title', ''),
        'description': request.form.get('description', '')
    }
    
    if content_store.update_carousel_item(index, item_data):
        flash('Carousel item updated successfully', 'success')
    else:
        flash('Failed to update carousel item', 'error')
    
    return redirect(url_for('admin_carousel'))

@app.route('/admin/carousel/delete/<int:index>')
@admin_required
def admin_delete_carousel(index):
    """Delete a carousel item"""
    if content_store.remove_carousel_item(index):
        flash('Carousel item deleted successfully', 'success')
    else:
        flash('Failed to delete carousel item', 'error')
    
    return redirect(url_for('admin_carousel'))

@app.route('/admin/jobs')
@admin_required
def admin_jobs():
    """Job management page"""
    jobs_list = job_store.get_all_jobs()
    return render_template('admin/jobs.html', jobs=jobs_list)
    
@app.route('/admin/jobs/delete/<int:job_id>')
@admin_required
def admin_delete_job(job_id):
    """Delete a job"""
    job = job_store.get_job(job_id)
    if job:
        # Remove the job from the job store
        job_store.jobs = [j for j in job_store.jobs if j['id'] != job_id]
        flash(f'Job "{job["title"]}" deleted successfully', 'success')
    else:
        flash('Job not found', 'error')
    
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/export', methods=['POST'])
@admin_required
def admin_export_jobs():
    """Export jobs to CSV or JSON"""
    export_format = request.form.get('format', 'csv')
    jobs_list = job_store.get_all_jobs()
    
    if export_format == 'csv':
        output = io.StringIO()
        fieldnames = ['id', 'title', 'company', 'location', 'description', 'requirements',
                    'salary_range', 'job_type', 'job_category', 'date_posted', 'application_url']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for job in jobs_list:
            # Convert datetime to string
            job_copy = job.copy()
            if isinstance(job_copy.get('date_posted'), datetime.datetime):
                job_copy['date_posted'] = job_copy['date_posted'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Write only the fields we care about
            writer.writerow({field: job_copy.get(field, '') for field in fieldnames})
        
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=jobs_export.csv'
        return response
    
    elif export_format == 'json':
        # Convert datetime objects to strings for JSON serialization
        jobs_json = []
        for job in jobs_list:
            job_copy = job.copy()
            if isinstance(job_copy.get('date_posted'), datetime.datetime):
                job_copy['date_posted'] = job_copy['date_posted'].strftime('%Y-%m-%d %H:%M:%S')
            jobs_json.append(job_copy)
        
        response = Response(json.dumps(jobs_json, indent=2), mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=jobs_export.json'
        return response
    
    else:
        flash('Unsupported export format', 'error')
        return redirect(url_for('admin_jobs'))

@app.route('/admin/scrape-job', methods=['GET', 'POST'])
@admin_required
def admin_scrape_job():
    """Admin page for scraping jobs from URLs"""
    if request.method == 'POST':
        url = request.form.get('url', '')
        if not url or not is_valid_url(url):
            flash('Please enter a valid URL', 'error')
            return render_template('admin/scrape_job.html')
            
        try:
            job_data = extract_job_details(url)
            if "error" in job_data:
                # Try fallback extraction method
                job_data = fallback_extraction(url)
                
            # Add the job directly
            job_id = job_store.add_job(job_data)
            flash(f'Job successfully scraped and added (ID: {job_id})', 'success')
            return redirect(url_for('admin_jobs'))
            
        except Exception as e:
            logging.error(f"Error during job scraping: {str(e)}")
            flash(f"Could not scrape job details: {str(e)}", "error")
            
    return render_template('admin/scrape_job.html')
