"""Twscrape client wrapper for read operations."""

from typing import List, Optional
from twscrape import API, gather
from twscrape.models import Tweet, User


class TwscrapeClient:
    """Wrapper for Twscrape API for read operations."""

    def __init__(self, accounts_file: Optional[str] = None):
        self.api = API()
        self.accounts_file = accounts_file

    async def setup(self):
        """Initialize API (placeholder for account pool setup)."""
        # Phase 1: No account pool setup
        # Future: Load accounts from accounts_file
        pass

    async def search_tweets(
        self, query: str, limit: int = 20, filter_type: Optional[str] = None
    ) -> List[dict]:
        """Search tweets by query."""
        try:
            tweets = await gather(self.api.search(query, limit=limit))
            return [self._serialize_tweet(t) for t in tweets]
        except Exception as e:
            raise Exception(f"Failed to search tweets: {e}")

    async def get_tweet(self, tweet_id: str) -> dict:
        """Get single tweet by ID."""
        try:
            tweet = await self.api.tweet_details(int(tweet_id))
            return self._serialize_tweet(tweet)
        except Exception as e:
            raise Exception(f"Failed to get tweet: {e}")

    async def get_user_tweets(self, username: str, limit: int = 20) -> List[dict]:
        """Get tweets from user timeline."""
        try:
            # Get user ID first
            user = await self.api.user_by_login(username)
            user_id = user.id
            # Use user_tweets with user ID (not username)
            tweets = await gather(self.api.user_tweets(user_id, limit=limit))
            return [self._serialize_tweet(t) for t in tweets]
        except Exception as e:
            raise Exception(f"Failed to get user tweets: {e}")

    async def get_user(self, username: str) -> dict:
        """Get user profile."""
        try:
            user = await self.api.user_by_login(username)
            return self._serialize_user(user)
        except Exception as e:
            raise Exception(f"Failed to get user: {e}")

    async def get_mentions(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get mentions for user."""
        try:
            # Twscrape doesn't have direct mentions API
            # Workaround: search for @username
            query = f"@{user_id}"
            tweets = await gather(self.api.search(query, limit=limit))
            return [self._serialize_tweet(t) for t in tweets]
        except Exception as e:
            raise Exception(f"Failed to get mentions: {e}")

    def _serialize_tweet(self, tweet: Tweet) -> dict:
        """Convert Tweet object to dict."""
        return {
            "id": str(tweet.id),
            "text": tweet.rawContent,
            "author": {
                "username": tweet.user.username,
                "name": tweet.user.displayname,
                "followers": tweet.user.followersCount,
            },
            "created_at": str(tweet.date),
            "metrics": {
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "replies": tweet.replyCount,
                "views": tweet.viewCount or 0,
            },
            "in_reply_to": str(tweet.inReplyToTweetId) if tweet.inReplyToTweetId else None,
        }

    def _serialize_user(self, user: User) -> dict:
        """Convert User object to dict."""
        return {
            "id": str(user.id),
            "username": user.username,
            "name": user.displayname,
            "description": user.rawDescription,
            "created_at": str(user.created),
            "metrics": {
                "followers": getattr(user, 'followersCount', 0),
                "following": getattr(user, 'friendsCount', getattr(user, 'followingCount', 0)),
                "tweets": getattr(user, 'statusesCount', 0),
            },
            "verified": getattr(user, 'isBlueVerified', False),
        }
