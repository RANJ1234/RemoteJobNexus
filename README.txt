# Remote Job Nexus - Deployment Guide

## Files to Upload to cPanel
1. All Python files (especially minimal.py)
2. requirements.txt
3. passenger_wsgi.py
4. .htaccess
5. templates/ folder (if using Flask templates)
6. static/ folder (if using static assets)

## Deployment Steps
1. Upload all files to the "Remote hive" directory in your public_html folder
2. Set up a Python environment in cPanel (Python Selector)
3. Install dependencies: 
   - In cPanel Terminal, navigate to your app directory
   - Run: pip install -r requirements.txt
4. Set file permissions:
   - 644 for regular files (.py, .html, .css, .js)
   - 755 for directories and executable scripts (.sh)
5. Restart Python application in cPanel

## Testing
- Visit your domain in a browser to check if the app is running
- Default route should display "Remote Work Server OK"

## Troubleshooting
- Check error logs in cPanel
- Ensure Python version matches requirements (3.11+ recommended)
- Verify all dependencies are installed correctly 