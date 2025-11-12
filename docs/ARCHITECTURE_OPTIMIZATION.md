# MCP X Server - Architecture Optimization Design

## Executive Summary

This document outlines a comprehensive optimization strategy for mcp-x-server that will:
- **Eliminate 455 lines of boilerplate code** (24% reduction)
- **Reduce initial token overhead by 80%+** (from ~3,500 to ~700 tokens)
- **Enable single-source-of-truth tool definitions** (docstrings + type hints → schemas)
- **Improve maintainability** (add new tool = write method only)

Based on Anthropic's "Code execution with MCP" recommendations, we implement:
1. **AST-based tool discovery** - Generate schemas from code
2. **File-based tool structure** - Organize tools for progressive disclosure
3. **Context optimization** - Lazy loading, caching, and intelligent filtering

---

## 1. Core Architecture Changes

### 1.1 Tool Registry System

**New Component**: `src/registry/tool_registry.py`

```python
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
from mcp.types import Tool
import inspect

@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    func: Callable
    schema: Tool
    category: str
    rate_limit_type: str
    phase: str  # "basic", "advanced", "expert"
    popularity: int  # Usage frequency

class ToolRegistry:
    """Central registry for MCP tools with lazy loading support."""

    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._schema_cache: Optional[List[Tool]] = None
        self._category_cache: Dict[str, List[Tool]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        schema: Tool,
        category: str = "general",
        rate_limit_type: str = "read",
        phase: str = "basic",
        popularity: int = 0
    ):
        """Register a tool with metadata."""
        self._tools[name] = ToolMetadata(
            name=name,
            func=func,
            schema=schema,
            category=category,
            rate_limit_type=rate_limit_type,
            phase=phase,
            popularity=popularity
        )
        self._invalidate_cache()

    async def call(self, name: str, arguments: dict) -> Any:
        """Call a registered tool by name."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        tool = self._tools[name]
        return await tool.func(**arguments)

    def get_all_schemas(self) -> List[Tool]:
        """Get all tool schemas (cached)."""
        if self._schema_cache is None:
            self._schema_cache = [t.schema for t in self._tools.values()]
        return self._schema_cache

    def get_schemas_by_category(self, category: str) -> List[Tool]:
        """Get schemas for a specific category."""
        if category not in self._category_cache:
            self._category_cache[category] = [
                t.schema for t in self._tools.values()
                if t.category == category
            ]
        return self._category_cache[category]

    def get_popular_schemas(self, limit: int = 10) -> List[Tool]:
        """Get most popular tool schemas for initial load."""
        sorted_tools = sorted(
            self._tools.values(),
            key=lambda t: t.popularity,
            reverse=True
        )
        return [t.schema for t in sorted_tools[:limit]]

    def get_basic_schemas(self) -> List[Tool]:
        """Get basic/essential tool schemas for initial load."""
        return [
            t.schema for t in self._tools.values()
            if t.phase == "basic"
        ]

    def _invalidate_cache(self):
        """Invalidate all caches after registration."""
        self._schema_cache = None
        self._category_cache = {}
```

**Benefits**:
- ✅ O(1) tool lookup (vs O(n) elif chain)
- ✅ Support for lazy loading strategies
- ✅ Cached schema generation
- ✅ Category-based filtering
- ✅ Popularity-based prioritization

---

### 1.2 Tool Decorator System

**New Component**: `src/registry/decorators.py`

```python
from typing import Callable, Optional
from functools import wraps

def mcp_tool(
    category: str = "general",
    rate_limit_type: str = "read",
    phase: str = "basic",
    popularity: int = 0,
    enabled: bool = True
):
    """
    Decorator to mark a method as an MCP tool.

    Args:
        category: Tool category (read, write, engagement, etc.)
        rate_limit_type: Rate limit pool ("read" or "write")
        phase: Complexity phase ("basic", "advanced", "expert")
        popularity: Usage frequency score (higher = more popular)
        enabled: Whether tool is currently enabled
    """
    def decorator(func: Callable) -> Callable:
        # Attach metadata to function
        func._mcp_tool = True
        func._mcp_category = category
        func._mcp_rate_limit_type = rate_limit_type
        func._mcp_phase = phase
        func._mcp_popularity = popularity
        func._mcp_enabled = enabled

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Future: Add rate limiting, logging, telemetry here
            return await func(*args, **kwargs)

        # Preserve metadata on wrapper
        wrapper._mcp_tool = True
        wrapper._mcp_category = category
        wrapper._mcp_rate_limit_type = rate_limit_type
        wrapper._mcp_phase = phase
        wrapper._mcp_popularity = popularity
        wrapper._mcp_enabled = enabled
        wrapper._original_func = func

        return wrapper
    return decorator


def validate_params(validators: dict):
    """
    Decorator to automatically validate parameters.

    Args:
        validators: Dict mapping param names to validator functions

    Example:
        @validate_params({
            'query': validate_search_query,
            'limit': validate_limit
        })
        async def search_tweets(self, query: str, limit: int = 20):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate each parameter
            validated_kwargs = kwargs.copy()
            for param_name, validator in validators.items():
                if param_name in validated_kwargs:
                    validated_kwargs[param_name] = validator(validated_kwargs[param_name])

            return await func(*args, **validated_kwargs)

        return wrapper
    return decorator


def rate_limit(operation: str):
    """
    Decorator to enforce rate limiting.

    Args:
        operation: Rate limit pool ("read" or "write")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Wait if rate limit exceeded
            if hasattr(self, 'rate_limiter'):
                await self.rate_limiter.wait_if_needed(operation)

            return await func(self, *args, **kwargs)

        return wrapper
    return decorator
```

---

### 1.3 AST-Based Schema Generator

**New Component**: `src/registry/schema_generator.py`

```python
import inspect
import ast
import re
from typing import Callable, Dict, Any, Optional, get_type_hints, get_origin, get_args
from mcp.types import Tool


class SchemaGenerator:
    """Generate MCP Tool schemas from method signatures and docstrings."""

    PYTHON_TO_JSON_TYPE = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }

    @classmethod
    def generate(cls, func: Callable) -> Tool:
        """
        Generate a complete Tool schema from a function.

        Args:
            func: The function to generate schema for

        Returns:
            Tool object with name, description, and inputSchema
        """
        name = func.__name__
        description = cls._extract_description(func)
        input_schema = cls._generate_input_schema(func)

        return Tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )

    @classmethod
    def _extract_description(cls, func: Callable) -> str:
        """Extract short description from docstring (first line)."""
        doc = inspect.getdoc(func)
        if not doc:
            return f"Execute {func.__name__}"

        # Get first non-empty line
        lines = doc.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('@'):
                return line

        return f"Execute {func.__name__}"

    @classmethod
    def _generate_input_schema(cls, func: Callable) -> Dict[str, Any]:
        """Generate JSON schema for function parameters."""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        param_docs = cls._parse_param_docs(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip 'self' and 'cls'
            if param_name in ('self', 'cls'):
                continue

            # Get type from hints
            param_type = type_hints.get(param_name, Any)
            json_type, is_optional = cls._python_type_to_json(param_type)

            # Build property schema
            prop_schema = {"type": json_type}

            # Add description from docstring
            if param_name in param_docs:
                prop_schema["description"] = param_docs[param_name]

            # Add default value info to description
            if param.default != inspect.Parameter.empty:
                if "description" in prop_schema:
                    prop_schema["description"] += f" (default: {param.default})"
                else:
                    prop_schema["description"] = f"Default: {param.default}"

            properties[param_name] = prop_schema

            # Add to required if no default and not optional
            if param.default == inspect.Parameter.empty and not is_optional:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    @classmethod
    def _python_type_to_json(cls, python_type) -> tuple[str, bool]:
        """
        Convert Python type hint to JSON schema type.

        Returns:
            (json_type, is_optional)
        """
        # Handle Optional[T]
        origin = get_origin(python_type)
        if origin is type(None) or python_type is type(None):
            return "null", True

        # Handle Optional[T] (Union[T, None])
        if origin is type(Optional) or (origin and str(origin) == 'typing.Union'):
            args = get_args(python_type)
            if len(args) == 2 and type(None) in args:
                # This is Optional[T]
                inner_type = args[0] if args[1] is type(None) else args[1]
                json_type, _ = cls._python_type_to_json(inner_type)
                return json_type, True

        # Handle List[T]
        if origin is list:
            return "array", False

        # Handle Dict[K, V]
        if origin is dict:
            return "object", False

        # Handle basic types
        if python_type in cls.PYTHON_TO_JSON_TYPE:
            return cls.PYTHON_TO_JSON_TYPE[python_type], False

        # Default to string
        return "string", False

    @classmethod
    def _parse_param_docs(cls, func: Callable) -> Dict[str, str]:
        """
        Parse parameter descriptions from docstring Args section.

        Returns:
            Dict mapping parameter names to descriptions
        """
        doc = inspect.getdoc(func)
        if not doc:
            return {}

        param_docs = {}

        # Find Args section
        args_match = re.search(r'Args:(.*?)(?=Returns:|Raises:|Examples?:|Notes?:|\Z)',
                               doc, re.DOTALL | re.IGNORECASE)
        if not args_match:
            return {}

        args_section = args_match.group(1)

        # Parse each parameter line
        # Format: "param_name: description" or "param_name (type): description"
        param_pattern = r'^\s*(\w+)(?:\s*\([^)]+\))?\s*:\s*(.+?)(?=^\s*\w+(?:\s*\([^)]+\))?\s*:|$)'
        matches = re.finditer(param_pattern, args_section, re.MULTILINE | re.DOTALL)

        for match in matches:
            param_name = match.group(1).strip()
            description = match.group(2).strip()
            # Remove extra whitespace and newlines
            description = re.sub(r'\s+', ' ', description)
            param_docs[param_name] = description

        return param_docs
```

**Example Usage**:

```python
# Original method (in tools/read_tools.py)
@mcp_tool(category="read", phase="basic", popularity=10)
async def search_tweets(
    self,
    query: str,
    limit: Optional[int] = 20,
    filter_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search tweets by keyword/hashtag with optional filters.

    Args:
        query: Search query (keywords, hashtags, etc.)
        limit: Maximum number of results (default: 20, max: 100)
        filter_type: Optional filter ('top', 'latest', 'people', 'photos', 'videos')

    Returns:
        List of tweet objects with id, text, author, metrics, etc.
    """
    ...

# Auto-generated schema
schema = SchemaGenerator.generate(search_tweets)
# Tool(
#     name="search_tweets",
#     description="Search tweets by keyword/hashtag with optional filters.",
#     inputSchema={
#         "type": "object",
#         "properties": {
#             "query": {
#                 "type": "string",
#                 "description": "Search query (keywords, hashtags, etc.)"
#             },
#             "limit": {
#                 "type": "integer",
#                 "description": "Maximum number of results (default: 20, max: 100) (default: 20)"
#             },
#             "filter_type": {
#                 "type": "string",
#                 "description": "Optional filter ('top', 'latest', 'people', 'photos', 'videos')"
#             }
#         },
#         "required": ["query"]
#     }
# )
```

**Benefits**:
- ✅ Single source of truth (method signature + docstring)
- ✅ Automatic schema generation
- ✅ Type safety guaranteed
- ✅ Docstring parsing for descriptions
- ✅ Optional parameter detection
- ✅ Default value extraction

---

### 1.4 Tool Discovery System

**New Component**: `src/registry/discovery.py`

```python
import inspect
from typing import List, Type, Any
from .tool_registry import ToolRegistry
from .schema_generator import SchemaGenerator


class ToolDiscovery:
    """Discover and register MCP tools from classes."""

    @staticmethod
    def discover_tools(*tool_classes: Type) -> ToolRegistry:
        """
        Discover all @mcp_tool decorated methods from classes.

        Args:
            *tool_classes: Classes containing tool methods

        Returns:
            ToolRegistry with all discovered tools registered
        """
        registry = ToolRegistry()

        for tool_class in tool_classes:
            ToolDiscovery._discover_from_class(registry, tool_class)

        return registry

    @staticmethod
    def _discover_from_class(registry: ToolRegistry, tool_class: Type):
        """Discover tools from a single class."""
        # Get instance (assume no-arg constructor or singleton)
        if hasattr(tool_class, 'instance'):
            instance = tool_class.instance
        else:
            # Create instance (will need client instances)
            # In practice, server.py will pass initialized instances
            return

        # Iterate through methods
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            # Check if method is decorated with @mcp_tool
            if hasattr(method, '_mcp_tool') and method._mcp_tool:
                # Check if enabled
                if not method._mcp_enabled:
                    continue

                # Generate schema
                original_func = getattr(method, '_original_func', method)
                schema = SchemaGenerator.generate(original_func)

                # Register tool
                registry.register(
                    name=name,
                    func=method,
                    schema=schema,
                    category=method._mcp_category,
                    rate_limit_type=method._mcp_rate_limit_type,
                    phase=method._mcp_phase,
                    popularity=method._mcp_popularity
                )

    @staticmethod
    def discover_tools_from_instances(
        registry: ToolRegistry,
        *instances: Any
    ):
        """
        Discover tools from instantiated objects.

        Args:
            registry: Registry to add tools to
            *instances: Instantiated tool class objects
        """
        for instance in instances:
            for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
                if hasattr(method, '_mcp_tool') and method._mcp_tool:
                    if not method._mcp_enabled:
                        continue

                    original_func = getattr(method, '_original_func', method)
                    schema = SchemaGenerator.generate(original_func)

                    registry.register(
                        name=name,
                        func=method,
                        schema=schema,
                        category=method._mcp_category,
                        rate_limit_type=method._mcp_rate_limit_type,
                        phase=method._mcp_phase,
                        popularity=method._mcp_popularity
                    )
```

---

## 2. File-Based Tool Structure

### 2.1 Reorganized Directory Structure

```
src/
├── registry/
│   ├── __init__.py
│   ├── tool_registry.py       # Central registry
│   ├── decorators.py          # @mcp_tool, @validate_params, @rate_limit
│   ├── schema_generator.py    # AST-based schema generation
│   └── discovery.py           # Auto-discovery system
├── tools/
│   ├── __init__.py
│   ├── base.py                # Base tool class
│   ├── read/
│   │   ├── __init__.py
│   │   ├── search.py          # search_tweets, search_users
│   │   ├── fetch.py           # get_tweet, get_user, get_user_tweets
│   │   ├── engagement.py      # get_likers, get_retweeters, get_quote_tweets
│   │   └── timeline.py        # get_home_timeline, get_mentions
│   └── write/
│       ├── __init__.py
│       ├── compose.py         # post_tweet, reply_to_tweet, quote_tweet
│       ├── engagement.py      # like_tweet, retweet, bookmark_tweet
│       ├── moderation.py      # mute_user, block_user
│       └── social.py          # follow_user, unfollow_user
├── server.py                  # Slim MCP server (now ~150 lines)
└── ...
```

### 2.2 Benefits of File-Based Structure

1. **Progressive Disclosure**:
   - Agent can explore `tools/read/` to find read operations
   - Agent can list files to discover available tools
   - Similar to Anthropic's example with `servers/google-drive/getDocument.ts`

2. **Logical Grouping**:
   - Tools organized by functionality
   - Easier to find related tools
   - Clear separation of concerns

3. **Smaller Files**:
   - Each file <100 lines
   - Easier to read and maintain
   - Better code organization

4. **Lazy Loading Potential**:
   - Import only needed modules
   - Reduce startup time
   - Lower memory footprint

---

## 3. Context Optimization Strategies

### 3.1 Lazy Schema Loading

**Strategy 1: Basic Tools First** (Recommended)

```python
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    """Return only basic/essential tools on first call."""
    # Return 10 most popular or "basic" phase tools
    return self.registry.get_basic_schemas()
```

**Benefits**:
- Initial load: 10 tools × 400 bytes = 4 KB (~1,000 tokens) vs 14.5 KB (~3,500 tokens)
- **70% token reduction** on initialization
- Agent sees most useful tools immediately

**Strategy 2: Category-Based Loading**

```python
# Agent can request specific categories
tools = registry.get_schemas_by_category("read")  # Only read operations
tools = registry.get_schemas_by_category("write")  # Only write operations
```

**Strategy 3: Search-Based Discovery**

```python
def search_tools(query: str, limit: int = 5) -> list[Tool]:
    """Search for tools by name or description."""
    matching = []
    for tool in registry.get_all_schemas():
        if query.lower() in tool.name.lower() or query.lower() in tool.description.lower():
            matching.append(tool)
            if len(matching) >= limit:
                break
    return matching
```

### 3.2 Schema Caching

```python
class ToolRegistry:
    def get_all_schemas(self) -> List[Tool]:
        """Get all schemas (cached after first generation)."""
        if self._schema_cache is None:
            # Generate once, cache forever (until invalidation)
            self._schema_cache = [
                SchemaGenerator.generate(t.func)
                for t in self._tools.values()
            ]
        return self._schema_cache
```

**Benefits**:
- First call: Generate schemas (~10ms)
- Subsequent calls: Return cached (< 1ms)
- Especially important with AST parsing overhead

### 3.3 Minimal Schema Variants

**Idea**: Provide multiple schema detail levels

```python
def get_minimal_schemas(self) -> List[Tool]:
    """Return minimal schemas (name + short description only)."""
    return [
        Tool(
            name=t.name,
            description=t.schema.description.split('.')[0],  # First sentence
            inputSchema={"type": "object", "properties": {}}  # Empty
        )
        for t in self._tools.values()
    ]

def get_full_schema(self, tool_name: str) -> Tool:
    """Return full schema for a specific tool."""
    return self._tools[tool_name].schema
```

**Usage**:
1. Agent receives minimal schemas (names + 1-line descriptions)
2. Agent requests full schema for tools it wants to use
3. Reduces initial overhead by 90%+

---

## 4. Implementation Plan

### Phase 1: Foundation (Week 1)

**Day 1-2: Tool Registry**
- [ ] Create `src/registry/tool_registry.py`
- [ ] Create `src/registry/decorators.py`
- [ ] Add `@mcp_tool` decorator to 5 sample tools
- [ ] Test manual registration + dynamic dispatch
- [ ] **Deliverable**: Registry works, eliminates elif chain

**Day 3-4: Decorator Integration**
- [ ] Add `@mcp_tool` to all 35 tools
- [ ] Add `@validate_params` decorator
- [ ] Add `@rate_limit` decorator
- [ ] Test all tools with decorators
- [ ] **Deliverable**: All tools decorated, validation automatic

**Day 5: Testing**
- [ ] Unit tests for registry
- [ ] Unit tests for decorators
- [ ] Integration tests with MCP server
- [ ] **Deliverable**: Green tests, no regressions

### Phase 2: AST Magic (Week 2)

**Day 1-2: Schema Generator**
- [ ] Create `src/registry/schema_generator.py`
- [ ] Implement `_python_type_to_json()`
- [ ] Implement `_parse_param_docs()`
- [ ] Test with 5 sample tools
- [ ] **Deliverable**: Schema generator works

**Day 3-4: Discovery System**
- [ ] Create `src/registry/discovery.py`
- [ ] Implement `discover_tools()`
- [ ] Auto-register all tools
- [ ] Remove manual Tool definitions from server.py
- [ ] **Deliverable**: 420 lines eliminated from server.py

**Day 5: Integration & Testing**
- [ ] Test all 35 tools with generated schemas
- [ ] Compare generated vs manual schemas
- [ ] Fix any schema mismatches
- [ ] **Deliverable**: All tools work with generated schemas

### Phase 3: Context Optimization (Week 3)

**Day 1-2: File Reorganization**
- [ ] Create new directory structure
- [ ] Move tools to category subdirectories
- [ ] Update imports
- [ ] Test all tools still work
- [ ] **Deliverable**: Organized file structure

**Day 3-4: Lazy Loading**
- [ ] Implement basic/popular tool filtering
- [ ] Update `list_tools()` to return basic tools first
- [ ] Add category-based filtering
- [ ] Test token reduction
- [ ] **Deliverable**: 70% token reduction achieved

**Day 5: Documentation & Polish**
- [ ] Update README with new architecture
- [ ] Add developer guide for adding new tools
- [ ] Add examples of decorator usage
- [ ] **Deliverable**: Complete documentation

---

## 5. Expected Outcomes

### 5.1 Code Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| server.py lines | 607 | ~150 | ↓ 75% |
| Tool definitions | 420 lines | 0 lines | ↓ 100% |
| Tool routing | 70 lines | 5 lines | ↓ 93% |
| Total codebase | 1,879 lines | ~1,450 lines | ↓ 23% |

### 5.2 Context Efficiency

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial tool schemas | 35 tools | 10 tools | ↓ 71% |
| Schema size | ~14.5 KB | ~4 KB | ↓ 72% |
| Token overhead | ~3,500 tokens | ~1,000 tokens | ↓ 71% |
| Schema generation | Manual | Automatic | ∞ |

### 5.3 Developer Experience

**Before** (adding a new tool):
1. Write method in `tools/read_tools.py` or `tools/post_tools.py` (~20 lines)
2. Add Tool definition in `server.py` (~12 lines)
3. Add elif branch in `server.py` (~2 lines)
4. Test all 3 places stay in sync
5. **Total**: 34 lines across 2 files

**After** (adding a new tool):
1. Write method with `@mcp_tool` decorator (~20 lines)
2. **Total**: 20 lines in 1 file (schema auto-generated)

**Improvement**: 42% less code, 50% fewer files, automatic synchronization

---

## 6. Risk Mitigation

### 6.1 Backwards Compatibility

**Risk**: Breaking existing tool calls

**Mitigation**:
- Keep tool names identical
- Keep parameter names identical
- Generated schemas should match manual schemas exactly
- Extensive testing before deployment

### 6.2 Schema Generation Accuracy

**Risk**: Generated schemas don't match expectations

**Mitigation**:
- Compare generated vs manual schemas in tests
- Manual override mechanism if needed:
  ```python
  @mcp_tool(schema_override=custom_schema)
  async def complex_tool(...):
      ...
  ```
- Comprehensive type hint coverage (already exists)

### 6.3 Performance Impact

**Risk**: AST parsing adds latency

**Mitigation**:
- Generate schemas once at startup, cache forever
- Benchmark schema generation time
- If needed, pre-generate and serialize schemas

### 6.4 MCP Protocol Limitations

**Risk**: MCP doesn't support lazy/dynamic tool loading

**Current Status**: MCP `list_tools()` returns all tools upfront

**Mitigation**:
- Still implement lazy loading internally (return subset)
- Agent can request more tools if needed
- Future: Propose MCP protocol extension for dynamic discovery

---

## 7. Future Enhancements

### 7.1 Plugin System

Allow external tools to be registered:

```python
# In external package
from mcp_x_server.registry import mcp_tool

@mcp_tool(category="custom")
async def my_custom_tool(param: str) -> dict:
    """My custom tool."""
    ...

# Auto-discovered via entry points
registry.discover_plugins()
```

### 7.2 Schema Versioning

Support multiple schema versions:

```python
@mcp_tool(version="2.0", deprecated="1.0")
async def search_tweets(...):
    ...
```

### 7.3 Usage Analytics

Track tool usage for intelligent prioritization:

```python
registry.get_popular_tools(days=30, limit=10)  # Most used in last 30 days
```

### 7.4 A/B Testing

Test new implementations:

```python
@mcp_tool(variant="v2", rollout_percent=10)
async def search_tweets_v2(...):
    ...
```

---

## 8. Success Metrics

### 8.1 Technical Metrics
- [ ] Code reduction: ≥ 400 lines eliminated
- [ ] Token reduction: ≥ 70% on initialization
- [ ] Schema accuracy: 100% match with manual schemas
- [ ] Test coverage: ≥ 90%
- [ ] Performance: Schema generation < 100ms

### 8.2 Developer Metrics
- [ ] Time to add new tool: < 5 minutes
- [ ] Files to modify: 1 (down from 2)
- [ ] Lines to write: ≤ 20 (down from 34)

### 8.3 User Metrics
- [ ] Tool discovery time: < 2 seconds
- [ ] Context overhead: < 1,000 tokens
- [ ] Tool execution: No regressions

---

## 9. Conclusion

This architecture optimization will transform mcp-x-server from a manually-maintained tool collection into a self-documenting, automatically-generated MCP server. By leveraging AST-based discovery and intelligent caching, we achieve:

1. **Massive code reduction** (455 lines, 24%)
2. **Dramatic token savings** (70% reduction)
3. **Better maintainability** (single source of truth)
4. **Improved DX** (add tool = write method)
5. **Future-proof architecture** (plugin system ready)

The implementation follows Anthropic's recommendations from "Code execution with MCP" and applies proven patterns from the software engineering world to the MCP ecosystem.

**Next Step**: Begin Phase 1 implementation and create GitHub PR for community review.
