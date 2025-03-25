#!/usr/bin/env python3
"""
Test script for the job scraper functionality
"""
import sys
import json
import argparse
from web_scraper import test_extraction, is_valid_url

def main():
    """Main function to run the job scraper test"""
    parser = argparse.ArgumentParser(description='Extract job details from a URL')
    parser.add_argument('url', nargs='?', help='URL of the job posting to scrape')
    args = parser.parse_args()
    
    # Get URL from command line or prompt user
    url = args.url
    if not url:
        url = input("Enter the URL of a job posting: ")
        
    # Validate URL
    if not is_valid_url(url):
        print(f"Error: '{url}' is not a valid URL")
        return 1
        
    print(f"\nExtracting job details from: {url}")
    print("This may take a few seconds...\n")
    
    # Extract job details
    result = test_extraction(url)
    
    # Print results
    if result.get('extracted_successfully'):
        print("✅ Successfully extracted job details:\n")
        # Print job details in a readable format
        print(f"Title: {result['title']}")
        print(f"Company: {result['company']}")
        print(f"Location: {result['location']}")
        
        if result['job_type']:
            print(f"Job Type: {result['job_type']}")
            
        if result['category']:
            print(f"Category: {result['category']}")
            
        if result['subcategory']:
            print(f"Subcategory: {result['subcategory']}")
            
        if result['salary']:
            print(f"Salary: {result['salary']}")
            
        print("\nDescription Preview:")
        print(f"{result['description_preview']}")
        
        if result['requirements_preview']:
            print("\nRequirements Preview:")
            print(f"{result['requirements_preview']}")
            
        print("\nFull data (JSON format):")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to extract job details")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())