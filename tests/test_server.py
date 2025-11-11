"""Test MCP X Server initialization and components."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import MCPXServer
from src.auth.account_manager import AccountManager
from src.clients.twikit_client import TwiKitClient


async def test_auth():
    """Test authentication."""
    print("Testing authentication...")
    am = AccountManager("config/cookies.json")
    cookies = am.load_cookies()
    auth_token = am.get_auth_token()
    ct0_token = am.get_ct0_token()

    assert len(cookies) > 0, "No cookies loaded"
    assert auth_token is not None, "No auth token found"
    assert ct0_token is not None, "No CT0 token found"

    print(f"✓ Cookies loaded: {len(cookies)} cookies")
    print(f"✓ Auth token: {auth_token[:20]}...")
    print(f"✓ CT0 token: {ct0_token[:20]}...")


async def test_twikit_client():
    """Test TwiKit client."""
    print("\nTesting TwiKit client...")
    am = AccountManager("config/cookies.json")
    cookies = am.load_cookies()
    client = TwiKitClient(cookies)
    await client.authenticate()

    assert client._authenticated, "Client not authenticated"
    print("✓ TwiKit client initialized and authenticated")


async def test_server_init():
    """Test server initialization."""
    print("\nTesting server initialization...")
    server = MCPXServer()

    assert server.server.name == "mcp-x-server"
    assert server.read_tools is not None
    assert server.write_tools is not None
    assert len(server.rate_limiter.configs) == 2

    await server.twscrape_client.setup()

    print("✓ Server initialized successfully")
    print(f"✓ Server name: {server.server.name}")
    print(f"✓ Read tools: {type(server.read_tools).__name__}")
    print(f"✓ Write tools: {type(server.write_tools).__name__}")
    print(f"✓ Rate limiter: {list(server.rate_limiter.configs.keys())}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP X Server Test Suite")
    print("=" * 60)

    try:
        await test_auth()
        await test_twikit_client()
        await test_server_init()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
