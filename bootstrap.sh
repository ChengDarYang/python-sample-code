#!/bin/bash

# Bootstrap script for Python Flask application
# This script installs dependencies and starts the server

echo "🚀 Starting bootstrap process..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Python3 and pip3 are available"

# Install requirements
echo "📦 Installing requirements from requirements.txt..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Start the server
echo "🌐 Starting Flask server..."
python3 server.py
