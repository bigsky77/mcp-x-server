# Development Guide

## Project Structure

```
mcp-x-server/
├── src/
│   ├── server.py              # MCP server entry point
│   ├── auth/
│   │   └── account_manager.py # Cookie-based authentication
│   ├── clients/
│   │   ├── twikit_client.py   # Write operations (TwiKit)
│   │   └── twscrape_client.py # Read operations (Twscrape)
│   ├── tools/
│   │   ├── read_tools.py      # Read MCP primitives
│   │   └── post_tools.py      # Write MCP primitives
│   └── utils/
│       ├── rate_limiter.py    # Rate limiting
│       └── validators.py      # Input validation
├── config/
│   ├── config.yaml            # Server configuration
│   └── cookies.json           # Auth cookies (gitignored)
└── docs/                      # Documentation
```

## Adding New Tools

### 1. Define the tool function

In `src/tools/read_tools.py` or `src/tools/post_tools.py`:

```python
async def new_tool(self, param: str) -> Dict[str, Any]:
    """Tool description."""
    # Validate inputs
    param = validate_param(param)

    # Call client
    result = await self.client.some_method(param)
    return result
```

### 2. Register in server

In `src/server.py`, add to `list_tools()`:

```python
Tool(
    name="new_tool",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"},
        },
        "required": ["param"],
    },
)
```

### 3. Add handler

In `call_tool()`:

```python
elif name == "new_tool":
    result = await self.read_tools.new_tool(**arguments)
```

## Client Extensions

### TwiKit (Write Operations)

Add methods to `src/clients/twikit_client.py`:

```python
async def new_write_operation(self, param: str) -> dict:
    """New write operation."""
    await self.authenticate()
    try:
        result = await self.client.some_api_call(param)
        return {"status": "success", "data": result}
    except Exception as e:
        raise Exception(f"Operation failed: {e}")
```

### Twscrape (Read Operations)

Add methods to `src/clients/twscrape_client.py`:

```python
async def new_read_operation(self, param: str) -> List[dict]:
    """New read operation."""
    try:
        data = await gather(self.api.some_scrape(param))
        return [self._serialize(item) for item in data]
    except Exception as e:
        raise Exception(f"Operation failed: {e}")
```

## Testing

Run tests:

```bash
# Run test suite
python tests/test_server.py

# Test write operations
python tests/test_write_only.py

# Manual testing
python -c "
import asyncio
from src.server import MCPXServer

async def test():
    server = MCPXServer()
    # Test components

asyncio.run(test())
"
```

## Rate Limiting

Current limits (configured in `config/config.yaml`):

- **Read**: 300 requests / 15 minutes
- **Write**: 50 requests / 24 hours

Modify in config:

```yaml
rate_limits:
  read:
    requests_per_window: 300
    window_seconds: 900
  write:
    requests_per_window: 50
    window_seconds: 86400
```

## Code Style

- **Formatting**: Black (line length: 100)
- **Linting**: Ruff
- **Type hints**: Use where appropriate
- **Docstrings**: Google style

Format code:

```bash
black src/
ruff check src/
```

## Common Tasks

### Adding a New Validator

In `src/utils/validators.py`:

```python
def validate_custom_param(param: str) -> str:
    """Validate custom parameter."""
    if not param or len(param) < 3:
        raise ValidationError("Parameter too short")
    return param.strip()
```

### Updating Rate Limits

Edit `config/config.yaml` and restart the server:

```yaml
rate_limits:
  read:
    requests_per_window: 500  # Increased from 300
    window_seconds: 900
```

### Debugging Authentication

Check cookies:

```bash
python -c "
from src.auth.account_manager import AccountManager
am = AccountManager('config/cookies.json')
print(f'Auth token: {am.get_auth_token()[:20]}...')
print(f'CT0 token: {am.get_ct0_token()[:20]}...')
"
```
