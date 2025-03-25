#!/bin/bash
# Simple server launcher for Remote Work Job Board

# Make sure we're using UTF-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=job_api.py

# Start the server
echo "Starting Remote Work Job Board server..."
exec python job_api.py