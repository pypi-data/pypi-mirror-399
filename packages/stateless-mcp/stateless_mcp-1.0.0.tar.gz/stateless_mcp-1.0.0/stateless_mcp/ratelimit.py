"""Rate limiting for stateless MCP."""

import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from threading import Lock


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter.

    Tracks requests in a sliding time window per key (IP, user, tool, etc.)
    """

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = Lock()

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for key.

        Args:
            key: Identifier (IP, user ID, etc.)

        Returns:
            True if allowed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Remove old requests outside window
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()

            # Check if under limit
            if len(self.requests[key]) >= self.max_requests:
                return False

            # Add current request
            self.requests[key].append(now)
            return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old requests
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()

            return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str) -> int:
        """Get timestamp when limit resets for key."""
        with self.lock:
            if not self.requests[key]:
                return int(time.time())

            oldest_request = self.requests[key][0]
            return int(oldest_request + self.window_seconds)


class RateLimitManager:
    """Manage multiple rate limiters."""

    def __init__(self):
        self.limiters: Dict[str, SlidingWindowRateLimiter] = {}

    def add_limiter(self, name: str, max_requests: int, window_seconds: int):
        """Add a rate limiter."""
        self.limiters[name] = SlidingWindowRateLimiter(max_requests, window_seconds)

    def check_limit(self, limiter_name: str, key: str) -> bool:
        """
        Check if request passes rate limit.

        Args:
            limiter_name: Name of the rate limiter
            key: Key to check (IP, user, etc.)

        Returns:
            True if allowed

        Raises:
            HTTPException: If rate limit exceeded
        """
        if limiter_name not in self.limiters:
            return True

        limiter = self.limiters[limiter_name]
        if not limiter.is_allowed(key):
            remaining = limiter.get_remaining(key)
            reset_time = limiter.get_reset_time(key)

            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(limiter.max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time())),
                }
            )

        return True

    def get_rate_limit_headers(self, limiter_name: str, key: str) -> Dict[str, str]:
        """Get rate limit headers for response."""
        if limiter_name not in self.limiters:
            return {}

        limiter = self.limiters[limiter_name]
        return {
            "X-RateLimit-Limit": str(limiter.max_requests),
            "X-RateLimit-Remaining": str(limiter.get_remaining(key)),
            "X-RateLimit-Reset": str(limiter.get_reset_time(key)),
        }


# Global rate limit manager
_rate_limit_manager = RateLimitManager()


def get_rate_limit_manager() -> RateLimitManager:
    """Get global rate limit manager."""
    return _rate_limit_manager


def parse_rate_limit(rate_str: str) -> tuple:
    """
    Parse rate limit string like "100/minute" or "10/second".

    Args:
        rate_str: Rate limit string

    Returns:
        Tuple of (max_requests, window_seconds)
    """
    parts = rate_str.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate limit format: {rate_str}")

    max_requests = int(parts[0])
    unit = parts[1].lower()

    unit_seconds = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }

    if unit not in unit_seconds:
        raise ValueError(f"Invalid time unit: {unit}")

    return max_requests, unit_seconds[unit]


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier from request.

    Uses X-Forwarded-For if available, otherwise client IP.

    Args:
        request: FastAPI request

    Returns:
        Client identifier string
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
