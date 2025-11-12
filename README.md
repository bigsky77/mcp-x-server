# MCP X Server

Minimalist X (Twitter) MCP server with 35 tools for Claude Code.

## Quick Install (3 Steps)

```bash
# 1. Clone and setup
git clone https://github.com/bigsky77/mcp-x-server.git
cd mcp-x-server
./scripts/setup.sh

# 2. Add your cookies (export from browser while logged into twitter.com)
# Save to config/cookies.json

# 3. Add to Claude Code
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

Test it works:
```bash
claude mcp call mcp-x-server search_tweets '{"query":"AI", "limit":1}'
```

## What You Get

**35 MCP Tools** organized by category:

### Basic Operations (10 tools)
- Search tweets, get user profiles, timelines, mentions
- Post tweets, reply, like, retweet, delete

### Engagement & Context (7 tools)
- Quote tweets with commentary
- Get full conversation threads
- See who liked/retweeted
- Get user's liked tweets
- Access home timeline

### Relationships (4 tools)
- Follow/unfollow users
- Get followers and following lists

### Moderation (6 tools)
- Unlike tweets, remove retweets
- Mute/unmute, block/unblock users

### Lists (4 tools)
- Create and manage Twitter lists
- Add/remove users from lists

### Discovery (4 tools)
- Search users
- Bookmark tweets
- Check rate limits

**See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete tool parameters.**

## Usage

Just ask Claude in natural language:

```
"Search for tweets about AI"
"Get the latest tweets from @sama"
"Post a tweet: Hello from MCP X Server!"
"Quote tweet 1234567890 with: Great insights!"
"Get the full conversation thread for tweet 1234567890"
"Follow @elonmusk and add them to my AI Leaders list"
"Create a private list called AI Researchers"
"Check my rate limits"
```

## Architecture

**Simple three-file design:**
- `twikit_client.py` - Write operations (posting, liking, etc.)
- `twscrape_client.py` - Read operations (searching, fetching)
- `server.py` - MCP server with 35 tools

**Authentication:** Cookie-based (export from browser)
**Rate Limits:** ~300 reads/15min, ~50 writes/24h

## Status

✅ **31 of 35 tools working** (89% success rate)

⚠️ 4 tools limited by twscrape API:
- `get_home_timeline`
- `get_lists`
- `get_likers`
- `get_user_likes`

See [Issue #1](https://github.com/bigsky77/mcp-x-server/issues/1) for workarounds.

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

**Cookie issues?**
```bash
# Validate cookies file
cat config/cookies.json | python -m json.tool
```

**Install from another directory?**
```bash
# From your project directory
git clone https://github.com/bigsky77/mcp-x-server.git
cd mcp-x-server
./scripts/setup.sh
# Add cookies to config/cookies.json
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

## Requirements

- Python 3.10+
- X (Twitter) account cookies
- Claude Code installed

## Project Structure

```
mcp-x-server/
├── config/
│   ├── config.yaml         # Server configuration
│   └── cookies.json        # Auth cookies (you provide)
├── src/
│   ├── server.py           # MCP server (35 tools)
│   ├── auth/               # Cookie authentication
│   ├── clients/            # TwiKit + Twscrape clients
│   └── utils/              # Rate limiting
├── scripts/
│   ├── setup.sh            # Install dependencies
│   └── verify.sh           # Test installation
└── docs/
    └── API_REFERENCE.md    # Complete tool documentation
```

## Documentation

- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete tool list with parameters
- **[GitHub Issues](https://github.com/bigsky77/mcp-x-server/issues)** - Report bugs

## Contributing

Contributions welcome! Focus areas:
- Fix the 4 limited tools (twscrape alternatives)
- Add more engagement tools
- Improve error handling

## License

MIT License - See LICENSE file for details

---

**Built with:** TwiKit, Twscrape, MCP SDK
**Compatible with:** Claude Code (Anthropic)
