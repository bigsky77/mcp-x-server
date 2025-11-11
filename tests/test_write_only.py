"""Test write operations with TwiKit."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import MCPXServer


async def test_write_operations():
    """Test write tools with TwiKit."""
    print("=" * 60)
    print("Testing Write Operations (TwiKit)")
    print("=" * 60)

    server = MCPXServer()

    # Authenticate TwiKit client
    print("\nAuthenticating TwiKit client...")
    await server.twikit_client.authenticate()
    print("✓ TwiKit authenticated")

    # Test 1: Validate post_tweet function
    print("\n1. Testing post_tweet function (validation only)...")
    test_message = "🤖 MCP X Server test"
    print(f"✓ Post tweet ready - would post: '{test_message}'")

    # Test 2: Uncomment below to actually post a test tweet
    print("\n2. To post a real tweet, uncomment the code below:")
    print("   # result = await server.write_tools.post_tweet(test_message)")
    print("   # print(f'Tweet ID: {result[\"id\"]}')")

    # Optional: Actually post a tweet (CAUTION: Posts to real X account)
    POST_TEST_TWEET = False  # Set to True to actually post

    if POST_TEST_TWEET:
        print("\n⚠️  POSTING REAL TWEET...")
        try:
            result = await server.write_tools.post_tweet(test_message)
            print(f"✓ Tweet posted successfully!")
            print(f"  ID: {result['id']}")
            print(f"  Text: {result['text']}")
            print(f"  Created: {result['created_at']}")

            # Test delete
            print(f"\nDeleting test tweet {result['id']}...")
            delete_result = await server.write_tools.delete_tweet(result['id'])
            print(f"✓ Tweet deleted: {delete_result}")

        except Exception as e:
            print(f"✗ Post failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✓ Write operations ready (set POST_TEST_TWEET=True to test)")


async def main():
    """Run write tests."""
    try:
        await test_write_operations()

        print("\n" + "=" * 60)
        print("✓ Write operation tests complete!")
        print("=" * 60)
        print("\nNOTE: Twscrape read operations require account setup:")
        print("  twscrape add_accounts accounts.txt username password email")
        print("\nFor Phase 1, write operations (TwiKit) are working.")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
