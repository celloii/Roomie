#!/bin/bash
# Build script for Render deployment
set -e

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Verifying gunicorn installation..."
python -m pip show gunicorn || pip install gunicorn

echo "Build complete!"

