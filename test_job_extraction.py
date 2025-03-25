"""
Test script for job extraction functionality
"""
import sys
import json
import os
import re
from bs4 import BeautifulSoup
from web_scraper import extract_job_from_json_ld, is_valid_url

def test_local_extraction():
    """
    Test extraction using a local HTML file to avoid 403 errors from job sites
    """
    # Path to test HTML file
    html_file = "test_job_posting.html"
    
    if not os.path.exists(html_file):
        print(f"Test file not found: {html_file}")
        sys.exit(1)
    
    print(f"Extracting job details from local file: {html_file}")
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Test the JSON-LD extraction
    print("\nTesting JSON-LD Extraction:")
    json_ld_data = extract_job_from_json_ld(html_content)
    
    if json_ld_data:
        print("✓ Successfully extracted structured data")
        print(f"Title: {json_ld_data.get('title', 'Not found')}")
        print(f"Company: {json_ld_data.get('company', 'Not found')}")
        print(f"Location: {json_ld_data.get('location', 'Not found')}")
        print(f"Job Type: {json_ld_data.get('job_type', 'Not found')}")
        print(f"Salary: {json_ld_data.get('salary', 'Not found')}")
        
        # Print first 100 chars of description
        description = json_ld_data.get('description', '')
        print(f"Description: {description[:100]}..." if description else "Description: Not found")
    else:
        print("× Failed to extract JSON-LD data")
    
    # Test the HTML parsing extraction
    print("\nTesting HTML Parsing:")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract basic data using BeautifulSoup
    title = soup.title.get_text() if soup.title else "Not found"
    company = soup.select_one('.company-info h2')
    company = company.get_text() if company else "Not found"
    
    job_description = soup.select_one('#job-description')
    description = job_description.get_text() if job_description else "Not found"
    
    requirements = soup.select_one('#requirements')
    requirements = requirements.get_text() if requirements else "Not found"
    
    print(f"Title: {title}")
    print(f"Company: {company}")
    print(f"Description: {description[:100]}..." if len(description) > 100 else description)
    print(f"Requirements: {requirements[:100]}..." if len(requirements) > 100 else requirements)
    
    return True

if __name__ == "__main__":
    test_local_extraction()