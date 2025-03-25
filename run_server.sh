#!/bin/bash
# Simple server launcher for Remote Work Job Board

# Make sure we're using UTF-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=job_api.py

# Kill any existing processes on port 8080
pkill -f "python.*job_api.py" || true

# Start the server
echo "Starting Remote Work Job Board server on port 8080..."
exec python job_api.py