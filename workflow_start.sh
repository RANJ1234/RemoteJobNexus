#!/bin/bash
# This script is used to start the application using Gunicorn

# Run the application with Gunicorn
exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app