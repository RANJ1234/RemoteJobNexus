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
                body { font-family: Arial, sans-serif; margin: 0; padding: 50px; background-color: #f8f9fa; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #4a6ee0; text-align: center; }
                p { line-height: 1.6; color: #333; }
                .status { text-align: center; margin: 20px 0; padding: 10px; background: #e8f5e9; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Remote Work Job Board</h1>
                <div class="status">
                    <p>✅ Server is running</p>
                </div>
                <p>Welcome to the Remote Work Job Board. The application is starting up and will be ready in a moment.</p>
                <p>This is a super minimal version that should start very quickly.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}', 200, {'Content-Type': 'application/json'}

# For direct execution
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)