import requests
from bs4 import BeautifulSoup
import logging
import re
import trafilatura
from urllib.parse import urlparse


def is_valid_url(url):
    """Check if the provided URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_job_details(url):
    """
    Extract job details from a given URL.
    
    This function attempts to scrape job information from common job posting sites.
    It first uses trafilatura for general text extraction, then applies heuristics
    to identify job details from the extracted content.
    
    Returns a dictionary with extracted job details.
    """
    if not is_valid_url(url):
        return {"error": "Invalid URL format"}
    
    job_data = {
        "title": "",
        "company": "",
        "location": "Remote",
        "description": "",
        "requirements": "",
        "salary_range": "",
        "application_url": "",
        "job_type": "Full-time",
        "job_category": "White-collar",
        "source_url": url
    }
    
    try:
        # First try using trafilatura for general content extraction
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise Exception("Failed to download page content")
        
        # Extract the main text content
        text_content = trafilatura.extract(downloaded)
        if not text_content:
            raise Exception("Failed to extract text content")
        
        # Extract specific job details using heuristics
        # Parse the content and try to identify job details
        
        # Extract job title (usually at the beginning)
        title_patterns = [
            r"(?i)position:?\s*([^\n\.]+)",
            r"(?i)job title:?\s*([^\n\.]+)",
            r"(?i)role:?\s*([^\n\.]+)",
            r"(?i)^([^\n\.]{5,50})\s*\n"  # First line if it's reasonable length for a title
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text_content)
            if match:
                job_data["title"] = match.group(1).strip()
                break
                
        # Extract company name
        company_patterns = [
            r"(?i)company:?\s*([^\n\.]+)",
            r"(?i)at\s+([A-Z][^\n\.]{2,30})",
            r"(?i)with\s+([A-Z][^\n\.]{2,30})\s+is"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text_content)
            if match:
                job_data["company"] = match.group(1).strip()
                break
                
        # Extract location (focusing on remote work)
        if re.search(r"(?i)remote", text_content):
            # Try to determine if there are location restrictions
            remote_patterns = [
                r"(?i)remote\s*\(([^\)]+)\)",
                r"(?i)remote[\s\-]+([A-Za-z0-9\s,]+)",
                r"(?i)location:?\s*remote\s*([A-Za-z0-9\s,]+)"
            ]
            
            for pattern in remote_patterns:
                match = re.search(pattern, text_content)
                if match:
                    job_data["location"] = f"Remote ({match.group(1).strip()})"
                    break
            else:
                job_data["location"] = "Remote (Worldwide)"
                
        # Extract salary information if available
        salary_patterns = [
            r"(?i)salary:?\s*([^\n\.]+)",
            r"(?i)compensation:?\s*([^\n\.]+)",
            r"(?i)pay:?\s*([^\n\.]+)",
            r"(?i)\$\s*(\d{2,3}[,\.]?\d{3})\s*[-–]\s*\$?\s*(\d{2,3}[,\.]?\d{3})"
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text_content)
            if match:
                if pattern.endswith(")"):
                    job_data["salary_range"] = match.group(1).strip()
                else:
                    try:
                        # If it's the pattern with actual numbers, format it nicely
                        min_salary = match.group(1)
                        max_salary = match.group(2)
                        job_data["salary_range"] = f"${min_salary} - ${max_salary}"
                    except:
                        job_data["salary_range"] = match.group(1).strip()
                break
        
        # Extract job type
        job_type_patterns = [
            r"(?i)job type:?\s*([^\n\.]+)",
            r"(?i)employment type:?\s*([^\n\.]+)",
            r"(?i)(full[\s-]*time|part[\s-]*time|contract|freelance|temporary)"
        ]
        
        for pattern in job_type_patterns:
            match = re.search(pattern, text_content)
            if match:
                job_data["job_type"] = match.group(1).strip().title()
                break
                
        # Try to determine job category (blue/white/grey-collar)
        blue_collar_keywords = [
            r"(?i)(manufacturing|factory|construction|maintenance|technician|mechanic|electrician|plumber|driver|operator|laborer|warehouse|assembly)",
            r"(?i)(physical labor|trades|craft|repair|hands-on|mechanical|technical|installation|field service)"
        ]
        
        grey_collar_keywords = [
            r"(?i)(healthcare|nurse|medical|teacher|education|culinary|chef|hospitality|retail|service industry)",
            r"(?i)(firefighter|police|security|childcare|elder care|salon|cosmetology|customer service)"
        ]
        
        # First check for blue-collar
        for pattern in blue_collar_keywords:
            if re.search(pattern, text_content):
                job_data["job_category"] = "Blue-collar"
                break
                
        # Then check for grey-collar if not already categorized as blue-collar
        if job_data["job_category"] == "White-collar":  # default value
            for pattern in grey_collar_keywords:
                if re.search(pattern, text_content):
                    job_data["job_category"] = "Grey-collar"
                    break
        
        # If neither blue nor grey collar patterns are found, stick with the default white-collar
        
        # For description, extract a relevant portion of text
        # Look for sections that might contain job descriptions
        description_sections = re.findall(r"(?i)(job description|about the role|responsibilities|about the position)(.+?)(requirements|qualifications|about you|who you are|apply now|apply today)", text_content, re.DOTALL)
        if description_sections:
            job_data["description"] = description_sections[0][1].strip()
        else:
            # If no clear sections, take the first few paragraphs
            paragraphs = text_content.split('\n\n')
            job_data["description"] = '\n\n'.join(paragraphs[1:min(4, len(paragraphs))])
        
        # Extract requirements section
        requirements_sections = re.findall(r"(?i)(requirements|qualifications|what you'll need|what we're looking for|who you are)(.+?)(benefits|perks|why join|how to apply|apply now)", text_content, re.DOTALL)
        if requirements_sections:
            job_data["requirements"] = requirements_sections[0][1].strip()
        
        # Use the original URL as application URL if no specific one is found
        job_data["application_url"] = url
        
        # Clean up and limit long text fields
        for field in ["description", "requirements"]:
            if len(job_data[field]) > 2000:
                job_data[field] = job_data[field][:2000] + "..."
        
        return job_data
        
    except Exception as e:
        logging.error(f"Error extracting job details: {str(e)}")
        return {"error": f"Could not extract job details: {str(e)}", "source_url": url}


def fallback_extraction(url):
    """
    Fallback method to extract basic information when the main method fails.
    Uses BeautifulSoup for direct HTML parsing.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title from page title or h1
        title = soup.title.string if soup.title else ""
        if not title or len(title) > 100:
            h1_tag = soup.find('h1')
            title = h1_tag.text.strip() if h1_tag else "Job Position"
        
        # Extract text content
        paragraphs = soup.find_all('p')
        content = " ".join([p.text for p in paragraphs[:5]])
        
        return {
            "title": title[:100],
            "company": "",
            "location": "Remote",
            "description": content[:500],
            "requirements": "",
            "salary_range": "",
            "application_url": url,
            "job_type": "Full-time",
            "job_category": "White-collar",
            "source_url": url
        }
    except Exception as e:
        logging.error(f"Fallback extraction failed: {str(e)}")
        return {
            "title": "Unknown Position",
            "company": "",
            "location": "Remote",
            "description": "Could not extract job details. Please fill in the information manually.",
            "requirements": "",
            "salary_range": "",
            "application_url": url,
            "job_type": "Full-time",
            "job_category": "White-collar",
            "source_url": url
        }
