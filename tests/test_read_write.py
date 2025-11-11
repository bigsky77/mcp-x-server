"""Test read and write operations."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import MCPXServer


async def test_read_operations():
    """Test read tools."""
    print("=" * 60)
    print("Testing Read Operations")
    print("=" * 60)

    server = MCPXServer()
    await server.twscrape_client.setup()

    # Test 1: Search tweets
    print("\n1. Testing search_tweets...")
    try:
        results = await server.read_tools.search_tweets("AI", limit=3)
        print(f"✓ Found {len(results)} tweets")
        if results:
            print(f"  Sample: {results[0]['text'][:80]}...")
    except Exception as e:
        print(f"✗ Search failed: {e}")

    # Test 2: Get user
    print("\n2. Testing get_user...")
    try:
        user = await server.read_tools.get_user("sama")
        print(f"✓ User: @{user['username']} ({user['name']})")
        print(f"  Followers: {user['metrics']['followers']:,}")
    except Exception as e:
        print(f"✗ Get user failed: {e}")

    # Test 3: Get user tweets
    print("\n3. Testing get_user_tweets...")
    try:
        tweets = await server.read_tools.get_user_tweets("sama", limit=3)
        print(f"✓ Found {len(tweets)} tweets from @sama")
        if tweets:
            print(f"  Latest: {tweets[0]['text'][:80]}...")
    except Exception as e:
        print(f"✗ Get user tweets failed: {e}")


async def test_write_operations():
    """Test write tools."""
    print("\n" + "=" * 60)
    print("Testing Write Operations")
    print("=" * 60)

    server = MCPXServer()

    # Test: Post tweet (with confirmation)
    print("\n⚠️  Write operations will post to X!")
    print("Testing post_tweet with a test message...")

    test_message = "🤖 Testing MCP X Server - automated test post"

    try:
        # Uncomment to actually post:
        # result = await server.write_tools.post_tweet(test_message)
        # print(f"✓ Tweet posted! ID: {result['id']}")
        # print(f"  Text: {result['text']}")

        print(f"✓ Post tweet function ready (skipped actual posting)")
        print(f"  Would post: '{test_message}'")
    except Exception as e:
        print(f"✗ Post tweet failed: {e}")


async def main():
    """Run read/write tests."""
    try:
        await test_read_operations()
        await test_write_operations()

        print("\n" + "=" * 60)
        print("✓ Read/Write tests complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
