"""
Simplest possible Flask application for the Remote Work Job Board
This file contains absolutely minimal code to ensure fast startup
"""
from flask import Flask, jsonify

# Create the application with minimal configuration
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    """Simple homepage"""
    return "<html><body><h1>Remote Work Job Board</h1><p>Starting up...</p></body></html>"

# No conditional execution block to reduce parsing time