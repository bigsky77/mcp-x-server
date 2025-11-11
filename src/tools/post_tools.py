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

    async def quote_tweet(
        self, tweet_id: str, text: str, media_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a quote tweet.

        Args:
            tweet_id: ID of tweet to quote
            text: Quote comment text (max 280 characters)
            media_ids: Optional list of media IDs to attach

        Returns:
            Posted quote tweet object
        """
        tweet_id = validate_tweet_id(tweet_id)
        text = validate_tweet_text(text)
        result = await self.client.quote_tweet(tweet_id, text, media_ids=media_ids)
        return result

    async def follow_user(self, user_id: str) -> Dict[str, Any]:
        """
        Follow a user.

        Args:
            user_id: User ID to follow

        Returns:
            Result with user info and following status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.follow_user(user_id)
        return result

    async def unfollow_user(self, user_id: str) -> Dict[str, Any]:
        """
        Unfollow a user.

        Args:
            user_id: User ID to unfollow

        Returns:
            Result with user info and following status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.unfollow_user(user_id)
        return result

    async def unlike_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Remove like from a tweet.

        Args:
            tweet_id: ID of tweet to unlike

        Returns:
            Result with tweet_id and liked status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.unlike_tweet(tweet_id)
        return result

    async def unretweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Remove retweet from a tweet.

        Args:
            tweet_id: ID of tweet to unretweet

        Returns:
            Result with tweet_id and retweeted status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.unretweet(tweet_id)
        return result

    async def mute_user(self, user_id: str) -> Dict[str, Any]:
        """
        Mute a user.

        Args:
            user_id: User ID to mute

        Returns:
            Result with user info and muted status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.mute_user(user_id)
        return result

    async def unmute_user(self, user_id: str) -> Dict[str, Any]:
        """
        Unmute a user.

        Args:
            user_id: User ID to unmute

        Returns:
            Result with user info and muted status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.unmute_user(user_id)
        return result

    async def block_user(self, user_id: str) -> Dict[str, Any]:
        """
        Block a user.

        Args:
            user_id: User ID to block

        Returns:
            Result with user info and blocked status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.block_user(user_id)
        return result

    async def unblock_user(self, user_id: str) -> Dict[str, Any]:
        """
        Unblock a user.

        Args:
            user_id: User ID to unblock

        Returns:
            Result with user info and blocked status
        """
        from ..utils.validators import validate_user_id
        user_id = validate_user_id(user_id)
        result = await self.client.unblock_user(user_id)
        return result

    async def bookmark_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Bookmark a tweet.

        Args:
            tweet_id: ID of tweet to bookmark

        Returns:
            Result with tweet_id and bookmarked status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.bookmark_tweet(tweet_id)
        return result

    async def unbookmark_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Remove bookmark from a tweet.

        Args:
            tweet_id: ID of tweet to unbookmark

        Returns:
            Result with tweet_id and bookmarked status
        """
        tweet_id = validate_tweet_id(tweet_id)
        result = await self.client.unbookmark_tweet(tweet_id)
        return result

    async def create_list(
        self, name: str, description: Optional[str] = None, private: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new Twitter list.

        Args:
            name: List name
            description: Optional list description
            private: Whether the list is private

        Returns:
            Created list object with id and details
        """
        from ..utils.validators import validate_list_name
        name = validate_list_name(name)
        result = await self.client.create_list(name, description=description, private=private)
        return result

    async def add_to_list(self, list_id: str, user_id: str) -> Dict[str, Any]:
        """
        Add user to a list.

        Args:
            list_id: List ID
            user_id: User ID to add

        Returns:
            Result with list_id, user_id and added status
        """
        from ..utils.validators import validate_list_id, validate_user_id
        list_id = validate_list_id(list_id)
        user_id = validate_user_id(user_id)
        result = await self.client.add_to_list(list_id, user_id)
        return result

    async def remove_from_list(self, list_id: str, user_id: str) -> Dict[str, Any]:
        """
        Remove user from a list.

        Args:
            list_id: List ID
            user_id: User ID to remove

        Returns:
            Result with list_id, user_id and removed status
        """
        from ..utils.validators import validate_list_id, validate_user_id
        list_id = validate_list_id(list_id)
        user_id = validate_user_id(user_id)
        result = await self.client.remove_from_list(list_id, user_id)
        return result
