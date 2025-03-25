#!/bin/bash

# Start the Flask app with no database dependencies
gunicorn --bind 0.0.0.0:5000 no_db_main:app