#!/usr/bin/env python3
"""
Simple Flask application for Remote Job Nexus
"""
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Remote Job Nexus</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #2c3e50; }
            .container { max-width: 800px; margin: 0 auto; }
            .success { color: #27ae60; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Remote Job Nexus</h1>
            <p class="success">✓ Python application successfully deployed!</p>
            <p>This is a simple Python application deployed on Razorhost.</p>
            <p>The deployment was completed using a simplified method for beginners.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)