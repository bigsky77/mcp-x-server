# MCP X Server - API Reference

Complete reference for all 35 MCP tools.

## Basic Read Operations (5 tools)

### search_tweets
Search tweets by keyword or hashtag.

**Parameters:**
- `query` (string, required) - Search query
- `limit` (integer) - Max results (default: 20, max: 100)
- `filter_type` (string) - Filter: "top", "latest", "people", "photos", "videos"

**Example:** `{"query": "#AI", "limit": 10, "filter_type": "latest"}`

### get_tweet
Get single tweet by ID with full metadata.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID

**Example:** `{"tweet_id": "1234567890"}`

### get_user_tweets
Get tweets from user timeline.

**Parameters:**
- `username` (string, required) - Twitter username (with or without @)
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"username": "sama", "limit": 10}`

### get_user
Get user profile and statistics.

**Parameters:**
- `username` (string, required) - Twitter username

**Example:** `{"username": "elonmusk"}`

### get_mentions
Get mentions for specified user.

**Parameters:**
- `username` (string, required) - Username to search mentions for
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"username": "sama", "limit": 20}`

---

## Basic Write Operations (5 tools)

### post_tweet
Post a new tweet.

**Parameters:**
- `text` (string, required) - Tweet text (max 280 chars)
- `media_ids` (array) - Optional media IDs to attach

**Example:** `{"text": "Hello from MCP X Server!"}`

### reply_to_tweet
Reply to an existing tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to reply to
- `text` (string, required) - Reply text (max 280 chars)

**Example:** `{"tweet_id": "1234567890", "text": "Great post!"}`

### like_tweet
Like a tweet by ID.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to like

**Example:** `{"tweet_id": "1234567890"}`

### retweet
Retweet a tweet by ID.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to retweet

**Example:** `{"tweet_id": "1234567890"}`

### delete_tweet
Delete own tweet by ID.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to delete

**Example:** `{"tweet_id": "1234567890"}`

---

## Engagement & Context (7 tools)

### quote_tweet
Create a quote tweet with commentary.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to quote
- `text` (string, required) - Quote comment text (max 280 chars)
- `media_ids` (array) - Optional media IDs

**Example:** `{"tweet_id": "1234567890", "text": "Excellent analysis!"}`

### get_tweet_context
Get full conversation thread and context for a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID
- `include_replies` (boolean) - Include replies (default: true)
- `max_depth` (integer) - Max depth for parent tweets (default: 10)

**Example:** `{"tweet_id": "1234567890", "include_replies": true}`

### get_quote_tweets
Get quote tweets of a specific tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"tweet_id": "1234567890", "limit": 20}`

### get_likers
Get users who liked a tweet. ⚠️ Limited by twscrape API.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"tweet_id": "1234567890", "limit": 20}`

### get_retweeters
Get users who retweeted a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"tweet_id": "1234567890", "limit": 20}`

### get_user_likes
Get tweets liked by user. ⚠️ Limited by twscrape API.

**Parameters:**
- `user_id` (string, required) - User ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"user_id": "1234567890", "limit": 20}`

### get_home_timeline
Get authenticated user's home timeline. ⚠️ Limited by twscrape API.

**Parameters:**
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"limit": 20}`

---

## Relationship Management (4 tools)

### follow_user
Follow a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to follow

**Example:** `{"user_id": "1234567890"}`

### unfollow_user
Unfollow a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to unfollow

**Example:** `{"user_id": "1234567890"}`

### get_followers
Get followers list for a user.

**Parameters:**
- `user_id` (string, required) - User ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"user_id": "1234567890", "limit": 50}`

### get_following
Get following list for a user.

**Parameters:**
- `user_id` (string, required) - User ID
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"user_id": "1234567890", "limit": 50}`

---

## Moderation & Cleanup (6 tools)

### unlike_tweet
Remove like from a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to unlike

**Example:** `{"tweet_id": "1234567890"}`

### unretweet
Remove retweet from a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to unretweet

**Example:** `{"tweet_id": "1234567890"}`

### mute_user
Mute a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to mute

**Example:** `{"user_id": "1234567890"}`

### unmute_user
Unmute a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to unmute

**Example:** `{"user_id": "1234567890"}`

### block_user
Block a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to block

**Example:** `{"user_id": "1234567890"}`

### unblock_user
Unblock a user by ID.

**Parameters:**
- `user_id` (string, required) - User ID to unblock

**Example:** `{"user_id": "1234567890"}`

---

## List Management (4 tools)

### get_lists
Get lists owned by a user. ⚠️ Limited by twscrape API.

**Parameters:**
- `user_id` (string, required) - User ID

**Example:** `{"user_id": "1234567890"}`

### create_list
Create a new Twitter list.

**Parameters:**
- `name` (string, required) - List name (max 25 chars)
- `description` (string) - Optional list description
- `private` (boolean) - Whether the list is private (default: false)

**Example:** `{"name": "AI Researchers", "description": "Top AI researchers", "private": true}`

### add_to_list
Add user to a list.

**Parameters:**
- `list_id` (string, required) - List ID
- `user_id` (string, required) - User ID to add

**Example:** `{"list_id": "1234567890", "user_id": "9876543210"}`

### remove_from_list
Remove user from a list.

**Parameters:**
- `list_id` (string, required) - List ID
- `user_id` (string, required) - User ID to remove

**Example:** `{"list_id": "1234567890", "user_id": "9876543210"}`

---

## Discovery & Monitoring (4 tools)

### search_users
Search for users by query.

**Parameters:**
- `query` (string, required) - Search query
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"query": "AI researcher", "limit": 10}`

### bookmark_tweet
Bookmark a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to bookmark

**Example:** `{"tweet_id": "1234567890"}`

### unbookmark_tweet
Remove bookmark from a tweet.

**Parameters:**
- `tweet_id` (string, required) - Tweet ID to unbookmark

**Example:** `{"tweet_id": "1234567890"}`

### get_bookmarks
Get bookmarked tweets for authenticated user.

**Parameters:**
- `limit` (integer) - Max results (default: 20, max: 100)

**Example:** `{"limit": 20}`

### get_rate_limits
Get current API rate limit status.

**Parameters:** None

**Example:** `{}`

---

## Common Response Formats

### Tweet Object
```json
{
  "id": "1234567890",
  "text": "Tweet content",
  "author": {
    "username": "user",
    "name": "Display Name"
  },
  "created_at": "2024-01-01T12:00:00",
  "metrics": {
    "likes": 10,
    "retweets": 5,
    "replies": 2
  }
}
```

### User Object
```json
{
  "id": "1234567890",
  "username": "user",
  "name": "Display Name",
  "followers": 1000,
  "following": 500,
  "verified": false
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Rate Limits

- **Read operations:** ~300 requests / 15 minutes
- **Write operations:** ~50 requests / 24 hours

Use `get_rate_limits` to check current quotas.

---

## Notes

⚠️ **4 tools have limitations** due to twscrape API constraints:
- `get_home_timeline`
- `get_lists`
- `get_likers`
- `get_user_likes`

These tools are implemented but may return limited data. See [Issue #1](https://github.com/bigsky77/mcp-x-server/issues/1) for workarounds.

## Getting User/Tweet IDs

Most tools require numeric IDs. To get them:

**For usernames:**
```
# Use get_user to get user_id from username
get_user(username="sama") → returns user object with "id" field
```

**For tweet IDs:**
- Tweet IDs are visible in tweet URLs: `twitter.com/user/status/[TWEET_ID]`
- Or use `search_tweets` to find tweets and get their IDs
