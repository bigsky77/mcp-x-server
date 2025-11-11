#!/bin/bash
# Setup script for MCP X Server

echo "Setting up MCP X Server..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

# Check for cookies file
if [ ! -f "config/cookies.json" ]; then
    echo "WARNING: config/cookies.json not found!"
    echo "Please copy your cookies file to config/cookies.json"
fi

echo "Setup complete!"
echo "Run './scripts/run.sh' to start the server"
