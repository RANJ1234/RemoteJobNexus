from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# This will be set by the delayed loader
db = None

# ====================================================
# User Account Model
# ====================================================
class UserAccount(UserMixin, object):
    if db is not None:
        __tablename__ = 'user_accounts'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), unique=True, nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        full_name = db.Column(db.String(100))
        role = db.Column(db.String(20), default='user')  # admin, employer, user
        google_id = db.Column(db.String(100), unique=True, nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.now)
        last_login = db.Column(db.DateTime)
        is_active = db.Column(db.Boolean, default=True)
        reset_token = db.Column(db.String(100), nullable=True)
        reset_token_expiry = db.Column(db.DateTime, nullable=True)
    else:
        id = None
        username = None
        email = None
        password_hash = None
        full_name = None
        role = None
        google_id = None
        created_at = None
        last_login = None
        is_active = None
        reset_token = None
        reset_token_expiry = None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.now() + timedelta(hours=24)
        return self.reset_token
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_employer(self):
        return self.role == 'employer'

# We'll define the rest of the models when the db is actually set
if db is not None:
    # ====================================================
    # Job Model
    # ====================================================
    class Job(db.Model):
        __tablename__ = 'jobs'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255), nullable=False)
        company = db.Column(db.String(100), nullable=False)
        location = db.Column(db.String(100), nullable=False)
        salary = db.Column(db.String(100))
        job_type = db.Column(db.String(50))  # Full-time, Part-time, Contract, etc.
        category = db.Column(db.String(50))  # technology, creative, professional, etc.
        subcategory = db.Column(db.String(100))  # Software Development, Design, Accounting, etc.
        description = db.Column(db.Text, nullable=False)
        requirements = db.Column(db.Text)
        contact_email = db.Column(db.String(100))
        application_url = db.Column(db.String(255))
        posted_date = db.Column(db.DateTime, default=datetime.now)
        is_active = db.Column(db.Boolean, default=True)
        views = db.Column(db.Integer, default=0)
        source_url = db.Column(db.String(255))  # If scraped from another site
        
        # Relationships
        user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=True)
        user = db.relationship('UserAccount', backref=db.backref('jobs', lazy=True))
        
        def to_dict(self):
            return {
                'id': self.id,
                'title': self.title,
                'company': self.company,
                'location': self.location,
                'salary': self.salary,
                'job_type': self.job_type,
                'category': self.category,
                'subcategory': self.subcategory,
                'description': self.description,
                'requirements': self.requirements,
                'contact_email': self.contact_email,
                'application_url': self.application_url,
                'posted_date': self.posted_date.strftime('%Y-%m-%d') if self.posted_date else None,
                'is_active': self.is_active,
                'views': self.views
            }

    # ====================================================
    # Blog Post Model
    # ====================================================
    class BlogPost(db.Model):
        __tablename__ = 'blog_posts'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255), nullable=False)
        content = db.Column(db.Text, nullable=False)
        author = db.Column(db.String(100), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.now)
        updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
        tags = db.Column(db.String(255))  # Comma-separated tags
        featured_image = db.Column(db.String(255))
        is_published = db.Column(db.Boolean, default=True)
        views = db.Column(db.Integer, default=0)
        
        # Relationships
        user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=True)
        user = db.relationship('UserAccount', backref=db.backref('blog_posts', lazy=True))
        
        def get_tags_list(self):
            if self.tags:
                return [tag.strip() for tag in self.tags.split(',')]
            return []

    # ====================================================
    # Website Content Model (for CMS)
    # ====================================================
    class WebsiteContent(db.Model):
        __tablename__ = 'website_content'
        
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text)  # JSON content stored as text
        updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # ====================================================
    # Site Visit Model (for analytics)
    # ====================================================
    class SiteVisit(db.Model):
        __tablename__ = 'site_visits'
        
        id = db.Column(db.Integer, primary_key=True)
        page = db.Column(db.String(255), nullable=False)
        ip_address = db.Column(db.String(50))
        visit_date = db.Column(db.DateTime, default=datetime.now)
        user_agent = db.Column(db.String(255))
        referrer = db.Column(db.String(255))
        
        # Relationship for authenticated users
        user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=True)
        user = db.relationship('UserAccount', backref=db.backref('visits', lazy=True))

    # ====================================================
    # Job Application Model
    # ====================================================
    class JobApplication(db.Model):
        __tablename__ = 'job_applications'
        
        id = db.Column(db.Integer, primary_key=True)
        job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=True)
        applicant_name = db.Column(db.String(100), nullable=False)
        applicant_email = db.Column(db.String(100), nullable=False)
        cover_letter = db.Column(db.Text)
        resume_path = db.Column(db.String(255))
        applied_at = db.Column(db.DateTime, default=datetime.now)
        status = db.Column(db.String(20), default='new')  # new, reviewed, contacted, rejected, hired
        
        # Relationships
        job = db.relationship('Job', backref=db.backref('applications', lazy=True))
        user = db.relationship('UserAccount', backref=db.backref('applications', lazy=True))

    # ====================================================
    # Newsletter Subscriber Model
    # ====================================================
    class NewsletterSubscriber(db.Model):
        __tablename__ = 'newsletter_subscribers'
        
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True, nullable=False)
        first_name = db.Column(db.String(50))
        subscribed_at = db.Column(db.DateTime, default=datetime.now)
        is_active = db.Column(db.Boolean, default=True)
        job_category_preference = db.Column(db.String(50))  # Preferred job category for targeted emails
else:
    # Create placeholder classes
    class Job(object):
        pass
        
    class BlogPost(object):
        pass
        
    class WebsiteContent(object):
        pass
        
    class SiteVisit(object):
        pass
        
    class JobApplication(object):
        pass
        
    class NewsletterSubscriber(object):
        pass