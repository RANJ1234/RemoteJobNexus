#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the super minimal application
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 10 super_minimal:app