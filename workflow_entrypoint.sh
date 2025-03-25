#!/bin/bash
# This script serves as the entry point for Replit workflows
# It ensures the Flask server starts correctly

set -e  # Exit on error
set -u  # Treat unset variables as an error

# Print status message
echo "Starting Remote Work Job Board server..."

# Run the Python entry point
exec python3 entrypoint.py