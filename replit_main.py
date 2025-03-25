"""
Ultra minimal Flask application for Replit
"""
from flask import Flask

# Create application
app = Flask(__name__)

@app.route('/')
def index():
    """Homepage"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Remote Work Job Board</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #4a6ee0; }
            </style>
        </head>
        <body>
            <h1>Remote Work Job Board</h1>
            <p>The application is starting up...</p>
            <p>Please wait or <a href="/health">check the health status</a>.</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# For direct execution
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)