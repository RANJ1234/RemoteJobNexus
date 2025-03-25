#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the minimal application with a single worker and short timeout
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 8 --timeout 30 minimal_app:app