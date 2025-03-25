"""
Super minimal Flask application that should start up very quickly.
"""
from flask import Flask

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Simple homepage"""
    return """
    <html>
        <head>
            <title>Remote Work Job Board</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .container { text-align: center; padding: 20px; }
                h1 { color: #4a6ee0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Remote Work Job Board</h1>
                <p>The application is starting up. Please refresh in a moment.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Remote Work Job Board API is running"}, 200

# For direct execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)