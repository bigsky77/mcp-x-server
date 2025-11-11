"""MCP read tools for X API."""

from typing import Any, Dict, List, Optional
from ..clients.twscrape_client import TwscrapeClient
from ..utils.validators import (
    validate_tweet_id,
    validate_username,
    validate_search_query,
    validate_limit,
)


class ReadTools:
    """MCP tools for reading/scraping X data."""

    def __init__(self, client: TwscrapeClient):
        self.client = client

    async def search_tweets(
        self, query: str, limit: Optional[int] = None, filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search tweets by keyword/hashtag.

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

    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get single tweet by ID.

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet object with full metadata
        """
        tweet_id = validate_tweet_id(tweet_id)
        tweet = await self.client.get_tweet(tweet_id)
        return tweet

    async def get_user_tweets(self, username: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get tweets from user timeline.

        Args:
            username: X username (with or without @)
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of tweet objects from user's timeline
        """
        username = validate_username(username)
        limit = validate_limit(limit)

        tweets = await self.client.get_user_tweets(username, limit=limit)
        return tweets

    async def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user profile.

        Args:
            username: X username (with or without @)

        Returns:
            User object with profile data and metrics
        """
        username = validate_username(username)
        user = await self.client.get_user(username)
        return user

    async def get_mentions(self, username: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get mentions for authenticated account.

        Args:
            username: Username to search mentions for
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of tweets mentioning the user
        """
        username = validate_username(username)
        limit = validate_limit(limit)

        mentions = await self.client.get_mentions(username, limit=limit)
        return mentions
