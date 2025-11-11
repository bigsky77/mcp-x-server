# Quick Start Guide

## Installation

```bash
./scripts/setup.sh
```

**What it does:**
- Creates Python virtual environment
- Installs TwiKit, Twscrape, MCP SDK
- Verifies cookies file exists

## Verification

```bash
./scripts/verify.sh
```

**Expected output:**
```
✓ Cookies loaded: 24 cookies
✓ Auth token: e7d249c9df3bbc5edf3b...
✓ TwiKit client initialized
✓ Server initialized with 10 MCP tools
✓ All tests passed!
```

## Running the Server

### Option 1: Standalone

```bash
./scripts/run.sh
```

### Option 2: With Claude Code (Recommended)

```bash
claude mcp add mcp-x-server python -m src.server --cwd /Users/bigsky/mcp-x-server
```

Verify installation:

```bash
claude mcp list
```

## Available MCP Tools

### Read Operations
1. `search_tweets` - Search by keyword/hashtag
2. `get_tweet` - Get single tweet by ID
3. `get_user_tweets` - Get user timeline
4. `get_user` - Get user profile
5. `get_mentions` - Get mentions for user

### Write Operations
1. `post_tweet` - Post new tweet
2. `reply_to_tweet` - Reply to tweet
3. `like_tweet` - Like tweet
4. `retweet` - Retweet
5. `delete_tweet` - Delete tweet

## Example Usage

Once connected to Claude Code, try these prompts:

```
"Search for tweets about #AI"
"Get the latest 10 tweets from @sama"
"Post a tweet: Hello from MCP X Server!"
"Get user profile for @elonmusk"
"Reply to tweet 1234567890: Great post!"
```

## Project Structure

```
mcp-x-server/
├── config/
│   ├── config.yaml         # Server configuration
│   └── cookies.json        # Auth cookies ✓
├── src/
│   ├── server.py          # Main MCP server ✓
│   ├── auth/              # Authentication ✓
│   ├── clients/           # TwiKit + Twscrape ✓
│   ├── tools/             # MCP primitives ✓
│   └── utils/             # Rate limiting ✓
└── tests/
    └── test_server.py     # Test suite ✓
```

## Rate Limits

- **Read**: 300 requests / 15 minutes
- **Write**: 50 requests / 24 hours

Configure in `config/config.yaml` if needed.

## Troubleshooting

**Server won't start:**
```bash
source venv/bin/activate
python tests/test_server.py
```

**Auth issues:**
- Re-export cookies from browser
- Ensure `auth_token` and `ct0` cookies are present
- Check `config/cookies.json` exists

**Import errors:**
```bash
pip install -e .
```

**Read operations failing:**
- Twscrape requires account setup (optional)
- Write operations (TwiKit) work with cookies only

## Testing Write Operations

```bash
# Test (without posting)
python tests/test_write_only.py

# To actually post a tweet, edit test_write_only.py:
# Set POST_TEST_TWEET = True
```

## Next Steps

1. **Connect to Claude Code**: Add the MCP server
2. **Test read operations**: Search and fetch tweets
3. **Test write operations**: Post a test tweet
4. **Explore tools**: Try all 10 MCP primitives

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [SETUP.md](SETUP.md) - Detailed setup guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Developer guide

---

**Status**: ✓ Ready for use
**Tools**: 10 MCP primitives
**Tests**: All passing
