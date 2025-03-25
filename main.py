
import os
from flask import Flask

# Create a minimal app initially for quick startup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Basic route to show the app is running
@app.route('/')
def quick_start():
    return """
    <html>
    <head>
        <title>Remote Work - Loading...</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; }
            .loading { animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
        </style>
        <script>
            // Redirect to real app after brief delay
            setTimeout(function() {
                window.location.href = '/loading_complete';
            }, 1000);
        </script>
    </head>
    <body>
        <h1 class="loading">Remote Work</h1>
        <p>Starting application...</p>
    </body>
    </html>
    """

# This will create a separate worker thread to import and initialize the full app
# outside of the request processing path, allowing the server to respond immediately
import threading
def load_full_app():
    global app
    
    # Import the full app after responding to initial requests
    from app import app as full_app
    import routes
    
    # Replace the minimal app with the fully loaded app
    app = full_app
    
    # Add a route to check when loading is complete
    @app.route('/loading_complete')
    def loading_complete():
        return """
        <html>
        <head>
            <title>Remote Work - Ready</title>
            <meta http-equiv="refresh" content="0;url=/">
        </head>
        <body>
            <p>Application loaded. Redirecting...</p>
        </body>
        </html>
        """

# Start loading the full app in a background thread
threading.Thread(target=load_full_app, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
