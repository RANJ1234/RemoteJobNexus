import os
import logging
from flask import Flask, render_template, jsonify

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an absolute minimal application for fast startup
app = Flask(__name__)

# Simple route to respond immediately
@app.route('/')
def index():
    return render_template('maintenance.html')

# API endpoint for status check
@app.route('/api/status')
def status():
    return jsonify({
        "status": "running",
        "message": "Application is starting. Please wait a moment.",
        "version": "1.0"
    })

# Health check endpoint for the workflow
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# Make sure we have a loading template
if not os.path.exists('templates/loading.html'):
    os.makedirs('templates', exist_ok=True)
    with open('templates/loading.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Loading Remote Work</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #333;
        }
        .loading-container {
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        h1 {
            margin-top: 0;
            color: #2c3e50;
        }
        .spinner {
            width: 70px;
            text-align: center;
            margin: 2rem auto;
        }
        .spinner > div {
            width: 18px;
            height: 18px;
            background-color: #3498db;
            border-radius: 100%;
            display: inline-block;
            animation: sk-bouncedelay 1.4s infinite ease-in-out both;
            margin: 0 4px;
        }
        .spinner .bounce1 {
            animation-delay: -0.32s;
        }
        .spinner .bounce2 {
            animation-delay: -0.16s;
        }
        @keyframes sk-bouncedelay {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }
        .message {
            margin-bottom: 1rem;
            font-size: 16px;
        }
        .progress {
            height: 6px;
            background-color: #eee;
            border-radius: 4px;
            margin: 1.5rem 0;
            overflow: hidden;
        }
        .progress-bar {
            width: 0%;
            height: 100%;
            background-color: #3498db;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="loading-container">
        <h1>Remote Work</h1>
        <p class="message">The application is starting up...</p>
        <div class="spinner">
            <div class="bounce1"></div>
            <div class="bounce2"></div>
            <div class="bounce3"></div>
        </div>
        <div class="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        <p id="statusMessage">Initializing components...</p>
    </div>

    <script>
        // Check load status and redirect when ready
        let progress = 10;
        let isRedirecting = false;
        
        function updateProgress() {
            if (progress < 90) {
                progress += Math.random() * 5;
                document.getElementById('progressBar').style.width = progress + '%';
            }
        }
        
        function checkStatus() {
            if (isRedirecting) return;
            
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.loaded) {
                        progress = 100;
                        document.getElementById('progressBar').style.width = '100%';
                        document.getElementById('statusMessage').textContent = 'Application ready! Redirecting...';
                        isRedirecting = true;
                        
                        // Redirect to home page
                        setTimeout(() => {
                            window.location.href = '/home';
                        }, 500);
                    } else {
                        updateProgress();
                        setTimeout(checkStatus, 1000);
                    }
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                    document.getElementById('statusMessage').textContent = 'Error connecting to server...';
                    setTimeout(checkStatus, 2000);
                });
        }
        
        // Start checking
        updateProgress();
        setTimeout(checkStatus, 1000);
    </script>
</body>
</html>
        """)

# This is the application that will be served by Gunicorn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)