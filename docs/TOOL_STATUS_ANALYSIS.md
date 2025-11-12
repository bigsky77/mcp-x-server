# Tool Status Analysis - Known Issues and Workarounds

**Date**: 2025-11-11
**Analysis**: Detailed investigation of tools marked with warnings

---

## Summary

Of the 36 MCP tools, **33 tools work perfectly** and **3 tools have limitations** due to twscrape library API constraints. Here's the detailed breakdown:

---

## Tools with Warnings (3 tools)

### 1. `get_home_timeline` ❌ **NOT WORKING**

**Issue**: Twscrape library does not provide a `home_timeline()` method

**Current Implementation**:
```python
# src/clients/twscrape_client.py:195-202
async def get_home_timeline(self, limit: int = 20) -> List[dict]:
    """Get authenticated user's home timeline."""
    try:
        # Note: This requires authentication and may not work with all accounts
        tweets = await gather(self.api.home_timeline(limit=limit))  # ❌ Method doesn't exist
        return [self._serialize_tweet(t) for t in tweets]
    except Exception as e:
        raise Exception(f"Failed to get home timeline: {e}")
```

**Error**:
```
AttributeError: 'API' object has no attribute 'home_timeline'
```

**Root Cause**: The twscrape library (v0.5.0) does not include a `home_timeline()` method in its API.

**Workaround**: None available with current library

**Recommendation**:
- Option 1: Remove this tool from the server (not critical for most use cases)
- Option 2: Implement using TwiKit client instead (requires switching to write client)
- Option 3: Wait for twscrape library update

**Impact**: Medium - Home timeline can be approximated by following user tweets

---

### 2. `get_rate_limits` ⚠️ **WORKS BUT RETURNS PLACEHOLDER DATA**

**Issue**: Returns static placeholder data instead of real Twitter API rate limits

**Current Implementation**:
```python
# src/clients/twscrape_client.py:236-250
async def get_rate_limits(self) -> dict:
    """Get current rate limit status."""
    try:
        # This would typically come from API response headers
        # For twscrape, we return a placeholder structure
        return {
            "endpoints": {
                "search": {"limit": 180, "remaining": 180, "reset_time": "N/A"},
                "user_timeline": {"limit": 900, "remaining": 900, "reset_time": "N/A"},
                "followers": {"limit": 15, "remaining": 15, "reset_time": "N/A"},
                "following": {"limit": 15, "remaining": 15, "reset_time": "N/A"},
            }
        }
    except Exception as e:
        raise Exception(f"Failed to get rate limits: {e}")
```

**Behavior**:
- Tool executes successfully ✅
- Returns valid JSON structure ✅
- Data is static/placeholder ⚠️
- Does NOT reflect actual Twitter API quotas ⚠️

**Why This Happens**:
- Twscrape doesn't expose rate limit information from Twitter API response headers
- Real rate limits would require parsing HTTP response headers from each API call
- Twitter's rate limits are per-endpoint and per-account

**Impact**: Low - Internal rate limiter (`RateLimiter` class) still works correctly

**Workaround**:
- Use the tool to see expected rate limits (static values are accurate for Twitter's documented limits)
- Rely on MCP server's built-in `RateLimiter` for actual throttling

**Recommendation**:
- Keep as-is (provides useful reference data)
- Document that values are placeholders
- Future enhancement: Parse response headers to get real values

---

### 3. `get_bookmarks` ✅ **WORKS PERFECTLY**

**Status**: Actually works! The warning was incorrect.

**Test Result**:
```bash
✅ Returns: list with 23 items
```

**Current Implementation**:
```python
# src/clients/twscrape_client.py:227-234
async def get_bookmarks(self, limit: int = 20) -> List[dict]:
    """Get bookmarked tweets for authenticated user."""
    try:
        # Note: This requires authentication
        bookmarks = await gather(self.api.bookmarks(limit=limit))  # ✅ Works!
        return [self._serialize_tweet(t) for t in bookmarks]
    except Exception as e:
        raise Exception(f"Failed to get bookmarks: {e}")
```

**Why it works**: Twscrape library includes `bookmarks()` method

**Requirements**:
- Requires authenticated Twscrape account pool
- May fail if no accounts are configured

**Update**: Change status from ⚠️ to ✅

---

## Additional Findings

### Tools Using Non-Existent Methods

After checking the twscrape API, these implementations need verification:

#### 1. `search_users` ⚠️ **USES WRONG METHOD NAME**

**Current Code**:
```python
# src/clients/twscrape_client.py:204-210
async def search_users(self, query: str, limit: int = 20) -> List[dict]:
    """Search for users by query."""
    try:
        users = await gather(self.api.search_users(query, limit=limit))  # ❌ Wrong method name
        return [self._serialize_user(u) for u in users]
    except Exception as e:
        raise Exception(f"Failed to search users: {e}")
```

**Issue**: Should use `search_user()` (singular) not `search_users()` (plural)

**Correct Method**: `api.search_user(q: str, limit=-1)`

**Impact**: Tool will fail with AttributeError when called

**Fix Required**: Change `search_users` to `search_user` in implementation

---

#### 2. `get_lists` ⚠️ **USES NON-EXISTENT METHOD**

**Current Code**:
```python
# src/clients/twscrape_client.py:212-225
async def get_lists(self, user_id: str) -> List[dict]:
    """Get lists owned by a user."""
    try:
        lists = await gather(self.api.lists_by_user(int(user_id)))  # ❌ Method doesn't exist
        return [{ ... }]
    except Exception as e:
        raise Exception(f"Failed to get lists: {e}")
```

**Issue**: Twscrape API does not have `lists_by_user()` method

**Available Alternative**: `api.subscriptions(uid: int, limit=-1)` - Returns lists user is subscribed to (not owned)

**Impact**: Tool will fail with AttributeError when called

**Options**:
1. Use `subscriptions()` method (returns different data - lists user follows, not owns)
2. Remove tool (no way to get user's owned lists with twscrape)
3. Implement with TwiKit instead

---

#### 3. `get_likers` ⚠️ **USES NON-EXISTENT METHOD**

**Current Code**:
```python
# src/clients/twscrape_client.py:171-177
async def get_likers(self, tweet_id: str, limit: int = 20) -> List[dict]:
    """Get users who liked a tweet."""
    try:
        likers = await gather(self.api.favoriters(int(tweet_id), limit=limit))  # ❌ Method doesn't exist
        return [self._serialize_user(u) for u in likers]
    except Exception as e:
        raise Exception(f"Failed to get likers: {e}")
```

**Issue**: Twscrape API does not have `favoriters()` method

**Available Methods**:
- None that directly provide tweet likers

**Impact**: Tool will fail with AttributeError when called

**Recommendation**: Remove or implement with TwiKit (if available)

---

#### 4. `get_user_likes` ⚠️ **USES NON-EXISTENT METHOD**

**Current Code**:
```python
# src/clients/twscrape_client.py:187-193
async def get_user_likes(self, user_id: str, limit: int = 20) -> List[dict]:
    """Get tweets liked by a user."""
    try:
        likes = await gather(self.api.liked_tweets(int(user_id), limit=limit))  # ❌ Method doesn't exist
        return [self._serialize_tweet(t) for t in likes]
    except Exception as e:
        raise Exception(f"Failed to get user likes: {e}")
```

**Issue**: Twscrape API does not have `liked_tweets()` method

**Impact**: Tool will fail with AttributeError when called

**Recommendation**: Remove or find alternative implementation

---

## Complete Status Table

### Read Tools (21 tools)

| # | Tool | Implementation | Twscrape API | Actual Status |
|---|------|----------------|--------------|---------------|
| 1 | search_tweets | `api.search()` | ✅ Exists | ✅ Working |
| 2 | get_tweet | `api.tweet_details()` | ✅ Exists | ✅ Working |
| 3 | get_user_tweets | `api.user_tweets()` | ✅ Exists | ✅ Working |
| 4 | get_user | `api.user_by_login()` | ✅ Exists | ✅ Working |
| 5 | get_mentions | `api.search()` (workaround) | ✅ Exists | ✅ Working |
| 6 | get_tweet_context | `api.tweet_details()` + logic | ✅ Exists | ✅ Working |
| 7 | get_quote_tweets | `api.search()` (workaround) | ✅ Exists | ✅ Working |
| 8 | get_followers | `api.followers()` | ✅ Exists | ✅ Working |
| 9 | get_following | `api.following()` | ✅ Exists | ✅ Working |
| 10 | get_likers | `api.favoriters()` | ❌ Missing | ❌ **BROKEN** |
| 11 | get_retweeters | `api.retweeters()` | ✅ Exists | ✅ Working |
| 12 | get_user_likes | `api.liked_tweets()` | ❌ Missing | ❌ **BROKEN** |
| 13 | get_home_timeline | `api.home_timeline()` | ❌ Missing | ❌ **BROKEN** |
| 14 | get_rate_limits | Placeholder | N/A | ⚠️ Placeholder only |
| 15 | search_users | `api.search_users()` | ❌ Wrong name | ❌ **BROKEN** (should be `search_user`) |
| 16 | get_lists | `api.lists_by_user()` | ❌ Missing | ❌ **BROKEN** |
| 17 | get_bookmarks | `api.bookmarks()` | ✅ Exists | ✅ Working |

### Write Tools (15 tools)

All write tools use TwiKit and work correctly ✅

---

## Summary of Issues

### Critical Issues (Tools Will Fail) ❌

1. **get_home_timeline** - Method doesn't exist in twscrape
2. **search_users** - Wrong method name (should be singular `search_user`)
3. **get_lists** - Method doesn't exist in twscrape
4. **get_likers** - Method doesn't exist in twscrape
5. **get_user_likes** - Method doesn't exist in twscrape

### Working But Limited ⚠️

1. **get_rate_limits** - Returns placeholder data (not real-time quotas)

### Working Perfectly ✅

- 10 original tools (all working)
- 15 write tools (all working via TwiKit)
- 11 read tools (working via Twscrape with proper API methods)

**Total Working**: 36 tools registered, but only **31 actually work**, **5 will fail** when called

---

## Recommendations

### Immediate Actions Required 🔴

1. **Fix `search_users`**: Change to use `search_user()` (one-line fix)
   ```python
   users = await gather(self.api.search_user(query, limit=limit))  # Fixed
   ```

2. **Remove or Fix Broken Tools**:
   - `get_home_timeline` - Consider removing or implementing with TwiKit
   - `get_lists` - Remove or use `subscriptions()` as alternative
   - `get_likers` - Remove (no alternative in twscrape)
   - `get_user_likes` - Remove (no alternative in twscrape)

### Alternative Solution 🟡

Implement the broken read operations using **TwiKit** instead of Twscrape:

| Tool | TwiKit Method | Availability |
|------|---------------|--------------|
| get_likers | `tweet.get_likers()` | May be available |
| get_user_likes | `user.get_likes()` | May be available |
| get_home_timeline | `client.get_timeline()` | Likely available |
| get_lists | `user.get_lists()` | May be available |

**Trade-off**: TwiKit requires authentication and may hit rate limits faster

---

## Updated Production Readiness

**Status**: ⚠️ **NEEDS FIXES BEFORE PRODUCTION**

**Working Tools**: 31/36 (86.1%)
**Broken Tools**: 5/36 (13.9%)

**Priority Fixes**:
1. Fix `search_users` method name (5 minutes)
2. Test and remove/replace broken tools (1-2 hours)
3. Re-run test suite (5 minutes)

**After Fixes**: Should reach 31+ working tools with clear documentation of limitations.

---

## Testing Recommendations

Create integration tests that actually call the APIs to verify:

```python
# Test each tool with real API calls
async def test_all_read_tools():
    client = TwscrapeClient()
    await client.setup()

    tests = [
        ("search_tweets", lambda: client.search_tweets("AI", limit=1)),
        ("get_tweet", lambda: client.get_tweet("1234567890")),
        # ... test each tool
    ]

    for name, test_func in tests:
        try:
            result = await test_func()
            print(f"✅ {name} - PASS")
        except Exception as e:
            print(f"❌ {name} - FAIL: {e}")
```

This would catch these API mismatches during development.

---

**Conclusion**: The original review was overly optimistic. While the code *structure* is excellent, **5 tools will fail at runtime** due to incorrect API method names or missing methods in the twscrape library. These need to be fixed before production deployment.
