"""MCP write tools for X API."""

from typing import Any, Dict, Optional, List
from ..clients.twikit_client import TwiKitClient
from ..utils.validators import validate_tweet_id, validate_tweet_text


class WriteTools:
    """MCP tools for posting/writing to X."""

    def __init__(self, client: TwiKitClient):
        self.client = client

    async def post_tweet(
        self, text: str, media_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a new tweet.

        Args:
            text: Tweet text (max 280 characters)
            media_ids: Optional list of media IDs to attach

        Returns:
            Posted tweet object with id, text, created_at
        """
        text = validate_tweet_text(text)
        result = await self.client.post_tweet(text, media_ids=media_ids)
        return result

    async def reply_to_tweet(self, tweet_id: str, text: str) -> Dict[str, Any]:
        """
        Reply to an existing tweet.

        Args:
            tweet_id: ID of tweet to reply to
            text: Reply text (max 280 characters)

        Returns:
            Posted reply object with id, text, reply_to
        """
        tweet_id = validate_tweet_id(tweet_id)
        text = validate_tweet_text(text)

        result = await self.client.reply_to_tweet(tweet_id, text)
        return result

    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Like a tweet.

        Args:
            tweet_id: ID of tweet to like

        Returns:
            Result with tweet_id and liked status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.like_tweet(tweet_id)
        return result

    async def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Retweet a tweet.

        Args:
            tweet_id: ID of tweet to retweet

        Returns:
            Result with tweet_id and retweeted status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.retweet(tweet_id)
        return result

    async def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Delete own tweet.

        Args:
            tweet_id: ID of tweet to delete

        Returns:
            Result with tweet_id and deleted status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.delete_tweet(tweet_id)
        return result
