#!/usr/bin/env python3
"""
Standalone server entry point for the Remote Work Job Board.
This file provides a clean, direct way to start the server without dependence on
external workflow configurations.
"""
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('job_board')
logger.info("Starting Remote Work Job Board application...")

# Import the Flask application from job_api
try:
    from job_api import app
    
    # Start the Flask application
    if __name__ == "__main__":
        logger.info("Starting web server on port 5000...")
        app.run(host="0.0.0.0", port=5000, debug=True)
except Exception as e:
    logger.error(f"Failed to start application: {e}")
    raise