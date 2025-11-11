# Setup Guide

## Prerequisites

- Python 3.10+
- X (Twitter) account cookies

## Installation

1. **Run setup script:**
```bash
./scripts/setup.sh
```

2. **Verify cookies file exists:**
```bash
ls config/cookies.json
```

## Cookie Extraction

Export cookies from your browser session:

1. Log in to X (Twitter) in your browser
2. Use a cookie export extension (e.g., "EditThisCookie", "Cookie-Editor")
3. Export cookies as JSON
4. Save to `config/cookies.json`

Required cookies:
- `auth_token`
- `ct0` (CSRF token)

## Running the Server

**Standalone:**
```bash
./scripts/run.sh
```

**With Claude Code MCP:**
```bash
claude mcp add mcp-x-server python -m src.server --cwd /Users/bigsky/mcp-x-server
```

## Testing

Test individual components:

```python
# Test authentication
python -c "
from src.auth.account_manager import AccountManager
am = AccountManager('config/cookies.json')
print('Auth token:', am.get_auth_token()[:20] + '...')
"

# Test client initialization
python -c "
from src.clients.twikit_client import TwiKitClient
from src.auth.account_manager import AccountManager
am = AccountManager('config/cookies.json')
client = TwiKitClient(am.load_cookies())
print('TwiKit client initialized')
"
```

## Troubleshooting

**Missing cookies:**
- Ensure `config/cookies.json` exists and has valid format
- Re-export cookies if expired

**Rate limit errors:**
- Check rate limit settings in `config/config.yaml`
- Wait for rate limit window to reset

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -e .` to reinstall dependencies

## MCP Tool Usage

Once connected to Claude Code, available tools:

**Read operations:**
- `search_tweets` - Search by keyword
- `get_tweet` - Get single tweet
- `get_user_tweets` - User timeline
- `get_user` - User profile
- `get_mentions` - Mentions for user

**Write operations:**
- `post_tweet` - Post new tweet
- `reply_to_tweet` - Reply to tweet
- `like_tweet` - Like tweet
- `retweet` - Retweet
- `delete_tweet` - Delete tweet

Example prompts:
```
"Search for tweets about #AI"
"Get the latest 10 tweets from @elonmusk"
"Post a tweet: Hello from MCP!"
```
