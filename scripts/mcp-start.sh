#!/bin/bash
# MCP X Server startup script with proper directory handling
cd "$(dirname "$0")/.."
source venv/bin/activate
exec python -m src.server
