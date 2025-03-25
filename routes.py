import os
import json
from flask import render_template, request, redirect, url_for, flash, g, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from io import BytesIO
import pandas as pd
from functools import wraps
from datetime import datetime

# Import database models
from models import UserAccount, Job, BlogPost, SiteVisit, WebsiteContent, JobApplication
from db import db

# Import scraper for URL-based job extraction
from scraper import extract_job_details
from web_scraper import get_website_text_content

def register_routes(app):
    """Register all application routes with the Flask app"""
    
    # ==== Route Decorator Functions ====
    def admin_required(f):
        """Decorator to require admin role for a route"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin():
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function
        
    # ==== Utility Functions ====
    def track_page_visit(page):
        """Track a page visit for analytics"""
        visit = SiteVisit(
            page=page,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            referrer=request.referrer,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(visit)
        db.session.commit()
    
    # ==== Context Processors ====
    @app.context_processor
    def utility_processor():
        """Add utility functions to the template context"""
        def format_date(date):
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    return date
            return date.strftime('%B %d, %Y')
        
        return dict(format_date=format_date)
    
    # ==== Error Handlers ====
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        return render_template('500.html'), 500
    
    # ==== Public Routes ====
    @app.route('/')
    def index():
        """Homepage with featured jobs and search bar"""
        track_page_visit('home')
        
        # Get featured jobs
        featured_jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(6).all()
        
        return render_template(
            'index.html',
            featured_jobs=featured_jobs,
            content=g.content_store.get_section('homepage')
        )
        
    @app.route('/jobs')
    def jobs():
        """Job listings page with all available jobs"""
        track_page_visit('jobs')
        
        # Get search query
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        # Base query
        job_query = Job.query.filter_by(is_active=True)
        
        # Apply search filter if provided
        if query:
            search = f"%{query}%"
            job_query = job_query.filter(
                (Job.title.ilike(search)) | 
                (Job.description.ilike(search)) | 
                (Job.company.ilike(search)) | 
                (Job.location.ilike(search))
            )
            
        # Apply category filter if provided
        if category:
            job_query = job_query.filter(Job.category == category)
        
        # Get jobs
        all_jobs = job_query.order_by(Job.posted_date.desc()).all()
        
        return render_template(
            'jobs.html',
            jobs=all_jobs,
            query=query,
            category=category,
            categories=g.content_store.get_section('categories')
        )
        
    @app.route('/jobs/<int:job_id>')
    def job_detail(job_id):
        """Job detail page with full information"""
        track_page_visit(f'job/{job_id}')
        
        # Get job by ID
        job = Job.query.get_or_404(job_id)
        
        # Increment view counter
        job.views += 1
        db.session.commit()
        
        return render_template('job_detail.html', job=job)
        
    @app.route('/post-job', methods=['GET', 'POST'])
    def post_job():
        """Job submission form for employers"""
        track_page_visit('post-job')
        
        if request.method == 'POST':
            # Extract form data
            job_data = {
                'title': request.form.get('title'),
                'company': request.form.get('company'),
                'location': request.form.get('location'),
                'salary': request.form.get('salary'),
                'job_type': request.form.get('job_type'),
                'category': request.form.get('category'),
                'description': request.form.get('description'),
                'requirements': request.form.get('requirements'),
                'contact_email': request.form.get('contact_email'),
                'application_url': request.form.get('application_url'),
                'is_active': True,
                'user_id': current_user.id if current_user.is_authenticated else None
            }
            
            # Create new job
            job = Job(**job_data)
            db.session.add(job)
            db.session.commit()
            
            flash('Job posted successfully!', 'success')
            return redirect(url_for('job_detail', job_id=job.id))
            
        return render_template('post_job.html')
        
    @app.route('/api/extract-job', methods=['POST'])
    def api_extract_job():
        """API endpoint for URL-based job detail extraction"""
        url = request.json.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
            
        # Extract job details
        job_data = extract_job_details(url)
        
        if not job_data:
            return jsonify({'error': 'Failed to extract job details'}), 400
            
        return jsonify(job_data)
        
    @app.route('/blog')
    def blog():
        """Blog listing page"""
        track_page_visit('blog')
        
        # Get all published blog posts
        posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
        
        return render_template('blog.html', posts=posts)
        
    @app.route('/blog/<int:post_id>')
    def blog_post(post_id):
        """Single blog post page"""
        track_page_visit(f'blog/{post_id}')
        
        # Get post by ID
        post = BlogPost.query.get_or_404(post_id)
        
        # Increment view counter
        post.views += 1
        db.session.commit()
        
        return render_template('blog_post.html', post=post)
        
    @app.route('/text-extractor', methods=['GET', 'POST'])
    def text_extractor():
        """Page for extracting text content from any website"""
        track_page_visit('text-extractor')
        
        extracted_text = None
        url = None
        
        if request.method == 'POST':
            url = request.form.get('url')
            if url:
                extracted_text = get_website_text_content(url)
                
        return render_template('text_extractor.html', extracted_text=extracted_text, url=url)
        
    # ==== Admin Routes ====
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Login page for both admin and employees"""
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
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
                
        return render_template('admin/login.html')
        
    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        """Logout route"""
        logout_user()
        flash('You have been logged out', 'success')
        return redirect(url_for('admin_login'))
        
    @app.route('/admin/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
        """Admin dashboard page"""
        track_page_visit('admin/dashboard')
        
        # Get analytics data
        total_jobs = Job.query.count()
        active_jobs = Job.query.filter_by(is_active=True).count()
        total_users = UserAccount.query.count()
        
        # Get site visits by page
        page_visits = db.session.query(
            SiteVisit.page, 
            db.func.count(SiteVisit.id).label('count')
        ).group_by(SiteVisit.page).order_by(db.desc('count')).limit(5).all()
        
        # Get visits by date
        date_visits = db.session.query(
            db.func.date(SiteVisit.visit_date).label('date'),
            db.func.count(SiteVisit.id).label('count')
        ).group_by('date').order_by(db.desc('date')).limit(7).all()
        
        # Get job categories
        job_categories = db.session.query(
            Job.category,
            db.func.count(Job.id).label('count')
        ).group_by(Job.category).all()
        
        return render_template(
            'admin/dashboard.html',
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            total_users=total_users,
            page_visits=page_visits,
            date_visits=date_visits,
            job_categories=job_categories
        )
        
    @app.route('/admin/content', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_content():
        """Content management page"""
        track_page_visit('admin/content')
        
        return render_template('admin/content.html', content=g.content_store.content)
        
    @app.route('/admin/content/update', methods=['POST'])
    @login_required
    @admin_required
    def admin_update_content():
        """Update website content"""
        section = request.form.get('section')
        content_data = request.form.get('content')
        
        try:
            # Parse content data as JSON
            content_data = json.loads(content_data)
            
            # Update content
            g.content_store.update_section(section, content_data)
            
            flash('Content updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating content: {str(e)}', 'danger')
            
        return redirect(url_for('admin_content'))
        
    @app.route('/admin/carousel')
    @login_required
    @admin_required
    def admin_carousel():
        """Carousel management page"""
        track_page_visit('admin/carousel')
        
        return render_template('admin/carousel.html', carousel=g.content_store.get_section('carousel'))
        
    @app.route('/admin/carousel/add', methods=['POST'])
    @login_required
    @admin_required
    def admin_add_carousel():
        """Add a carousel item"""
        item_data = {
            'title': request.form.get('title'),
            'subtitle': request.form.get('subtitle'),
            'image_url': request.form.get('image_url'),
            'cta_text': request.form.get('cta_text'),
            'cta_url': request.form.get('cta_url')
        }
        
        g.content_store.add_carousel_item(item_data)
        flash('Carousel item added successfully', 'success')
        
        return redirect(url_for('admin_carousel'))
        
    @app.route('/admin/carousel/update/<int:index>', methods=['POST'])
    @login_required
    @admin_required
    def admin_update_carousel(index):
        """Update a carousel item"""
        item_data = {
            'title': request.form.get('title'),
            'subtitle': request.form.get('subtitle'),
            'image_url': request.form.get('image_url'),
            'cta_text': request.form.get('cta_text'),
            'cta_url': request.form.get('cta_url')
        }
        
        result = g.content_store.update_carousel_item(index, item_data)
        
        if result:
            flash('Carousel item updated successfully', 'success')
        else:
            flash('Error updating carousel item', 'danger')
            
        return redirect(url_for('admin_carousel'))
        
    @app.route('/admin/carousel/delete/<int:index>')
    @login_required
    @admin_required
    def admin_delete_carousel(index):
        """Delete a carousel item"""
        result = g.content_store.remove_carousel_item(index)
        
        if result:
            flash('Carousel item deleted successfully', 'success')
        else:
            flash('Error deleting carousel item', 'danger')
            
        return redirect(url_for('admin_carousel'))
        
    @app.route('/admin/jobs')
    @login_required
    @admin_required
    def admin_jobs():
        """Job management page"""
        track_page_visit('admin/jobs')
        
        # Get all jobs
        all_jobs = Job.query.order_by(Job.posted_date.desc()).all()
        
        return render_template('admin/jobs.html', jobs=all_jobs)
        
    @app.route('/admin/jobs/delete/<int:job_id>')
    @login_required
    @admin_required
    def admin_delete_job(job_id):
        """Delete a job"""
        job = Job.query.get_or_404(job_id)
        
        db.session.delete(job)
        db.session.commit()
        
        flash('Job deleted successfully', 'success')
        return redirect(url_for('admin_jobs'))
        
    @app.route('/admin/jobs/export')
    @login_required
    @admin_required
    def admin_export_jobs():
        """Export jobs to Excel"""
        # Get query parameters
        format_type = request.args.get('format', 'excel')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        # Base query
        query = Job.query
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Job.posted_date >= start_date)
        if end_date:
            query = query.filter(Job.posted_date <= end_date)
            
        # Get jobs
        jobs = query.order_by(Job.posted_date.desc()).all()
        
        # Create DataFrame
        data = []
        for job in jobs:
            data.append({
                'ID': job.id,
                'Title': job.title,
                'Company': job.company,
                'Location': job.location,
                'Category': job.category,
                'Type': job.job_type,
                'Salary': job.salary,
                'Posted Date': job.posted_date.strftime('%Y-%m-%d'),
                'Active': 'Yes' if job.is_active else 'No',
                'Views': job.views
            })
            
        df = pd.DataFrame(data)
        
        # Create output file
        output = BytesIO()
        
        if format_type == 'excel':
            # Export to Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Jobs')
                
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='jobs_export.xlsx'
            )
        else:
            # Export to CSV
            df.to_csv(output, index=False)
            
            output.seek(0)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name='jobs_export.csv'
            )
            
    @app.route('/admin/scrape-job', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_scrape_job():
        """Admin page for scraping jobs from URLs"""
        track_page_visit('admin/scrape-job')
        
        if request.method == 'POST':
            url = request.form.get('url')
            
            if url:
                # Extract job details
                job_data = extract_job_details(url)
                
                if job_data:
                    # Add source URL
                    job_data['source_url'] = url
                    
                    # Create new job
                    job = Job(**job_data)
                    db.session.add(job)
                    db.session.commit()
                    
                    flash('Job scraped and added successfully', 'success')
                    return redirect(url_for('job_detail', job_id=job.id))
                else:
                    flash('Failed to extract job details from the provided URL', 'danger')
            else:
                flash('Please provide a URL', 'danger')
                
        return render_template('admin/scrape_job.html')
        
    @app.route('/admin/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_users():
        """User management page"""
        track_page_visit('admin/users')
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            # Check if username or email already exists
            existing_user = UserAccount.query.filter(
                (UserAccount.username == username) | (UserAccount.email == email)
            ).first()
            
            if existing_user:
                flash('Username or email already exists', 'danger')
            else:
                # Create new user
                new_user = UserAccount(
                    username=username,
                    email=email,
                    role=role,
                    is_active=True
                )
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                
                flash('User added successfully', 'success')
                
        # Get all users
        users = UserAccount.query.all()
        
        return render_template('admin/users.html', users=users)
        
    @app.route('/admin/users/delete/<username>')
    @login_required
    @admin_required
    def admin_delete_user(username):
        """Delete a user"""
        if username == 'admin':
            flash('Cannot delete admin user', 'danger')
            return redirect(url_for('admin_users'))
            
        user = UserAccount.query.filter_by(username=username).first_or_404()
        
        db.session.delete(user)
        db.session.commit()
        
        flash('User deleted successfully', 'success')
        return redirect(url_for('admin_users'))
        
    @app.route('/admin/change-password', methods=['POST'])
    @login_required
    def admin_change_password():
        """Change password route"""
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        if current_user.check_password(current_password):
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('Password changed successfully', 'success')
        else:
            flash('Current password is incorrect', 'danger')
            
        return redirect(url_for('admin_dashboard'))
        
    @app.route('/admin/forgot-password', methods=['GET', 'POST'])
    def admin_forgot_password():
        """Forgot password page"""
        if request.method == 'POST':
            email = request.form.get('email')
            
            user = UserAccount.query.filter_by(email=email).first()
            
            if user:
                # Generate reset token
                token = user.generate_reset_token()
                
                # In a real app, send an email with the reset link
                # For demo, just show the token
                reset_url = url_for('admin_reset_password', token=token, _external=True)
                
                flash(f'Password reset link: {reset_url}', 'info')
            else:
                # Don't reveal if email exists
                flash('If your email is in our system, you will receive a reset link', 'info')
                
        return render_template('admin/forgot_password.html')
        
    @app.route('/admin/reset-password', methods=['GET', 'POST'])
    def admin_reset_password():
        """Reset password page"""
        token = request.args.get('token') or request.form.get('token')
        
        if not token:
            flash('Invalid reset token', 'danger')
            return redirect(url_for('admin_login'))
            
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            
            # Find user with this token
            user = UserAccount.query.filter_by(reset_token=token).first()
            
            if user and user.reset_token_expiry > datetime.now():
                user.set_password(new_password)
                user.reset_token = None
                user.reset_token_expiry = None
                db.session.commit()
                
                flash('Password reset successfully. You can now log in with your new password.', 'success')
                return redirect(url_for('admin_login'))
            else:
                flash('Invalid or expired reset token', 'danger')
                
        return render_template('admin/reset_password.html', token=token)
    
    # Return the Flask app
    return app