"""
Startup script for the Remote Work Job Board application.
This script initializes the Flask application and handles the gradual loading of components.
"""
import os
import logging
import threading
import time

from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Global state for application components
app_state = {
    "db_ready": False,
    "templates_ready": False,
    "full_app_ready": False
}

# Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "components": {
            "db": app_state["db_ready"],
            "templates": app_state["templates_ready"],
            "full_app": app_state["full_app_ready"]
        }
    }), 200

@app.route('/')
def index():
    """Homepage with loading indicator"""
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
                .status {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #f8f9fa;
                }
                .status .component {
                    display: inline-block;
                    margin: 5px 10px;
                }
                .status .label {
                    font-weight: bold;
                    margin-right: 5px;
                }
                .status .pending {
                    color: #ffc107;
                }
                .status .ready {
                    color: #28a745;
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
                <p>Welcome to the Remote Work Job Board! The application is starting up.</p>
                <p id="status-message">Please wait while we initialize all components...</p>
                
                <div class="status">
                    <div class="component">
                        <span class="label">Database:</span>
                        <span id="db-status" class="pending">Loading...</span>
                    </div>
                    <div class="component">
                        <span class="label">Templates:</span>
                        <span id="templates-status" class="pending">Loading...</span>
                    </div>
                    <div class="component">
                        <span class="label">Full App:</span>
                        <span id="app-status" class="pending">Loading...</span>
                    </div>
                </div>
                
                <a href="/health" class="btn">Check Health</a>
                
                <script>
                    // Check the application status every 2 seconds
                    const checkStatus = async () => {
                        try {
                            const response = await fetch('/health');
                            const data = await response.json();
                            
                            // Update component status indicators
                            if (data.components.db) {
                                document.getElementById('db-status').textContent = 'Ready';
                                document.getElementById('db-status').className = 'ready';
                            }
                            
                            if (data.components.templates) {
                                document.getElementById('templates-status').textContent = 'Ready';
                                document.getElementById('templates-status').className = 'ready';
                            }
                            
                            if (data.components.full_app) {
                                document.getElementById('app-status').textContent = 'Ready';
                                document.getElementById('app-status').className = 'ready';
                                document.getElementById('status-message').textContent = 'Application fully loaded! Please refresh the page.';
                                document.getElementById('loading-spinner').style.borderTopColor = '#28a745';
                                // Refresh after a short delay
                                setTimeout(() => {
                                    window.location.reload();
                                }, 3000);
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

def initialize_database():
    """Initialize database and models in the background"""
    logger.info("Starting database initialization")
    
    try:
        # Sleep a bit to simulate database initialization
        time.sleep(1)
        
        # Configure database connection
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        
        # Import and initialize flask-sqlalchemy
        from flask_sqlalchemy import SQLAlchemy
        from sqlalchemy.orm import DeclarativeBase
        
        class Base(DeclarativeBase):
            pass
        
        # Create db instance
        db = SQLAlchemy(model_class=Base)
        db.init_app(app)
        
        # We need to push an application context to work with the database
        with app.app_context():
            # Now import models after db is initialized
            import models
            
            # Create tables
            db.create_all()
            logger.info("Database tables created successfully")
            
        # Mark the database as ready
        app_state["db_ready"] = True
        logger.info("Database initialization complete")
        
        # Initialize templates after database is ready
        initialize_templates()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def initialize_templates():
    """Initialize templates and static files"""
    logger.info("Starting templates initialization")
    
    try:
        # Sleep a bit to simulate template loading
        time.sleep(1)
        
        # Mark templates as ready
        app_state["templates_ready"] = True
        logger.info("Templates initialization complete")
        
        # Now that all components are ready, initialize the full application
        initialize_full_application()
        
    except Exception as e:
        logger.error(f"Error initializing templates: {e}")

def initialize_full_application():
    """Initialize the full application with all routes and features"""
    logger.info("Starting full application initialization")
    
    try:
        # Sleep a bit to simulate full application initialization
        time.sleep(1)
        
        # Mark the full application as ready
        app_state["full_app_ready"] = True
        logger.info("Full application initialization complete")
        
    except Exception as e:
        logger.error(f"Error initializing full application: {e}")

def start_initialization():
    """Start the background initialization process"""
    thread = threading.Thread(target=initialize_database)
    thread.daemon = True
    thread.start()
    logger.info("Background initialization started")

# Start the initialization process in the background
start_initialization()

# For direct execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)