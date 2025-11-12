# MCP X Server - Installation Guide

This guide shows you how to install and run the MCP X Server in any directory.

## Prerequisites

- Python 3.10 or higher
- Claude Code CLI installed
- X (Twitter) account cookies

## Installation Steps

### 1. Clone the Repository

```bash
# Clone to your desired location
git clone https://github.com/bigsky77/mcp-x-server.git
cd mcp-x-server
```

### 2. Run Setup Script

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Check for cookies configuration

```bash
./scripts/setup.sh
```

### 3. Configure X (Twitter) Cookies

You need to extract cookies from your browser while logged into X (Twitter):

**Option 1: Using Browser Extension (Recommended)**
1. Install "EditThisCookie" (Chrome) or "Cookie Quick Manager" (Firefox)
2. Log into twitter.com/x.com
3. Export cookies as JSON
4. Save to `config/cookies.json`

**Option 2: Manual Copy**
```bash
# Copy the example file
cp config/cookies.example.json config/cookies.json

# Edit and add your cookies
# You need: auth_token, ct0, guest_id
```

Required cookies:
- `auth_token` - Your authentication token
- `ct0` - CSRF token
- `guest_id` - Guest ID (if applicable)

### 4. Add to Claude Code

The correct command syntax is:

```bash
# Make sure you're in the mcp-x-server directory
cd /path/to/mcp-x-server

# Add using the virtual environment's Python
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

**Why this syntax?**
- `$(pwd)/venv/bin/python` - Uses the virtual environment's Python with all dependencies
- `-m src.server` - Runs the server as a Python module
- No `--cwd` flag needed - the venv Python knows where to find modules

### 5. Verify Installation

```bash
# List MCP servers
claude mcp list

# You should see mcp-x-server in the list
```

### 6. Test the Server

```bash
# From another terminal, test a simple tool
claude mcp call mcp-x-server search_tweets '{"query":"AI", "limit":1}'
```

If you see tweet results, everything is working!

## Alternative Installation Methods

### Method 1: Using Shell Script Wrapper

Create a startup script that activates the venv:

```bash
# Create scripts/mcp-start.sh
cat > scripts/mcp-start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
python -m src.server
EOF

# Make executable
chmod +x scripts/mcp-start.sh

# Add to Claude
claude mcp add mcp-x-server "$(pwd)/scripts/mcp-start.sh"
```

### Method 2: Global Python Path

If you want to use system Python (not recommended):

```bash
# Install globally
pip install -e .

# Add to Claude
claude mcp add mcp-x-server python -m src.server
```

## Troubleshooting

### Issue: "Module not found" error

**Solution:** Make sure you're using the venv Python:
```bash
# Check which Python is being used
which python
# Should show: /path/to/mcp-x-server/venv/bin/python

# Reinstall if needed
rm -rf venv
./scripts/setup.sh
```

### Issue: "Cookies invalid" error

**Solution:** Re-export fresh cookies from your browser:
1. Make sure you're logged into X/Twitter
2. Export cookies again (they may have expired)
3. Replace `config/cookies.json`
4. Restart the MCP server

### Issue: Server doesn't start

**Solution:** Check the logs:
```bash
# Run the server manually to see errors
source venv/bin/activate
python -m src.server

# Common issues:
# - Missing cookies file
# - Invalid Python version
# - Missing dependencies
```

### Issue: "Command not found: claude"

**Solution:** Install Claude Code CLI:
```bash
# Follow Claude Code installation guide
# https://docs.anthropic.com/claude/docs/claude-code
```

## Installing in Another Repository

If you want to use this server from a different project:

### Option 1: Clone as Submodule

```bash
# In your project directory
git submodule add https://github.com/bigsky77/mcp-x-server.git mcp-servers/mcp-x-server
cd mcp-servers/mcp-x-server
./scripts/setup.sh

# Add to Claude from your project root
claude mcp add mcp-x-server "$(pwd)/mcp-servers/mcp-x-server/venv/bin/python" -m src.server
```

### Option 2: Separate Installation

```bash
# Install anywhere on your system
cd ~/mcp-servers  # or any directory
git clone https://github.com/bigsky77/mcp-x-server.git
cd mcp-x-server
./scripts/setup.sh

# Add to Claude with absolute path
claude mcp add mcp-x-server "$HOME/mcp-servers/mcp-x-server/venv/bin/python" -m src.server
```

## Environment Variables

You can customize behavior with environment variables:

```bash
# Add with custom config
claude mcp add mcp-x-server \
  -e CONFIG_PATH=/path/to/config.yaml \
  -e LOG_LEVEL=DEBUG \
  -- "$(pwd)/venv/bin/python" -m src.server
```

Available variables:
- `CONFIG_PATH` - Path to config.yaml (default: config/config.yaml)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `COOKIES_FILE` - Path to cookies.json (default: config/cookies.json)

## Uninstalling

To remove the MCP server:

```bash
# Remove from Claude
claude mcp remove mcp-x-server

# Delete files (optional)
cd /path/to/mcp-x-server/..
rm -rf mcp-x-server
```

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for usage examples
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
- See [DEVELOPMENT.md](DEVELOPMENT.md) if you want to contribute

## Known Issues

⚠️ **5 Tools Currently Non-Functional**

Due to twscrape API limitations, these tools will fail:
- `get_home_timeline` - Method not available in twscrape
- `get_lists` - Method not available in twscrape
- `get_likers` - Method not available in twscrape
- `get_user_likes` - Method not available in twscrape
- `search_users` - Has a bug (uses plural instead of singular)

See [Issue #1](https://github.com/bigsky77/mcp-x-server/issues/1) for details.

**Workaround:** Use alternative tools or wait for fix.

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: https://github.com/bigsky77/mcp-x-server/issues
- 💬 Discussions: https://github.com/bigsky77/mcp-x-server/discussions
