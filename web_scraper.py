import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura
from datetime import datetime

def is_valid_url(url):
    """Check if a URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_job_details(url):
    """
    Extract job details from a URL using trafilatura and BeautifulSoup.
    
    Args:
        url: The job posting URL
        
    Returns:
        Dictionary with job details and success status
    """
    # Response object format
    response_data = {
        'success': False,
        'job': {
            'title': '',
            'company': '',
            'location': 'Remote',
            'job_type': '',
            'category': '',
            'subcategory': '',
            'salary': '',
            'description': '',
            'requirements': '',
            'application_url': url,
            'source_url': url,
            'contact_email': ''
        },
        'error': None
    }
    
    try:
        # Basic request to get the page content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            response_data['error'] = f"Failed to fetch URL, status code: {response.status_code}"
            return response_data
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title from page title or common job title elements
        if soup.title:
            title = soup.title.get_text().strip()
            # Clean up common patterns in titles
            title = re.sub(r'\s*[\|\-–—]\s*.*$', '', title)
            response_data['job']['title'] = title
        
        # Try to find common job posting elements
        job_container = None
        
        # Look for common job posting containers
        for selector in ['#job-description', '.job-description', '.job-posting', 
                        '.job-details', '#job-details', 'article.job']:
            container = soup.select_one(selector)
            if container:
                job_container = container
                break
        
        # If no specific container found, use the body
        if not job_container:
            job_container = soup.body
        
        if job_container:
            # Extract text content
            content = job_container.get_text()
            
            # Try to extract company name
            company_pattern = r'Company:?\s*([A-Za-z0-9\s&\.,]+?)(?:\n|\.|$)|at\s+([A-Za-z0-9\s&\.,]+?)(?:\n|\.|$)'
            company_match = re.search(company_pattern, content)
            if company_match:
                response_data['job']['company'] = (company_match.group(1) or company_match.group(2)).strip()
            else:
                # Try to get company from domain
                domain = urlparse(url).netloc
                domain_parts = domain.split('.')
                if len(domain_parts) > 1:
                    response_data['job']['company'] = domain_parts[-2].capitalize()
            
            # Try to extract location
            location_pattern = r'Location:?\s*([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)|in\s+([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)'
            location_match = re.search(location_pattern, content)
            if location_match:
                response_data['job']['location'] = (location_match.group(1) or location_match.group(2)).strip()
            
            # Try to extract job type
            job_type_pattern = r'(Full[ -]Time|Part[ -]Time|Contract|Temporary|Freelance)'
            job_type_match = re.search(job_type_pattern, content, re.IGNORECASE)
            if job_type_match:
                response_data['job']['job_type'] = job_type_match.group(1).strip()
            
            # Try to extract salary
            salary_pattern = r'Salary:?\s*([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))'
            salary_match = re.search(salary_pattern, content, re.IGNORECASE)
            if salary_match:
                response_data['job']['salary'] = salary_match.group(1).strip()
            
            # Try to extract email
            email_pattern = r'([\w\.-]+@[\w\.-]+\.\w+)'
            email_match = re.search(email_pattern, content)
            if email_match:
                response_data['job']['contact_email'] = email_match.group(1).strip()
            
            # Guess job category and subcategory based on keywords
            categories = {
                'technology': ['developer', 'engineer', 'software', 'data', 'IT', 'web', 'cloud', 'devops', 'security', 'cyber'],
                'creative': ['designer', 'writer', 'marketing', 'content', 'media', 'graphic', 'video', 'photography', 'social'],
                'professional': ['manager', 'executive', 'director', 'analyst', 'consultant', 'sales', 'legal', 'accounting'],
                'healthcare': ['health', 'medical', 'nurse', 'doctor', 'therapist', 'clinical', 'patient'],
                'education': ['teacher', 'professor', 'instructor', 'tutor', 'curriculum', 'education'],
                'skilled-trades': ['technician', 'mechanic', 'electrician', 'plumber', 'carpenter', 'maintenance']
            }
            
            # Subcategories mapping
            subcategories = {
                'technology': {
                    'software': 'Software Development',
                    'data': 'Data Science',
                    'web': 'Software Development',
                    'network': 'IT & Networking',
                    'cloud': 'DevOps',
                    'security': 'Cybersecurity',
                    'cyber': 'Cybersecurity',
                    'product': 'Product Management',
                    'devops': 'DevOps'
                },
                'creative': {
                    'design': 'Design',
                    'graphic': 'Design',
                    'ui': 'Design',
                    'ux': 'Design',
                    'content': 'Writing',
                    'write': 'Writing',
                    'market': 'Marketing',
                    'video': 'Video Production',
                    'anim': 'Animation',
                    'social': 'Social Media'
                },
                'professional': {
                    'account': 'Accounting',
                    'finance': 'Accounting',
                    'legal': 'Legal',
                    'hr': 'HR',
                    'human resource': 'HR',
                    'service': 'Customer Service',
                    'sales': 'Sales',
                    'consult': 'Consulting'
                },
                'healthcare': {
                    'tele': 'Telemedicine',
                    'code': 'Medical Coding',
                    'coach': 'Health Coaching',
                    'mental': 'Mental Health',
                    'psych': 'Mental Health',
                    'write': 'Medical Writing'
                },
                'education': {
                    'teach': 'Online Teaching',
                    'curriculum': 'Curriculum Development',
                    'consult': 'Educational Consulting',
                    'tutor': 'Tutoring',
                    'course': 'Course Creation'
                },
                'skilled-trades': {
                    'tech': 'Remote Technician',
                    'project': 'Project Management',
                    'quality': 'Quality Assurance',
                    'qa': 'Quality Assurance',
                    'install': 'Virtual Installation Support'
                }
            }
            
            # Find best matching category
            best_category = None
            max_matches = 0
            
            for category, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword.lower() in content.lower())
                if matches > max_matches:
                    max_matches = matches
                    best_category = category
            
            if best_category:
                response_data['job']['category'] = best_category
                
                # Find best matching subcategory
                best_subcategory = None
                max_sub_matches = 0
                
                for keyword, subcategory in subcategories[best_category].items():
                    if keyword.lower() in content.lower():
                        matches = content.lower().count(keyword.lower())
                        if matches > max_sub_matches:
                            max_sub_matches = matches
                            best_subcategory = subcategory
                
                if best_subcategory:
                    response_data['job']['subcategory'] = best_subcategory
            
            # Extract requirements if found
            req_section = re.search(r'Requirements:?\s*([\s\S]+?)(?:Responsibilities|Benefits|About Us|Apply Now|$)', 
                                  content, re.IGNORECASE)
            if req_section:
                response_data['job']['requirements'] = req_section.group(1).strip()
                # Use the content before requirements as description
                req_start = content.find(req_section.group(0))
                if req_start > 100:
                    response_data['job']['description'] = content[:req_start].strip()
                else:
                    response_data['job']['description'] = content
            else:
                # No clear requirements section found
                response_data['job']['description'] = content
        
        # Set success to true if we at least got a title and description
        if response_data['job']['title'] and response_data['job']['description']:
            response_data['success'] = True
    
    except Exception as e:
        # If anything fails, capture the error
        response_data['error'] = f"Error extracting job details: {str(e)}"
    
    return response_data