# MCP X Server

Minimalist X (Twitter) MCP server providing read and write primitives.

## Quick Start

```bash
# Setup
./scripts/setup.sh

# Verify
./scripts/verify.sh

# Add to Claude Code
claude mcp add mcp-x-server python -m src.server --cwd /Users/bigsky/mcp-x-server
```

## MCP Tools

### Read Operations (5 tools)
- `search_tweets` - Search tweets by keyword/hashtag
- `get_tweet` - Get single tweet by ID
- `get_user_tweets` - Get user timeline
- `get_user` - Get user profile
- `get_mentions` - Get mentions

### Write Operations (5 tools)
- `post_tweet` - Post new tweet
- `reply_to_tweet` - Reply to tweet
- `like_tweet` - Like tweet
- `retweet` - Retweet
- `delete_tweet` - Delete tweet

## Usage Examples

Once connected to Claude Code:

```
"Search for tweets about #AI with limit 10"
"Get the latest tweets from @sama"
"Post a tweet: Hello from MCP X Server!"
"Get user profile for @elonmusk"
```

## Architecture

**Simple three-file design:**
- `twikit_client.py` - Write operations (posting, liking, etc.)
- `twscrape_client.py` - Read operations (searching, fetching)
- `server.py` - MCP server exposing 10 tools

**Authentication:** Cookie-based (extract from browser)
**Rate Limits:** 300 reads/15min, 50 writes/24h

## Documentation

- [QUICKSTART.md](docs/QUICKSTART.md) - Getting started guide
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [SETUP.md](docs/SETUP.md) - Detailed installation
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Developer guide

## Requirements

- Python 3.10+
- X (Twitter) account cookies
- TwiKit and Twscrape libraries

## Status

✓ Ready for production use
✓ All tests passing
✓ 10 MCP tools available
