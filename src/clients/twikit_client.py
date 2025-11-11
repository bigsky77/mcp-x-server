"""TwiKit client wrapper for write operations."""

from typing import Optional
from twikit import Client
from twikit.errors import BadRequest, Unauthorized


class TwiKitClient:
    """Wrapper for TwiKit client with cookie authentication."""

    def __init__(self, cookies: list):
        self.client = Client(language="en-US")
        self.cookies = cookies
        self._authenticated = False

    async def authenticate(self):
        """Authenticate using cookies."""
        if self._authenticated:
            return

        try:
            # Set cookies on client - http.cookies is the correct path
            for cookie in self.cookies:
                self.client.http.cookies.set(cookie["name"], cookie["value"])
            self._authenticated = True
        except Exception as e:
            raise Exception(f"TwiKit authentication failed: {e}")

    async def post_tweet(self, text: str, media_ids: Optional[list] = None) -> dict:
        """Post a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.create_tweet(text=text, media_ids=media_ids)
            return {
                "id": tweet.id,
                "text": tweet.text,
                "created_at": str(tweet.created_at),
                "author": tweet.user.screen_name,
            }
        except (BadRequest, Unauthorized) as e:
            raise Exception(f"Failed to post tweet: {e}")

    async def reply_to_tweet(self, tweet_id: str, text: str) -> dict:
        """Reply to a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.create_tweet(text=text, reply_to=tweet_id)
            return {
                "id": tweet.id,
                "text": tweet.text,
                "reply_to": tweet_id,
                "created_at": str(tweet.created_at),
            }
        except Exception as e:
            raise Exception(f"Failed to reply: {e}")

    async def like_tweet(self, tweet_id: str) -> dict:
        """Like a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.favorite()
            return {"id": tweet_id, "liked": True}
        except Exception as e:
            raise Exception(f"Failed to like tweet: {e}")

    async def retweet(self, tweet_id: str) -> dict:
        """Retweet a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.retweet()
            return {"id": tweet_id, "retweeted": True}
        except Exception as e:
            raise Exception(f"Failed to retweet: {e}")

    async def delete_tweet(self, tweet_id: str) -> dict:
        """Delete a tweet."""
        await self.authenticate()
        try:
            await self.client.delete_tweet(tweet_id)
            return {"id": tweet_id, "deleted": True}
        except Exception as e:
            raise Exception(f"Failed to delete tweet: {e}")

    async def quote_tweet(self, tweet_id: str, text: str, media_ids: Optional[list] = None) -> dict:
        """Create a quote tweet."""
        await self.authenticate()
        try:
            # TwiKit's create_tweet with quote parameter
            tweet = await self.client.create_tweet(
                text=text,
                media_ids=media_ids,
                quote=tweet_id
            )
            return {
                "id": tweet.id,
                "text": tweet.text,
                "quoted_tweet_id": tweet_id,
                "created_at": str(tweet.created_at),
                "author": tweet.user.screen_name,
            }
        except Exception as e:
            raise Exception(f"Failed to quote tweet: {e}")

    async def follow_user(self, user_id: str) -> dict:
        """Follow a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.follow()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "following": True,
            }
        except Exception as e:
            raise Exception(f"Failed to follow user: {e}")

    async def unfollow_user(self, user_id: str) -> dict:
        """Unfollow a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.unfollow()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "following": False,
            }
        except Exception as e:
            raise Exception(f"Failed to unfollow user: {e}")

    async def unlike_tweet(self, tweet_id: str) -> dict:
        """Remove like from a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.unfavorite()
            return {"id": tweet_id, "liked": False}
        except Exception as e:
            raise Exception(f"Failed to unlike tweet: {e}")

    async def unretweet(self, tweet_id: str) -> dict:
        """Remove retweet from a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.unretweet()
            return {"id": tweet_id, "retweeted": False}
        except Exception as e:
            raise Exception(f"Failed to unretweet: {e}")

    async def mute_user(self, user_id: str) -> dict:
        """Mute a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.mute()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "muted": True,
            }
        except Exception as e:
            raise Exception(f"Failed to mute user: {e}")

    async def unmute_user(self, user_id: str) -> dict:
        """Unmute a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.unmute()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "muted": False,
            }
        except Exception as e:
            raise Exception(f"Failed to unmute user: {e}")

    async def block_user(self, user_id: str) -> dict:
        """Block a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.block()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "blocked": True,
            }
        except Exception as e:
            raise Exception(f"Failed to block user: {e}")

    async def unblock_user(self, user_id: str) -> dict:
        """Unblock a user."""
        await self.authenticate()
        try:
            user = await self.client.get_user_by_id(user_id)
            await user.unblock()
            return {
                "user_id": user_id,
                "username": user.screen_name,
                "blocked": False,
            }
        except Exception as e:
            raise Exception(f"Failed to unblock user: {e}")

    async def bookmark_tweet(self, tweet_id: str) -> dict:
        """Bookmark a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.bookmark()
            return {"id": tweet_id, "bookmarked": True}
        except Exception as e:
            raise Exception(f"Failed to bookmark tweet: {e}")

    async def unbookmark_tweet(self, tweet_id: str) -> dict:
        """Remove bookmark from a tweet."""
        await self.authenticate()
        try:
            tweet = await self.client.get_tweet_by_id(tweet_id)
            await tweet.unbookmark()
            return {"id": tweet_id, "bookmarked": False}
        except Exception as e:
            raise Exception(f"Failed to unbookmark tweet: {e}")

    async def create_list(self, name: str, description: Optional[str] = None, private: bool = False) -> dict:
        """Create a new Twitter list."""
        await self.authenticate()
        try:
            twitter_list = await self.client.create_list(
                name=name,
                description=description or "",
                is_private=private
            )
            return {
                "list_id": twitter_list.id,
                "name": twitter_list.name,
                "description": twitter_list.description,
                "private": private,
            }
        except Exception as e:
            raise Exception(f"Failed to create list: {e}")

    async def add_to_list(self, list_id: str, user_id: str) -> dict:
        """Add user to a list."""
        await self.authenticate()
        try:
            twitter_list = await self.client.get_list(list_id)
            await twitter_list.add_member(user_id)
            return {
                "list_id": list_id,
                "user_id": user_id,
                "added": True,
            }
        except Exception as e:
            raise Exception(f"Failed to add user to list: {e}")

    async def remove_from_list(self, list_id: str, user_id: str) -> dict:
        """Remove user from a list."""
        await self.authenticate()
        try:
            twitter_list = await self.client.get_list(list_id)
            await twitter_list.remove_member(user_id)
            return {
                "list_id": list_id,
                "user_id": user_id,
                "removed": True,
            }
        except Exception as e:
            raise Exception(f"Failed to remove user from list: {e}")
