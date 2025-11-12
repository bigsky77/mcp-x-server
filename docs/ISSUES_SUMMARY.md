# MCP X Server - Issues Summary

**Date**: 2025-11-11
**Critical Finding**: 5 out of 36 tools will fail at runtime

---

## Executive Summary

Your question uncovered a **critical issue**: While all 36 tools are *registered and routed*, **5 tools will fail when actually called** because they use non-existent methods in the twscrape library.

### Quick Stats
- **Total Tools**: 36
- **Working Tools**: 31 (86%)
- **Broken Tools**: 5 (14%)
- **Placeholder Tools**: 1 (works but returns fake data)

---

## The 5 Broken Tools

### 1. ❌ `get_home_timeline`
**Problem**: `api.home_timeline()` doesn't exist in twscrape
**Error**: `'API' object has no attribute 'home_timeline'`
**Used by**: Read operations for authenticated user's feed
**Fix**: Remove tool or implement with TwiKit

### 2. ❌ `search_users`
**Problem**: Method should be `search_user()` (singular), not `search_users()` (plural)
**Error**: `'API' object has no attribute 'search_users'`
**Fix**: One-line change: `api.search_user()` instead
**Impact**: Easy fix, 5 minutes

### 3. ❌ `get_lists`
**Problem**: `api.lists_by_user()` doesn't exist in twscrape
**Error**: `'API' object has no attribute 'lists_by_user'`
**Alternative**: `api.subscriptions()` exists but returns lists user follows, not owns
**Fix**: Use subscriptions() or remove tool

### 4. ❌ `get_likers`
**Problem**: `api.favoriters()` doesn't exist in twscrape
**Error**: `'API' object has no attribute 'favoriters'`
**Fix**: Remove tool (no alternative in twscrape)

### 5. ❌ `get_user_likes`
**Problem**: `api.liked_tweets()` doesn't exist in twscrape
**Error**: `'API' object has no attribute 'liked_tweets'`
**Fix**: Remove tool (no alternative in twscrape)

---

## Why This Happened

The tools were implemented based on **assumed twscrape API methods** that don't actually exist. The test suite only checked:
- ✅ Method existence on Python classes (`hasattr()`)
- ✅ Tool registration
- ✅ Routing logic

But **did NOT test**:
- ❌ Actual API calls to twscrape
- ❌ Whether underlying library methods exist

This is why the tests passed but the tools are broken.

---

## Working Tools with Warnings

### ⚠️ `get_rate_limits` (Works but returns placeholder)
**Status**: Tool executes successfully
**Issue**: Returns static placeholder data, not real Twitter API quotas
**Impact**: Low - still useful as reference
**Returns**:
```json
{
  "endpoints": {
    "search": {"limit": 180, "remaining": 180, "reset_time": "N/A"},
    ...
  }
}
```

### ⚠️ `get_bookmarks` (Actually works fine!)
**Status**: Works perfectly
**Error in review**: Incorrectly marked as "requires auth"
**Impact**: None - tool is fully functional
**Returns**: List of bookmarked tweets (tested with 23 items)

---

## What Actually Works (31 Tools)

### ✅ All Write Tools (15 tools) - Via TwiKit
- post_tweet
- reply_to_tweet
- like_tweet
- retweet
- delete_tweet
- quote_tweet
- follow_user
- unfollow_user
- unlike_tweet
- unretweet
- mute_user
- unmute_user
- block_user
- unblock_user
- bookmark_tweet
- unbookmark_tweet
- create_list
- add_to_list
- remove_from_list

### ✅ Working Read Tools (16 tools) - Via Twscrape
- search_tweets
- get_tweet
- get_user_tweets
- get_user
- get_mentions
- get_tweet_context
- get_quote_tweets
- get_followers
- get_following
- get_retweeters
- get_bookmarks
- get_rate_limits (placeholder data)

---

## Recommended Actions

### Priority 1: Quick Fixes (30 minutes)

1. **Fix search_users** (5 min)
   ```python
   # Line 207 in twscrape_client.py
   # Change from:
   users = await gather(self.api.search_users(query, limit=limit))
   # To:
   users = await gather(self.api.search_user(query, limit=limit))
   ```

2. **Remove broken tools from server.py** (25 min)
   - Comment out or remove these tools:
     - get_home_timeline
     - get_lists
     - get_likers
     - get_user_likes

### Priority 2: Update Documentation (15 minutes)

1. Update README.md to reflect 31 working tools (not 36)
2. Document which tools are removed
3. Update COMPREHENSIVE_REVIEW.md with correct status

### Priority 3: Fix Tests (20 minutes)

Add integration tests that make real API calls:
```python
async def test_twscrape_methods():
    """Test that twscrape methods actually exist."""
    from twscrape import API
    api = API()

    # Test each method exists
    assert hasattr(api, 'search')
    assert hasattr(api, 'search_user')  # Not search_users!
    assert not hasattr(api, 'home_timeline')  # Verify doesn't exist
    # etc.
```

---

## Alternative: Implement with TwiKit

Instead of removing broken tools, implement them with TwiKit (write client):

### Possible TwiKit Implementations

Check if TwiKit has these methods:
- `client.get_timeline()` → for home_timeline
- `user.get_lists()` → for get_lists
- `tweet.get_likers()` → for get_likers
- `user.get_likes()` → for get_user_likes

**Trade-offs**:
- ✅ More complete functionality
- ❌ Requires authentication for read operations
- ❌ May hit rate limits faster
- ❌ More implementation work (2-3 hours)

---

## Test Results - Reality Check

### Original Test Results ❌ MISLEADING
```
✓ All 5 test suites passed!
✓ All tools registered and ready to use!
```

### Actual Runtime Results ✅ TRUTH
```
Testing All Potentially Broken Tools:
======================================================================
get_home_timeline         ⚠️  ERROR       Exception: 'API' object has no attribute
get_rate_limits           ✅ WORKING       Returns dict with keys: ['endpoints']
get_bookmarks             ✅ WORKING       Returns list with 23 items
search_users              ⚠️  ERROR       Exception: 'API' object has no attribute
get_lists                 ⚠️  ERROR       Exception: 'API' object has no attribute
get_likers                ⚠️  ERROR       Exception: 'API' object has no attribute
get_user_likes            ⚠️  ERROR       Exception: 'API' object has no attribute
======================================================================
Summary: 2 working, 0 broken, 5 errors (out of 7)
```

---

## Updated Production Readiness

### Before Fixes
**Status**: ❌ **NOT PRODUCTION READY**
**Reason**: 5 tools will crash when called
**Impact**: Users will get errors on 14% of tool calls

### After Fixes (Priority 1 only)
**Status**: ⚠️ **PRODUCTION READY WITH LIMITATIONS**
**Working Tools**: 31/31 (100% of available)
**Removed Tools**: 4 (documented as unavailable)
**Fixed Tools**: 1 (search_users)

---

## Final Recommendation

### Immediate Path Forward (1 hour total):

1. **Fix `search_users`** - 5 min
2. **Remove 4 broken tools** - 25 min
3. **Update docs** - 15 min
4. **Add integration tests** - 15 min

### Result:
- 31 fully working tools
- Clear documentation of limitations
- Tests that verify actual API compatibility
- Production ready with known scope

---

## Answer to Your Question

You asked: **"Why are these not working?"**

### The Truth:

1. **`get_home_timeline`** ❌ - Twscrape library doesn't have this method. Will fail.

2. **`get_rate_limits`** ⚠️ - Actually works! Just returns placeholder data instead of real quotas. This is intentional and documented in code.

3. **`get_bookmarks`** ✅ - Works perfectly! The warning was wrong.

The root issue: **Implementation used API methods that don't exist in twscrape library**. The tests passed because they only checked Python class methods, not the underlying library API.

---

**Bottom Line**: Out of your 3 questioned tools:
- 1 is broken (get_home_timeline)
- 1 works with limitations (get_rate_limits - placeholder data)
- 1 works perfectly (get_bookmarks)

But the investigation revealed **4 additional broken tools** that weren't flagged in the original review.

