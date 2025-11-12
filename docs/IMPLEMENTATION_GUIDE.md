# Implementation Guide - AST-Based Tool Discovery & Context Optimization

This guide walks you through implementing the architecture changes described in `ARCHITECTURE_OPTIMIZATION.md`.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Existing mcp-x-server codebase
- Understanding of decorators and async Python

### High-Level Steps
1. Create registry infrastructure
2. Add decorators to existing tools
3. Implement AST-based schema generation
4. Update server.py to use registry
5. Test and validate
6. Reorganize file structure (optional)

---

## Step-by-Step Implementation

### Step 1: Create Tool Registry (30 minutes)

**Create** `src/registry/__init__.py`:
```python
from .tool_registry import ToolRegistry
from .decorators import mcp_tool, validate_params, rate_limit
from .schema_generator import SchemaGenerator
from .discovery import ToolDiscovery

__all__ = [
    'ToolRegistry',
    'mcp_tool',
    'validate_params',
    'rate_limit',
    'SchemaGenerator',
    'ToolDiscovery'
]
```

**Create** `src/registry/tool_registry.py`:
```python
# See ARCHITECTURE_OPTIMIZATION.md Section 1.1 for full code
```

**Test**:
```python
# test_registry.py
import pytest
from src.registry import ToolRegistry

def test_registry_registration():
    registry = ToolRegistry()

    async def sample_tool(param: str) -> dict:
        return {"result": param}

    from mcp.types import Tool
    schema = Tool(name="sample_tool", description="Test", inputSchema={})

    registry.register(
        name="sample_tool",
        func=sample_tool,
        schema=schema,
        category="test"
    )

    assert len(registry.get_all_schemas()) == 1
    assert registry._tools["sample_tool"].name == "sample_tool"

@pytest.mark.asyncio
async def test_registry_call():
    registry = ToolRegistry()

    async def sample_tool(param: str) -> dict:
        return {"result": param}

    from mcp.types import Tool
    schema = Tool(name="sample_tool", description="Test", inputSchema={})

    registry.register("sample_tool", sample_tool, schema, "test")

    result = await registry.call("sample_tool", {"param": "hello"})
    assert result == {"result": "hello"}
```

Run: `pytest tests/test_registry.py`

---

### Step 2: Create Decorators (30 minutes)

**Create** `src/registry/decorators.py`:
```python
# See ARCHITECTURE_OPTIMIZATION.md Section 1.2 for full code
```

**Test**:
```python
# test_decorators.py
import pytest
from src.registry.decorators import mcp_tool, validate_params

@mcp_tool(category="test", phase="basic", popularity=5)
async def decorated_tool(param: str) -> dict:
    """Test tool."""
    return {"result": param}

def test_mcp_tool_decorator():
    assert hasattr(decorated_tool, '_mcp_tool')
    assert decorated_tool._mcp_tool == True
    assert decorated_tool._mcp_category == "test"
    assert decorated_tool._mcp_phase == "basic"
    assert decorated_tool._mcp_popularity == 5

@pytest.mark.asyncio
async def test_mcp_tool_execution():
    result = await decorated_tool(param="hello")
    assert result == {"result": "hello"}

def mock_validator(value: str) -> str:
    if not value:
        raise ValueError("Cannot be empty")
    return value.upper()

@validate_params({'param': mock_validator})
async def validated_tool(param: str) -> dict:
    return {"result": param}

@pytest.mark.asyncio
async def test_validate_params():
    result = await validated_tool(param="hello")
    assert result == {"result": "HELLO"}  # Validator uppercased it
```

Run: `pytest tests/test_decorators.py`

---

### Step 3: Add Decorators to Existing Tools (1 hour)

**Update** `src/tools/read_tools.py`:

**Before**:
```python
async def search_tweets(
    self, query: str, limit: Optional[int] = None, filter_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search tweets by keyword/hashtag.

    Args:
        query: Search query (keywords, hashtags, etc.)
        limit: Maximum number of results (default: 20, max: 100)
        filter_type: Optional filter ('top', 'latest', 'people', 'photos', 'videos')

    Returns:
        List of tweet objects with id, text, author, metrics, etc.
    """
    query = validate_search_query(query)
    limit = validate_limit(limit)
    tweets = await self.client.search_tweets(query, limit=limit, filter_type=filter_type)
    return tweets
```

**After**:
```python
from src.registry.decorators import mcp_tool, validate_params, rate_limit

@mcp_tool(category="read", phase="basic", popularity=10, rate_limit_type="read")
@rate_limit("read")
@validate_params({
    'query': validate_search_query,
    'limit': validate_limit
})
async def search_tweets(
    self, query: str, limit: Optional[int] = 20, filter_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search tweets by keyword/hashtag with optional filters.

    Args:
        query: Search query (keywords, hashtags, etc.)
        limit: Maximum number of results (default: 20, max: 100)
        filter_type: Optional filter ('top', 'latest', 'people', 'photos', 'videos')

    Returns:
        List of tweet objects with id, text, author, metrics, etc.
    """
    # Validation now happens in decorator
    tweets = await self.client.search_tweets(query, limit=limit, filter_type=filter_type)
    return tweets
```

**Changes**:
1. Import decorators at top of file
2. Add `@mcp_tool()` with metadata
3. Add `@rate_limit()` (optional)
4. Add `@validate_params()` (optional, removes manual validation calls)
5. Move default value to parameter signature (`limit: Optional[int] = 20`)
6. Remove manual validation calls inside method (now in decorator)

**Repeat for all 35 tools**:
- Read tools: `src/tools/read_tools.py` (18 methods)
- Write tools: `src/tools/post_tools.py` (17 methods)

**Categorization Guide**:

| Category | Tools | Phase | Popularity |
|----------|-------|-------|------------|
| read | search_tweets, get_tweet, get_user, get_user_tweets | basic | 10 |
| read | get_mentions, get_home_timeline, get_followers, get_following | basic | 8 |
| read | get_tweet_context, get_quote_tweets, get_likers, get_retweeters | advanced | 5 |
| read | get_user_likes, get_bookmarks, search_users | advanced | 5 |
| read | get_lists | advanced | 3 |
| write | post_tweet, reply_to_tweet, like_tweet, retweet | basic | 10 |
| write | follow_user, unfollow_user, bookmark_tweet | basic | 8 |
| write | quote_tweet, delete_tweet, unlike_tweet, unretweet | advanced | 5 |
| write | mute_user, unmute_user, block_user, unblock_user | advanced | 3 |
| write | unbookmark_tweet, create_list, add_to_list, remove_from_list | advanced | 3 |

**Example: Complete Tool with All Decorators**:
```python
@mcp_tool(
    category="write",
    phase="basic",
    popularity=10,
    rate_limit_type="write"
)
@rate_limit("write")
@validate_params({
    'text': validate_tweet_text,
    'media_ids': lambda x: x  # Passthrough
})
async def post_tweet(
    self,
    text: str,
    media_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Post a new tweet.

    Args:
        text: Tweet text (max 280 chars)
        media_ids: Optional media IDs

    Returns:
        Tweet object with id, text, created_at, author
    """
    result = await self.client.post_tweet(text=text, media_ids=media_ids)
    return result
```

---

### Step 4: Create Schema Generator (2 hours)

**Create** `src/registry/schema_generator.py`:
```python
# See ARCHITECTURE_OPTIMIZATION.md Section 1.3 for full code
```

**Test**:
```python
# test_schema_generator.py
import pytest
from typing import Optional, List, Dict, Any
from src.registry.schema_generator import SchemaGenerator
from src.registry.decorators import mcp_tool

@mcp_tool(category="test")
async def sample_tool(
    required_param: str,
    optional_param: Optional[int] = 20,
    optional_str: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Sample tool for testing.

    Args:
        required_param: This is required
        optional_param: This is optional (default: 20)
        optional_str: This is also optional

    Returns:
        List of results
    """
    pass

def test_schema_generation():
    schema = SchemaGenerator.generate(sample_tool)

    assert schema.name == "sample_tool"
    assert "Sample tool for testing" in schema.description

    props = schema.inputSchema["properties"]
    assert "required_param" in props
    assert props["required_param"]["type"] == "string"
    assert "This is required" in props["required_param"]["description"]

    assert "optional_param" in props
    assert props["optional_param"]["type"] == "integer"
    assert "optional" in props["optional_param"]["description"].lower()
    assert "default: 20" in props["optional_param"]["description"]

    assert "optional_str" in props
    assert props["optional_str"]["type"] == "string"

    required = schema.inputSchema["required"]
    assert "required_param" in required
    assert "optional_param" not in required
    assert "optional_str" not in required
```

Run: `pytest tests/test_schema_generator.py`

---

### Step 5: Create Discovery System (1 hour)

**Create** `src/registry/discovery.py`:
```python
# See ARCHITECTURE_OPTIMIZATION.md Section 1.4 for full code
```

**Test**:
```python
# test_discovery.py
import pytest
from src.registry.discovery import ToolDiscovery
from src.registry.decorators import mcp_tool
from src.registry.tool_registry import ToolRegistry

class SampleTools:
    def __init__(self, client):
        self.client = client

    @mcp_tool(category="test", phase="basic", popularity=5)
    async def tool_one(self, param: str) -> dict:
        """Tool one."""
        return {"result": param}

    @mcp_tool(category="test", phase="advanced", popularity=3)
    async def tool_two(self, param: int) -> dict:
        """Tool two."""
        return {"number": param}

def test_discovery():
    tools = SampleTools(client=None)
    registry = ToolRegistry()

    ToolDiscovery.discover_tools_from_instances(registry, tools)

    schemas = registry.get_all_schemas()
    assert len(schemas) == 2

    names = [s.name for s in schemas]
    assert "tool_one" in names
    assert "tool_two" in names

@pytest.mark.asyncio
async def test_discovered_tool_execution():
    tools = SampleTools(client=None)
    registry = ToolRegistry()

    ToolDiscovery.discover_tools_from_instances(registry, tools)

    result = await registry.call("tool_one", {"param": "hello"})
    assert result == {"result": "hello"}
```

Run: `pytest tests/test_discovery.py`

---

### Step 6: Update server.py (1 hour)

**Before** (607 lines):
```python
class MCPXServer:
    def __init__(self, config_path: str = "config/config.yaml"):
        # ... initialization ...

        self._register_handlers()

    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(name="search_tweets", description="...", inputSchema={...}),
                Tool(name="get_tweet", description="...", inputSchema={...}),
                # ... 33 more Tool definitions (420 lines)
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            try:
                if name == "search_tweets":
                    result = await self.read_tools.search_tweets(**arguments)
                elif name == "get_tweet":
                    result = await self.read_tools.get_tweet(**arguments)
                # ... 33 more elif branches (70 lines)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**After** (~150 lines):
```python
from src.registry import ToolRegistry, ToolDiscovery

class MCPXServer:
    def __init__(self, config_path: str = "config/config.yaml"):
        # ... initialization ...

        # Create and populate registry
        self.registry = ToolRegistry()
        ToolDiscovery.discover_tools_from_instances(
            self.registry,
            self.read_tools,
            self.write_tools
        )

        self._register_handlers()

    def _register_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            # Option 1: Return all tools (backwards compatible)
            return self.registry.get_all_schemas()

            # Option 2: Return basic tools only (70% token reduction)
            # return self.registry.get_basic_schemas()

            # Option 3: Return popular tools (smart prioritization)
            # return self.registry.get_popular_schemas(limit=10)

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            try:
                result = await self.registry.call(name, arguments)
                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**Changes**:
1. Import registry classes
2. Create `self.registry` in `__init__`
3. Use `ToolDiscovery.discover_tools_from_instances()` to auto-register
4. Replace 420-line tool list with `self.registry.get_all_schemas()`
5. Replace 70-line elif chain with `self.registry.call(name, arguments)`
6. **Result**: 490 lines eliminated, now ~150 lines

---

### Step 7: Testing & Validation (2 hours)

**1. Unit Tests**:
```bash
pytest tests/test_registry.py
pytest tests/test_decorators.py
pytest tests/test_schema_generator.py
pytest tests/test_discovery.py
```

**2. Integration Test**:
```python
# test_integration.py
import pytest
from src.server import MCPXServer

@pytest.mark.asyncio
async def test_server_tool_discovery():
    """Test that server discovers all tools correctly."""
    server = MCPXServer(config_path="config/config.yaml")

    schemas = server.registry.get_all_schemas()
    assert len(schemas) == 35, f"Expected 35 tools, got {len(schemas)}"

    # Check all tool names are present
    tool_names = [s.name for s in schemas]
    expected_tools = [
        "search_tweets", "get_tweet", "get_user_tweets", "get_user", "get_mentions",
        "post_tweet", "reply_to_tweet", "like_tweet", "retweet", "delete_tweet",
        # ... add all 35 tool names
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"

@pytest.mark.asyncio
async def test_tool_execution():
    """Test that tools execute correctly through registry."""
    server = MCPXServer(config_path="config/config.yaml")

    # Mock the client to avoid real API calls
    class MockClient:
        async def search_tweets(self, query, limit, filter_type):
            return [{"id": "123", "text": "test tweet"}]

    server.read_tools.client = MockClient()

    result = await server.registry.call("search_tweets", {
        "query": "test",
        "limit": 10,
        "filter_type": None
    })

    assert isinstance(result, list)
    assert len(result) > 0
```

Run: `pytest tests/test_integration.py`

**3. Manual Testing**:
```bash
# Start server
python -m src.server

# In Claude Code, test a tool
mcp__mcp-x-server__search_tweets(query="test", limit=5)
```

**4. Schema Comparison**:
```python
# scripts/compare_schemas.py
"""
Compare manually-defined schemas with AST-generated schemas.
"""
from src.server import MCPXServer
from src.registry import SchemaGenerator

# Load server (this generates schemas from AST)
server = MCPXServer()
generated_schemas = {s.name: s for s in server.registry.get_all_schemas()}

# Load old manual schemas (from backup or git history)
# old_schemas = load_old_schemas()

# Compare
for name, generated in generated_schemas.items():
    # if name in old_schemas:
    #     old = old_schemas[name]
    #     assert generated.description == old.description
    #     assert generated.inputSchema == old.inputSchema
    print(f"✓ {name}: OK")

print(f"\nAll {len(generated_schemas)} schemas validated!")
```

Run: `python scripts/compare_schemas.py`

---

### Step 8: File Reorganization (Optional, 2 hours)

**Create new directory structure**:
```bash
mkdir -p src/tools/read
mkdir -p src/tools/write

# Move read tools to categories
# search.py: search_tweets, search_users
# fetch.py: get_tweet, get_user, get_user_tweets
# engagement.py: get_likers, get_retweeters, get_quote_tweets
# timeline.py: get_home_timeline, get_mentions
# ... etc

# Move write tools to categories
# compose.py: post_tweet, reply_to_tweet, quote_tweet
# engagement.py: like_tweet, retweet, bookmark_tweet
# moderation.py: mute_user, block_user, unmute_user, unblock_user
# social.py: follow_user, unfollow_user
# ... etc
```

**Update imports**:
```python
# src/tools/__init__.py
from .read import ReadTools
from .write import WriteTools

__all__ = ['ReadTools', 'WriteTools']

# src/tools/read/__init__.py
from .search import SearchTools
from .fetch import FetchTools
from .engagement import EngagementTools
from .timeline import TimelineTools

class ReadTools:
    """Aggregates all read operation tools."""
    def __init__(self, client):
        self.search = SearchTools(client)
        self.fetch = FetchTools(client)
        self.engagement = EngagementTools(client)
        self.timeline = TimelineTools(client)

    # Expose methods at top level for backwards compatibility
    def __getattr__(self, name):
        for category in [self.search, self.fetch, self.engagement, self.timeline]:
            if hasattr(category, name):
                return getattr(category, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
```

**Test after reorganization**:
```bash
pytest tests/
python -m src.server  # Should start without errors
```

---

## Validation Checklist

After implementation, verify:

- [ ] All 35 tools have `@mcp_tool` decorator
- [ ] All tools generate valid schemas
- [ ] Schema properties match method parameters
- [ ] Schema descriptions match docstrings
- [ ] Required parameters correctly identified
- [ ] Optional parameters correctly identified
- [ ] Default values in schema descriptions
- [ ] Tool categories assigned correctly
- [ ] Rate limit types assigned correctly
- [ ] Registry discovers all tools
- [ ] `server.py` reduced to ~150 lines
- [ ] All tests pass (`pytest tests/`)
- [ ] Server starts without errors
- [ ] Tools callable through MCP
- [ ] Tool responses unchanged
- [ ] Token overhead reduced (measure initial handshake)

---

## Rollback Plan

If issues arise:

1. **Partial Rollback**: Keep registry, revert to manual schemas
   ```python
   # In server.py
   @self.server.list_tools()
   async def list_tools() -> list[Tool]:
       # Use manually-defined schemas temporarily
       return MANUAL_TOOL_DEFINITIONS
   ```

2. **Full Rollback**: Revert to previous version
   ```bash
   git revert <commit-hash>
   ```

3. **Gradual Migration**: Migrate tools one category at a time
   ```python
   # Mix manual and auto-generated
   manual_schemas = [...]  # Remaining tools
   auto_schemas = registry.get_schemas_by_category("read")
   return manual_schemas + auto_schemas
   ```

---

## Performance Benchmarks

**Measure these metrics**:

1. **Schema Generation Time**:
   ```python
   import time
   start = time.time()
   schemas = registry.get_all_schemas()
   print(f"Schema generation: {(time.time() - start) * 1000:.2f}ms")
   # Target: < 100ms
   ```

2. **Server Startup Time**:
   ```bash
   time python -m src.server --test-mode
   # Target: < 2 seconds
   ```

3. **Tool Execution Time** (no regression):
   ```python
   import time
   start = time.time()
   result = await registry.call("search_tweets", {...})
   print(f"Execution: {(time.time() - start) * 1000:.2f}ms")
   # Should match previous execution time
   ```

4. **Token Overhead**:
   ```python
   import json
   schemas = registry.get_basic_schemas()  # Or get_all_schemas()
   schema_json = json.dumps([s.dict() for s in schemas])
   tokens = len(schema_json) / 4  # Rough estimate
   print(f"Token overhead: ~{tokens:.0f} tokens")
   # Target: < 1,000 tokens (down from 3,500)
   ```

---

## Common Issues & Solutions

### Issue 1: Schema Generation Fails
**Symptom**: `SchemaGenerator.generate()` throws error

**Solutions**:
- Check that docstring has `Args:` section
- Verify all parameters have type hints
- Check for complex types (use `from typing import ...`)
- Add manual schema override if needed

### Issue 2: Tool Not Discovered
**Symptom**: Tool missing from `registry.get_all_schemas()`

**Solutions**:
- Verify `@mcp_tool` decorator is present
- Check `_mcp_enabled = True` (default)
- Ensure method is on tool class instance
- Check discovery includes the tool class

### Issue 3: Validation Not Working
**Symptom**: Invalid parameters not caught

**Solutions**:
- Check `@validate_params` is above method (after `@mcp_tool`)
- Verify validator function names are correct
- Ensure validators raise exceptions on failure
- Check parameter names match exactly

### Issue 4: Rate Limiting Not Enforced
**Symptom**: Tools not rate limited

**Solutions**:
- Check `@rate_limit` decorator is present
- Verify `self.rate_limiter` exists on tool class
- Implement `rate_limiter.wait_if_needed()` if missing
- Check rate limit configuration in config.yaml

### Issue 5: Import Errors
**Symptom**: `ModuleNotFoundError` or circular imports

**Solutions**:
- Add `src/registry/__init__.py`
- Use absolute imports (`from src.registry import ...`)
- Check PYTHONPATH includes project root
- Avoid circular dependencies

---

## Development Workflow

### Adding a New Tool

**Before** (old way):
1. Add method to `tools/read_tools.py` or `tools/post_tools.py`
2. Add Tool definition in `server.py` (12 lines)
3. Add elif branch in `server.py` (2 lines)
4. Ensure names match across all 3 places

**After** (new way):
1. Add method with decorator:
   ```python
   @mcp_tool(category="read", phase="basic", popularity=5)
   async def my_new_tool(self, param: str) -> dict:
       """My new tool does X.

       Args:
           param: Parameter description

       Returns:
           Result description
       """
       result = await self.client.do_something(param)
       return result
   ```
2. **Done!** Schema auto-generated, tool auto-registered.

### Modifying an Existing Tool

**Before** (old way):
1. Update method implementation
2. Update Tool schema in `server.py`
3. Ensure both stay in sync

**After** (new way):
1. Update method (signature, docstring, or implementation)
2. **Done!** Schema auto-updates.

---

## Next Steps

After completing this implementation:

1. **Measure Results**: Benchmark token reduction, code reduction
2. **Create PR**: Document changes, results, and rationale
3. **Community Review**: Get feedback from MCP community
4. **Iterate**: Address feedback, optimize further
5. **Document Patterns**: Create guide for other MCP servers

---

## Resources

- **Anthropic Blog**: [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Python AST**: https://docs.python.org/3/library/ast.html
- **Type Hints**: https://docs.python.org/3/library/typing.html
- **Decorators**: https://realpython.com/primer-on-python-decorators/

---

## Support

Questions or issues?

- Check existing issues: https://github.com/bigsky/mcp-x-server/issues
- Create new issue with `[AST Implementation]` prefix
- Tag maintainers: @bigsky

**Happy coding! 🚀**
