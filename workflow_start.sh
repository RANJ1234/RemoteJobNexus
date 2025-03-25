#!/bin/bash
# Run Flask application with gunicorn
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app