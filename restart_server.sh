#!/bin/bash

# Kill any existing gunicorn processes
pkill -f gunicorn || true

# Start the minimal stable version
gunicorn --bind 0.0.0.0:5000 minimal_stable:app