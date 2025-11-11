#!/bin/bash
# MCP X Server startup script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the server
python -m src.server
