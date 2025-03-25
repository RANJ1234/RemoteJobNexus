#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the optimized application
exec gunicorn --bind 0.0.0.0:5000 --reuse-port optimized_app:app