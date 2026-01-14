# [RFC] AST-Based Tool Discovery & Context Optimization for MCP X Server

## 🎯 Overview

This PR proposes a comprehensive architectural optimization for mcp-x-server based on Anthropic's ["Code execution with MCP: Building more efficient AI agents"](https://www.anthropic.com/engineering/code-execution-with-mcp) recommendations.

**Key Goals:**
- **Reduce codebase by 24%** (455 lines eliminated)
- **Reduce token overhead by 70%** (3,500 → 1,000 tokens on init)
- **Enable single-source-of-truth tool definitions** (docstrings + type hints → schemas)
- **Improve developer experience** (add tool = write method, done)

## 📊 Impact Summary

### Code Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| `server.py` lines | 607 | ~150 | ↓ 75% |
| Tool schema definitions | 420 lines | 0 lines | ↓ 100% |
| Tool routing code | 70 lines | 5 lines | ↓ 93% |
| Total codebase | 1,879 lines | ~1,450 lines | ↓ 23% |

### Context Efficiency

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial tool schemas sent | 35 tools | 10 tools | ↓ 71% |
| Schema payload size | ~14.5 KB | ~4 KB | ↓ 72% |
| Token overhead (estimated) | ~3,500 tokens | ~1,000 tokens | ↓ 71% |
| Schema source | Manual | Auto-generated | ∞ |

### Developer Experience

| Task | Before | After | Improvement |
|------|--------|-------|-------------|
| Files to modify | 2 files | 1 file | ↓ 50% |
| Lines to write | 34 lines | 20 lines | ↓ 41% |
| Synchronization | Manual | Automatic | ∞ |
| Time to add tool | ~15 min | ~5 min | ↓ 67% |

## 🔑 Key Changes

### 1. AST-Based Schema Generation

**Before** (manual, 12 lines per tool):
```python
# In server.py
Tool(
    name="search_tweets",
    description="Search tweets by keyword/hashtag with optional filters",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
            "filter_type": {"type": "string", "description": "Filter: top, latest, people, photos, videos"},
        },
        "required": ["query"],
    },
)
```

**After** (automatic, 0 lines):
```python
# In tools/read_tools.py - just add decorator
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
    # Implementation...
```

**Schema auto-generated from:**
- Method signature → parameter types, defaults, required vs optional
- Docstring → descriptions for tool and parameters
- Type hints → JSON schema types

### 2. Dynamic Tool Registry

**Before** (35-branch elif chain):
```python
@self.server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "search_tweets":
        result = await self.read_tools.search_tweets(**arguments)
    elif name == "get_tweet":
        result = await self.read_tools.get_tweet(**arguments)
    # ... 33 more elif branches (70 lines)
    else:
        raise ValueError(f"Unknown tool: {name}")
```

**After** (registry-based dispatch):
```python
@self.server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        result = await self.registry.call(name, arguments)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

**Benefits:**
- O(1) lookup vs O(n) linear search
- Plugin-style architecture (add tool = register, done)
- Eliminates 70 lines of boilerplate

### 3. Lazy Schema Loading

**Strategy: Return "basic" tools first, full list on demand**

```python
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    # Return 10 most popular/basic tools instead of all 35
    return self.registry.get_basic_schemas()
    # Or: return self.registry.get_popular_schemas(limit=10)
```

**Token Reduction:**
- 10 tools × 400 bytes = 4 KB (~1,000 tokens)
- vs 35 tools × 415 bytes = 14.5 KB (~3,500 tokens)
- **Result: 70% token reduction on initialization**

### 4. Decorator-Based Validation & Rate Limiting

**Before** (manual validation in every method):
```python
async def search_tweets(self, query: str, limit: Optional[int] = None):
    query = validate_search_query(query)
    limit = validate_limit(limit)
    # ... rest of implementation
```

**After** (automatic via decorators):
```python
@mcp_tool(category="read", phase="basic")
@rate_limit("read")
@validate_params({
    'query': validate_search_query,
    'limit': validate_limit
})
async def search_tweets(self, query: str, limit: Optional[int] = 20):
    # Validation and rate limiting happen automatically
    # ... implementation
```

## 🏗️ Architecture

### New Components

```
src/
├── registry/
│   ├── __init__.py
│   ├── tool_registry.py       # Central tool registry with caching
│   ├── decorators.py          # @mcp_tool, @validate_params, @rate_limit
│   ├── schema_generator.py    # AST-based schema generation from code
│   └── discovery.py           # Auto-discover tools from decorated methods
└── ...
```

### Tool Flow

```
1. Developer writes method with @mcp_tool decorator
2. ToolDiscovery finds all decorated methods
3. SchemaGenerator parses signature + docstring → JSON schema
4. ToolRegistry registers tool + schema
5. MCP server exposes via list_tools() and call_tool()
```

### Single Source of Truth

```
Method Signature + Docstring = Tool Definition
         ↓
   AST Parser
         ↓
   JSON Schema
         ↓
   MCP Tool
```

## 📚 Documentation

This PR includes comprehensive documentation:

1. **`docs/ARCHITECTURE_OPTIMIZATION.md`** (9,000+ words)
   - Complete architecture design
   - Detailed component specifications
   - Implementation plan with timelines
   - Benefits, risks, and mitigation strategies

2. **`docs/IMPLEMENTATION_GUIDE.md`** (6,000+ words)
   - Step-by-step implementation instructions
   - Code examples for each step
   - Testing and validation procedures
   - Common issues and solutions

3. **Comprehensive Analysis Report** (agent-generated)
   - Current codebase analysis (1,879 lines across 7 files)
   - Tool organization patterns
   - Optimization opportunities with ROI rankings
   - Specific recommendations for mcp-x-server

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Create tool registry infrastructure
- [ ] Create decorator system
- [ ] Add decorators to all 35 tools
- [ ] Test registry with manual registration

**Deliverable:** Working registry, decorators on all tools

### Phase 2: AST Magic (Week 2)
- [ ] Implement schema generator (AST parsing + docstring parsing)
- [ ] Implement auto-discovery system
- [ ] Remove 420 lines of manual schemas from server.py
- [ ] Compare generated vs manual schemas

**Deliverable:** Full AST-based generation, 420 lines eliminated

### Phase 3: Context Optimization (Week 3)
- [ ] Implement lazy schema loading
- [ ] Measure token reduction
- [ ] Optional: Reorganize files by category
- [ ] Polish and document

**Deliverable:** 70% token reduction, complete documentation

## ✅ Testing Strategy

### Unit Tests
- ToolRegistry registration and lookup
- Decorator functionality (@mcp_tool, @validate_params, @rate_limit)
- SchemaGenerator accuracy (signature → schema)
- ToolDiscovery auto-registration

### Integration Tests
- All 35 tools discovered correctly
- All tools executable through registry
- Schemas match expected format
- MCP server initialization

### Validation Tests
- Generated schemas match manual schemas exactly
- All required parameters identified correctly
- All optional parameters identified correctly
- Default values in schema descriptions
- Tool execution behavior unchanged

### Performance Benchmarks
- Schema generation time < 100ms
- Server startup time < 2 seconds
- Tool execution time (no regression)
- Token overhead measured and validated

## 🎨 Example: Adding a New Tool

### Before (old architecture)
1. Write method in `tools/read_tools.py` (20 lines)
2. Add Tool schema in `server.py` (12 lines)
3. Add elif branch in `server.py` (2 lines)
4. Ensure names stay synchronized
5. **Total: 34 lines across 2 files**

### After (new architecture)
1. Write method with decorator (20 lines in 1 file):
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
2. **Done!** Schema auto-generated, tool auto-registered, routing automatic.

**Savings: 41% less code, 50% fewer files, automatic synchronization**

## 🔍 Rationale

### Why This Matters

1. **Context is Expensive**
   - Claude's context window is valuable
   - 3,500 tokens of tool schemas = 3,500 tokens NOT available for user data
   - Lazy loading reduces overhead by 70%+

2. **Maintenance is Painful**
   - Currently: change signature → update 3 places (method, schema, routing)
   - After: change signature → schema auto-updates
   - Single source of truth prevents desynchronization bugs

3. **Scaling is Difficult**
   - 35 tools = manageable manually
   - 100+ tools = manual maintenance breaks down
   - AST-based approach scales to any number of tools

4. **Anthropic Recommends It**
   - From "Code execution with MCP" blog post
   - Proven pattern: "reduced token usage from 150,000 to 2,000 tokens—a 98.7% reduction"
   - Similar approach used by Cloudflare ("Code Mode")

### Inspiration

This design follows Anthropic's recommendations from ["Code execution with MCP"](https://www.anthropic.com/engineering/code-execution-with-mcp):

> "Present MCP servers as code APIs rather than direct tool calls. The agent can then write code to interact with MCP servers. This approach addresses both challenges: agents can load only the tools they need and process data in the execution environment before passing results back to the model."

While our implementation differs (we generate schemas from code, rather than presenting code directly), the **core principle is the same**: leverage code structure to reduce context overhead and improve maintainability.

## ⚠️ Risks & Mitigation

### Risk 1: Schema Generation Accuracy
**Mitigation**: Extensive testing, compare generated vs manual schemas, manual override option

### Risk 2: Breaking Changes
**Mitigation**: Keep tool names/parameters identical, gradual rollout, comprehensive tests

### Risk 3: Performance Impact
**Mitigation**: Cache generated schemas, benchmark startup time, optimize if needed

### Risk 4: MCP Protocol Limitations
**Mitigation**: Implement lazy loading internally, propose protocol extensions if needed

## 🤔 Open Questions

1. **Lazy Loading Strategy**: Which approach is best?
   - Option A: Return basic/popular tools first (recommended)
   - Option B: Return minimal schemas, full schema on request
   - Option C: Category-based loading

2. **File Reorganization**: Reorganize tools by category now or later?
   - Pro: Better organization, easier navigation
   - Con: More churn in this PR, can be done separately

3. **Backwards Compatibility**: Support old clients?
   - Tool names/parameters unchanged → fully compatible
   - Schema format unchanged → fully compatible
   - Should we version the server?

4. **Community Feedback**: What concerns does the community have?
   - Implementation complexity?
   - Maintenance burden?
   - Edge cases not covered?

## 📝 Checklist

### Documentation
- [x] Architecture design document (`ARCHITECTURE_OPTIMIZATION.md`)
- [x] Implementation guide (`IMPLEMENTATION_GUIDE.md`)
- [x] PR description with examples and rationale
- [ ] Update README with new architecture section
- [ ] Add developer guide for adding new tools

### Implementation
- [ ] Create `src/registry/` module
- [ ] Implement `ToolRegistry`
- [ ] Implement decorators (`@mcp_tool`, `@validate_params`, `@rate_limit`)
- [ ] Implement `SchemaGenerator` (AST + docstring parsing)
- [ ] Implement `ToolDiscovery`
- [ ] Add decorators to all 35 tools
- [ ] Update `server.py` to use registry
- [ ] Remove manual schemas (420 lines)
- [ ] Remove elif chain (70 lines)

### Testing
- [ ] Unit tests for registry
- [ ] Unit tests for decorators
- [ ] Unit tests for schema generator
- [ ] Unit tests for discovery
- [ ] Integration tests (all tools discovered)
- [ ] Validation tests (schemas match)
- [ ] Performance benchmarks
- [ ] Manual testing with Claude Code

### Validation
- [ ] All 35 tools discovered correctly
- [ ] All schemas accurate
- [ ] All tools executable
- [ ] Token overhead reduced by 70%+
- [ ] No regressions in tool behavior
- [ ] Server startup time < 2s
- [ ] Schema generation time < 100ms

## 🙏 Request for Feedback

This is a **Request for Comments (RFC)** at this stage. The implementation is ready to begin, but we want community input first:

1. **Architecture Review**: Does the proposed design make sense?
2. **Implementation Concerns**: Are there edge cases we're missing?
3. **Alternative Approaches**: Are there better ways to achieve these goals?
4. **Community Priorities**: Is this optimization valuable for the MCP ecosystem?

Please review the detailed documentation in `docs/` and share your thoughts!

## 🔗 Related Resources

- **Anthropic Blog Post**: [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Python AST Module**: https://docs.python.org/3/library/ast.html
- **Cloudflare's "Code Mode"**: Referenced in Anthropic blog post

---

**Reviewers**: @anthropic-team @mcp-community @bigsky

**Questions?** Comment on this PR or reach out in the MCP Discord.

**Let's make MCP servers more efficient! 🚀**
