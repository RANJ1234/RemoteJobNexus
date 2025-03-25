#!/bin/bash

# Kill any existing Python or Gunicorn processes
pkill -f gunicorn || true
pkill -f "python" || true

# Start the bootstrap server - the key is to start with simplest possible server
exec python bootstrap.py