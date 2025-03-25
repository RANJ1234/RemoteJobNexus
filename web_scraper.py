import re
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

def _import_trafilatura():
    """Import trafilatura only when needed to speed up app loading."""
    try:
        import trafilatura
        return trafilatura
    except ImportError:
        return None

def get_website_text_content(url: str) -> str:
    """
    Extract the main text content from a website.
    
    Args:
        url: The URL of the website to extract text from
        
    Returns:
        Extracted text content as a string
    """
    trafilatura = _import_trafilatura()
    if not trafilatura:
        return "Error: Trafilatura module not available"
    
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "Error: Could not download content from URL"
        
        text = trafilatura.extract(downloaded)
        return text or "No content could be extracted"
    except Exception as e:
        return f"Error extracting content: {str(e)}"

def extract_job_details(url: str) -> dict:
    """
    Extract job details from a job posting URL.
    
    Args:
        url: The URL of the job posting
        
    Returns:
        Dictionary containing extracted job details
    """
    # Default empty job details
    job_details = {
        'title': '',
        'company': '',
        'location': '',
        'job_type': '',
        'category': '',
        'salary': '',
        'description': '',
        'requirements': '',
        'application_url': url,
        'source_url': url
    }
    
    # Get text content
    content = get_website_text_content(url)
    if content.startswith("Error:"):
        # Fallback to basic extraction
        return fallback_extraction(url)
    
    # Try to identify job title (usually at the beginning)
    title_match = re.search(r'^(.+?)(?:\n|$)', content)
    if title_match:
        job_details['title'] = title_match.group(1).strip()
    
    # Try to extract company name
    company_patterns = [
        r'(?:at|with|for)\s+([A-Z][A-Za-z0-9\s&\.,]+?)(?:\sin|\s-|\n|$)',
        r'Company:?\s*([A-Z][A-Za-z0-9\s&\.,]+?)(?:\s|\n|$)'
    ]
    for pattern in company_patterns:
        company_match = re.search(pattern, content)
        if company_match:
            job_details['company'] = company_match.group(1).strip()
            break
    
    # Try to extract location
    location_patterns = [
        r'Location:?\s*([A-Za-z0-9\s\.,]+?)(?:\n|\s-|$)',
        r'(?:in|at)\s+([A-Za-z0-9\s\.,]+?)(?:\n|\s-|$)'
    ]
    for pattern in location_patterns:
        location_match = re.search(pattern, content)
        if location_match:
            job_details['location'] = location_match.group(1).strip()
            break
    
    # Try to extract job type
    job_type_patterns = [
        r'(Full[ -]Time|Part[ -]Time|Contract|Temporary|Freelance)',
        r'Job Type:?\s*([A-Za-z\s-]+?)(?:\n|\s-|$)'
    ]
    for pattern in job_type_patterns:
        job_type_match = re.search(pattern, content, re.IGNORECASE)
        if job_type_match:
            job_details['job_type'] = job_type_match.group(1).strip()
            break
    
    # Try to extract salary
    salary_patterns = [
        r'Salary:?\s*([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))',
        r'([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))',
        r'Salary:?\s*([$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))'
    ]
    for pattern in salary_patterns:
        salary_match = re.search(pattern, content, re.IGNORECASE)
        if salary_match:
            job_details['salary'] = salary_match.group(1).strip()
            break
    
    # Try to determine category (white-collar, blue-collar, grey-collar)
    white_collar_keywords = ['manager', 'executive', 'director', 'analyst', 'consultant', 
                           'administrator', 'coordinator', 'specialist', 'professional']
    blue_collar_keywords = ['worker', 'technician', 'mechanic', 'operator', 'driver', 
                          'construction', 'labor', 'maintenance', 'assembly']
    grey_collar_keywords = ['healthcare', 'nurse', 'doctor', 'teacher', 'professor', 
                          'education', 'social', 'hospitality', 'culinary', 'chef']
    
    # Count keyword occurrences
    white_count = sum(1 for keyword in white_collar_keywords if re.search(r'\b' + keyword + r'\b', content, re.IGNORECASE))
    blue_count = sum(1 for keyword in blue_collar_keywords if re.search(r'\b' + keyword + r'\b', content, re.IGNORECASE))
    grey_count = sum(1 for keyword in grey_collar_keywords if re.search(r'\b' + keyword + r'\b', content, re.IGNORECASE))
    
    # Determine category based on highest count
    if white_count > blue_count and white_count > grey_count:
        job_details['category'] = 'white-collar'
    elif blue_count > white_count and blue_count > grey_count:
        job_details['category'] = 'blue-collar'
    elif grey_count > 0:
        job_details['category'] = 'grey-collar'
    
    # Split content into description and requirements
    req_pattern = r'(?:Requirements|Qualifications|What You\'ll Need|Skills Required)[:.]?\s*([\s\S]+?)(?:Benefits|About Us|Apply Now|$)'
    req_match = re.search(req_pattern, content, re.IGNORECASE)
    
    if req_match:
        # If requirements section is found, split content
        req_start = content.find(req_match.group(0))
        if req_start > 100:  # Ensure we have enough content for description
            job_details['description'] = content[:req_start].strip()
            job_details['requirements'] = req_match.group(1).strip()
        else:
            job_details['description'] = content
    else:
        # No clear requirements section, use whole content as description
        job_details['description'] = content
    
    return job_details

def fallback_extraction(url: str) -> dict:
    """
    Fallback method for extracting basic job information from a URL.
    
    Args:
        url: The URL to extract information from
        
    Returns:
        Dictionary with basic job details
    """
    job_details = {
        'title': '',
        'company': '',
        'location': '',
        'job_type': '',
        'category': '',
        'salary': '',
        'description': '',
        'requirements': '',
        'application_url': url,
        'source_url': url
    }
    
    try:
        # Parse URL to get domain
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        
        # Try to extract company from domain
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            job_details['company'] = domain_parts[-2].capitalize()
        
        # Basic request to get title from HTML
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Get title
            if soup.title:
                title = soup.title.text.strip()
                # Clean up common patterns in titles
                title = re.sub(r'\s*[\|\-–—]\s*.*$', '', title)  # Remove everything after |, -, –, or —
                job_details['title'] = title
            
            # Try to extract description
            description = ""
            # Look for common job description containers
            for selector in ['#job-description', '.job-description', '[data-cy="job-description"]', 
                          '.description', '#description', '[role="description"]']:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text().strip()
                    break
            
            if not description:
                # Try meta description as fallback
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and 'content' in meta_desc.attrs:
                    description = meta_desc['content']
            
            job_details['description'] = description
    
    except Exception:
        # If all fails, return the basic empty structure
        pass
    
    return job_details