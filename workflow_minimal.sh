#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the minimal application with delayed database loading
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 30 --preload minimal_app:app