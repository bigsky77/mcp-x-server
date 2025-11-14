"""Test script for TwitterAPI.io client."""

import asyncio
import os
from pathlib import Path
from src.clients.twitterapi_client import TwitterAPIClient


# Load .env.local
env_file = Path(__file__).parent / ".env.local"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value


async def test_search_tweets():
    """Test search tweets functionality."""
    print("Testing search_tweets...")
    client = TwitterAPIClient()

    try:
        result = await client.search_tweets("AI", limit=2)
        print(f"✓ search_tweets: Found {len(result)} tweets")
        if result:
            print(f"  First tweet: {result[0].get('text', '')[:100]}...")
    except Exception as e:
        print(f"✗ search_tweets failed: {e}")


async def test_get_user():
    """Test get user functionality."""
    print("\nTesting get_user...")
    client = TwitterAPIClient()

    try:
        result = await client.get_user("elonmusk")
        print(f"✓ get_user: Got user @{result.get('username')}")
        print(f"  Name: {result.get('name')}")
        print(f"  Followers: {result.get('metrics', {}).get('followers')}")
    except Exception as e:
        print(f"✗ get_user failed: {e}")


async def test_get_tweet():
    """Test get tweet functionality."""
    print("\nTesting get_tweet...")
    client = TwitterAPIClient()

    try:
        # Using a known tweet ID - Elon's first tweet
        result = await client.get_tweet("20")
        print(f"✓ get_tweet: Got tweet {result.get('id')}")
        print(f"  Text: {result.get('text', '')[:100]}...")
    except Exception as e:
        print(f"✗ get_tweet failed: {e}")


async def test_get_followers():
    """Test get followers functionality."""
    print("\nTesting get_followers...")
    client = TwitterAPIClient()

    try:
        result = await client.get_followers("elonmusk", limit=5)
        print(f"✓ get_followers: Found {len(result)} followers")
    except Exception as e:
        print(f"✗ get_followers failed: {e}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TwitterAPI.io Client Tests")
    print("=" * 60)

    await test_search_tweets()
    await test_get_user()
    await test_get_tweet()
    await test_get_followers()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
