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

    async def get_tweet_context(self, tweet_id: str, include_replies: bool = True, max_depth: int = 10) -> dict:
        """Get full conversation thread and context for a tweet."""
        try:
            tweet = await self.api.tweet_details(int(tweet_id))

            parent_tweets = []
            current_tweet = tweet
            depth = 0

            # Get parent tweets (conversation thread)
            while current_tweet.inReplyToTweetId and depth < max_depth:
                try:
                    parent = await self.api.tweet_details(int(current_tweet.inReplyToTweetId))
                    parent_tweets.insert(0, self._serialize_tweet(parent))
                    current_tweet = parent
                    depth += 1
                except:
                    break

            # Get replies if requested
            replies = []
            if include_replies:
                try:
                    # Use conversation_id or tweet_id to get replies
                    reply_tweets = await gather(self.api.search(f"conversation_id:{tweet_id}", limit=20))
                    replies = [self._serialize_tweet(t) for t in reply_tweets if str(t.inReplyToTweetId) == tweet_id]
                except:
                    pass

            return {
                "conversation_id": str(tweet.conversationId) if hasattr(tweet, 'conversationId') else tweet_id,
                "parent_tweets": parent_tweets,
                "main_tweet": self._serialize_tweet(tweet),
                "replies": replies,
                "full_thread": parent_tweets + [self._serialize_tweet(tweet)] + replies,
            }
        except Exception as e:
            raise Exception(f"Failed to get tweet context: {e}")

    async def get_quote_tweets(self, tweet_id: str, limit: int = 20) -> List[dict]:
        """Get quote tweets of a specific tweet."""
        try:
            # Search for quotes using tweet URL
            query = f"quoted_tweet_id:{tweet_id}"
            tweets = await gather(self.api.search(query, limit=limit))
            return [self._serialize_tweet(t) for t in tweets]
        except Exception as e:
            raise Exception(f"Failed to get quote tweets: {e}")

    async def get_followers(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get followers for a user."""
        try:
            followers = await gather(self.api.followers(int(user_id), limit=limit))
            return [self._serialize_user(u) for u in followers]
        except Exception as e:
            raise Exception(f"Failed to get followers: {e}")

    async def get_following(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get following list for a user."""
        try:
            following = await gather(self.api.following(int(user_id), limit=limit))
            return [self._serialize_user(u) for u in following]
        except Exception as e:
            raise Exception(f"Failed to get following: {e}")

    async def get_likers(self, tweet_id: str, limit: int = 20) -> List[dict]:
        """Get users who liked a tweet."""
        try:
            likers = await gather(self.api.favoriters(int(tweet_id), limit=limit))
            return [self._serialize_user(u) for u in likers]
        except Exception as e:
            raise Exception(f"Failed to get likers: {e}")

    async def get_retweeters(self, tweet_id: str, limit: int = 20) -> List[dict]:
        """Get users who retweeted a tweet."""
        try:
            retweeters = await gather(self.api.retweeters(int(tweet_id), limit=limit))
            return [self._serialize_user(u) for u in retweeters]
        except Exception as e:
            raise Exception(f"Failed to get retweeters: {e}")

    async def get_user_likes(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get tweets liked by a user."""
        try:
            likes = await gather(self.api.liked_tweets(int(user_id), limit=limit))
            return [self._serialize_tweet(t) for t in likes]
        except Exception as e:
            raise Exception(f"Failed to get user likes: {e}")

    async def get_home_timeline(self, limit: int = 20) -> List[dict]:
        """Get authenticated user's home timeline."""
        try:
            # Note: This requires authentication and may not work with all accounts
            tweets = await gather(self.api.home_timeline(limit=limit))
            return [self._serialize_tweet(t) for t in tweets]
        except Exception as e:
            raise Exception(f"Failed to get home timeline: {e}")

    async def search_users(self, query: str, limit: int = 20) -> List[dict]:
        """Search for users by query."""
        try:
            # Fixed: twscrape uses search_user (singular) not search_users (plural)
            users = await gather(self.api.search_user(query, limit=limit))
            return [self._serialize_user(u) for u in users]
        except Exception as e:
            raise Exception(f"Failed to search users: {e}")

    async def get_lists(self, user_id: str) -> List[dict]:
        """Get lists owned by a user."""
        try:
            lists = await gather(self.api.lists_by_user(int(user_id)))
            return [{
                "list_id": str(lst.id),
                "name": lst.name,
                "description": getattr(lst, 'description', ''),
                "member_count": getattr(lst, 'memberCount', 0),
                "subscriber_count": getattr(lst, 'subscriberCount', 0),
                "private": getattr(lst, 'isPrivate', False),
            } for lst in lists]
        except Exception as e:
            raise Exception(f"Failed to get lists: {e}")

    async def get_bookmarks(self, limit: int = 20) -> List[dict]:
        """Get bookmarked tweets for authenticated user."""
        try:
            # Note: This requires authentication
            bookmarks = await gather(self.api.bookmarks(limit=limit))
            return [self._serialize_tweet(t) for t in bookmarks]
        except Exception as e:
            raise Exception(f"Failed to get bookmarks: {e}")

    async def get_rate_limits(self) -> dict:
        """Get current rate limit status."""
        try:
            # This would typically come from API response headers
            # For twscrape, we return a placeholder structure
            return {
                "endpoints": {
                    "search": {"limit": 180, "remaining": 180, "reset_time": "N/A"},
                    "user_timeline": {"limit": 900, "remaining": 900, "reset_time": "N/A"},
                    "followers": {"limit": 15, "remaining": 15, "reset_time": "N/A"},
                    "following": {"limit": 15, "remaining": 15, "reset_time": "N/A"},
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get rate limits: {e}")
