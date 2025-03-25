import os
import json
import logging
from datetime import datetime
from flask import Flask, g

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Content store for website content
class ContentStore:
    def __init__(self, db_session):
        self._content = {}  # Initialize with empty dict to avoid None errors
        self.db_session = db_session
        self._initialized = False
    
    @property
    def content(self):
        """Lazy-loaded content - only initialize when needed"""
        if not self._initialized:
            self._initialize_content()
        return self._content
    
    def _initialize_content(self):
        """Initialize the default content for the website"""
        from models import WebsiteContent
        
        # Check if content exists in database
        content_record = WebsiteContent.query.first()
        
        if content_record and content_record.content:
            # Load content from database
            self._content = json.loads(content_record.content)
        else:
            # Create default content
            self._content = {
                'site_info': {
                    'title': 'Remote Work',
                    'tagline': 'Find Remote Jobs Worldwide',
                    'description': 'The best place to find and post remote jobs across blue-collar, white-collar, and grey-collar industries.',
                    'footer_text': '© 2025 Remote Work. All rights reserved.'
                },
                'homepage': {
                    'hero_title': 'Remote Work for Everyone',
                    'hero_subtitle': 'Discover remote opportunities across blue, white, and grey-collar jobs worldwide',
                    'cta_button': 'Find Jobs',
                    'cta_url': '/jobs',
                    'section_titles': {
                        'featured': 'Featured Remote Jobs',
                        'categories': 'Job Categories',
                        'testimonials': 'Success Stories'
                    }
                },
                'categories': {
                    'white_collar': {
                        'title': 'White-Collar Jobs',
                        'description': 'Professional, managerial, and administrative remote positions',
                        'examples': 'Software Developers, Marketers, Accountants, HR Managers'
                    },
                    'blue_collar': {
                        'title': 'Blue-Collar Jobs',
                        'description': 'Technical, trade, and manual labor positions with remote components',
                        'examples': 'Remote Construction Managers, Virtual Electrician Consultants, Remote Safety Inspectors'
                    },
                    'grey_collar': {
                        'title': 'Grey-Collar Jobs',
                        'description': 'Hybrid positions combining technical and professional skills',
                        'examples': 'IT Technicians, Healthcare Technicians, Culinary Consultants'
                    }
                },
                'carousel': [
                    {
                        'title': 'Find Your Remote Dream Job',
                        'subtitle': 'Browse thousands of remote opportunities worldwide',
                        'image_url': '/static/images/slide1.jpg',
                        'cta_text': 'Start Searching',
                        'cta_url': '/jobs'
                    },
                    {
                        'title': 'Hire Remote Talent',
                        'subtitle': 'Post jobs and reach qualified remote candidates',
                        'image_url': '/static/images/slide2.jpg',
                        'cta_text': 'Post a Job',
                        'cta_url': '/post-job'
                    },
                    {
                        'title': 'Remote Work Resources',
                        'subtitle': 'Learn how to thrive in a remote work environment',
                        'image_url': '/static/images/slide3.jpg',
                        'cta_text': 'Read Our Blog',
                        'cta_url': '/blog'
                    }
                ]
            }
            
            # Save default content to database
            if not content_record:
                content_record = WebsiteContent(content=json.dumps(self._content))
                self.db_session.add(content_record)
            else:
                content_record.content = json.dumps(self._content)
                
            self.db_session.commit()
            
        self._initialized = True

    def get_section(self, section_name):
        """Get content for a specific section"""
        sections = section_name.split('.')
        result = self.content
        for section in sections:
            if section in result:
                result = result[section]
            else:
                return None
        return result
    
    def update_section(self, section_name, content_data):
        """Update content for a specific section"""
        from models import WebsiteContent
        
        sections = section_name.split('.')
        target = self.content
        
        # Navigate to the parent section
        for section in sections[:-1]:
            if section not in target:
                target[section] = {}
            target = target[section]
        
        # Update the final section
        target[sections[-1]] = content_data
        
        # Save changes to database
        content_record = WebsiteContent.query.first()
        if not content_record:
            content_record = WebsiteContent(content=json.dumps(self.content))
            self.db_session.add(content_record)
        else:
            content_record.content = json.dumps(self.content)
            
        self.db_session.commit()
        return True
    
    def add_carousel_item(self, item_data):
        """Add a new carousel item"""
        from models import WebsiteContent
        
        if 'carousel' not in self.content:
            self.content['carousel'] = []
        
        self.content['carousel'].append(item_data)
        
        # Save changes to database
        content_record = WebsiteContent.query.first()
        if content_record:
            content_record.content = json.dumps(self.content)
            self.db_session.commit()
            
        return len(self.content['carousel']) - 1  # Return the index of the new item
    
    def remove_carousel_item(self, index):
        """Remove a carousel item by index"""
        from models import WebsiteContent
        
        if 'carousel' in self.content and 0 <= index < len(self.content['carousel']):
            self.content['carousel'].pop(index)
            
            # Save changes to database
            content_record = WebsiteContent.query.first()
            if content_record:
                content_record.content = json.dumps(self.content)
                self.db_session.commit()
                
            return True
        return False
    
    def update_carousel_item(self, index, item_data):
        """Update a carousel item by index"""
        from models import WebsiteContent
        
        if 'carousel' in self.content and 0 <= index < len(self.content['carousel']):
            self.content['carousel'][index] = item_data
            
            # Save changes to database
            content_record = WebsiteContent.query.first()
            if content_record:
                content_record.content = json.dumps(self.content)
                self.db_session.commit()
                
            return True
        return False
    
    def add_post(self, title, content, author, tags=None):
        """Add a new blog post"""
        from models import BlogPost
        
        # Create new blog post in database
        new_post = BlogPost(
            title=title,
            content=content,
            author=author,
            tags=','.join(tags) if tags else ''
        )
        self.db_session.add(new_post)
        self.db_session.commit()
        
        return str(new_post.id)
    
    def get_post(self, post_id):
        """Get a specific blog post by ID"""
        from models import BlogPost
        
        post = BlogPost.query.get(post_id)
        if not post:
            return None
            
        return {
            'id': str(post.id),
            'title': post.title,
            'content': post.content,
            'author': post.author,
            'date': post.created_at.strftime('%Y-%m-%d'),
            'tags': post.tags.split(',') if post.tags else []
        }
    
    def get_all_posts(self):
        """Get all blog posts, sorted by date"""
        from models import BlogPost
        
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return [
            {
                'id': str(post.id),
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'date': post.created_at.strftime('%Y-%m-%d'),
                'tags': post.tags.split(',') if post.tags else []
            }
            for post in posts
        ]

# ====================================================
# Initialize database and app components
# ====================================================
def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure app
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['ADMIN_URL_PREFIX'] = '/admin'
    
    # Initialize database and login manager
    from db import db, init_app, login_manager
    init_app(app)
    
    # Create content store instance
    content_store = None
    
    # Store in global context
    @app.before_request
    def before_request():
        # Set up database tables if they don't exist yet
        if not getattr(g, '_db_initialized', False):
            db.create_all()
            g._db_initialized = True
            
        # Set up demo data on first request
        if not getattr(g, '_demo_initialized', False):
            init_demo_data(db.session)
            g._demo_initialized = True
            
        # Set up content store
        nonlocal content_store
        if content_store is None:
            content_store = ContentStore(db.session)
        g.content_store = content_store
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
    
    # Minimal initialization during startup to ensure fast application loading
    # We'll delay database operations until the first request
    
    return app

def init_demo_data(db_session):
    """Initialize demo data for the application"""
    from models import UserAccount, Job
    
    # Create admin user if not exists
    admin = UserAccount.query.filter_by(username='admin').first()
    if not admin:
        admin = UserAccount(
            username='admin',
            email='admin@remotework.com',
            full_name='Admin User',
            role='admin',
            is_active=True
        )
        admin.set_password('remotework_admin2025')
        db_session.add(admin)
        db_session.commit()
        logger.info("Admin user created")
    
    # Add sample jobs if none exist
    if Job.query.count() == 0:
        sample_jobs = [
            {
                'title': 'Senior Frontend Developer',
                'company': 'TechCorp Inc.',
                'location': 'Remote (Worldwide)',
                'salary': '$100,000 - $130,000',
                'job_type': 'Full-time',
                'category': 'white-collar',
                'description': 'We are looking for an experienced frontend developer proficient in React, TypeScript and modern CSS. Must have 5+ years of experience building responsive web applications.',
                'requirements': '- 5+ years of React experience\n- Strong TypeScript skills\n- Experience with state management solutions\n- Understanding of responsive design principles\n- Good communication skills',
                'contact_email': 'careers@techcorp.example.com',
                'application_url': 'https://techcorp.example.com/careers/frontend-dev',
                'posted_date': datetime.now(),
                'is_active': True
            },
            {
                'title': 'Remote Construction Project Manager',
                'company': 'Global Builders',
                'location': 'Remote (US Based)',
                'salary': '$85,000 - $110,000',
                'job_type': 'Contract',
                'category': 'blue-collar',
                'description': 'Seeking an experienced construction project manager to oversee projects remotely. Will coordinate with on-site staff and manage project timelines and budgets.',
                'requirements': '- 8+ years in construction management\n- Experience with remote team coordination\n- Proficient with project management software\n- Strong communication and leadership skills\n- PMP certification preferred',
                'contact_email': 'jobs@globalbuilders.example.com',
                'application_url': 'https://globalbuilders.example.com/apply',
                'posted_date': datetime.now(),
                'is_active': True
            },
            {
                'title': 'Virtual Customer Service Representative',
                'company': 'SupportHub',
                'location': 'Remote (APAC timezone)',
                'salary': '$40,000 - $55,000',
                'job_type': 'Full-time',
                'category': 'grey-collar',
                'description': 'Join our team providing excellent customer service through chat and phone support. Help customers solve issues with our software products.',
                'requirements': '- 2+ years in customer service\n- Excellent written and verbal communication\n- Basic troubleshooting skills\n- Experience with CRM systems\n- Reliable internet connection\n- Must be able to work APAC business hours',
                'contact_email': 'support.hiring@supporthub.example.com',
                'application_url': 'https://supporthub.example.com/careers',
                'posted_date': datetime.now(),
                'is_active': True
            }
        ]
        
        for job_data in sample_jobs:
            job = Job(**job_data)
            db_session.add(job)
        
        db_session.commit()
        logger.info("Sample jobs added to database")

# Create the app instance
app = create_app()