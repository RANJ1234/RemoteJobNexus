#!/usr/bin/env python3
"""
Entry point for the Remote Work Job Board application.
This is a simple wrapper around job_api.py to ensure consistent startup.
"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('remote_work')

logger.info("Starting Remote Work Job Board application...")

# Make sure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Import and run the application from job_api
try:
    logger.info("Importing job_api module...")
    from job_api import app
    
    logger.info("Starting Flask server...")
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)
except Exception as e:
    logger.error(f"Error starting application: {e}")
    raise