"""MCP X Server - Main entry point."""

import asyncio
import logging
from pathlib import Path
from typing import Any

import yaml
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .auth.account_manager import AccountManager
from .clients.twikit_client import TwiKitClient
from .clients.twscrape_client import TwscrapeClient
from .tools.read_tools import ReadTools
from .tools.post_tools import WriteTools
from .utils.rate_limiter import RateLimiter, RateLimitConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-x-server")


class MCPXServer:
    """MCP X Server implementation."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.server = Server("mcp-x-server")

        # Initialize components
        self.account_manager = AccountManager(
            cookies_file=self.config["auth"]["cookies_file"],
            accounts_file=self.config["auth"].get("accounts_file"),
        )

        # Initialize clients
        cookies = self.account_manager.load_cookies()
        self.twikit_client = TwiKitClient(cookies)
        self.twscrape_client = TwscrapeClient(
            accounts_file=self.config["auth"].get("accounts_file")
        )

        # Initialize tools
        self.read_tools = ReadTools(self.twscrape_client)
        self.write_tools = WriteTools(self.twikit_client)

        # Initialize rate limiter
        self.rate_limiter = RateLimiter({
            "read": RateLimitConfig(
                requests_per_window=self.config["rate_limits"]["read"]["requests_per_window"],
                window_seconds=self.config["rate_limits"]["read"]["window_seconds"],
            ),
            "write": RateLimitConfig(
                requests_per_window=self.config["rate_limits"]["write"]["requests_per_window"],
                window_seconds=self.config["rate_limits"]["write"]["window_seconds"],
            ),
        })

        self._register_handlers()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _register_handlers(self):
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available MCP tools."""
            return [
                # Read tools
                Tool(
                    name="search_tweets",
                    description="Search tweets by keyword/hashtag with optional filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                            "filter_type": {"type": "string", "description": "Filter: top, latest, people, photos, videos"},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_tweet",
                    description="Get single tweet by ID with full metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="get_user_tweets",
                    description="Get tweets from user timeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "X username"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["username"],
                    },
                ),
                Tool(
                    name="get_user",
                    description="Get user profile and statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "X username"},
                        },
                        "required": ["username"],
                    },
                ),
                Tool(
                    name="get_mentions",
                    description="Get mentions for specified user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username to search mentions for"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["username"],
                    },
                ),
                # Write tools
                Tool(
                    name="post_tweet",
                    description="Post a new tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Tweet text (max 280 chars)"},
                            "media_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional media IDs"},
                        },
                        "required": ["text"],
                    },
                ),
                Tool(
                    name="reply_to_tweet",
                    description="Reply to an existing tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to reply to"},
                            "text": {"type": "string", "description": "Reply text (max 280 chars)"},
                        },
                        "required": ["tweet_id", "text"],
                    },
                ),
                Tool(
                    name="like_tweet",
                    description="Like a tweet by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to like"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="retweet",
                    description="Retweet a tweet by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to retweet"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="delete_tweet",
                    description="Delete own tweet by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to delete"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                # Phase 1: Core Gaps
                Tool(
                    name="quote_tweet",
                    description="Create a quote tweet with commentary",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to quote"},
                            "text": {"type": "string", "description": "Quote comment text (max 280 chars)"},
                            "media_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional media IDs"},
                        },
                        "required": ["tweet_id", "text"],
                    },
                ),
                Tool(
                    name="get_tweet_context",
                    description="Get full conversation thread and context for a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID"},
                            "include_replies": {"type": "boolean", "description": "Include replies (default: true)"},
                            "max_depth": {"type": "integer", "description": "Max depth for parent tweets (default: 10)"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="get_quote_tweets",
                    description="Get quote tweets of a specific tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="follow_user",
                    description="Follow a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to follow"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="unfollow_user",
                    description="Unfollow a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to unfollow"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="get_followers",
                    description="Get followers list for a user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="get_following",
                    description="Get following list for a user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["user_id"],
                    },
                ),
                # Phase 2: Intelligence
                Tool(
                    name="get_retweeters",
                    description="Get users who retweeted a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                # Phase 3: Operations
                Tool(
                    name="unlike_tweet",
                    description="Remove like from a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to unlike"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="unretweet",
                    description="Remove retweet from a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to unretweet"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="get_rate_limits",
                    description="Get current API rate limit status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="mute_user",
                    description="Mute a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to mute"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="unmute_user",
                    description="Unmute a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to unmute"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="block_user",
                    description="Block a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to block"},
                        },
                        "required": ["user_id"],
                    },
                ),
                Tool(
                    name="unblock_user",
                    description="Unblock a user by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID to unblock"},
                        },
                        "required": ["user_id"],
                    },
                ),
                # Phase 4: Advanced
                Tool(
                    name="create_list",
                    description="Create a new Twitter list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "List name (max 25 chars)"},
                            "description": {"type": "string", "description": "Optional list description"},
                            "private": {"type": "boolean", "description": "Whether the list is private"},
                        },
                        "required": ["name"],
                    },
                ),
                Tool(
                    name="add_to_list",
                    description="Add user to a list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "list_id": {"type": "string", "description": "List ID"},
                            "user_id": {"type": "string", "description": "User ID to add"},
                        },
                        "required": ["list_id", "user_id"],
                    },
                ),
                Tool(
                    name="remove_from_list",
                    description="Remove user from a list",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "list_id": {"type": "string", "description": "List ID"},
                            "user_id": {"type": "string", "description": "User ID to remove"},
                        },
                        "required": ["list_id", "user_id"],
                    },
                ),
                Tool(
                    name="search_users",
                    description="Search for users by query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="bookmark_tweet",
                    description="Bookmark a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to bookmark"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="unbookmark_tweet",
                    description="Remove bookmark from a tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {"type": "string", "description": "Tweet ID to unbookmark"},
                        },
                        "required": ["tweet_id"],
                    },
                ),
                Tool(
                    name="get_bookmarks",
                    description="Get bookmarked tweets for authenticated user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max results (default: 20, max: 100)"},
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute MCP tool."""
            try:
                # Route to appropriate tool
                if name == "search_tweets":
                    result = await self.read_tools.search_tweets(**arguments)
                elif name == "get_tweet":
                    result = await self.read_tools.get_tweet(**arguments)
                elif name == "get_user_tweets":
                    result = await self.read_tools.get_user_tweets(**arguments)
                elif name == "get_user":
                    result = await self.read_tools.get_user(**arguments)
                elif name == "get_mentions":
                    result = await self.read_tools.get_mentions(**arguments)
                elif name == "post_tweet":
                    result = await self.write_tools.post_tweet(**arguments)
                elif name == "reply_to_tweet":
                    result = await self.write_tools.reply_to_tweet(**arguments)
                elif name == "like_tweet":
                    result = await self.write_tools.like_tweet(**arguments)
                elif name == "retweet":
                    result = await self.write_tools.retweet(**arguments)
                elif name == "delete_tweet":
                    result = await self.write_tools.delete_tweet(**arguments)
                # Phase 1: Core Gaps
                elif name == "quote_tweet":
                    result = await self.write_tools.quote_tweet(**arguments)
                elif name == "get_tweet_context":
                    result = await self.read_tools.get_tweet_context(**arguments)
                elif name == "get_quote_tweets":
                    result = await self.read_tools.get_quote_tweets(**arguments)
                elif name == "follow_user":
                    result = await self.write_tools.follow_user(**arguments)
                elif name == "unfollow_user":
                    result = await self.write_tools.unfollow_user(**arguments)
                elif name == "get_followers":
                    result = await self.read_tools.get_followers(**arguments)
                elif name == "get_following":
                    result = await self.read_tools.get_following(**arguments)
                # Phase 2: Intelligence
                elif name == "get_retweeters":
                    result = await self.read_tools.get_retweeters(**arguments)
                # Phase 3: Operations
                elif name == "unlike_tweet":
                    result = await self.write_tools.unlike_tweet(**arguments)
                elif name == "unretweet":
                    result = await self.write_tools.unretweet(**arguments)
                elif name == "get_rate_limits":
                    result = await self.read_tools.get_rate_limits()
                elif name == "mute_user":
                    result = await self.write_tools.mute_user(**arguments)
                elif name == "unmute_user":
                    result = await self.write_tools.unmute_user(**arguments)
                elif name == "block_user":
                    result = await self.write_tools.block_user(**arguments)
                elif name == "unblock_user":
                    result = await self.write_tools.unblock_user(**arguments)
                # Phase 4: Advanced
                elif name == "create_list":
                    result = await self.write_tools.create_list(**arguments)
                elif name == "add_to_list":
                    result = await self.write_tools.add_to_list(**arguments)
                elif name == "remove_from_list":
                    result = await self.write_tools.remove_from_list(**arguments)
                elif name == "search_users":
                    result = await self.read_tools.search_users(**arguments)
                elif name == "bookmark_tweet":
                    result = await self.write_tools.bookmark_tweet(**arguments)
                elif name == "unbookmark_tweet":
                    result = await self.write_tools.unbookmark_tweet(**arguments)
                elif name == "get_bookmarks":
                    result = await self.read_tools.get_bookmarks(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error executing {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting MCP X Server...")

        # Setup clients
        await self.twscrape_client.setup()

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """Main entry point."""
    server = MCPXServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
