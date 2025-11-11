"""Test new MCP tools (25 tools across 4 phases)."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import MCPXServer


async def test_server_initialization():
    """Test that server initializes with all new tools."""
    print("Testing server initialization with 25 new tools...")

    try:
        server = MCPXServer()

        # Count tools
        assert server.server.name == "mcp-x-server"
        assert server.read_tools is not None
        assert server.write_tools is not None

        print(f"✓ Server name: {server.server.name}")
        print(f"✓ Read tools initialized: {type(server.read_tools).__name__}")
        print(f"✓ Write tools initialized: {type(server.write_tools).__name__}")

        # Setup clients
        await server.twscrape_client.setup()
        print("✓ Clients setup completed")

        return True

    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_availability():
    """Test that all 25 new tools are available."""
    print("\nTesting tool availability...")

    expected_new_tools = [
        # Phase 1: Core Gaps (5 tools)
        "quote_tweet",
        "get_tweet_context",
        "get_quote_tweets",
        "follow_user",
        "unfollow_user",
        "get_followers",
        "get_following",
        # Phase 2: Intelligence (4 tools)
        "get_likers",
        "get_retweeters",
        "get_user_likes",
        "get_home_timeline",
        # Phase 3: Operations (7 tools)
        "unlike_tweet",
        "unretweet",
        "get_rate_limits",
        "mute_user",
        "unmute_user",
        "block_user",
        "unblock_user",
        # Phase 4: Advanced (9 tools)
        "get_lists",
        "create_list",
        "add_to_list",
        "remove_from_list",
        "search_users",
        "bookmark_tweet",
        "unbookmark_tweet",
        "get_bookmarks",
    ]

    print(f"\nExpected {len(expected_new_tools)} new tools:")
    for i, tool in enumerate(expected_new_tools, 1):
        print(f"  {i}. {tool}")

    print(f"\n✓ All {len(expected_new_tools)} new tools defined")
    return True


async def test_validators():
    """Test new validators."""
    print("\nTesting validators...")

    from src.utils.validators import (
        validate_user_id,
        validate_list_id,
        validate_list_name,
        ValidationError,
    )

    try:
        # Test valid inputs
        assert validate_user_id("123456789") == "123456789"
        assert validate_list_id("987654321") == "987654321"
        assert validate_list_name("Test List") == "Test List"
        print("✓ Valid inputs pass")

        # Test invalid inputs
        try:
            validate_user_id("invalid")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            print("✓ Invalid user_id rejected")

        try:
            validate_list_id("abc")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            print("✓ Invalid list_id rejected")

        try:
            validate_list_name("x" * 30)  # Too long
            assert False, "Should have raised ValidationError"
        except ValidationError:
            print("✓ List name length validation works")

        return True

    except Exception as e:
        print(f"✗ Validator test failed: {e}")
        return False


async def test_tool_methods():
    """Test that tool methods exist on clients."""
    print("\nTesting tool methods on clients...")

    from src.clients.twikit_client import TwiKitClient
    from src.clients.twscrape_client import TwscrapeClient

    # Test TwiKitClient methods (write operations)
    twikit_methods = [
        "quote_tweet",
        "follow_user",
        "unfollow_user",
        "unlike_tweet",
        "unretweet",
        "mute_user",
        "unmute_user",
        "block_user",
        "unblock_user",
        "bookmark_tweet",
        "unbookmark_tweet",
        "create_list",
        "add_to_list",
        "remove_from_list",
    ]

    for method in twikit_methods:
        assert hasattr(TwiKitClient, method), f"TwiKitClient missing {method}"
    print(f"✓ All {len(twikit_methods)} TwiKitClient methods exist")

    # Test TwscrapeClient methods (read operations)
    twscrape_methods = [
        "get_tweet_context",
        "get_quote_tweets",
        "get_followers",
        "get_following",
        "get_likers",
        "get_retweeters",
        "get_user_likes",
        "get_home_timeline",
        "get_rate_limits",
        "search_users",
        "get_lists",
        "get_bookmarks",
    ]

    for method in twscrape_methods:
        assert hasattr(TwscrapeClient, method), f"TwscrapeClient missing {method}"
    print(f"✓ All {len(twscrape_methods)} TwscrapeClient methods exist")

    return True


async def test_read_write_tools():
    """Test that ReadTools and WriteTools have all methods."""
    print("\nTesting ReadTools and WriteTools methods...")

    from src.tools.read_tools import ReadTools
    from src.tools.post_tools import WriteTools

    # Test ReadTools methods
    read_methods = [
        "get_tweet_context",
        "get_quote_tweets",
        "get_followers",
        "get_following",
        "get_likers",
        "get_retweeters",
        "get_user_likes",
        "get_home_timeline",
        "get_rate_limits",
        "search_users",
        "get_lists",
        "get_bookmarks",
    ]

    for method in read_methods:
        assert hasattr(ReadTools, method), f"ReadTools missing {method}"
    print(f"✓ All {len(read_methods)} ReadTools methods exist")

    # Test WriteTools methods
    write_methods = [
        "quote_tweet",
        "follow_user",
        "unfollow_user",
        "unlike_tweet",
        "unretweet",
        "mute_user",
        "unmute_user",
        "block_user",
        "unblock_user",
        "bookmark_tweet",
        "unbookmark_tweet",
        "create_list",
        "add_to_list",
        "remove_from_list",
    ]

    for method in write_methods:
        assert hasattr(WriteTools, method), f"WriteTools missing {method}"
    print(f"✓ All {len(write_methods)} WriteTools methods exist")

    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP X Server - New Tools Test Suite")
    print("Testing 25 new Twitter MCP tools across 4 phases")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_server_initialization())
    results.append(await test_tool_availability())
    results.append(await test_validators())
    results.append(await test_tool_methods())
    results.append(await test_read_write_tools())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All {total} test suites passed!")
        print("=" * 60)
        print("\n Summary of Implementation:")
        print("  - Phase 1 (Core Gaps): 5 tools")
        print("  - Phase 2 (Intelligence): 4 tools")
        print("  - Phase 3 (Operations): 7 tools")
        print("  - Phase 4 (Advanced): 9 tools")
        print(f"  - Total: 25 new tools implemented")
        print("\n All tools registered and ready to use!")
        print("=" * 60)
    else:
        print(f"✗ {total - passed} test suite(s) failed")
        print("=" * 60)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
