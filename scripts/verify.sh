#!/bin/bash
# Verification script for MCP X Server

echo "MCP X Server Verification"
echo "=========================="

# Check Python version
echo -n "Python version: "
python3 --version

# Check virtual environment
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
else
    echo "✗ Virtual environment not found"
    exit 1
fi

# Check cookies file
if [ -f "config/cookies.json" ]; then
    echo "✓ Cookies file exists"
else
    echo "✗ Cookies file not found"
    exit 1
fi

# Run tests
echo ""
echo "Running tests..."
python tests/test_server.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ MCP X Server is ready!"
    echo ""
    echo "Next steps:"
    echo "  1. Run server: ./scripts/run.sh"
    echo "  2. Add to Claude Code:"
    echo "     claude mcp add mcp-x-server python -m src.server --cwd $(pwd)"
else
    echo ""
    echo "✗ Verification failed"
    exit 1
fi
