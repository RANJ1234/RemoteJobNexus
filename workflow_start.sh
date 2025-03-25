#!/bin/bash

# Kill any existing gunicorn processes
pkill gunicorn || true
sleep 2

# Run Flask application with gunicorn
gunicorn --bind 0.0.0.0:5000 --reload main:app