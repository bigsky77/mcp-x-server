"""TwitterAPI.io client wrapper for read operations."""

import os
from typing import List, Optional, Dict, Any
import aiohttp
import logging

logger = logging.getLogger("mcp-x-server")


class TwitterAPIClient:
    """Wrapper for TwitterAPI.io for read operations."""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.twitterapi.io"
        self.api_key = api_key or os.getenv("TWITTER_API")
        if not self.api_key:
            raise ValueError("TWITTER_API key not found in environment")
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to TwitterAPI.io."""
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")

    async def search_tweets(
        self, query: str, limit: int = 20, filter_type: Optional[str] = None
    ) -> List[dict]:
        """Search tweets by query."""
        try:
            # Map filter_type to queryType
            query_type = "Latest"
            if filter_type and filter_type.lower() == "top":
                query_type = "Top"

            params = {
                "query": query,
                "queryType": query_type,
                "cursor": ""
            }

            all_tweets = []
            cursor = ""

            # Fetch tweets until we have enough or no more pages
            while len(all_tweets) < limit:
                params["cursor"] = cursor
                result = await self._make_request("/twitter/tweet/advanced_search", params)

                tweets = result.get("tweets", [])
                all_tweets.extend(tweets)

                if not result.get("has_next_page", False):
                    break

                cursor = result.get("next_cursor", "")
                if not cursor:
                    break

            # Limit to requested count
            return [self._serialize_tweet(t) for t in all_tweets[:limit]]
        except Exception as e:
            raise Exception(f"Failed to search tweets: {e}")

    async def get_tweet(self, tweet_id: str) -> dict:
        """Get single tweet by ID."""
        try:
            params = {"tweet_ids": tweet_id}
            result = await self._make_request("/twitter/tweets", params)

            tweets = result.get("tweets", [])
            if not tweets:
                raise Exception(f"Tweet {tweet_id} not found")

            return self._serialize_tweet(tweets[0])
        except Exception as e:
            raise Exception(f"Failed to get tweet: {e}")

    async def get_user_tweets(self, username: str, limit: int = 20) -> List[dict]:
        """Get tweets from user timeline."""
        try:
            # First get user info to get user ID
            user_info = await self.get_user(username)
            user_id = user_info.get("id")

            # Use search with from: operator as workaround
            # TwitterAPI.io doesn't have a direct user tweets endpoint in the docs we found
            query = f"from:{username}"
            params = {
                "query": query,
                "queryType": "Latest",
                "cursor": ""
            }

            all_tweets = []
            cursor = ""

            while len(all_tweets) < limit:
                params["cursor"] = cursor
                result = await self._make_request("/twitter/tweet/advanced_search", params)

                tweets = result.get("tweets", [])
                all_tweets.extend(tweets)

                if not result.get("has_next_page", False):
                    break

                cursor = result.get("next_cursor", "")
                if not cursor:
                    break

            return [self._serialize_tweet(t) for t in all_tweets[:limit]]
        except Exception as e:
            raise Exception(f"Failed to get user tweets: {e}")

    async def get_user(self, username: str) -> dict:
        """Get user profile."""
        try:
            params = {"userName": username}
            result = await self._make_request("/twitter/user/info", params)

            user_data = result.get("data", {})
            return self._serialize_user(user_data)
        except Exception as e:
            raise Exception(f"Failed to get user: {e}")

    async def get_mentions(self, username: str, limit: int = 20) -> List[dict]:
        """Get mentions for user."""
        try:
            query = f"@{username}"
            params = {
                "query": query,
                "queryType": "Latest",
                "cursor": ""
            }

            all_tweets = []
            cursor = ""

            while len(all_tweets) < limit:
                params["cursor"] = cursor
                result = await self._make_request("/twitter/tweet/advanced_search", params)

                tweets = result.get("tweets", [])
                all_tweets.extend(tweets)

                if not result.get("has_next_page", False):
                    break

                cursor = result.get("next_cursor", "")
                if not cursor:
                    break

            return [self._serialize_tweet(t) for t in all_tweets[:limit]]
        except Exception as e:
            raise Exception(f"Failed to get mentions: {e}")

    async def get_followers(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get followers for a user."""
        try:
            # TwitterAPI.io uses username, not user_id
            # We need to handle this - for now assume user_id could be username
            params = {
                "userName": user_id,
                "cursor": "",
                "pageSize": min(limit, 200)
            }

            all_followers = []
            cursor = ""

            while len(all_followers) < limit:
                params["cursor"] = cursor
                result = await self._make_request("/twitter/user/followers", params)

                followers = result.get("followers", [])
                all_followers.extend(followers)

                if len(followers) == 0:
                    break

                # Check if we need more pages
                if len(followers) < params["pageSize"]:
                    break

            return [self._serialize_user(u) for u in all_followers[:limit]]
        except Exception as e:
            raise Exception(f"Failed to get followers: {e}")

    async def get_following(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get following list for a user."""
        try:
            # Similar to followers - use search workaround or dedicated endpoint if available
            # For now, return empty as we don't have the endpoint documented
            logger.warning("get_following not fully implemented with TwitterAPI.io - endpoint may not be available")
            return []
        except Exception as e:
            raise Exception(f"Failed to get following: {e}")

    async def get_retweeters(self, tweet_id: str, limit: int = 20) -> List[dict]:
        """Get users who retweeted a tweet."""
        try:
            # Not documented in the API we reviewed
            logger.warning("get_retweeters not fully implemented with TwitterAPI.io - endpoint may not be available")
            return []
        except Exception as e:
            raise Exception(f"Failed to get retweeters: {e}")

    async def search_users(self, query: str, limit: int = 20) -> List[dict]:
        """Search for users by query."""
        try:
            # Not documented in the API we reviewed
            logger.warning("search_users not fully implemented with TwitterAPI.io - endpoint may not be available")
            return []
        except Exception as e:
            raise Exception(f"Failed to search users: {e}")

    async def get_bookmarks(self, limit: int = 20) -> List[dict]:
        """Get bookmarked tweets for authenticated user."""
        try:
            # Not documented in the API we reviewed
            logger.warning("get_bookmarks not fully implemented with TwitterAPI.io - endpoint may not be available")
            return []
        except Exception as e:
            raise Exception(f"Failed to get bookmarks: {e}")

    async def get_tweet_context(self, tweet_id: str, include_replies: bool = True, max_depth: int = 10) -> dict:
        """Get full conversation thread and context for a tweet."""
        try:
            # Get the main tweet first
            tweet = await self.get_tweet(tweet_id)

            parent_tweets = []
            current_tweet_data = tweet
            depth = 0

            # Get parent tweets if this is a reply
            while current_tweet_data.get("in_reply_to") and depth < max_depth:
                try:
                    parent_id = current_tweet_data["in_reply_to"]
                    parent = await self.get_tweet(parent_id)
                    parent_tweets.insert(0, parent)
                    current_tweet_data = parent
                    depth += 1
                except:
                    break

            # Get replies if requested
            replies = []
            if include_replies:
                try:
                    # Search for replies to this tweet
                    conversation_id = tweet.get("id")
                    # Note: This may not work perfectly without proper conversation_id support
                    query = f"conversation_id:{conversation_id}"
                    reply_result = await self.search_tweets(query, limit=20)
                    replies = [r for r in reply_result if r.get("in_reply_to") == tweet_id]
                except:
                    pass

            return {
                "conversation_id": tweet.get("id"),
                "parent_tweets": parent_tweets,
                "main_tweet": tweet,
                "replies": replies,
                "full_thread": parent_tweets + [tweet] + replies,
            }
        except Exception as e:
            raise Exception(f"Failed to get tweet context: {e}")

    async def get_quote_tweets(self, tweet_id: str, limit: int = 20) -> List[dict]:
        """Get quote tweets of a specific tweet."""
        try:
            # Get the tweet first to get username
            tweet = await self.get_tweet(tweet_id)
            username = tweet.get("author", {}).get("username", "")

            # Search for quotes using URL
            query = f"url:twitter.com/{username}/status/{tweet_id}"
            return await self.search_tweets(query, limit=limit)
        except Exception as e:
            raise Exception(f"Failed to get quote tweets: {e}")

    async def get_rate_limits(self) -> dict:
        """Get current rate limit status."""
        try:
            # TwitterAPI.io doesn't provide a rate limit endpoint in the docs
            # Return placeholder information
            return {
                "endpoints": {
                    "search": {"limit": "200 QPS", "remaining": "N/A", "reset_time": "N/A"},
                    "user_info": {"limit": "200 QPS", "remaining": "N/A", "reset_time": "N/A"},
                    "tweets": {"limit": "200 QPS", "remaining": "N/A", "reset_time": "N/A"},
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get rate limits: {e}")

    def _serialize_tweet(self, tweet: dict) -> dict:
        """Convert TwitterAPI.io tweet to standard format."""
        author = tweet.get("author", {})

        return {
            "id": str(tweet.get("id", "")),
            "text": tweet.get("text", ""),
            "author": {
                "username": author.get("userName", ""),
                "name": author.get("name", ""),
                "followers": author.get("followers", 0),
            },
            "created_at": tweet.get("createdAt", ""),
            "metrics": {
                "likes": tweet.get("likeCount", 0),
                "retweets": tweet.get("retweetCount", 0),
                "replies": tweet.get("replyCount", 0),
                "views": tweet.get("viewCount", 0),
            },
            "in_reply_to": str(tweet.get("inReplyToId")) if tweet.get("inReplyToId") else None,
        }

    def _serialize_user(self, user: dict) -> dict:
        """Convert TwitterAPI.io user to standard format."""
        return {
            "id": str(user.get("id", "")),
            "username": user.get("userName", ""),
            "name": user.get("name", ""),
            "description": user.get("description", ""),
            "created_at": user.get("createdAt", ""),
            "metrics": {
                "followers": user.get("followers", 0),
                "following": user.get("following", 0),
                "tweets": user.get("statusesCount", 0),
            },
            "verified": user.get("isBlueVerified", False),
        }
