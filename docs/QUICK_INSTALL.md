# Quick Installation Guide

**Install MCP X Server in 3 minutes**

## Prerequisites
- Python 3.10+
- Claude Code installed
- X (Twitter) cookies

## Installation (Copy-Paste)

```bash
# 1. Clone and navigate
git clone https://github.com/bigsky77/mcp-x-server.git
cd mcp-x-server

# 2. Setup (installs dependencies)
./scripts/setup.sh

# 3. Add your cookies
# Export cookies from browser while logged into twitter.com
# Save to config/cookies.json

# 4. Add to Claude Code
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server

# 5. Test it works
claude mcp call mcp-x-server search_tweets '{"query":"AI", "limit":1}'
```

## That's it!

You now have 31 working Twitter/X tools available in Claude Code.

### Quick Test in Claude Code

Just ask Claude:
```
Search for tweets about AI
```

Claude will automatically use your MCP X Server!

## Install from Another Directory

If you want to install it alongside another project:

```bash
# From your project directory
cd ~/my-project

# Clone as subdirectory
git clone https://github.com/bigsky77/mcp-x-server.git mcp-x-server
cd mcp-x-server

# Setup
./scripts/setup.sh

# Add your cookies to config/cookies.json

# Add to Claude with full path
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server

# Done! Test from anywhere:
claude mcp call mcp-x-server search_tweets '{"query":"test", "limit":1}'
```

## Troubleshooting

**Server not starting?**
```bash
# Check Python version (need 3.10+)
python3 --version

# Manually test
cd mcp-x-server
source venv/bin/activate
python -m src.server
# Press Ctrl+C to stop
```

**Cookies issues?**
```bash
# Make sure file exists and is valid JSON
cat config/cookies.json | python -m json.tool
```

**Need help?**
- Detailed guide: [docs/INSTALLATION.md](INSTALLATION.md)
- Testing guide: [docs/TESTING_AND_USAGE.md](TESTING_AND_USAGE.md)
- Issues: https://github.com/bigsky77/mcp-x-server/issues

## What You Get

✅ 31 working tools (89% success rate)
- Search tweets and users
- Post, reply, quote tweets
- Like, retweet, bookmark
- Follow, mute, block users
- Manage lists
- Get profiles and timelines

⚠️ 4 tools not working (twscrape library limitations):
- get_home_timeline
- get_lists
- get_likers
- get_user_likes

See [TESTING_AND_USAGE.md](TESTING_AND_USAGE.md) for workarounds.
