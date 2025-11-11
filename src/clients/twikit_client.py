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
