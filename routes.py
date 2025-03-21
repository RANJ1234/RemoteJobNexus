from flask import render_template, request, redirect, url_for, flash, jsonify
import datetime
import logging
from app import app, job_store
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
