import os
import logging
from flask import Flask
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
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
            'date_posted': datetime.now(),
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

# Add some initial jobs for demonstration
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

# Import routes after app initialization to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
