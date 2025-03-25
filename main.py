"""
Main entry point for the Remote Work Job Board application.
This version is extremely optimized for faster startup in the Replit environment.
"""
import os
import logging

from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/')
def index():
    """Simple homepage that loads without database dependencies"""
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
                <div class="loading"></div>
                <p>Welcome to the Remote Work Job Board! The application is starting up.</p>
                <p>Please wait a moment while we initialize the job database...</p>
                <a href="/health" class="btn">Check Health</a>
                
                <script>
                    // Auto-refresh the page after 10 seconds
                    setTimeout(() => {
                        window.location.reload();
                    }, 10000);
                </script>
            </div>
        </body>
    </html>
    """
    return render_template_string(html)

# For direct execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)