import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

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
        Dictionary with job details
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
    
    try:
        # Basic request to get the page content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return job_details
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title from page title or common job title elements
        if soup.title:
            title = soup.title.get_text().strip()
            # Clean up common patterns in titles
            title = re.sub(r'\s*[\|\-–—]\s*.*$', '', title)
            job_details['title'] = title
        
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
                job_details['company'] = (company_match.group(1) or company_match.group(2)).strip()
            else:
                # Try to get company from domain
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc
                domain_parts = domain.split('.')
                if len(domain_parts) > 1:
                    job_details['company'] = domain_parts[-2].capitalize()
            
            # Try to extract location
            location_pattern = r'Location:?\s*([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)|in\s+([A-Za-z0-9\s\.,]+?)(?:\n|\.|$)'
            location_match = re.search(location_pattern, content)
            if location_match:
                job_details['location'] = (location_match.group(1) or location_match.group(2)).strip()
            
            # Try to extract job type
            job_type_pattern = r'(Full[ -]Time|Part[ -]Time|Contract|Temporary|Freelance)'
            job_type_match = re.search(job_type_pattern, content, re.IGNORECASE)
            if job_type_match:
                job_details['job_type'] = job_type_match.group(1).strip()
            
            # Try to extract salary
            salary_pattern = r'Salary:?\s*([$€£]?[\d,.]+\s*[-–]\s*[$€£]?[\d,.]+\s*(?:per|\/|\s)?(?:year|yr|month|annum|hour|hr))'
            salary_match = re.search(salary_pattern, content, re.IGNORECASE)
            if salary_match:
                job_details['salary'] = salary_match.group(1).strip()
            
            # Guess job category based on keywords
            white_collar_keywords = ['manager', 'executive', 'director', 'analyst', 'consultant']
            blue_collar_keywords = ['worker', 'technician', 'mechanic', 'operator', 'driver']
            grey_collar_keywords = ['healthcare', 'nurse', 'teacher', 'professor', 'chef']
            
            # Simple keyword matching
            if any(keyword in content.lower() for keyword in white_collar_keywords):
                job_details['category'] = 'white-collar'
            elif any(keyword in content.lower() for keyword in blue_collar_keywords):
                job_details['category'] = 'blue-collar'
            elif any(keyword in content.lower() for keyword in grey_collar_keywords):
                job_details['category'] = 'grey-collar'
            
            # Extract requirements if found
            req_section = re.search(r'Requirements:?\s*([\s\S]+?)(?:Responsibilities|Benefits|About Us|Apply Now|$)', 
                                  content, re.IGNORECASE)
            if req_section:
                job_details['requirements'] = req_section.group(1).strip()
                # Use the content before requirements as description
                req_start = content.find(req_section.group(0))
                if req_start > 100:
                    job_details['description'] = content[:req_start].strip()
                else:
                    job_details['description'] = content
            else:
                # No clear requirements section found
                job_details['description'] = content
    
    except Exception as e:
        # If anything fails, return what we've got so far
        job_details['description'] = f"Error extracting job details: {str(e)}"
    
    return job_details