# Testing Plan for Twitter MCP Tools Expansion

## Overview
Comprehensive testing strategy for 25 new Twitter MCP tools ensuring quality, reliability, and maintainability.

## Testing Pyramid

```
        /\
       /E2E\         5% - End-to-End (Full workflows)
      /------\
     /Integration\   25% - Integration (API interactions)
    /------------\
   /    Unit      \  70% - Unit (Individual functions)
  /----------------\
```

---

## Test Categories

### 1. Unit Tests (70% of tests)

**Purpose**: Test individual functions in isolation

**Files to Create/Expand**:
- `tests/test_read_tools.py`
- `tests/test_post_tools.py`
- `tests/test_list_tools.py`
- `tests/test_validators.py`
- `tests/test_clients.py`

**Mocking Strategy**:
```python
# Mock external API calls
@pytest.fixture
def mock_twikit_client():
    with patch('src.clients.twikit_client.TwiKitClient') as mock:
        yield mock

# Example test
@pytest.mark.asyncio
async def test_quote_tweet(mock_twikit_client):
    mock_twikit_client.quote_tweet.return_value = {
        "created_tweet_id": "123",
        "url": "https://x.com/user/status/123",
        "success": True
    }

    tools = WriteTools(mock_twikit_client)
    result = await tools.quote_tweet("456", "Great point!")

    assert result["success"] == True
    assert result["created_tweet_id"] == "123"
```

---

### 2. Integration Tests (25% of tests)

**Purpose**: Test interactions between components and real API calls

**Files to Create**:
- `tests/integration/test_quote_workflows.py`
- `tests/integration/test_thread_context.py`
- `tests/integration/test_follow_workflows.py`
- `tests/integration/test_engagement_tracking.py`
- `tests/integration/test_list_management.py`

**Setup Requirements**:
```python
# tests/integration/conftest.py
import pytest
from src.clients.twikit_client import TwiKitClient
from src.clients.twscrape_client import TwscrapeClient

@pytest.fixture(scope="session")
async def real_twikit_client():
    """Real TwiKit client for integration tests."""
    # Use test account credentials
    client = TwiKitClient(cookies_file="config/test_cookies.json")
    yield client
    # Cleanup if needed

@pytest.fixture(scope="session")
async def real_twscrape_client():
    """Real Twscrape client for integration tests."""
    client = TwscrapeClient(accounts_file="config/test_accounts.txt")
    await client.setup()
    yield client
```

**Example Integration Test**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_tweet_workflow(real_twikit_client):
    """Test complete quote tweet workflow."""
    # 1. Find a tweet to quote
    read_tools = ReadTools(real_twscrape_client)
    tweets = await read_tools.search_tweets("python", limit=1)
    original_tweet = tweets[0]

    # 2. Quote it
    write_tools = WriteTools(real_twikit_client)
    result = await write_tools.quote_tweet(
        original_tweet["id"],
        "Testing quote tweet functionality"
    )

    assert result["success"] == True
    assert "created_tweet_id" in result

    # 3. Verify quote tweet exists
    quote_tweet = await read_tools.get_tweet(result["created_tweet_id"])
    assert quote_tweet is not None

    # 4. Cleanup - delete quote tweet
    await write_tools.delete_tweet(result["created_tweet_id"])
```

---

### 3. End-to-End Tests (5% of tests)

**Purpose**: Test complete user workflows

**Files to Create**:
- `tests/e2e/test_engagement_strategy.py`
- `tests/e2e/test_relationship_building.py`

**Example E2E Test**:
```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_engagement_strategy():
    """
    Simulates a complete engagement strategy:
    1. Search for relevant tweets
    2. Get tweet context
    3. Reply with context-aware response
    4. Follow engaging users
    5. Add to segmented lists
    6. Track engagement metrics
    """
    # Setup
    server = MCPXServer()

    # 1. Search for tweets
    tweets = await server.read_tools.search_tweets("#AI", limit=5)
    assert len(tweets) > 0

    # 2. Get context for first tweet
    tweet = tweets[0]
    context = await server.read_tools.get_tweet_context(tweet["id"])
    assert "full_thread" in context

    # 3. Reply with context
    reply = await server.write_tools.reply_to_tweet(
        tweet["id"],
        "Interesting perspective on AI!"
    )
    assert reply["success"] == True

    # 4. Follow the author
    follow_result = await server.write_tools.follow_user(
        username=tweet["author"]["username"]
    )
    assert follow_result["relationship_status"] == "following"

    # 5. Add to "AI Thought Leaders" list
    list_result = await server.list_tools.add_to_list(
        "ai_thought_leaders",
        tweet["author"]["id"]
    )
    assert list_result["success"] == True

    # 6. Track engagement on our reply
    await asyncio.sleep(60)  # Wait for engagement
    likers = await server.read_tools.get_likers(reply["created_tweet_id"])
    # Assert likers data structure

    # Cleanup
    await server.write_tools.delete_tweet(reply["created_tweet_id"])
    await server.write_tools.unfollow_user(username=tweet["author"]["username"])
```

---

## Test Coverage Targets

### By Module

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| `src/tools/read_tools.py` | 95% | Critical |
| `src/tools/post_tools.py` | 95% | Critical |
| `src/tools/list_tools.py` | 90% | High |
| `src/clients/twikit_client.py` | 85% | High |
| `src/clients/twscrape_client.py` | 85% | High |
| `src/utils/validators.py` | 100% | Critical |
| `src/utils/rate_limiter.py` | 90% | High |
| `src/server.py` | 80% | Medium |

### Overall Target: 90%+

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term tests/

# View HTML report
open htmlcov/index.html
```

---

## Test Fixtures

### Mock Data Fixtures

**File**: `tests/fixtures/mock_data.py`

```python
"""Mock data for testing."""

MOCK_TWEET = {
    "id": "1234567890",
    "text": "This is a test tweet",
    "author": {
        "id": "9876543210",
        "username": "testuser",
        "name": "Test User",
        "follower_count": 1000
    },
    "created_at": "2025-11-11T12:00:00Z",
    "metrics": {
        "likes": 10,
        "retweets": 5,
        "replies": 3,
        "quotes": 2
    }
}

MOCK_CONVERSATION_THREAD = {
    "conversation_id": "1111111111",
    "parent_tweets": [
        {"id": "1111111111", "text": "Original tweet", "author": {...}},
        {"id": "2222222222", "text": "First reply", "author": {...}}
    ],
    "replies": [
        {"id": "3333333333", "text": "Reply 1", "author": {...}},
        {"id": "4444444444", "text": "Reply 2", "author": {...}}
    ],
    "full_thread": [...]  # Ordered chronologically
}

MOCK_USER = {
    "id": "9876543210",
    "username": "testuser",
    "name": "Test User",
    "bio": "Test bio",
    "follower_count": 1000,
    "following_count": 500,
    "tweet_count": 5000,
    "verified": False
}

MOCK_FOLLOWERS = {
    "users": [
        {"id": "111", "username": "follower1", ...},
        {"id": "222", "username": "follower2", ...},
    ],
    "next_token": "abc123",
    "total_count": 250
}

# ... more mock data
```

### Database Fixtures

**File**: `tests/fixtures/database.py`

```python
@pytest.fixture(scope="function")
def test_db():
    """Create temporary test database."""
    db_path = "test_accounts.db"

    # Create test DB
    conn = sqlite3.connect(db_path)
    # Setup schema
    # Insert test data

    yield conn

    # Cleanup
    conn.close()
    os.remove(db_path)
```

---

## Test Scenarios by Tool

### Phase 1: Core Gaps

#### 1. Quote Tweet Tests

**File**: `tests/unit/test_quote_tweet.py`

```python
class TestQuoteTweet:
    @pytest.mark.asyncio
    async def test_quote_tweet_success(self):
        """Test successful quote tweet creation."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_with_media(self):
        """Test quote tweet with media attachments."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_text_validation(self):
        """Test tweet text validation (280 char limit)."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_invalid_id(self):
        """Test error handling for invalid tweet ID."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_deleted_tweet(self):
        """Test quoting a deleted tweet."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_private_account(self):
        """Test quoting tweet from private account."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweet_rate_limit(self):
        """Test rate limiting behavior."""
        pass
```

#### 2. Thread Context Tests

**File**: `tests/unit/test_thread_context.py`

```python
class TestThreadContext:
    @pytest.mark.asyncio
    async def test_single_tweet_no_context(self):
        """Test tweet with no replies or parents."""
        pass

    @pytest.mark.asyncio
    async def test_short_thread(self):
        """Test 2-3 tweet thread."""
        pass

    @pytest.mark.asyncio
    async def test_deep_thread(self):
        """Test thread with 10+ levels."""
        pass

    @pytest.mark.asyncio
    async def test_thread_with_branches(self):
        """Test thread with multiple reply branches."""
        pass

    @pytest.mark.asyncio
    async def test_deleted_parent_handling(self):
        """Test handling of deleted parent tweets."""
        pass

    @pytest.mark.asyncio
    async def test_max_depth_limit(self):
        """Test max_depth parameter enforcement."""
        pass

    @pytest.mark.asyncio
    async def test_include_replies_false(self):
        """Test with include_replies=False."""
        pass

    @pytest.mark.asyncio
    async def test_thread_ordering(self):
        """Test that full_thread is ordered chronologically."""
        pass
```

#### 3. Follow/Unfollow Tests

**File**: `tests/unit/test_follow_operations.py`

```python
class TestFollowOperations:
    @pytest.mark.asyncio
    async def test_follow_by_user_id(self):
        """Test following user by ID."""
        pass

    @pytest.mark.asyncio
    async def test_follow_by_username(self):
        """Test following user by username."""
        pass

    @pytest.mark.asyncio
    async def test_follow_already_following(self):
        """Test idempotency - following already followed user."""
        pass

    @pytest.mark.asyncio
    async def test_unfollow_user(self):
        """Test unfollowing user."""
        pass

    @pytest.mark.asyncio
    async def test_unfollow_not_following(self):
        """Test unfollowing user not currently followed."""
        pass

    @pytest.mark.asyncio
    async def test_follow_private_account(self):
        """Test following private account (sends request)."""
        pass

    @pytest.mark.asyncio
    async def test_follow_blocked_user(self):
        """Test error when trying to follow blocked user."""
        pass
```

#### 4. Followers/Following Tests

**File**: `tests/unit/test_followers.py`

```python
class TestFollowerLists:
    @pytest.mark.asyncio
    async def test_get_followers_default(self):
        """Test getting followers with default params."""
        pass

    @pytest.mark.asyncio
    async def test_get_followers_pagination(self):
        """Test pagination through large follower list."""
        pass

    @pytest.mark.asyncio
    async def test_get_followers_max_results(self):
        """Test max_results parameter."""
        pass

    @pytest.mark.asyncio
    async def test_get_following(self):
        """Test getting following list."""
        pass

    @pytest.mark.asyncio
    async def test_followers_private_account(self):
        """Test getting followers of private account."""
        pass

    @pytest.mark.asyncio
    async def test_followers_suspended_account(self):
        """Test error handling for suspended account."""
        pass
```

#### 5. Quote Tweets Discovery Tests

**File**: `tests/unit/test_quote_tweets.py`

```python
class TestQuoteTweetsDiscovery:
    @pytest.mark.asyncio
    async def test_get_quote_tweets(self):
        """Test retrieving quote tweets."""
        pass

    @pytest.mark.asyncio
    async def test_no_quote_tweets(self):
        """Test tweet with no quotes."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweets_pagination(self):
        """Test paginating through many quotes."""
        pass

    @pytest.mark.asyncio
    async def test_quote_tweets_ordering(self):
        """Test that quotes are ordered by time."""
        pass
```

---

### Phase 2: Engagement Intelligence

#### 6. Engagement Tracking Tests

**File**: `tests/unit/test_engagement_tracking.py`

```python
class TestEngagementTracking:
    @pytest.mark.asyncio
    async def test_get_likers(self):
        """Test getting users who liked a tweet."""
        pass

    @pytest.mark.asyncio
    async def test_get_likers_includes_following_status(self):
        """Test that is_following_you flag is included."""
        pass

    @pytest.mark.asyncio
    async def test_get_retweeters(self):
        """Test getting retweeters."""
        pass

    @pytest.mark.asyncio
    async def test_get_user_likes(self):
        """Test getting tweets liked by user."""
        pass

    @pytest.mark.asyncio
    async def test_get_user_likes_private_account(self):
        """Test privacy handling for private accounts."""
        pass
```

#### 7. Home Timeline Tests

**File**: `tests/unit/test_home_timeline.py`

```python
class TestHomeTimeline:
    @pytest.mark.asyncio
    async def test_get_home_timeline_default(self):
        """Test getting home timeline with defaults."""
        pass

    @pytest.mark.asyncio
    async def test_home_timeline_since_id(self):
        """Test polling for new tweets with since_id."""
        pass

    @pytest.mark.asyncio
    async def test_home_timeline_until_id(self):
        """Test getting older tweets with until_id."""
        pass

    @pytest.mark.asyncio
    async def test_home_timeline_pagination(self):
        """Test pagination through timeline."""
        pass
```

---

### Phase 3: Operations

#### 8. Cleanup Operations Tests

**File**: `tests/unit/test_cleanup_operations.py`

```python
class TestCleanupOperations:
    @pytest.mark.asyncio
    async def test_unlike_tweet(self):
        """Test unliking a tweet."""
        pass

    @pytest.mark.asyncio
    async def test_unlike_not_liked(self):
        """Test idempotency - unlike not-liked tweet."""
        pass

    @pytest.mark.asyncio
    async def test_unretweet(self):
        """Test removing a retweet."""
        pass

    @pytest.mark.asyncio
    async def test_unretweet_not_retweeted(self):
        """Test idempotency - unretweet not-retweeted."""
        pass
```

#### 9. Moderation Tests

**File**: `tests/unit/test_moderation.py`

```python
class TestModeration:
    @pytest.mark.asyncio
    async def test_mute_user(self):
        """Test muting a user."""
        pass

    @pytest.mark.asyncio
    async def test_unmute_user(self):
        """Test unmuting a user."""
        pass

    @pytest.mark.asyncio
    async def test_block_user(self):
        """Test blocking a user."""
        pass

    @pytest.mark.asyncio
    async def test_unblock_user(self):
        """Test unblocking a user."""
        pass

    @pytest.mark.asyncio
    async def test_block_prevents_interaction(self):
        """Test that blocking prevents seeing tweets."""
        pass
```

#### 10. Rate Limits Tests

**File**: `tests/unit/test_rate_limits.py`

```python
class TestRateLimits:
    @pytest.mark.asyncio
    async def test_get_rate_limits_all(self):
        """Test getting all rate limits."""
        pass

    @pytest.mark.asyncio
    async def test_get_rate_limits_filtered(self):
        """Test filtering specific endpoints."""
        pass

    @pytest.mark.asyncio
    async def test_rate_limit_calculation(self):
        """Test remaining count calculation."""
        pass

    @pytest.mark.asyncio
    async def test_reset_time_accuracy(self):
        """Test reset_time is accurate."""
        pass
```

#### 11. Metrics Tests

**File**: `tests/unit/test_metrics.py`

```python
class TestMetrics:
    @pytest.mark.asyncio
    async def test_get_tweet_metrics_own_tweet(self):
        """Test getting metrics for own tweet."""
        pass

    @pytest.mark.asyncio
    async def test_get_tweet_metrics_not_owner(self):
        """Test error when getting metrics for others' tweets."""
        pass

    @pytest.mark.asyncio
    async def test_metrics_data_structure(self):
        """Test that all expected metrics are returned."""
        pass
```

---

### Phase 4: Advanced Features

#### 12. List Management Tests

**File**: `tests/unit/test_list_management.py`

```python
class TestListManagement:
    @pytest.mark.asyncio
    async def test_create_list(self):
        """Test creating a new list."""
        pass

    @pytest.mark.asyncio
    async def test_create_private_list(self):
        """Test creating private list."""
        pass

    @pytest.mark.asyncio
    async def test_get_lists(self):
        """Test getting user's lists."""
        pass

    @pytest.mark.asyncio
    async def test_add_to_list(self):
        """Test adding user to list."""
        pass

    @pytest.mark.asyncio
    async def test_remove_from_list(self):
        """Test removing user from list."""
        pass

    @pytest.mark.asyncio
    async def test_add_duplicate_to_list(self):
        """Test adding already-member user."""
        pass
```

#### 13. User Search Tests

**File**: `tests/unit/test_user_search.py`

```python
class TestUserSearch:
    @pytest.mark.asyncio
    async def test_search_users_basic(self):
        """Test basic user search."""
        pass

    @pytest.mark.asyncio
    async def test_search_users_verified_filter(self):
        """Test filtering for verified users."""
        pass

    @pytest.mark.asyncio
    async def test_search_users_min_followers(self):
        """Test min_followers filter."""
        pass

    @pytest.mark.asyncio
    async def test_search_users_combined_filters(self):
        """Test multiple filters together."""
        pass
```

#### 14. Bookmarks Tests

**File**: `tests/unit/test_bookmarks.py`

```python
class TestBookmarks:
    @pytest.mark.asyncio
    async def test_bookmark_tweet(self):
        """Test bookmarking a tweet."""
        pass

    @pytest.mark.asyncio
    async def test_unbookmark_tweet(self):
        """Test removing bookmark."""
        pass

    @pytest.mark.asyncio
    async def test_get_bookmarks(self):
        """Test getting bookmark list."""
        pass

    @pytest.mark.asyncio
    async def test_bookmarks_pagination(self):
        """Test paginating through bookmarks."""
        pass
```

---

## Performance Tests

**File**: `tests/performance/test_rate_limiting.py`

```python
@pytest.mark.performance
class TestPerformance:
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced."""
        # Make 300 requests
        # Verify 301st is blocked
        pass

    @pytest.mark.asyncio
    async def test_pagination_performance(self):
        """Test pagination doesn't leak memory."""
        # Paginate through 1000+ items
        # Monitor memory usage
        pass

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        # Make 10 parallel requests
        # Verify all succeed
        pass
```

---

## Test Execution

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v --run-integration

# Specific test file
pytest tests/unit/test_quote_tweet.py -v

# Specific test
pytest tests/unit/test_quote_tweet.py::TestQuoteTweet::test_quote_tweet_success -v

# With coverage
pytest --cov=src --cov-report=html tests/

# Parallel execution
pytest -n auto tests/
```

### Continuous Integration

**File**: `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v --cov=src
      - run: pytest tests/integration/ -v --run-integration
      - uses: codecov/codecov-action@v3
```

---

## Success Criteria

- [ ] 90%+ overall code coverage
- [ ] 100% of critical paths tested
- [ ] All edge cases handled
- [ ] Performance tests pass
- [ ] Integration tests pass with real API
- [ ] No flaky tests
- [ ] All tests run in <5 minutes

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
