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

## MCP Tools (35 Total)

### Basic Read Operations (5 tools)
- `search_tweets` - Search tweets by keyword/hashtag
- `get_tweet` - Get single tweet by ID
- `get_user_tweets` - Get user timeline
- `get_user` - Get user profile
- `get_mentions` - Get mentions

### Basic Write Operations (5 tools)
- `post_tweet` - Post new tweet
- `reply_to_tweet` - Reply to tweet
- `like_tweet` - Like tweet
- `retweet` - Retweet
- `delete_tweet` - Delete tweet

### Engagement & Context (7 tools)
- `quote_tweet` - Create quote tweet with commentary
- `get_tweet_context` - Get full conversation thread
- `get_quote_tweets` - Get all quote tweets of a tweet
- `get_likers` - Get users who liked a tweet
- `get_retweeters` - Get users who retweeted
- `get_user_likes` - Get tweets liked by user
- `get_home_timeline` - Get authenticated user's timeline

### Relationship Management (4 tools)
- `follow_user` - Follow a user
- `unfollow_user` - Unfollow a user
- `get_followers` - Get user's followers
- `get_following` - Get users a user follows

### Moderation & Cleanup (6 tools)
- `unlike_tweet` - Remove a like
- `unretweet` - Remove a retweet
- `mute_user` - Mute a user
- `unmute_user` - Unmute a user
- `block_user` - Block a user
- `unblock_user` - Unblock a user

### List Management (4 tools)
- `get_lists` - Get user's lists
- `create_list` - Create new list
- `add_to_list` - Add user to list
- `remove_from_list` - Remove user from list

### Discovery & Monitoring (4 tools)
- `search_users` - Search for users
- `bookmark_tweet` - Bookmark a tweet
- `unbookmark_tweet` - Remove bookmark
- `get_bookmarks` - Get bookmarked tweets
- `get_rate_limits` - Check API rate limit status

## Usage Examples

Once connected to Claude Code:

**Basic Operations:**
```
"Search for tweets about #AI with limit 10"
"Get the latest tweets from @sama"
"Post a tweet: Hello from MCP X Server!"
"Get user profile for @elonmusk"
```

**Engagement & Context:**
```
"Quote tweet 1234567890 with: Great insights on AI!"
"Get the full conversation thread for tweet 1234567890"
"Who liked tweet 1234567890?"
"Show me tweets liked by @sama"
```

**Relationship Management:**
```
"Follow @elonmusk and add them to my AI Leaders list"
"Get followers of @sama"
"Unfollow @username"
```

**List Organization:**
```
"Create a private list called AI Researchers"
"Add @sama to my AI Leaders list"
"Show me all my lists"
```

**Monitoring:**
```
"Check my rate limits"
"Get my home timeline"
"Show my bookmarked tweets"
```

## Architecture

**Simple three-file design:**
- `twikit_client.py` - Write operations (posting, liking, following, etc.)
- `twscrape_client.py` - Read operations (searching, fetching, tracking)
- `server.py` - MCP server exposing 35 tools

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
✓ 35 MCP tools available
