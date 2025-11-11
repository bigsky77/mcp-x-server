# MCP X Server Architecture

## Overview

Minimalist X (Twitter) MCP server providing primitive operations for reading and posting. Implements core MCP tools using TwiKit (write operations) and Twscrape (read operations) with cookie-based authentication.

## MCP Primitives

### Read Tools
- `search_tweets` - Search tweets by keyword/hashtag with filters
- `get_tweet` - Fetch single tweet by ID with full metadata
- `get_user_tweets` - Retrieve tweets from specific user timeline
- `get_user` - Get user profile and statistics
- `get_mentions` - Fetch mentions for authenticated account

### Write Tools
- `post_tweet` - Create new tweet with text/media
- `reply_to_tweet` - Reply to existing tweet by ID
- `like_tweet` - Like tweet by ID
- `retweet` - Retweet by ID
- `delete_tweet` - Delete own tweet by ID

## Project Structure

```
mcp-x-server/
├── src/
│   ├── server.py              # Main MCP server entry point
│   ├── auth/
│   │   └── account_manager.py # Cookie-based authentication
│   ├── clients/
│   │   ├── twikit_client.py   # TwiKit wrapper (write operations)
│   │   └── twscrape_client.py # Twscrape wrapper (read operations)
│   ├── tools/
│   │   ├── read_tools.py      # MCP read primitives
│   │   └── post_tools.py      # MCP write primitives
│   └── utils/
│       ├── rate_limiter.py    # Request throttling
│       └── validators.py      # Input validation
├── config/
│   ├── cookies.json           # Auth cookies (gitignored)
│   └── config.yaml            # Server configuration
├── tests/
│   └── test_server.py         # Test suite
└── docs/
    └── ARCHITECTURE.md
```

## Implementation Notes

### Authentication
- **Twscrape**: Cookie-based account pool (optional, for read operations)
- **TwiKit**: Single account authentication via cookies
- Cookies must be manually extracted from browser sessions
- Required cookies: `auth_token`, `ct0` (CSRF token)

### Rate Limiting
- X API limits: 300 reads/15min, 50 posts/24h per account
- Exponential backoff on 429 responses
- Account rotation for read operations (Twscrape handles automatically)
- Write operations use single TwiKit account

### Error Handling
- Graceful degradation on rate limits
- Return partial results when possible
- Clear error messages for authentication and validation failures

### Design Constraints
- No database persistence
- No event logging or analytics
- No background workers or schedulers
- Synchronous MCP tool operations
- Single account for write operations
