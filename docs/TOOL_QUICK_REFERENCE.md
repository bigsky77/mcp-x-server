# Twitter MCP Tools - Quick Reference

Complete list of all 35 MCP tools available in the X Server.

## Original Tools (10)

### Read Operations (5)
| Tool | Description | Parameters |
|------|-------------|------------|
| `search_tweets` | Search tweets by keyword/hashtag | `query`, `limit`, `filter_type` |
| `get_tweet` | Get single tweet by ID | `tweet_id` |
| `get_user_tweets` | Get tweets from user timeline | `username`, `limit` |
| `get_user` | Get user profile | `username` |
| `get_mentions` | Get mentions for user | `username`, `limit` |

### Write Operations (5)
| Tool | Description | Parameters |
|------|-------------|------------|
| `post_tweet` | Post a new tweet | `text`, `media_ids` |
| `reply_to_tweet` | Reply to a tweet | `tweet_id`, `text` |
| `like_tweet` | Like a tweet | `tweet_id` |
| `retweet` | Retweet a tweet | `tweet_id` |
| `delete_tweet` | Delete own tweet | `tweet_id` |

## New Tools - Phase 1: Core Gaps (7)

| Tool | Type | Description | Parameters |
|------|------|-------------|------------|
| `quote_tweet` | Write | Create quote tweet with commentary | `tweet_id`, `text`, `media_ids` |
| `get_tweet_context` | Read | Get full conversation thread | `tweet_id`, `include_replies`, `max_depth` |
| `get_quote_tweets` | Read | Get quotes of a tweet | `tweet_id`, `limit` |
| `follow_user` | Write | Follow a user | `user_id` |
| `unfollow_user` | Write | Unfollow a user | `user_id` |
| `get_followers` | Read | Get user's followers | `user_id`, `limit` |
| `get_following` | Read | Get who user follows | `user_id`, `limit` |

## New Tools - Phase 2: Intelligence (4)

| Tool | Type | Description | Parameters |
|------|------|-------------|------------|
| `get_likers` | Read | Get users who liked a tweet | `tweet_id`, `limit` |
| `get_retweeters` | Read | Get users who retweeted | `tweet_id`, `limit` |
| `get_user_likes` | Read | Get tweets liked by user | `user_id`, `limit` |
| `get_home_timeline` | Read | Get home timeline feed | `limit` |

## New Tools - Phase 3: Operations (7)

| Tool | Type | Description | Parameters |
|------|------|-------------|------------|
| `unlike_tweet` | Write | Remove like from tweet | `tweet_id` |
| `unretweet` | Write | Remove retweet | `tweet_id` |
| `get_rate_limits` | Read | Check API rate limits | None |
| `mute_user` | Write | Mute a user | `user_id` |
| `unmute_user` | Write | Unmute a user | `user_id` |
| `block_user` | Write | Block a user | `user_id` |
| `unblock_user` | Write | Unblock a user | `user_id` |

## New Tools - Phase 4: Advanced (9)

| Tool | Type | Description | Parameters |
|------|------|-------------|------------|
| `get_lists` | Read | Get user's lists | `user_id` |
| `create_list` | Write | Create new list | `name`, `description`, `private` |
| `add_to_list` | Write | Add user to list | `list_id`, `user_id` |
| `remove_from_list` | Write | Remove user from list | `list_id`, `user_id` |
| `search_users` | Read | Search for users | `query`, `limit` |
| `bookmark_tweet` | Write | Bookmark a tweet | `tweet_id` |
| `unbookmark_tweet` | Write | Remove bookmark | `tweet_id` |
| `get_bookmarks` | Read | Get bookmarked tweets | `limit` |

## Tool Categories

### By Function
- **Tweets**: 11 tools (post, reply, quote, delete, like, unlike, retweet, unretweet, search, get, get_context)
- **Users**: 11 tools (get, search, follow, unfollow, mute, unmute, block, unblock, get_followers, get_following)
- **Engagement**: 6 tools (like, unlike, retweet, unretweet, get_likers, get_retweeters)
- **Lists**: 4 tools (get, create, add_to, remove_from)
- **Discovery**: 3 tools (search_tweets, search_users, get_home_timeline)
- **Curation**: 3 tools (bookmark, unbookmark, get_bookmarks)
- **Intelligence**: 4 tools (get_likers, get_retweeters, get_user_likes, get_quote_tweets)
- **Operations**: 2 tools (get_rate_limits, get_mentions)

### By Type
- **Read Operations**: 21 tools
- **Write Operations**: 14 tools

## Common Parameters

| Parameter | Type | Description | Default | Max |
|-----------|------|-------------|---------|-----|
| `tweet_id` | string | Numeric tweet ID | - | - |
| `user_id` | string | Numeric user ID | - | - |
| `username` | string | Twitter handle (with or without @) | - | - |
| `text` | string | Tweet text | - | 280 chars |
| `limit` | integer | Maximum results to return | 20 | 100 |
| `query` | string | Search query | - | - |
| `media_ids` | array | List of media IDs to attach | [] | - |
| `list_id` | string | Numeric list ID | - | - |
| `name` | string | List name | - | 25 chars |
| `description` | string | List description | "" | - |
| `private` | boolean | Whether list is private | false | - |
| `include_replies` | boolean | Include replies in context | true | - |
| `max_depth` | integer | Max parent tweet depth | 10 | - |

## Return Types

### Tweet Object
```json
{
  "id": "1234567890",
  "text": "Tweet content",
  "author": {
    "username": "user",
    "name": "Display Name",
    "followers": 1000
  },
  "created_at": "2024-01-01T12:00:00",
  "metrics": {
    "likes": 10,
    "retweets": 5,
    "replies": 2,
    "views": 100
  },
  "in_reply_to": "9876543210"
}
```

### User Object
```json
{
  "id": "1234567890",
  "username": "user",
  "name": "Display Name",
  "description": "Bio text",
  "created_at": "2020-01-01",
  "metrics": {
    "followers": 1000,
    "following": 500,
    "tweets": 10000
  },
  "verified": false
}
```

### List Object
```json
{
  "list_id": "1234567890",
  "name": "List Name",
  "description": "List description",
  "member_count": 50,
  "subscriber_count": 10,
  "private": false
}
```

### Context Object
```json
{
  "conversation_id": "1234567890",
  "parent_tweets": [],
  "main_tweet": {},
  "replies": [],
  "full_thread": []
}
```

## Error Handling

All tools return structured errors:
```json
{
  "success": false,
  "error": "Error message"
}
```

Common errors:
- Invalid tweet/user/list ID
- Authentication required
- Rate limit exceeded
- Tweet not found
- User not found
- Permission denied

## Rate Limits

Use `get_rate_limits()` to check current quotas:
```json
{
  "endpoints": {
    "search": {
      "limit": 180,
      "remaining": 150,
      "reset_time": "2024-01-01T13:00:00"
    }
  }
}
```

## Usage Tips

1. **Context-Aware Replies**: Use `get_tweet_context` before replying to understand conversation
2. **Engagement Analysis**: Combine `get_likers` and `get_retweeters` to identify influencers
3. **Network Building**: Use `get_followers` and `follow_user` for targeted following
4. **List Organization**: Create lists to segment accounts (e.g., S-tier, A-tier targets)
5. **Content Discovery**: Use `search_users` and `get_user_likes` to find relevant content
6. **Cleanup Operations**: Use `unlike_tweet` and `unretweet` to manage your profile
7. **Spam Control**: Use `mute_user` and `block_user` for moderation
8. **Curation**: Use bookmarks to save valuable content for later analysis

## Integration Examples

### Engagement Workflow
```
1. get_home_timeline() → Get latest tweets
2. get_tweet_context(tweet_id) → Understand conversation
3. reply_to_tweet(tweet_id, text) → Reply with context
4. like_tweet(tweet_id) → Engage
```

### Network Analysis
```
1. search_users(query) → Find target users
2. get_user(username) → Check profile
3. get_user_likes(user_id) → Analyze interests
4. follow_user(user_id) → Add to network
5. add_to_list(list_id, user_id) → Organize
```

### Content Research
```
1. search_tweets(query) → Find relevant content
2. get_quote_tweets(tweet_id) → See commentary
3. get_likers(tweet_id) → Find engaged users
4. bookmark_tweet(tweet_id) → Save for later
```

---

**Total Tools**: 35
**Documentation**: See `/docs/IMPLEMENTATION_SUMMARY.md` for details
**Tests**: Run `python tests/test_new_tools.py` to verify
