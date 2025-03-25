#!/usr/bin/env python3
"""
Simple launcher for the Remote Work Job Board
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('job_board_launcher')
logger.info("Starting Remote Work Job Board launcher...")

# Import the Flask application from job_api
try:
    # Import the Flask app
    from job_api import app
    
    # Start the Flask application
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Starting web server on port {port}...")
        app.run(host="0.0.0.0", port=port, debug=True)
except Exception as e:
    logger.error(f"Failed to start application: {e}")
    raise