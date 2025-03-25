"""
Ultra minimalist Flask application for Remote Work Job Board
"""
from flask import Flask

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
                    <p>✅ Minimal Server is running</p>
                </div>
                <p>Welcome to the Remote Work Job Board. This is a minimal server.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return '{"status":"ok"}'

if __name__ == '__main__':
    # Only bind to 0.0.0.0 if running in production
    app.run(host='0.0.0.0', port=5000)