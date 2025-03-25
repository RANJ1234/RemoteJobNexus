import os
import logging
import datetime
import threading
from flask import Flask

# Configure logging - set to WARNING level to minimize output and improve startup
logging.basicConfig(level=logging.WARNING)

# Create Flask app with minimal configurations initially
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# In-memory storage for jobs
# This will be replaced with a database in a production environment
class JobStore:
    def __init__(self):
        self.jobs = []
        self.job_id_counter = 1
    
    def add_job(self, job_data):
        job_id = self.job_id_counter
        self.job_id_counter += 1
        
        job = {
            'id': job_id,
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'location': job_data.get('location', 'Remote'),
            'description': job_data.get('description', ''),
            'requirements': job_data.get('requirements', ''),
            'salary_range': job_data.get('salary_range', ''),
            'application_url': job_data.get('application_url', ''),
            'contact_email': job_data.get('contact_email', ''),
            'job_type': job_data.get('job_type', 'Full-time'),
            'job_category': job_data.get('job_category', 'White-collar'),
            'date_posted': datetime.datetime.now(),
            'source_url': job_data.get('source_url', '')
        }
        
        self.jobs.append(job)
        return job_id
    
    def get_job(self, job_id):
        for job in self.jobs:
            if job['id'] == job_id:
                return job
        return None
    
    def get_all_jobs(self):
        return sorted(self.jobs, key=lambda x: x['date_posted'], reverse=True)
    
    def search_jobs(self, query):
        if not query:
            return self.get_all_jobs()
            
        query = query.lower()
        results = []
        
        for job in self.jobs:
            if (query in job['title'].lower() or 
                query in job['company'].lower() or 
                query in job['description'].lower()):
                results.append(job)
                
        return results

# Initialize the job store
job_store = JobStore()

# Demo job data - moved to a separate function to defer loading until needed
def init_demo_jobs():
    # Add initial jobs for demonstration only if none exist
    if not job_store.jobs:
        job_store.add_job({
            'title': 'Senior Frontend Developer',
            'company': 'Anime Tech Inc.',
            'location': 'Remote (Worldwide)',
            'description': 'We are looking for an experienced Frontend Developer with expertise in Three.js and WebGL.',
            'requirements': 'At least 3 years of experience with React, Three.js, and WebGL. Experience with anime-style design is a plus.',
            'salary_range': '$100,000 - $130,000',
            'application_url': 'https://example.com/apply',
            'contact_email': 'jobs@animetech.com',
            'job_type': 'Full-time'
        })

        job_store.add_job({
            'title': 'Backend Python Developer',
            'company': 'Sakura Systems',
            'location': 'Remote (US/EU)',
            'description': 'Join our team to develop scalable backend solutions for our growing platform.',
            'requirements': 'Strong experience with Python, Flask, and API development. Knowledge of database design and optimization.',
            'salary_range': '$90,000 - $120,000',
            'application_url': 'https://example.com/apply',
            'contact_email': 'careers@sakurasystems.com',
            'job_type': 'Full-time'
        })

        job_store.add_job({
            'title': '3D Designer / Animator',
            'company': 'NeoTokyo Graphics',
            'location': 'Remote (APAC Preferred)',
            'description': 'Create stunning 3D anime-style animations and designs for our gaming projects.',
            'requirements': 'Portfolio showing anime-inspired 3D work. Proficiency in Blender and/or Maya. Experience with character rigging and animation.',
            'salary_range': '$70,000 - $100,000',
            'application_url': 'https://example.com/apply',
            'contact_email': 'hiring@neotokyographics.jp',
            'job_type': 'Contract'
        })

# Content management for the admin panel
class ContentStore:
    def __init__(self):
        # Dictionary to store all site content by section - lazy initialization
        self.posts = []
        self.post_id_counter = 1
        self._content = None  # Lazy initialization
    
    @property
    def content(self):
        # Load content only when first accessed
        if self._content is None:
            self._content = self._initialize_content()
        return self._content
    
    def _initialize_content(self):
        # Initialize default content
        return {
            'homepage': {
                'hero_title': 'Find Your Remote Dream Job',
                'hero_subtitle': 'Connect with global opportunities - blue, white, and grey-collar positions available worldwide.',
                'featured_section_title': 'Featured Remote Positions',
                'featured_section_description': 'Discover top remote opportunities from around the world',
                'about_section_title': 'Why Remote Work?',
                'about_section_content': 'Remote work offers flexibility, work-life balance, and access to global opportunities. Our platform connects talented individuals with employers worldwide, regardless of location.'
            },
            'carousel': [
                {
                    'image_url': '/static/images/carousel1.jpg',
                    'title': 'Blue-Collar Remote Work',
                    'description': 'Remote opportunities for skilled trades and technical professionals'
                },
                {
                    'image_url': '/static/images/carousel2.jpg',
                    'title': 'White-Collar Positions',
                    'description': 'Professional roles from leading global companies'
                },
                {
                    'image_url': '/static/images/carousel3.jpg',
                    'title': 'Grey-Collar Careers',
                    'description': 'Remote options in healthcare, education, and service industries'
                }
            ],
            'footer': {
                'company_description': 'Remote Work connects global talent with employers worldwide, offering opportunities across all sectors.',
                'contact_email': 'contact@remotework.com',
                'social_links': {
                    'twitter': 'https://twitter.com/remotework',
                    'linkedin': 'https://linkedin.com/company/remotework',
                    'facebook': 'https://facebook.com/remotework'
                }
            }
        }
        
    def get_section(self, section_name):
        """Get content for a specific section"""
        return self.content.get(section_name, {})
    
    def update_section(self, section_name, content_data):
        """Update content for a specific section"""
        if section_name in self.content:
            self.content[section_name].update(content_data)
            return True
        return False
    
    def add_carousel_item(self, item_data):
        """Add a new carousel item"""
        if 'carousel' in self.content:
            self.content['carousel'].append(item_data)
            return True
        return False
    
    def remove_carousel_item(self, index):
        """Remove a carousel item by index"""
        if 'carousel' in self.content and 0 <= index < len(self.content['carousel']):
            self.content['carousel'].pop(index)
            return True
        return False
    
    def update_carousel_item(self, index, item_data):
        """Update a carousel item by index"""
        if 'carousel' in self.content and 0 <= index < len(self.content['carousel']):
            self.content['carousel'][index].update(item_data)
            return True
        return False
        
    # Blog-related methods
    def add_post(self, title, content, author, tags=None):
        """Add a new blog post"""
        if tags is None:
            tags = []
        post = {
            'id': self.post_id_counter,
            'title': title,
            'content': content,
            'author': author,
            'date_posted': datetime.datetime.now(),
            'tags': tags
        }
        self.posts.append(post)
        self.post_id_counter += 1
        return post['id']
    
    def get_post(self, post_id):
        """Get a specific blog post by ID"""
        for post in self.posts:
            if post['id'] == post_id:
                return post
        return None
    
    def get_all_posts(self):
        """Get all blog posts, sorted by date"""
        return sorted(self.posts, key=lambda x: x['date_posted'], reverse=True)

# Initialize the content store with lazy loading
content_store = ContentStore()

# Delayed initialization of user store and registration of routes
# We'll initialize these components just before they're needed
user_store = None  # Will be initialized on first use

# Create a context processor for initialization
@app.context_processor
def inject_init_function():
    # Make init_demo_jobs available to templates
    return {'init_demo_jobs': init_demo_jobs}

# Global initialization lock
_init_lock = threading.RLock()
_initialized = False

# This function ensures routes and user store are loaded before first request
@app.before_request
def ensure_initialization():
    global _initialized, user_store
    
    # Use a lock to prevent multiple threads initializing at once
    with _init_lock:
        if not _initialized:
            # Import and initialize User store
            from models import User
            user_store = User()
            
            # Import routes module to register all routes
            import routes
            
            # Mark as initialized
            _initialized = True

if __name__ == '__main__':
    # Import routes directly when running as main module
    import routes
    app.run(host='0.0.0.0', port=5000, debug=True)
