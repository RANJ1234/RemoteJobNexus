#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the simplest version directly with Python
python3 simplest.py