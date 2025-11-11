"""Input validation utilities."""

import re
from typing import Optional


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_tweet_id(tweet_id: str) -> str:
    """Validate tweet ID format."""
    if not tweet_id or not tweet_id.isdigit():
        raise ValidationError(f"Invalid tweet ID: {tweet_id}")
    return tweet_id


def validate_username(username: str) -> str:
    """Validate X username format."""
    username = username.lstrip("@")
    if not re.match(r"^[A-Za-z0-9_]{1,15}$", username):
        raise ValidationError(f"Invalid username: {username}")
    return username


def validate_tweet_text(text: str, max_length: int = 280) -> str:
    """Validate tweet text."""
    if not text or not text.strip():
        raise ValidationError("Tweet text cannot be empty")
    if len(text) > max_length:
        raise ValidationError(f"Tweet text exceeds {max_length} characters")
    return text.strip()


def validate_search_query(query: str) -> str:
    """Validate search query."""
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")
    return query.strip()


def validate_limit(limit: Optional[int], max_limit: int = 100) -> int:
    """Validate result limit parameter."""
    if limit is None:
        return 20  # default
    if limit < 1:
        raise ValidationError("Limit must be at least 1")
    if limit > max_limit:
        raise ValidationError(f"Limit cannot exceed {max_limit}")
    return limit
