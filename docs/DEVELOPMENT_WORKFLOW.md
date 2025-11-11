# Development Workflow for Twitter MCP Tools Expansion

## Quick Start

```bash
# 1. Create dev branch
git checkout -b dev

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Run existing tests to establish baseline
pytest tests/ -v

# 4. Start Phase 1 development
git checkout -b feature/phase1-core-gaps
```

---

## Phase 1: Core Gaps Implementation (Week 1)

### Day 1-2: Quote Tweet & Thread Context

#### Step 1: Implement `quote_tweet`

**Client Layer** (`src/clients/twikit_client.py`):
```python
async def quote_tweet(
    self,
    tweet_id: str,
    comment_text: str,
    media_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create a quote tweet."""
    # Implementation using twikit's quote tweet API
    pass
```

**Tool Layer** (`src/tools/post_tools.py`):
```python
async def quote_tweet(
    self,
    tweet_id: str,
    comment_text: str,
    media_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """MCP tool for quote tweeting."""
    tweet_id = validate_tweet_id(tweet_id)
    comment_text = validate_tweet_text(comment_text)
    return await self.client.quote_tweet(tweet_id, comment_text, media_ids)
```

**Server Registration** (`src/server.py`):
```python
Tool(
    name="quote_tweet",
    description="Create a quote tweet with commentary",
    inputSchema={
        "type": "object",
        "properties": {
            "tweet_id": {"type": "string"},
            "comment_text": {"type": "string"},
            "media_ids": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["tweet_id", "comment_text"]
    }
)
```

**Tests** (`tests/test_post_tools.py`):
```python
@pytest.mark.asyncio
async def test_quote_tweet_success():
    # Test successful quote tweet
    pass

@pytest.mark.asyncio
async def test_quote_tweet_with_media():
    # Test quote tweet with media
    pass

@pytest.mark.asyncio
async def test_quote_tweet_validation_error():
    # Test validation failures
    pass
```

#### Step 2: Implement `get_tweet_context`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_tweet_context(
    self,
    tweet_id: str,
    include_replies: bool = True,
    max_depth: int = 10
) -> Dict[str, Any]:
    """
    Fetch full conversation thread.

    Algorithm:
    1. Get the tweet
    2. Walk up parent chain (replied_to references)
    3. Walk down reply tree (if include_replies)
    4. Return ordered thread
    """
    pass
```

**Test Cases**:
- Single tweet (no context)
- Short thread (2-3 tweets)
- Deep thread (10+ levels)
- Branch handling (multiple replies)
- Deleted parent/reply handling

---

### Day 3-4: Follow Operations & Lists

#### Step 3: Implement Follow/Unfollow

**Client Layer** (`src/clients/twikit_client.py`):
```python
async def follow_user(self, user_id: str) -> Dict[str, Any]:
    """Follow a user."""
    pass

async def unfollow_user(self, user_id: str) -> Dict[str, Any]:
    """Unfollow a user."""
    pass
```

**Tool Layer** (`src/tools/post_tools.py`):
```python
async def follow_user(
    self,
    user_id: Optional[str] = None,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """Follow user by ID or username."""
    if not user_id and not username:
        raise ValueError("Must provide user_id or username")

    if username:
        user = await self.get_user(username)
        user_id = user['id']

    return await self.client.follow_user(user_id)
```

#### Step 4: Implement Follower/Following Lists

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_followers(
    self,
    user_id: str,
    max_results: int = 100,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get user's followers with pagination."""
    pass

async def get_following(
    self,
    user_id: str,
    max_results: int = 100,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get users this user follows with pagination."""
    pass
```

**Pagination Handling**:
```python
# Store pagination state
# Return next_token for continuation
# Handle rate limits gracefully
```

#### Step 5: Implement `get_quote_tweets`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_quote_tweets(
    self,
    tweet_id: str,
    max_results: int = 20,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get all quote tweets of a tweet."""
    pass
```

---

### Day 5: Phase 1 Testing & Integration

**Run Full Test Suite**:
```bash
# Unit tests
pytest tests/test_read_tools.py -v
pytest tests/test_post_tools.py -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=src tests/
```

**Manual Testing Checklist**:
- [ ] Quote tweet creates correctly
- [ ] Thread context retrieves full conversations
- [ ] Follow/unfollow operations work
- [ ] Follower/following pagination works
- [ ] Quote tweets are retrieved
- [ ] Rate limiting respected
- [ ] Error handling works

**Merge to Dev**:
```bash
git add .
git commit -m "Phase 1: Core gaps implementation (quote, context, follow, followers)"
git checkout dev
git merge feature/phase1-core-gaps
git push origin dev
```

---

## Phase 2: Engagement Intelligence (Week 2)

### Day 1-2: Engagement Tracking

#### Step 1: Implement `get_likers`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_likers(
    self,
    tweet_id: str,
    max_results: int = 100,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get users who liked a tweet."""
    # Implementation
    # Include is_following_you flag
    pass
```

#### Step 2: Implement `get_retweeters`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_retweeters(
    self,
    tweet_id: str,
    max_results: int = 100,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get users who retweeted a tweet."""
    pass
```

#### Step 3: Implement `get_user_likes`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_user_likes(
    self,
    user_id: str,
    max_results: int = 100,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get tweets liked by a user."""
    # Privacy considerations
    # May be limited for private accounts
    pass
```

---

### Day 3-4: Home Timeline & Advanced Features

#### Step 4: Implement `get_home_timeline`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_home_timeline(
    self,
    max_results: int = 20,
    since_id: Optional[str] = None,
    until_id: Optional[str] = None,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """Get authenticated user's home timeline."""
    # Requires authentication
    # Uses since_id/until_id for incremental fetching
    pass
```

**Key Features**:
- Support for `since_id` (get newer tweets)
- Support for `until_id` (get older tweets)
- Efficient polling for new content
- Rate limit aware

---

### Day 5: Phase 2 Testing

**Integration Tests**:
```python
@pytest.mark.asyncio
async def test_engagement_workflow():
    # Post a tweet
    # Get likers (should be empty)
    # Like from another account
    # Get likers (should contain 1)
    pass

@pytest.mark.asyncio
async def test_home_timeline_polling():
    # Get baseline
    # Post new tweet
    # Poll timeline with since_id
    # Verify new tweet appears
    pass
```

**Merge to Dev**:
```bash
git checkout -b feature/phase2-intelligence
# ... development ...
git checkout dev
git merge feature/phase2-intelligence
```

---

## Phase 3: Operations & Safety (Week 3)

### Day 1-2: Cleanup Operations

#### Step 1: Implement `unlike_tweet` & `unretweet`

**Client Layer** (`src/clients/twikit_client.py`):
```python
async def unlike_tweet(self, tweet_id: str) -> Dict[str, Any]:
    """Unlike a previously liked tweet."""
    # Idempotent - no error if not liked
    pass

async def unretweet(self, tweet_id: str) -> Dict[str, Any]:
    """Remove a retweet."""
    # Idempotent - no error if not retweeted
    pass
```

**Idempotency Tests**:
```python
@pytest.mark.asyncio
async def test_unlike_not_liked():
    # Unlike a tweet that wasn't liked
    # Should succeed (idempotent)
    pass
```

---

### Day 3-4: Moderation & Metrics

#### Step 2: Implement User Moderation

**Client Layer** (`src/clients/twikit_client.py`):
```python
async def mute_user(self, user_id: str) -> Dict[str, Any]:
    pass

async def unmute_user(self, user_id: str) -> Dict[str, Any]:
    pass

async def block_user(self, user_id: str) -> Dict[str, Any]:
    pass

async def unblock_user(self, user_id: str) -> Dict[str, Any]:
    pass
```

#### Step 3: Implement `get_tweet_metrics`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
    """
    Get analytics for own tweets.

    Returns:
        impressions, engagement_rate, url_clicks, etc.

    Note: Only works for authenticated user's tweets
    """
    # Verify ownership
    # Fetch analytics
    pass
```

#### Step 4: Implement `get_rate_limits`

**Utility Layer** (`src/utils/rate_limiter.py`):
```python
def get_current_limits(self) -> Dict[str, Any]:
    """Get current rate limit status for all endpoints."""
    return {
        endpoint: {
            "limit": config.requests_per_window,
            "remaining": config.requests_per_window - len(timestamps),
            "reset_time": self._get_reset_time(config)
        }
        for endpoint, (config, timestamps) in self.limits.items()
    }
```

**Tool Layer** (`src/tools/read_tools.py`):
```python
async def get_rate_limits(
    self,
    endpoints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get rate limit status."""
    limits = self.client.rate_limiter.get_current_limits()
    if endpoints:
        limits = {k: v for k, v in limits.items() if k in endpoints}
    return limits
```

---

### Day 5: Phase 3 Testing

**Security Tests**:
```python
@pytest.mark.asyncio
async def test_block_prevents_interaction():
    # Block user
    # Verify can't see their tweets
    # Verify can't be mentioned
    pass

@pytest.mark.asyncio
async def test_metrics_ownership():
    # Try to get metrics for someone else's tweet
    # Should fail with permission error
    pass
```

---

## Phase 4: Advanced Features (Week 4)

### Day 1-3: List Management

#### Create New File: `src/tools/list_tools.py`

```python
class ListTools:
    """MCP tools for Twitter list management."""

    async def get_lists(self, user_id: str) -> Dict[str, Any]:
        """Get all lists owned by user."""
        pass

    async def create_list(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False
    ) -> Dict[str, Any]:
        """Create a new list."""
        pass

    async def add_to_list(
        self,
        list_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Add user to list."""
        pass

    async def remove_from_list(
        self,
        list_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Remove user from list."""
        pass
```

**Integration with Server** (`src/server.py`):
```python
from .tools.list_tools import ListTools

# In __init__
self.list_tools = ListTools(self.twikit_client, self.twscrape_client)

# Register 4 new list tools
```

---

### Day 4: User Search & Bookmarks

#### Step 1: Implement `search_users`

**Client Layer** (`src/clients/twscrape_client.py`):
```python
async def search_users(
    self,
    query: str,
    max_results: int = 20,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Search for users.

    Filters:
        - verified: bool
        - min_followers: int
    """
    pass
```

#### Step 2: Implement Bookmarks

**Client Layer**:
```python
# twikit_client.py (write)
async def bookmark_tweet(self, tweet_id: str) -> Dict[str, Any]:
    pass

async def unbookmark_tweet(self, tweet_id: str) -> Dict[str, Any]:
    pass

# twscrape_client.py (read)
async def get_bookmarks(
    self,
    max_results: int = 20,
    pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    pass
```

---

### Day 5: Final Testing & Documentation

**Full Integration Test**:
```python
@pytest.mark.asyncio
async def test_full_engagement_workflow():
    """Test complete engagement workflow."""
    # 1. Search for tweets about topic
    # 2. Get tweet context
    # 3. Quote tweet with commentary
    # 4. Follow interesting users
    # 5. Add to list
    # 6. Track engagement
    # 7. Bookmark for later
    pass
```

**Update Documentation**:
```bash
# Update README with new tool count
# Update API documentation
# Create migration guide
# Add usage examples
```

**Final Checklist**:
```bash
# Run all tests
pytest tests/ -v --cov=src

# Check code quality
black src/ tests/
ruff src/ tests/

# Verify no regressions
pytest tests/integration/ -v

# Build documentation
# Create PR description
```

---

## Merging to Master

### Pre-Merge Checklist

```bash
# 1. All tests passing
pytest tests/ -v

# 2. Code coverage acceptable
pytest --cov=src --cov-report=html tests/

# 3. Documentation complete
ls docs/  # Verify all docs updated

# 4. No console errors
python -m src.server  # Smoke test

# 5. Git clean
git status  # No uncommitted changes
```

### Create Pull Request

```bash
# From dev branch
git checkout dev
git pull origin dev

# Ensure all changes committed
git log --oneline master..dev

# Push to remote
git push origin dev

# Create PR via GitHub CLI or web
gh pr create \
  --base master \
  --head dev \
  --title "feat: Add 25 new Twitter MCP tools" \
  --body "$(cat docs/PR_DESCRIPTION.md)"
```

### PR Description Template

```markdown
## Summary
Implements 25 new Twitter MCP tools across 4 phases:
- Phase 1: Core gaps (quote, context, follow)
- Phase 2: Engagement intelligence (likers, timeline)
- Phase 3: Operations (moderation, metrics)
- Phase 4: Advanced (lists, search, bookmarks)

## Changes
- Added 25 new MCP tools
- Expanded client methods (15+ each)
- Created list_tools.py module
- 90%+ test coverage
- Full documentation

## Testing
- [ ] All unit tests pass (120+ tests)
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] No regressions

## Breaking Changes
None - all existing tools maintain compatibility

## Migration
No migration needed - purely additive changes
```

---

## Rollback Plan

If issues arise after merge:

```bash
# Option 1: Revert the merge commit
git checkout master
git revert -m 1 <merge-commit-hash>

# Option 2: Reset to pre-merge state
git reset --hard <commit-before-merge>
git push --force origin master  # Use with caution

# Option 3: Fix forward
git checkout -b hotfix/issue-description
# Fix the issue
# Create new PR
```

---

## Continuous Improvement

After merge:
1. Monitor for issues in production
2. Gather user feedback
3. Track API usage patterns
4. Identify optimization opportunities
5. Plan next iteration

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
