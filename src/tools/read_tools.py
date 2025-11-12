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

    async def get_tweet_context(
        self, tweet_id: str, include_replies: Optional[bool] = True, max_depth: Optional[int] = 10
    ) -> Dict[str, Any]:
        """
        Get full conversation thread and context for a tweet.

        Args:
            tweet_id: Tweet ID
            include_replies: Whether to include replies (default: True)
            max_depth: Maximum depth for parent tweets (default: 10)

        Returns:
            Conversation context with parent tweets, main tweet, and replies
        """
        tweet_id = validate_tweet_id(tweet_id)
        context = await self.client.get_tweet_context(
            tweet_id, include_replies=include_replies, max_depth=max_depth
        )
        return context

    async def get_quote_tweets(self, tweet_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get quote tweets of a specific tweet.

        Args:
            tweet_id: Tweet ID
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of quote tweets
        """
        tweet_id = validate_tweet_id(tweet_id)
        limit = validate_limit(limit)
        quotes = await self.client.get_quote_tweets(tweet_id, limit=limit)
        return quotes

    async def get_followers(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get followers for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of user objects for followers
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        limit = validate_limit(limit)
        followers = await self.client.get_followers(user_id, limit=limit)
        return followers

    async def get_following(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get following list for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of user objects for accounts being followed
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        limit = validate_limit(limit)
        following = await self.client.get_following(user_id, limit=limit)
        return following

    async def get_retweeters(self, tweet_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get users who retweeted a tweet.

        Args:
            tweet_id: Tweet ID
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of user objects who retweeted
        """
        tweet_id = validate_tweet_id(tweet_id)
        limit = validate_limit(limit)
        retweeters = await self.client.get_retweeters(tweet_id, limit=limit)
        return retweeters

    async def search_users(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for users by query.

        Args:
            query: Search query
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of user objects matching the query
        """
        query = validate_search_query(query)
        limit = validate_limit(limit)
        users = await self.client.search_users(query, limit=limit)
        return users

    async def get_bookmarks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get bookmarked tweets for authenticated user.

        Args:
            limit: Maximum number of results (default: 20, max: 100)

        Returns:
            List of bookmarked tweets
        """
        limit = validate_limit(limit)
        bookmarks = await self.client.get_bookmarks(limit=limit)
        return bookmarks

    async def get_rate_limits(self) -> Dict[str, Any]:
        """
        Get current API rate limit status.

        Returns:
            Rate limit information for various endpoints
        """
        rate_limits = await self.client.get_rate_limits()
        return rate_limits
