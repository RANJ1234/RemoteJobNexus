"""
Minimal Flask application that loads quickly and responds to health checks.
"""
import os
import logging
import threading

from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Create a flag to track when the database is ready
db_ready = False

# Set up routes
@app.route('/health')
def health():
    """Health check endpoint"""
    global db_ready
    status = "ok" if db_ready else "initializing"
    return jsonify({"status": status}), 200

@app.route('/')
def index():
    """Simple homepage that loads without database dependencies"""
    global db_ready
    
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
                <div class="loading" id="loading-spinner"></div>
                <p id="status-message">Welcome to the Remote Work Job Board!</p>
                <p>The application is starting up. Please wait a moment...</p>
                <a href="/health" class="btn">Check Health</a>
                
                <script>
                    // Check the database status every 2 seconds
                    const checkStatus = async () => {
                        try {
                            const response = await fetch('/health');
                            const data = await response.json();
                            
                            if (data.status === 'ok') {
                                // Database is ready, redirect to full application
                                document.getElementById('status-message').textContent = 'Database initialized! Redirecting...';
                                document.getElementById('loading-spinner').style.borderTopColor = '#4CAF50';
                                setTimeout(() => {
                                    window.location.href = '/';
                                }, 2000);
                            } else {
                                // Check again in 2 seconds
                                setTimeout(checkStatus, 2000);
                            }
                        } catch (error) {
                            console.error('Error checking status:', error);
                            setTimeout(checkStatus, 5000);
                        }
                    };
                    
                    // Start checking status
                    checkStatus();
                </script>
            </div>
        </body>
    </html>
    """
    return render_template_string(html)

def start_background_loading():
    """Start loading database and models in the background"""
    global db_ready
    
    try:
        # Import the delayed loader
        from delayed_loader import start_delayed_loading
        
        # Start the delayed loading process
        thread = start_delayed_loading(app)
        
        # Set a callback to update our db_ready flag when the thread completes
        def check_thread():
            thread.join(timeout=0.1)
            global db_ready
            if not thread.is_alive():
                db_ready = True
                logger.info("Database initialization complete")
            else:
                # Check again in 1 second
                threading.Timer(1.0, check_thread).start()
        
        # Start checking the thread status
        threading.Timer(1.0, check_thread).start()
        
    except Exception as e:
        logger.error(f"Error starting background loading: {e}")

# Start the background loading process when the app starts
start_background_loading()

# For direct execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)