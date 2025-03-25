"""
Test script for job extraction functionality
"""
import sys
import json
from web_scraper import extract_job_details, is_valid_url

def test_extraction():
    """
    Simple test to verify job extraction functionality works
    """
    # Sample job posting URL
    url = "https://stackoverflow.com/jobs/123456/software-developer-remote"
    
    if not is_valid_url(url):
        print("Invalid URL format")
        sys.exit(1)
    
    print(f"Extracting job details from: {url}")
    result = extract_job_details(url)
    
    print("\nExtraction Results:")
    print(f"Success: {result['success']}")
    
    if result['success']:
        job = result['job']
        print(f"Title: {job.get('title', 'Not found')}")
        print(f"Company: {job.get('company', 'Not found')}")
        print(f"Location: {job.get('location', 'Not found')}")
        print(f"Job Type: {job.get('job_type', 'Not found')}")
        print(f"Category: {job.get('category', 'Not found')}")
        print(f"Subcategory: {job.get('subcategory', 'Not found')}")
        
        # Print first 100 chars of description
        description = job.get('description', '')
        print(f"Description: {description[:100]}..." if description else "Description: Not found")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result['success']

if __name__ == "__main__":
    test_extraction()