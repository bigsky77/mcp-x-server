# Twitter MCP Tool Implementation Plan

## Overview
This plan outlines the implementation of 15-20 additional MCP tools based on the recommendations in `TWITTER_MCP_TOOL_RECOMMENDATIONS.md`. The implementation will be done in a `dev` branch and merged to `master` upon completion.

## Current State
- **Existing Tools**: 10 (5 read + 5 write)
- **Target**: Add 15-20 new tools across 4 tiers
- **Branch Strategy**: `dev` → `master` via PR

## Implementation Phases

### Phase 1: Core Gaps (Week 1)
**Priority: CRITICAL** - These tools fill major functionality gaps

#### 1.1 Quote Tweet Operations
- **Tool**: `quote_tweet`
- **File**: `src/tools/post_tools.py`
- **Client**: TwiKit (write operation)
- **Input**: `tweet_id`, `comment_text`, `media_ids?`
- **Output**: `created_tweet_id`, `url`, `success`
- **Complexity**: Medium
- **Testing**: Unit + integration tests

#### 1.2 Thread Context
- **Tool**: `get_tweet_context`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape (read operation)
- **Input**: `tweet_id`, `include_replies?`, `max_depth?`
- **Output**: `conversation_id`, `parent_tweets[]`, `replies[]`, `full_thread[]`
- **Complexity**: High (recursive tree traversal)
- **Testing**: Unit tests with mock conversation threads

#### 1.3 Quote Tweets Discovery
- **Tool**: `get_quote_tweets`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `tweet_id`, `max_results?`, `pagination_token?`
- **Output**: `quotes[]`, `next_token?`, `total_count`
- **Complexity**: Medium
- **Testing**: Pagination tests

#### 1.4 Follow/Unfollow Operations
- **Tools**: `follow_user`, `unfollow_user`
- **File**: `src/tools/post_tools.py`
- **Client**: TwiKit
- **Input**: `user_id?`, `username?`
- **Output**: `success`, `relationship_status`, `user`
- **Complexity**: Low
- **Testing**: Mock API responses

#### 1.5 Follower/Following Lists
- **Tools**: `get_followers`, `get_following`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `user_id`, `max_results?`, `pagination_token?`
- **Output**: `users[]`, `next_token?`, `total_count`
- **Complexity**: Medium (pagination)
- **Testing**: Large list handling

---

### Phase 2: Engagement Intelligence (Week 2)
**Priority: HIGH** - Enable advanced engagement tracking

#### 2.1 Engagement Tracking
- **Tools**: `get_likers`, `get_retweeters`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `tweet_id`, `max_results?`, `pagination_token?`
- **Output**: `users[]`, `next_token?`, `total_count`
- **Complexity**: Medium
- **Testing**: Edge cases (private accounts, deleted users)

#### 2.2 User Interest Profiling
- **Tool**: `get_user_likes`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `user_id`, `max_results?`, `pagination_token?`
- **Output**: `tweets[]`, `next_token?`
- **Complexity**: Low
- **Testing**: Privacy handling

#### 2.3 Home Timeline
- **Tool**: `get_home_timeline`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `max_results?`, `since_id?`, `until_id?`, `pagination_token?`
- **Output**: `tweets[]`, `next_token?`
- **Complexity**: Medium
- **Testing**: Rate limit handling

---

### Phase 3: Operational Essentials (Week 3)
**Priority: MEDIUM** - Safety and performance tracking

#### 3.1 Engagement Cleanup
- **Tools**: `unlike_tweet`, `unretweet`
- **File**: `src/tools/post_tools.py`
- **Client**: TwiKit
- **Input**: `tweet_id`
- **Output**: `success`
- **Complexity**: Low
- **Testing**: Idempotency

#### 3.2 Analytics
- **Tool**: `get_tweet_metrics`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape (requires authentication)
- **Input**: `tweet_id`
- **Output**: `impressions`, `engagement_rate`, `url_clicks`, etc.
- **Complexity**: Medium (auth requirement)
- **Testing**: Mock analytics data

#### 3.3 Rate Limit Monitoring
- **Tool**: `get_rate_limits`
- **File**: `src/tools/read_tools.py`
- **Client**: Both clients (expose internal state)
- **Input**: `endpoints?`
- **Output**: `endpoints{endpoint: {limit, remaining, reset_time}}`
- **Complexity**: Low
- **Testing**: Mock rate limit responses

#### 3.4 User Moderation
- **Tools**: `mute_user`, `unmute_user`, `block_user`, `unblock_user`
- **File**: `src/tools/post_tools.py`
- **Client**: TwiKit
- **Input**: `user_id`
- **Output**: `success`, `action`
- **Complexity**: Low
- **Testing**: Error handling

---

### Phase 4: Advanced Features (Week 4)
**Priority: LOW** - Nice-to-have features

#### 4.1 List Management
- **Tools**: `get_lists`, `create_list`, `add_to_list`, `remove_from_list`
- **File**: New file `src/tools/list_tools.py`
- **Client**: TwiKit (write) + Twscrape (read)
- **Complexity**: Medium
- **Testing**: CRUD operations

#### 4.2 User Discovery
- **Tool**: `search_users`
- **File**: `src/tools/read_tools.py`
- **Client**: Twscrape
- **Input**: `query`, `max_results?`, `filters?`
- **Output**: `users[]`, `next_token?`
- **Complexity**: Medium
- **Testing**: Filter combinations

#### 4.3 Bookmarks (Bonus)
- **Tools**: `bookmark_tweet`, `unbookmark_tweet`, `get_bookmarks`
- **File**: `src/tools/post_tools.py` + `src/tools/read_tools.py`
- **Client**: TwiKit + Twscrape
- **Complexity**: Low
- **Testing**: Basic CRUD

---

## Technical Implementation Details

### File Structure Changes

```
src/
├── tools/
│   ├── __init__.py
│   ├── read_tools.py        # Expand from 5 to 15+ tools
│   ├── post_tools.py        # Expand from 5 to 12+ tools
│   └── list_tools.py        # NEW: List management (4 tools)
├── clients/
│   ├── twikit_client.py     # Add 10+ new methods
│   └── twscrape_client.py   # Add 12+ new methods
├── utils/
│   ├── validators.py        # Add validators for new params
│   └── formatters.py        # NEW: Format complex responses
└── server.py                # Register 15-20 new tools
```

### Testing Strategy

```
tests/
├── test_read_tools.py       # Expand with Phase 2 tests
├── test_post_tools.py       # Expand with Phase 1 + 3 tests
├── test_list_tools.py       # NEW: Phase 4 list tests
├── test_validators.py       # Add new validation tests
├── integration/
│   ├── test_quote_tweets.py
│   ├── test_thread_context.py
│   ├── test_follow_workflow.py
│   └── test_engagement_tracking.py
└── fixtures/
    ├── mock_conversations.json
    ├── mock_followers.json
    └── mock_engagement.json
```

### Client Implementation Pattern

Each new tool requires:
1. **Client method** (in `twikit_client.py` or `twscrape_client.py`)
2. **Tool wrapper** (in appropriate `*_tools.py` file)
3. **Validator** (in `validators.py`)
4. **Server registration** (in `server.py`)
5. **Tests** (unit + integration)

### Error Handling Standard

All tools will return structured errors:
```python
{
    "success": False,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "API rate limit exceeded",
        "details": {
            "reset_time": "2025-11-11T20:00:00Z",
            "limit": 300,
            "remaining": 0
        }
    }
}
```

---

## Branch Strategy

### 1. Initial Setup
```bash
# Create dev branch
git checkout -b dev

# Create feature branches for each phase
git checkout -b feature/phase1-core-gaps
git checkout -b feature/phase2-intelligence
git checkout -b feature/phase3-operations
git checkout -b feature/phase4-advanced
```

### 2. Development Workflow
- Each phase gets its own feature branch
- Regular commits with descriptive messages
- Merge feature branches to `dev` after testing
- Final merge from `dev` to `master` via PR

### 3. Testing Gates
- **Unit tests**: Must pass before committing
- **Integration tests**: Must pass before merging to `dev`
- **Full suite**: Must pass before PR to `master`

---

## Success Criteria

### Functional Requirements
- [ ] All 15-20 tools implemented
- [ ] All tools return consistent response formats
- [ ] Error handling covers edge cases
- [ ] Rate limiting properly enforced

### Testing Requirements
- [ ] 90%+ code coverage
- [ ] All integration tests pass
- [ ] No regressions in existing tools
- [ ] Performance benchmarks met

### Documentation Requirements
- [ ] README updated with new tools
- [ ] API documentation complete
- [ ] Usage examples provided
- [ ] Migration guide for users

---

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Phase 1 | 5 core tools + tests |
| 2 | Phase 2 | 5 intelligence tools + tests |
| 3 | Phase 3 | 5 operations tools + tests |
| 4 | Phase 4 | 5 advanced tools + tests + docs |

**Total Duration**: 4 weeks
**Target Completion**: 2025-12-09

---

## Risk Mitigation

### API Limitations
- **Risk**: Some APIs may not be available via Twikit/Twscrape
- **Mitigation**: Fallback to alternative approaches or mark as future work

### Rate Limiting
- **Risk**: Heavy testing could hit rate limits
- **Mitigation**: Use mocked responses for tests, real API for integration only

### Breaking Changes
- **Risk**: Updates could break existing functionality
- **Mitigation**: Comprehensive regression testing, versioning strategy

### Authentication Complexity
- **Risk**: Some tools require elevated permissions
- **Mitigation**: Clear documentation of permission requirements

---

## Next Steps

1. **Immediate**: Create `dev` branch and Phase 1 feature branch
2. **Day 1-2**: Implement `quote_tweet` and `get_tweet_context`
3. **Day 3-4**: Implement follow/unfollow operations
4. **Day 5**: Complete Phase 1 testing and merge to `dev`
5. **Week 2**: Begin Phase 2 implementation

---

## Tool Count Summary

**Current**: 10 tools
**Phase 1**: +5 tools (15 total)
**Phase 2**: +4 tools (19 total)
**Phase 3**: +7 tools (26 total)
**Phase 4**: +9 tools (35 total)

**Final Target**: 35 MCP tools (3.5x expansion)

---

## Additional Considerations

### Configuration Updates
- Update `config/config.yaml` for new rate limits
- Add new environment variables if needed
- Update MCP server metadata

### Backward Compatibility
- Maintain existing tool signatures
- Add new tools without breaking changes
- Version the API if breaking changes needed

### Performance Optimization
- Implement caching for frequently accessed data
- Batch operations where possible
- Optimize pagination handling

---

## Approval Checklist

Before merging `dev` → `master`:
- [ ] All phases complete
- [ ] All tests passing (unit + integration)
- [ ] Documentation updated
- [ ] README updated with new tool count
- [ ] No console errors or warnings
- [ ] Performance benchmarks acceptable
- [ ] Code review completed
- [ ] Migration guide ready

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Author**: Implementation Planning Team
