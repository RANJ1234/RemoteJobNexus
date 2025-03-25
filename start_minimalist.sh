#!/bin/bash

# Kill any existing Python processes
pkill -f python || true

# Start the minimalist Flask app directly
python minimalist.py