"""
WSGI entry point for the Remote Work Job Board application.
This file provides a cleaner entry point for Gunicorn.
"""
from super_minimal import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)