#!/bin/bash
# Use the minimal test server for quick startup
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload test_server:app
