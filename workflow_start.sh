#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the application
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 30 --preload app_wsgi:app