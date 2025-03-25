#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 60 super_minimal:app