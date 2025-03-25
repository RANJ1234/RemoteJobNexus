from flask import Flask, redirect, url_for, jsonify, render_template_string

# Create a minimal app instance that starts immediately
app = Flask(__name__)

# Simple key to identify this is the quick server
app.config['QUICK_SERVER'] = True

# Global variables to track loading status
LOADING_COMPLETE = False
REAL_APP = None
LOADING_ERROR = None

# Basic loading page route
@app.route('/')
def loading_page():
    global LOADING_COMPLETE, REAL_APP, LOADING_ERROR
    
    if LOADING_ERROR:
        # Show error if loading failed
        return render_template_string("""
        <html>
        <head>
            <title>Remote Work - Error</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; background-color: #f8f9fa; }
                .error { color: #dc3545; margin: 20px 0; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Remote Work</h1>
                <div class="error">
                    <h2>Error Loading Application</h2>
                    <p>{{ error }}</p>
                </div>
                <p>Please try refreshing the page or contact support if the problem persists.</p>
            </div>
        </body>
        </html>
        """, error=LOADING_ERROR)
    
    elif LOADING_COMPLETE and REAL_APP:
        # Redirect to the real app's home page when loading is complete
        return redirect('/home')
    else:
        # Show loading screen
        return render_template_string("""
        <html>
        <head>
            <title>Remote Work - Loading</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 100px; background-color: #f8f9fa; }
                .loading { margin: 20px 0; }
                .spinner { display: inline-block; width: 50px; height: 50px; border: 3px solid rgba(0,0,0,.1); border-radius: 50%; border-top-color: #3498db; animation: spin 1s ease-in-out infinite; }
                @keyframes spin { to { transform: rotate(360deg); } }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            </style>
            <script>
                // Auto-refresh every 2 seconds to check loading status
                setTimeout(function() { 
                    fetch('/loading-status')
                        .then(response => response.json())
                        .then(data => {
                            if (data.complete) {
                                window.location.href = '/';
                            } else {
                                // Refresh page if still loading
                                setTimeout(function() { 
                                    window.location.reload(); 
                                }, 2000);
                            }
                        });
                }, 1000);
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Remote Work</h1>
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Starting application... This may take a moment.</p>
                </div>
                <p>Loading your Remote Work job platform...</p>
            </div>
        </body>
        </html>
        """)

# Status API endpoint for the frontend to check
@app.route('/loading-status')
def loading_status():
    return jsonify({
        'complete': LOADING_COMPLETE,
        'error': LOADING_ERROR
    })

# Home route - only available after full app loads
@app.route('/home')
def home_redirect():
    if LOADING_COMPLETE and REAL_APP:
        return redirect('/')
    else:
        return redirect(url_for('loading_page'))

# Start loading the full app in a background thread
import threading
def load_full_application():
    global LOADING_COMPLETE, REAL_APP, LOADING_ERROR, app
    
    try:
        # Import the full app inside this function to avoid immediate loading
        import logging
        logging.basicConfig(level=logging.WARNING)  # Minimize logging during load
        
        import routes  # This will trigger the full app initialization
        from app import app as full_app
        
        # Replace routes in the quick app with the full app's routes
        REAL_APP = full_app
        
        # Register a special route to handle the transition
        @app.route('/<path:path>')
        def catch_all(path):
            if LOADING_COMPLETE:
                # Forward to the equivalent route in the full app
                return redirect(f'/{path}')
            else:
                return redirect(url_for('loading_page'))
        
        # Mark loading as complete
        LOADING_COMPLETE = True
        
    except Exception as e:
        # Capture any loading errors
        import traceback
        LOADING_ERROR = f"Error loading application: {str(e)}\n{traceback.format_exc()}"
        print(f"Error in background loading: {LOADING_ERROR}")

# Start the background loading thread
loading_thread = threading.Thread(target=load_full_application, daemon=True)
loading_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)