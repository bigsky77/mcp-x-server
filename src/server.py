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
