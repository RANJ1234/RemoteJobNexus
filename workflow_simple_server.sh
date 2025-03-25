#!/bin/bash

# Kill any existing Python processes
pkill -f python || true

# Start the simple server which will listen immediately on port 5000
exec python simple_server.py