#!/bin/bash
# Start script for production deployment
# This ensures gunicorn is available and starts the server

# Check if gunicorn is installed, if not install it
if ! command -v gunicorn &> /dev/null && ! python -m gunicorn --version &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Start the server
if command -v gunicorn &> /dev/null; then
    gunicorn server:app --bind 0.0.0.0:${PORT:-5000}
else
    python -m gunicorn server:app --bind 0.0.0.0:${PORT:-5000}
fi

