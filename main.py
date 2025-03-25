import os
from flask import Flask, render_template, jsonify, request

# Create a minimal but functional Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

@app.route('/')
def index():
    """Maintenance page or redirect to the main application once loaded"""
    return render_template('maintenance.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "The application is running"}), 200

@app.route('/api/status')
def api_status():
    """API status endpoint for frontend to poll"""
    return jsonify({
        "status": "maintenance",
        "message": "The application is starting up",
        "version": "1.0.0",
        "timestamp": None
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)