"""
Bootstrap application for Remote Work Job Board.
This script starts a minimal server immediately and then gradually loads the full application.
"""
import os
import logging
import threading
import time
import socket
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a minimal Flask application
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Track application state
APP_STATE = {
    'status': 'starting',
    'message': 'Initial bootstrap server started',
    'ready': False,
    'full_app_started': False,
    'database_ready': False,
    'errors': []
}

def start_full_application():
    """Start the full application in the background"""
    global APP_STATE
    
    try:
        APP_STATE['status'] = 'loading'
        APP_STATE['message'] = 'Loading full application...'
        
        time.sleep(2)  # Give the bootstrap server time to respond to health checks
        
        # Start the actual application server
        logger.info("Starting full application...")
        
        # Use Python's subprocess module to start Gunicorn with the real application
        cmd = [
            "gunicorn", 
            "--bind", "127.0.0.1:5001",  # Use a different port
            "--workers", "1", 
            "--timeout", "30",
            "replit_main:app"  # Use the minimal app we created earlier
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the port to be accessible
        for i in range(30):  # Try for 30 seconds
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", 5001))
                    logger.info("Full application started successfully")
                    APP_STATE['full_app_started'] = True
                    APP_STATE['status'] = 'ready'
                    APP_STATE['message'] = 'Full application is running'
                    APP_STATE['ready'] = True
                    break
            except:
                time.sleep(1)
        
        # Check if we were successful
        if not APP_STATE['full_app_started']:
            error_msg = "Failed to start full application"
            APP_STATE['errors'].append(error_msg)
            APP_STATE['status'] = 'error'
            APP_STATE['message'] = error_msg
            logger.error(error_msg)
            
    except Exception as e:
        error_msg = f"Error starting full application: {str(e)}"
        APP_STATE['errors'].append(error_msg)
        APP_STATE['status'] = 'error'
        APP_STATE['message'] = error_msg
        logger.error(error_msg)

# Routes for the bootstrap application
@app.route('/')
def index():
    """Homepage that shows current app status"""
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Remote Work Job Board</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background-color: #f8f9fa;
                    color: #333;
                }
                .container { 
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { 
                    color: #4a6ee0; 
                    margin-bottom: 20px;
                }
                .loading {
                    margin: 20px auto;
                    width: 50px;
                    height: 50px;
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #4a6ee0;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                p {
                    line-height: 1.6;
                    margin-bottom: 15px;
                }
                .status {
                    font-weight: bold;
                    margin-top: 20px;
                }
                .ready { color: #4CAF50; }
                .loading-text { color: #FFA500; }
                .error { color: #F44336; }
                .btn {
                    display: inline-block;
                    background-color: #4a6ee0;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 15px;
                    transition: background-color 0.3s;
                }
                .btn:hover {
                    background-color: #3a5bca;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Remote Work Job Board</h1>
                
                <div id="loading-spinner" class="loading" style="display: {{ 'block' if status != 'ready' else 'none' }}"></div>
                
                <p id="message">{{ message }}</p>
                
                <p class="status {{ 'ready' if status == 'ready' else 'loading-text' if status == 'loading' else 'error' if status == 'error' else '' }}">
                    Status: {{ status }}
                </p>
                
                {% if errors %}
                <div class="errors">
                    <h3>Errors:</h3>
                    <ul>
                        {% for error in errors %}
                        <li class="error">{{ error }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                <a href="/status" class="btn">Check Status</a>
                
                <script>
                    // Check status every 2 seconds if not ready
                    {% if status != 'ready' %}
                    setInterval(async () => {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
                        document.getElementById('message').textContent = data.message;
                        
                        const statusElem = document.querySelector('.status');
                        statusElem.textContent = 'Status: ' + data.status;
                        statusElem.className = 'status';
                        
                        if (data.status === 'ready') {
                            statusElem.classList.add('ready');
                            document.getElementById('loading-spinner').style.display = 'none';
                            setTimeout(() => {
                                window.location.href = '/';
                            }, 1000);
                        } else if (data.status === 'loading') {
                            statusElem.classList.add('loading-text');
                        } else if (data.status === 'error') {
                            statusElem.classList.add('error');
                        }
                    }, 2000);
                    {% endif %}
                </script>
            </div>
        </body>
    </html>
    """
    return render_template_string(
        html, 
        status=APP_STATE['status'],
        message=APP_STATE['message'],
        errors=APP_STATE['errors']
    )

@app.route('/status')
def status():
    """API endpoint for checking application status"""
    return jsonify(APP_STATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

# Start the background thread to load the full application
thread = threading.Thread(target=start_full_application)
thread.daemon = True
thread.start()

# For direct execution
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)