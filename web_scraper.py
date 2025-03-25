import re
import requests
import logging
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import trafilatura
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """
    Check if a URL is valid.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False

def get_website_text_content(url):
    """
    Extract clean text content from a website using trafilatura.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: The extracted text content
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, 
                                      include_tables=True, include_links=True)
            return text or ""
        return ""
    except Exception as e:
        logger.error(f"Error extracting text with trafilatura: {e}")
        return ""

def extract_job_details(url):
    """
    Extract job details from a URL using trafilatura and BeautifulSoup.
    Advanced version with fallback mechanisms and multiple extraction strategies.
    
    Args:
        url (str): The job posting URL
        
    Returns:
        dict: Dictionary with job details and success status
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
        
        # First try to extract from JSON-LD structured data
        json_ld_data = extract_job_from_json_ld(response.text)
        if json_ld_data and json_ld_data.get('title') and json_ld_data.get('description'):
            logger.info("Found job details in JSON-LD structured data")
            # Update relevant fields from structured data
            for key, value in json_ld_data.items():
                if key in response_data['job'] and value:
                    response_data['job'][key] = value
            
            # If we have essential data, we can mark as success
            if response_data['job']['title'] and response_data['job']['description']:
                response_data['success'] = True
                
        # Continue with traditional HTML parsing for any missing fields
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
        logger.error(f"Error extracting job details: {str(e)}")
        response_data['error'] = f"Error extracting job details: {str(e)}"
        
        # Try fallback extraction method
        try:
            fallback_data = fallback_extraction(url)
            if fallback_data['success']:
                # Update any empty fields with fallback data
                for key, value in fallback_data['job'].items():
                    if not response_data['job'][key] and value:
                        response_data['job'][key] = value
                
                # Update success status if we have title and description
                if response_data['job']['title'] and response_data['job']['description']:
                    response_data['success'] = True
        except Exception as fallback_error:
            logger.error(f"Fallback extraction also failed: {fallback_error}")
    
    return response_data

def fallback_extraction(url):
    """
    Fallback method to extract basic information when the main method fails.
    Uses a combination of techniques for more reliable extraction.
    
    Args:
        url (str): The job posting URL
        
    Returns:
        dict: Job details extracted via alternative methods
    """
    # Initialize response data
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
        # Use trafilatura for cleaner text extraction
        text_content = get_website_text_content(url)
        
        if not text_content:
            logger.warning(f"Trafilatura couldn't extract content from {url}")
            return response_data
            
        # Extract title using common patterns
        title_match = re.search(r'^(.+?)(?:\n|$|\|)', text_content)
        if title_match:
            response_data['job']['title'] = title_match.group(1).strip()
            
        # Try to extract company using common patterns
        company_patterns = [
            r'(?:at|with|for|by)\s+([A-Za-z0-9\s&\.,]+?)(?:\n|\.|$)',
            r'Company:?\s*([A-Za-z0-9\s&\.,]+?)(?:\n|\.|$)',
            r'About\s+([A-Za-z0-9\s&\.,]+?)(?:\n|\.|$)'
        ]
        
        for pattern in company_patterns:
            company_match = re.search(pattern, text_content)
            if company_match:
                response_data['job']['company'] = company_match.group(1).strip()
                break
                
        # If no company found, try domain name
        if not response_data['job']['company']:
            domain = urlparse(url).netloc
            domain_parts = domain.split('.')
            if len(domain_parts) > 1:
                response_data['job']['company'] = domain_parts[-2].capitalize()
        
        # Extract description
        response_data['job']['description'] = text_content
        
        # Extract job type
        job_type_patterns = [
            r'(Full[ -]Time|Part[ -]Time|Contract|Temporary|Freelance|Remote)',
            r'Job Type:?\s*([A-Za-z\s-]+)(?:\n|\.|$)',
            r'Employment Type:?\s*([A-Za-z\s-]+)(?:\n|\.|$)'
        ]
        
        for pattern in job_type_patterns:
            job_type_match = re.search(pattern, text_content, re.IGNORECASE)
            if job_type_match:
                response_data['job']['job_type'] = job_type_match.group(1).strip()
                break
                
        # Extract location - prefer anything with "remote" in it
        remote_pattern = r'(Remote|Work from home|Work from anywhere|Virtual position)'
        remote_match = re.search(remote_pattern, text_content, re.IGNORECASE)
        if remote_match:
            response_data['job']['location'] = remote_match.group(1).strip()
        else:
            # Try other location patterns
            location_patterns = [
                r'Location:?\s*([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)',
                r'based in\s+([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)',
                r'(?:in|at)\s+([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)'
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, text_content)
                if location_match:
                    response_data['job']['location'] = location_match.group(1).strip()
                    break
        
        # Extract salary if available
        salary_patterns = [
            r'Salary:?\s*([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))',
            r'(?:Pay|Compensation|Rate):?\s*([$€£]?[\d,.]+\s*[-–to]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))',
            r'([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+[k]?\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))'
        ]
        
        for pattern in salary_patterns:
            salary_match = re.search(pattern, text_content, re.IGNORECASE)
            if salary_match:
                response_data['job']['salary'] = salary_match.group(1).strip()
                break
                
        # Extract requirements
        req_patterns = [
            r'Requirements:?\s*([\s\S]+?)(?:Responsibilities|Benefits|About Us|Apply Now|$)',
            r'Qualifications:?\s*([\s\S]+?)(?:Responsibilities|Benefits|About Us|Apply Now|$)',
            r'Skills:?\s*([\s\S]+?)(?:Responsibilities|Benefits|About Us|Apply Now|$)'
        ]
        
        for pattern in req_patterns:
            req_match = re.search(pattern, text_content, re.IGNORECASE)
            if req_match:
                response_data['job']['requirements'] = req_match.group(1).strip()
                break
                
        # Set success status
        if response_data['job']['title'] and response_data['job']['description']:
            response_data['success'] = True
            
    except Exception as e:
        logger.error(f"Fallback extraction error: {e}")
        response_data['error'] = f"Fallback extraction failed: {str(e)}"
        
    return response_data

def test_extraction(url):
    """
    Test function to demonstrate the job extraction capabilities.
    
    Args:
        url (str): URL of a job posting
        
    Returns:
        dict: Extracted job details or error message
    """
    if not is_valid_url(url):
        return {"error": "Invalid URL format"}
    
    # Extract job details
    result = extract_job_details(url)
    
    # Return a clean version of the result with more readable formatting
    if result['success']:
        job = result['job']
        output = {
            "title": job['title'],
            "company": job['company'],
            "location": job['location'],
            "job_type": job['job_type'],
            "category": job['category'],
            "subcategory": job['subcategory'],
            "salary": job['salary'],
            "description_preview": job['description'][:150] + "..." if len(job['description']) > 150 else job['description'],
            "requirements_preview": job['requirements'][:150] + "..." if len(job['requirements']) > 150 else job['requirements'],
            "extracted_successfully": True
        }
        return output
    else:
        return {
            "error": result['error'],
            "extracted_successfully": False
        }

def extract_job_from_json_ld(html):
    """
    Extract job posting structured data from JSON-LD.
    Many job sites implement schema.org JobPosting structured data.
    
    Args:
        html (str): HTML content of the page
        
    Returns:
        dict: Job details from structured data or empty dict if none found
    """
    job_data = {}
    try:
        soup = BeautifulSoup(html, 'html.parser')
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Check if this is a JobPosting
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    # Extract relevant fields
                    job_data['title'] = data.get('title', '')
                    job_data['description'] = data.get('description', '')
                    
                    # Handle company/organization
                    if 'hiringOrganization' in data:
                        org = data['hiringOrganization']
                        if isinstance(org, dict):
                            job_data['company'] = org.get('name', '')
                    
                    # Handle location
                    if 'jobLocation' in data:
                        loc = data['jobLocation']
                        if isinstance(loc, dict) and 'address' in loc:
                            addr = loc['address']
                            if isinstance(addr, dict):
                                job_data['location'] = addr.get('addressLocality', '')
                                if 'addressRegion' in addr:
                                    job_data['location'] += f", {addr['addressRegion']}"
                    
                    # Employment type
                    job_data['job_type'] = data.get('employmentType', '')
                    
                    # Salary
                    if 'baseSalary' in data:
                        salary = data['baseSalary']
                        if isinstance(salary, dict):
                            if 'value' in salary:
                                value = salary['value']
                                if isinstance(value, dict):
                                    min_val = value.get('minValue', '')
                                    max_val = value.get('maxValue', '')
                                    unit = value.get('unitText', '')
                                    
                                    if min_val and max_val:
                                        job_data['salary'] = f"${min_val} - ${max_val} {unit}"
                    
                    # Only break if we found useful data
                    if job_data.get('title') and job_data.get('description'):
                        break
                        
                # Check if there's an array with JobPosting
                elif isinstance(data, dict) and '@graph' in data:
                    for item in data['@graph']:
                        if isinstance(item, dict) and item.get('@type') == 'JobPosting':
                            # Extract job details as above
                            job_data['title'] = item.get('title', '')
                            job_data['description'] = item.get('description', '')
                            
                            # Handle company/organization
                            if 'hiringOrganization' in item:
                                org = item['hiringOrganization']
                                if isinstance(org, dict):
                                    job_data['company'] = org.get('name', '')
                            
                            # Only break if we found useful data
                            if job_data.get('title') and job_data.get('description'):
                                break
                
            except json.JSONDecodeError:
                logger.warning("Invalid JSON-LD found")
                continue
                
    except Exception as e:
        logger.error(f"Error extracting JSON-LD job data: {e}")
    
    return job_data