"""
Minimal stable Flask application for Remote Work Job Board.
This version is designed to start quickly and reliably with minimal dependencies.
"""
from flask import Flask, render_template_string, jsonify

# Create app outside any function for Gunicorn
app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    """Simple homepage"""
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Remote Work Job Board</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    max-width: 800px;
                    margin: 0 auto;
                }
                h1 { color: #4a6ee0; }
                .status { 
                    margin: 20px 0;
                    padding: 15px;
                    background: #f0f4ff;
                    border-radius: 8px;
                }
                .message {
                    margin-top: 30px;
                    color: #555;
                }
            </style>
        </head>
        <body>
            <h1>Remote Work Job Board</h1>
            <div class="status">
                <p>✅ Server is running</p>
            </div>
            <div class="message">
                <p>Welcome to the Remote Work Job Board</p>
                <p>The full application will be available momentarily.</p>
            </div>
        </body>
    </html>
    """
    return render_template_string(html)

# For direct execution (not needed by Gunicorn)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)