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
✓ Server initialized with 35 MCP tools
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

## Available MCP Tools (35 Total)

### Basic Read Operations (5 tools)
1. `search_tweets` - Search by keyword/hashtag
2. `get_tweet` - Get single tweet by ID
3. `get_user_tweets` - Get user timeline
4. `get_user` - Get user profile
5. `get_mentions` - Get mentions for user

### Basic Write Operations (5 tools)
1. `post_tweet` - Post new tweet
2. `reply_to_tweet` - Reply to tweet
3. `like_tweet` - Like tweet
4. `retweet` - Retweet
5. `delete_tweet` - Delete tweet

### Engagement & Context (7 tools)
1. `quote_tweet` - Create quote tweet with commentary
2. `get_tweet_context` - Get full conversation thread
3. `get_quote_tweets` - Get all quote tweets of a tweet
4. `get_likers` - Get users who liked a tweet
5. `get_retweeters` - Get users who retweeted
6. `get_user_likes` - Get tweets liked by user
7. `get_home_timeline` - Get authenticated user's timeline

### Relationship Management (4 tools)
1. `follow_user` - Follow a user
2. `unfollow_user` - Unfollow a user
3. `get_followers` - Get user's followers
4. `get_following` - Get users a user follows

### Moderation & Cleanup (6 tools)
1. `unlike_tweet` - Remove a like
2. `unretweet` - Remove a retweet
3. `mute_user` - Mute a user
4. `unmute_user` - Unmute a user
5. `block_user` - Block a user
6. `unblock_user` - Unblock a user

### List Management (4 tools)
1. `get_lists` - Get user's lists
2. `create_list` - Create new list (public or private)
3. `add_to_list` - Add user to list
4. `remove_from_list` - Remove user from list

### Discovery & Monitoring (4 tools)
1. `search_users` - Search for users
2. `bookmark_tweet` - Bookmark a tweet
3. `unbookmark_tweet` - Remove bookmark
4. `get_bookmarks` - Get bookmarked tweets
5. `get_rate_limits` - Check API rate limit status

## Example Usage

Once connected to Claude Code, try these prompts:

### Basic Operations
```
"Search for tweets about #AI"
"Get the latest 10 tweets from @sama"
"Post a tweet: Hello from MCP X Server!"
"Get user profile for @elonmusk"
"Reply to tweet 1234567890: Great post!"
```

### Engagement & Context
```
"Quote tweet 1234567890 with: Excellent analysis!"
"Get the full conversation thread for tweet 1234567890"
"Show me the parent tweets and replies for tweet 1234567890"
"Who liked tweet 1234567890?"
"Who retweeted my last post?"
"Show me what tweets @sama has liked recently"
"Get my home timeline with the latest 20 tweets"
```

### Relationship Management
```
"Follow @elonmusk"
"Get followers of @sama"
"Get who @openai is following"
"Unfollow @username"
```

### List Organization
```
"Create a new list called AI Researchers"
"Create a private list called Personal Friends"
"Add @sama to my AI Researchers list"
"Remove @username from my list"
"Show me all my Twitter lists"
```

### Moderation & Cleanup
```
"Unlike tweet 1234567890"
"Unretweet tweet 1234567890"
"Mute @spambot"
"Block @trollaccount"
"Unblock @username"
```

### Discovery & Monitoring
```
"Search for users who work on AI"
"Bookmark tweet 1234567890 for later"
"Show me all my bookmarked tweets"
"Check my current API rate limits"
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
4. **Explore engagement tools**: Try quote tweets and thread context
5. **Build relationships**: Follow users and create lists
6. **Monitor activity**: Track engagement and rate limits
7. **Explore all tools**: Try all 35 MCP tools

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [SETUP.md](SETUP.md) - Detailed setup guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Developer guide

---

**Status**: ✓ Ready for use
**Tools**: 35 MCP tools
**Tests**: All passing
