# Twitter MCP - Additional Tool Recommendations

## Overview

This document proposes 10-15 high-impact tools to add to the Twitter MCP beyond the basic read/write operations. These tools address critical gaps in engagement, relationship management, and operational intelligence.

**Current Tools (Baseline):**
- Read: `search_tweets`, `get_tweet`, `get_user_tweets`, `get_user`, `get_mentions`
- Write: `post_tweet`, `reply_to_tweet`, `like_tweet`, `retweet`, `delete_tweet`

---

## Tier 1: Core Missing Operations (Must-Have)

### 1. `quote_tweet`
Create a quote tweet (tweet with embedded quoted tweet).

**Parameters:**
```typescript
{
  tweet_id: string,
  comment_text: string,
  media_ids?: string[]
}
```

**Returns:**
```typescript
{
  created_tweet_id: string,
  url: string,
  success: boolean
}
```

**Why:** Major engagement format missing from basic set. Essential for commentary and conversation participation.

---

### 2. `get_tweet_context`
Fetch full conversation thread and context for a tweet.

**Parameters:**
```typescript
{
  tweet_id: string,
  include_replies?: boolean,
  max_depth?: number
}
```

**Returns:**
```typescript
{
  conversation_id: string,
  parent_tweets: Tweet[],
  replies: Tweet[],
  full_thread: Tweet[] // ordered chronologically
}
```

**Why:** Critical for context-aware replies. Currently replying blind to conversation history.

---

### 3. `get_quote_tweets`
Retrieve all quote tweets of a specific tweet.

**Parameters:**
```typescript
{
  tweet_id: string,
  max_results?: number,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  quotes: [{
    quote_tweet_id: string,
    author: User,
    text: string,
    engagement: EngagementMetrics,
    created_at: string
  }],
  next_token?: string,
  total_count: number
}
```

**Why:** Track conversation spread and see who's engaging with content via quotes.

---

### 4. `follow_user` / `unfollow_user`
Manage following relationships.

**Parameters:**
```typescript
{
  user_id?: string,
  username?: string
}
```

**Returns:**
```typescript
{
  success: boolean,
  relationship_status: "following" | "not_following",
  user: User
}
```

**Why:** Core network building operation. Referenced in multiple scripts but no MCP tool exists.

---

### 5. `get_followers` / `get_following`
Retrieve follower/following lists for any user.

**Parameters:**
```typescript
{
  user_id: string,
  max_results?: number,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  users: User[],
  next_token?: string,
  total_count: number
}
```

**Why:** Essential for relationship tracking and network analysis. Required for 300-account targeting strategy.

---

## Tier 2: Engagement Intelligence

### 6. `get_likers`
Get users who liked a specific tweet.

**Parameters:**
```typescript
{
  tweet_id: string,
  max_results?: number,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  users: [{
    user_id: string,
    username: string,
    follower_count: number,
    is_following_you: boolean,
    bio: string
  }],
  next_token?: string,
  total_count: number
}
```

**Why:** Identify engaged users, find new targets, implement reciprocal engagement strategy.

---

### 7. `get_retweeters`
Get users who retweeted a specific tweet.

**Parameters:**
```typescript
{
  tweet_id: string,
  max_results?: number,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  users: User[],
  next_token?: string,
  total_count: number
}
```

**Why:** Track amplification, identify network amplifiers, measure content spread.

---

### 8. `get_user_likes`
Retrieve tweets liked by a specific user.

**Parameters:**
```typescript
{
  user_id: string,
  max_results?: number,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  tweets: Tweet[],
  next_token?: string
}
```

**Why:** Profile target interests for psychological analysis and better engagement matching.

---

### 9. `unlike_tweet` / `unretweet`
Remove like or retweet from a tweet.

**Parameters:**
```typescript
{
  tweet_id: string
}
```

**Returns:**
```typescript
{
  success: boolean
}
```

**Why:** Cleanup operations, reputation management, undo mistakes.

---

### 10. `get_tweet_metrics`
Get detailed analytics for own tweets (requires ownership).

**Parameters:**
```typescript
{
  tweet_id: string // must be authenticated user's tweet
}
```

**Returns:**
```typescript
{
  impressions: number,
  engagement_rate: number,
  url_clicks: number,
  profile_clicks: number,
  detail_expands: number,
  replies: number,
  likes: number,
  retweets: number,
  quotes: number
}
```

**Why:** Performance tracking for learning loops. Currently missing engagement data beyond basic counts.

---

## Tier 3: Operational Essentials

### 11. `get_home_timeline`
Fetch authenticated user's home timeline feed.

**Parameters:**
```typescript
{
  max_results?: number,
  since_id?: string,
  until_id?: string,
  pagination_token?: string
}
```

**Returns:**
```typescript
{
  tweets: Tweet[],
  next_token?: string
}
```

**Why:** Real-time feed monitoring. Required for `monitor_timeline.py` functionality.

---

### 12. `mute_user` / `unmute_user` / `block_user` / `unblock_user`
User moderation actions.

**Parameters:**
```typescript
{
  user_id: string
}
```

**Returns:**
```typescript
{
  success: boolean,
  action: "muted" | "unmuted" | "blocked" | "unblocked"
}
```

**Why:** Spam control, safety, cleanup. Required for pruning and list management.

---

### 13. `search_users`
Search for users by query/criteria.

**Parameters:**
```typescript
{
  query: string,
  max_results?: number,
  filters?: {
    verified?: boolean,
    min_followers?: number
  }
}
```

**Returns:**
```typescript
{
  users: User[],
  next_token?: string
}
```

**Why:** Account discovery. Find users matching specific criteria for targeting.

---

### 14. `get_lists` / `create_list` / `add_to_list` / `remove_from_list`
Twitter list management operations.

**Parameters:**
```typescript
// get_lists
{ user_id: string }

// create_list
{
  name: string,
  description?: string,
  private?: boolean
}

// add_to_list / remove_from_list
{
  list_id: string,
  user_id: string
}
```

**Returns:**
```typescript
// get_lists
{ lists: List[] }

// create_list
{ list_id: string, list: List }

// add_to_list / remove_from_list
{ success: boolean }
```

**Why:** Organization for 300-account targeting. Segment by tier (S, A, B, C, D).

---

### 15. `get_rate_limits`
Check current API rate limit status.

**Parameters:**
```typescript
{
  endpoints?: string[] // optional filter
}
```

**Returns:**
```typescript
{
  endpoints: {
    [endpoint: string]: {
      limit: number,
      remaining: number,
      reset_time: string
    }
  }
}
```

**Why:** Operational awareness. Prevent rate limit errors in automation workflows.

---

## Bonus Tools (Priority 16-20)

### 16. `bookmark_tweet` / `unbookmark_tweet` / `get_bookmarks`
Bookmark management for content curation.

**Why:** Save interesting content for analysis and reference.

---

### 17. `get_trending_topics`
Fetch current trending topics/hashtags.

**Why:** Context awareness, react to real-time events, timing optimization.

---

### 18. `get_conversation_participants`
List all participants in a conversation thread.

**Why:** Map conversation networks, identify high-value participants.

---

### 19. `upload_media`
Upload media separately from posting (images, videos, GIFs).

**Why:** Decouple media upload from tweet posting. Required for `generate-anime-image.js` workflow.

---

### 20. `get_notifications`
Fetch notifications for authenticated user.

**Why:** Real-time engagement tracking, quick response to interactions.

---

## Implementation Priority

### Phase 1 (Core Gaps) - Week 1
1. `quote_tweet` - Major engagement format
2. `get_tweet_context` - Context-aware replies
3. `follow_user` / `unfollow_user` - Network operations
4. `get_followers` / `get_following` - Relationship tracking

### Phase 2 (Intelligence) - Week 2
5. `get_likers` / `get_retweeters` - Engagement analysis
6. `get_user_likes` - Interest profiling
7. `get_quote_tweets` - Conversation tracking
8. `get_home_timeline` - Feed monitoring

### Phase 3 (Operations) - Week 3
9. `get_tweet_metrics` - Performance data
10. `unlike_tweet` / `unretweet` - Cleanup
11. `get_rate_limits` - Safety
12. `mute_user` / `block_user` - Moderation

### Phase 4 (Advanced) - Week 4
13. `get_lists` / `create_list` / `add_to_list` - Organization
14. `search_users` - Discovery
15. `bookmark_tweet` / `get_bookmarks` - Curation

---

## Impact Analysis

### Current Gaps Addressed

**Engagement:**
- ❌ → ✅ Quote tweet capability
- ❌ → ✅ Thread/conversation context
- ❌ → ✅ Engagement tracking (likers, retweeters)
- ❌ → ✅ Performance metrics

**Relationships:**
- ❌ → ✅ Follow/unfollow operations
- ❌ → ✅ Follower/following lists
- ❌ → ✅ User interest profiling
- ❌ → ✅ List management

**Operations:**
- ❌ → ✅ Home timeline monitoring
- ❌ → ✅ Rate limit awareness
- ❌ → ✅ User moderation (mute/block)
- ❌ → ✅ Account discovery

### Workflow Enhancements

**Before:** Tweet-centric operations (post, read, like)
**After:** Relationship-centric + context-aware operations

**Scripts Enabled:**
- `auto_reply_random.py` → Context-aware with `get_tweet_context`
- `follow_top_300.py` → Direct API via `follow_user`
- `monitor_timeline.py` → Real feed via `get_home_timeline`
- `engage_auto.py` → Better targeting via `get_likers` + `get_user_likes`
- List management scripts → Native via `create_list` / `add_to_list`

---

## Technical Considerations


### Error Handling
All tools should return structured errors:
```typescript
{
  success: false,
  error: {
    code: string,
    message: string,
    details?: any
  }
}
```

### Pagination
Tools returning lists should support cursor-based pagination via `pagination_token`.

---

## Conclusion

These 15 core tools (+5 bonus) transform the Twitter MCP from basic CRUD operations into a comprehensive engagement and relationship management platform. They directly support the BigSky agent's workflow for:

1. **Contextual engagement** (quote, thread context, conversation tracking)
2. **Relationship building** (follow, lists, interest profiling)
3. **Intelligence gathering** (likers, retweeters, metrics)
4. **Operational safety** (rate limits, moderation, cleanup)

All tools are practical Twitter API operations with clear implementation paths.
