#!/usr/bin/env python3
"""
Reliable workflow entry point for the Remote Work Job Board
"""
import os
import sys
import subprocess
import time


def start_server():
    """Start the job_api.py server in the foreground"""
    print("Starting Remote Work Job Board server...")
    
    # Execute job_api.py directly
    try:
        subprocess.run([sys.executable, "job_api.py"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to start the server")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
        sys.exit(0)


if __name__ == "__main__":
    # Start the server
    start_server()