"""Rate limiting for X API requests."""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_window: int
    window_seconds: int


class RateLimiter:
    """Token bucket rate limiter with per-operation tracking."""

    def __init__(self, config: Dict[str, RateLimitConfig]):
        """Initialize rate limiter with operation-specific configs."""
        self.configs = config
        self.request_times: Dict[str, deque] = {op: deque() for op in config.keys()}

    def check_limit(self, operation: str) -> tuple[bool, float]:
        """
        Check if request is within rate limit.

        Returns:
            tuple[bool, float]: (allowed, wait_time_seconds)
        """
        if operation not in self.configs:
            return True, 0.0

        config = self.configs[operation]
        now = time.time()
        window_start = now - config.window_seconds

        # Remove expired timestamps
        times = self.request_times[operation]
        while times and times[0] < window_start:
            times.popleft()

        # Check if under limit
        if len(times) < config.requests_per_window:
            return True, 0.0

        # Calculate wait time
        oldest = times[0]
        wait_time = oldest + config.window_seconds - now
        return False, max(0, wait_time)

    def record_request(self, operation: str):
        """Record a request timestamp."""
        if operation in self.request_times:
            self.request_times[operation].append(time.time())

    async def wait_if_needed(self, operation: str):
        """Wait if rate limit would be exceeded."""
        allowed, wait_time = self.check_limit(operation)
        if not allowed:
            await asyncio.sleep(wait_time)
        self.record_request(operation)


class ExponentialBackoff:
    """Exponential backoff for retry logic."""

    def __init__(self, base: float = 2.0, max_wait: float = 60.0):
        self.base = base
        self.max_wait = max_wait

    def calculate(self, attempt: int) -> float:
        """Calculate backoff time for given attempt number."""
        wait = min(self.base**attempt, self.max_wait)
        return wait
