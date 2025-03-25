"""
Super minimal Flask application that should start up very quickly.
"""
import flask

# Create the application without any dependencies
app = flask.Flask(__name__)

@app.route('/')
def index():
    """Simple homepage"""
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
            <p>Starting up...</p>
            <p>Minimal server active. <a href="/health">Check health</a></p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# Flask runs directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)