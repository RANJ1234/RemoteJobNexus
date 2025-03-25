#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the tiny server directly with Python
python3 tiny_server.py