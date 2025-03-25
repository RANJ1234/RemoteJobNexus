"""
API endpoints for the Remote Work Job Board job extraction feature
"""
import os
import json
from flask import Flask, request, jsonify, render_template
from web_scraper import is_valid_url, extract_job_details

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "remotework_secret_key")

@app.route('/')
def index():
    """Main homepage for the Remote Work Job Board"""
    return render_template('index.html')
    
@app.route('/job-extractor')
def job_extractor():
    """Job extraction tool page"""
    return render_template('job_extractor.html')
    
@app.route('/text-extractor')
def text_extractor():
    """Text extraction tool page"""
    return render_template('text_extractor.html')

@app.route('/api/extract-job', methods=['POST'])
def extract_job():
    """API endpoint to extract job details from a URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing URL parameter'
        }), 400
    
    url = data['url']
    
    if not is_valid_url(url):
        return jsonify({
            'success': False,
            'error': 'Invalid URL format'
        }), 400
    
    # Extract job details
    result = extract_job_details(url)
    
    return jsonify(result)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Start Flask application
    app.run(host='0.0.0.0', port=8080, debug=True)