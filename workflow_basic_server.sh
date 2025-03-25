#!/bin/bash

# Kill any existing Python processes
pkill -f python || true

# Start the basic server directly with Python
python3 basic_server.py