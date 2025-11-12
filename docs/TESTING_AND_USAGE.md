# MCP X Server - Testing and Usage Guide

## Quick Test After Installation

### 1. Verify Server is Registered

```bash
# Check if mcp-x-server appears in the list
claude mcp list
```

Expected output should include:
```
mcp-x-server
```

### 2. Test Basic Connectivity

Try the simplest read operation:

```bash
# Search for tweets about AI (limit to 1 for quick test)
claude mcp call mcp-x-server search_tweets '{"query":"AI", "limit":1}'
```

If this works, your server is properly configured!

## Working Tools (31 Total)

### ✅ Basic Read Operations (4/5 working)
- ✅ `search_tweets` - Search tweets by keyword/hashtag
- ✅ `get_tweet` - Get single tweet by ID
- ✅ `get_user_tweets` - Get user timeline
- ✅ `get_user` - Get user profile
- ✅ `get_mentions` - Get mentions

### ✅ Basic Write Operations (5/5 working)
- ✅ `post_tweet` - Post new tweet
- ✅ `reply_to_tweet` - Reply to tweet
- ✅ `like_tweet` - Like tweet
- ✅ `retweet` - Retweet
- ✅ `delete_tweet` - Delete tweet

### ⚠️ Engagement & Context (3/7 working)
- ✅ `quote_tweet` - Create quote tweet with commentary
- ✅ `get_tweet_context` - Get full conversation thread
- ✅ `get_quote_tweets` - Get all quote tweets of a tweet
- ❌ `get_likers` - NOT WORKING (twscrape API limitation)
- ✅ `get_retweeters` - Get users who retweeted
- ❌ `get_user_likes` - NOT WORKING (twscrape API limitation)
- ❌ `get_home_timeline` - NOT WORKING (twscrape API limitation)

### ✅ Relationship Management (4/4 working)
- ✅ `follow_user` - Follow a user
- ✅ `unfollow_user` - Unfollow a user
- ✅ `get_followers` - Get user's followers
- ✅ `get_following` - Get users a user follows

### ✅ Moderation & Cleanup (6/6 working)
- ✅ `unlike_tweet` - Remove a like
- ✅ `unretweet` - Remove a retweet
- ✅ `mute_user` - Mute a user
- ✅ `unmute_user` - Unmute a user
- ✅ `block_user` - Block a user
- ✅ `unblock_user` - Unblock a user

### ⚠️ List Management (2/4 working)
- ❌ `get_lists` - NOT WORKING (twscrape API limitation)
- ✅ `create_list` - Create new list
- ✅ `add_to_list` - Add user to list
- ✅ `remove_from_list` - Remove user from list

### ✅ Discovery & Monitoring (4/5 working)
- ✅ `search_users` - Search for users (FIXED!)
- ✅ `bookmark_tweet` - Bookmark a tweet
- ✅ `unbookmark_tweet` - Remove bookmark
- ✅ `get_bookmarks` - Get bookmarked tweets
- ✅ `get_rate_limits` - Check API rate limit status

## Test Commands

### Read Operations

```bash
# Search tweets
claude mcp call mcp-x-server search_tweets '{"query":"#AI", "limit":5}'

# Get specific tweet
claude mcp call mcp-x-server get_tweet '{"tweet_id":"1234567890"}'

# Get user profile
claude mcp call mcp-x-server get_user '{"username":"elonmusk"}'

# Get user's tweets
claude mcp call mcp-x-server get_user_tweets '{"username":"sama", "limit":10}'

# Search for users (NOW WORKING!)
claude mcp call mcp-x-server search_users '{"query":"AI researcher", "limit":5}'

# Get bookmarks
claude mcp call mcp-x-server get_bookmarks '{"limit":10}'

# Check rate limits
claude mcp call mcp-x-server get_rate_limits '{}'
```

### Write Operations (Use Carefully!)

```bash
# Post a tweet
claude mcp call mcp-x-server post_tweet '{"text":"Hello from MCP X Server!"}'

# Reply to a tweet
claude mcp call mcp-x-server reply_to_tweet '{"tweet_id":"1234567890", "text":"Great point!"}'

# Like a tweet
claude mcp call mcp-x-server like_tweet '{"tweet_id":"1234567890"}'

# Bookmark a tweet
claude mcp call mcp-x-server bookmark_tweet '{"tweet_id":"1234567890"}'

# Follow a user
claude mcp call mcp-x-server follow_user '{"username":"anthropicai"}'
```

### Engagement Operations

```bash
# Quote tweet
claude mcp call mcp-x-server quote_tweet '{"tweet_id":"1234567890", "text":"Interesting perspective on AI safety"}'

# Get conversation thread
claude mcp call mcp-x-server get_tweet_context '{"tweet_id":"1234567890"}'

# Get who retweeted
claude mcp call mcp-x-server get_retweeters '{"tweet_id":"1234567890", "limit":20}'
```

## Using with Claude Code Chat

Instead of command-line calls, you can use natural language in Claude Code:

**Example conversations:**

```
You: Search for the latest tweets about Claude AI

You: Get the profile for @anthropicai

You: Show me the last 10 tweets from @sama

You: Post a tweet saying "Testing my new MCP X Server!"

You: Search for users interested in machine learning

You: What are my current rate limits?
```

Claude Code will automatically call the appropriate MCP tools!

## Debugging Issues

### Issue: "Server not found"

```bash
# Check if server is registered
claude mcp list

# If not listed, re-add it
cd /path/to/mcp-x-server
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

### Issue: "Connection refused"

```bash
# Test if Python can run the server
cd /path/to/mcp-x-server
source venv/bin/activate
python -m src.server

# Should start without errors
# Ctrl+C to stop
```

### Issue: "Authentication failed"

```bash
# Check if cookies file exists
ls -la config/cookies.json

# Verify cookies are valid JSON
cat config/cookies.json | python -m json.tool

# Re-export fresh cookies from browser if needed
```

### Issue: Tool returns error

```bash
# Check which tools are broken (see Known Issues below)
# Enable debug logging
export LOG_LEVEL=DEBUG
claude mcp call mcp-x-server search_tweets '{"query":"test", "limit":1}'
```

## Known Issues and Workarounds

### ❌ 4 Tools Currently Non-Functional

Due to twscrape library API limitations:

1. **`get_home_timeline`**
   - Error: `AttributeError: 'API' object has no attribute 'home_timeline'`
   - Workaround: Use `get_user_tweets` with your username instead

2. **`get_lists`**
   - Error: `AttributeError: 'API' object has no attribute 'lists_by_user'`
   - Workaround: None available (twscrape limitation)

3. **`get_likers`**
   - Error: `AttributeError: 'API' object has no attribute 'favoriters'`
   - Workaround: None available (twscrape limitation)

4. **`get_user_likes`**
   - Error: `AttributeError: 'API' object has no attribute 'liked_tweets'`
   - Workaround: Use `get_bookmarks` if you want your own likes

### ✅ Fixed Issues

1. **`search_users`** - FIXED in latest version
   - Was: Using `search_users` (plural)
   - Now: Using `search_user` (singular)
   - Status: Working correctly

## Rate Limits

Be aware of X (Twitter) rate limits:

**Read Operations:**
- 300 requests per 15 minutes
- Automatically tracked by server

**Write Operations:**
- 50 tweets per 24 hours
- 1000 follows per 24 hours
- 1000 likes per 24 hours

Check current limits:
```bash
claude mcp call mcp-x-server get_rate_limits '{}'
```

## Advanced Usage

### Batch Operations

You can chain multiple operations in Claude Code:

```
You: Search for tweets about AI, get the top tweet, and quote tweet it with "Interesting read!"
```

Claude Code will:
1. Call `search_tweets` with query "AI"
2. Call `quote_tweet` with the top result

### Monitoring Workflows

```
You: Every hour, search for mentions of "MCP server" and bookmark interesting ones
```

Claude Code can create monitoring workflows using the MCP tools.

### Content Creation

```
You: Help me write a thread about MCP servers. Post the first tweet, then reply with 3 follow-up tweets.
```

Claude Code will use `post_tweet` and `reply_to_tweet` to create the thread.

## Environment-Specific Testing

### macOS
```bash
# Standard installation
cd ~/mcp-servers/mcp-x-server
./scripts/setup.sh
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

### Linux
```bash
# Same as macOS
cd ~/mcp-servers/mcp-x-server
./scripts/setup.sh
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

### Windows (WSL)
```bash
# Use WSL paths
cd /mnt/c/Users/YourName/mcp-servers/mcp-x-server
./scripts/setup.sh
claude mcp add mcp-x-server "$(pwd)/venv/bin/python" -m src.server
```

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for more examples
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [DEVELOPMENT.md](DEVELOPMENT.md) to contribute

## Support

If you encounter issues:

1. Check the [Known Issues](#known-issues-and-workarounds) section
2. Review [GitHub Issues](https://github.com/bigsky77/mcp-x-server/issues)
3. Create a new issue with:
   - Command you ran
   - Error message
   - Your OS and Python version
   - Output of `claude mcp list`

---

**Summary: 31 out of 35 tools working (89% success rate)**

The 4 non-working tools are due to twscrape library limitations, not configuration issues.
