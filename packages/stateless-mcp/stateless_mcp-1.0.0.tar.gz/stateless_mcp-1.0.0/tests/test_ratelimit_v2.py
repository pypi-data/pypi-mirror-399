"""Comprehensive tests for rate limiting module."""

import time
from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from stateless_mcp.ratelimit import (
    SlidingWindowRateLimiter,
    RateLimitManager,
    get_rate_limit_manager,
    parse_rate_limit,
    get_client_identifier,
)


class TestSlidingWindowRateLimiter:
    """Test SlidingWindowRateLimiter class."""

    def test_init(self):
        """Test limiter initialization."""
        limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)

        assert limiter.max_requests == 10
        assert limiter.window_seconds == 60
        assert len(limiter.requests) == 0

    def test_allow_within_limit(self):
        """Test allowing requests within limit."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)

        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True

    def test_block_over_limit(self):
        """Test blocking requests over limit."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is False  # Over limit

    def test_different_keys_independent(self):
        """Test that different keys have independent limits."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        # user1 uses their limit
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is False

        # user2 should still have their full limit
        assert limiter.is_allowed("user2") is True
        assert limiter.is_allowed("user2") is True
        assert limiter.is_allowed("user2") is False

    def test_window_sliding(self):
        """Test that window slides over time."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=1)

        # Use up limit
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is False

        # Wait for window to pass
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("user1") is True

    def test_partial_window_slide(self):
        """Test partial window sliding."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=2)

        # Make 3 requests
        assert limiter.is_allowed("user1") is True
        time.sleep(0.5)
        assert limiter.is_allowed("user1") is True
        time.sleep(0.5)
        assert limiter.is_allowed("user1") is True

        # At limit
        assert limiter.is_allowed("user1") is False

        # Wait for first request to age out
        time.sleep(1.1)  # Total 2.1 seconds since first request

        # Should allow one more
        assert limiter.is_allowed("user1") is True

    def test_get_remaining(self):
        """Test getting remaining requests."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

        assert limiter.get_remaining("user1") == 5

        limiter.is_allowed("user1")
        assert limiter.get_remaining("user1") == 4

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        assert limiter.get_remaining("user1") == 2

    def test_get_remaining_zero(self):
        """Test remaining at zero when limit reached."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")

        assert limiter.get_remaining("user1") == 0

    def test_get_reset_time(self):
        """Test getting reset time."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10)

        # Make a request
        limiter.is_allowed("user1")
        reset_time = limiter.get_reset_time("user1")

        # Reset time should be in the future
        current_time = int(time.time())
        assert reset_time > current_time
        assert reset_time <= current_time + 10

    def test_get_reset_time_no_requests(self):
        """Test reset time when no requests made."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)

        reset_time = limiter.get_reset_time("user1")

        # Should be current time
        assert abs(reset_time - int(time.time())) <= 1

    def test_thread_safety(self):
        """Test thread safety with lock."""
        limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)

        # Multiple rapid requests (simulating concurrent access)
        results = []
        for _ in range(50):
            results.append(limiter.is_allowed("user1"))

        # All should succeed (under limit)
        assert all(results)
        assert limiter.get_remaining("user1") == 50


class TestRateLimitManager:
    """Test RateLimitManager class."""

    def test_init(self):
        """Test manager initialization."""
        manager = RateLimitManager()

        assert len(manager.limiters) == 0

    def test_add_limiter(self):
        """Test adding a limiter."""
        manager = RateLimitManager()
        manager.add_limiter("api", max_requests=100, window_seconds=60)

        assert "api" in manager.limiters
        assert manager.limiters["api"].max_requests == 100
        assert manager.limiters["api"].window_seconds == 60

    def test_add_multiple_limiters(self):
        """Test adding multiple limiters."""
        manager = RateLimitManager()
        manager.add_limiter("api", 100, 60)
        manager.add_limiter("login", 5, 300)
        manager.add_limiter("heavy", 10, 3600)

        assert len(manager.limiters) == 3
        assert "api" in manager.limiters
        assert "login" in manager.limiters
        assert "heavy" in manager.limiters

    def test_check_limit_allowed(self):
        """Test checking limit when allowed."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=5, window_seconds=60)

        # Should not raise
        assert manager.check_limit("test", "user1") is True
        assert manager.check_limit("test", "user1") is True

    def test_check_limit_exceeded(self):
        """Test checking limit when exceeded."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=2, window_seconds=60)

        # Use up limit
        manager.check_limit("test", "user1")
        manager.check_limit("test", "user1")

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            manager.check_limit("test", "user1")

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    def test_check_limit_headers(self):
        """Test rate limit headers in exception."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=2, window_seconds=60)

        # Use up limit
        manager.check_limit("test", "user1")
        manager.check_limit("test", "user1")

        # Check headers
        with pytest.raises(HTTPException) as exc_info:
            manager.check_limit("test", "user1")

        headers = exc_info.value.headers
        assert "X-RateLimit-Limit" in headers
        assert headers["X-RateLimit-Limit"] == "2"
        assert "X-RateLimit-Remaining" in headers
        assert headers["X-RateLimit-Remaining"] == "0"
        assert "X-RateLimit-Reset" in headers
        assert "Retry-After" in headers

    def test_check_limit_nonexistent_limiter(self):
        """Test checking limit for non-existent limiter."""
        manager = RateLimitManager()

        # Should return True (no limiting)
        assert manager.check_limit("nonexistent", "user1") is True

    def test_get_rate_limit_headers(self):
        """Test getting rate limit headers."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=10, window_seconds=60)

        # Make some requests
        manager.check_limit("test", "user1")
        manager.check_limit("test", "user1")

        headers = manager.get_rate_limit_headers("test", "user1")

        assert headers["X-RateLimit-Limit"] == "10"
        assert headers["X-RateLimit-Remaining"] == "8"
        assert "X-RateLimit-Reset" in headers

    def test_get_rate_limit_headers_nonexistent(self):
        """Test getting headers for non-existent limiter."""
        manager = RateLimitManager()

        headers = manager.get_rate_limit_headers("nonexistent", "user1")

        assert headers == {}

    def test_independent_limiters(self):
        """Test that different limiters are independent."""
        manager = RateLimitManager()
        manager.add_limiter("strict", max_requests=1, window_seconds=60)
        manager.add_limiter("relaxed", max_requests=100, window_seconds=60)

        # Use strict limit
        manager.check_limit("strict", "user1")
        with pytest.raises(HTTPException):
            manager.check_limit("strict", "user1")

        # Relaxed should still work
        assert manager.check_limit("relaxed", "user1") is True


class TestParseRateLimit:
    """Test parse_rate_limit function."""

    def test_parse_per_second(self):
        """Test parsing per-second rate limit."""
        max_req, window = parse_rate_limit("10/second")

        assert max_req == 10
        assert window == 1

    def test_parse_per_minute(self):
        """Test parsing per-minute rate limit."""
        max_req, window = parse_rate_limit("100/minute")

        assert max_req == 100
        assert window == 60

    def test_parse_per_hour(self):
        """Test parsing per-hour rate limit."""
        max_req, window = parse_rate_limit("1000/hour")

        assert max_req == 1000
        assert window == 3600

    def test_parse_per_day(self):
        """Test parsing per-day rate limit."""
        max_req, window = parse_rate_limit("10000/day")

        assert max_req == 10000
        assert window == 86400

    def test_parse_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid rate limit format"):
            parse_rate_limit("invalid")

        with pytest.raises(ValueError, match="Invalid rate limit format"):
            parse_rate_limit("100")

        with pytest.raises(ValueError, match="Invalid rate limit format"):
            parse_rate_limit("100/minute/extra")

    def test_parse_invalid_unit(self):
        """Test parsing invalid time unit."""
        with pytest.raises(ValueError, match="Invalid time unit"):
            parse_rate_limit("100/week")

        with pytest.raises(ValueError, match="Invalid time unit"):
            parse_rate_limit("100/month")

    def test_parse_invalid_number(self):
        """Test parsing invalid number."""
        with pytest.raises(ValueError):
            parse_rate_limit("abc/minute")

        with pytest.raises(ValueError):
            parse_rate_limit("10.5/minute")

    def test_parse_zero_requests(self):
        """Test parsing zero requests."""
        max_req, window = parse_rate_limit("0/minute")

        assert max_req == 0
        assert window == 60

    def test_parse_large_number(self):
        """Test parsing large number of requests."""
        max_req, window = parse_rate_limit("1000000/hour")

        assert max_req == 1000000
        assert window == 3600


class TestGetClientIdentifier:
    """Test get_client_identifier function."""

    def test_client_from_request(self):
        """Test getting client from request."""
        request = Mock(spec=Request)
        request.headers.get.return_value = None
        request.client = Mock(host="192.168.1.1")

        identifier = get_client_identifier(request)

        assert identifier == "192.168.1.1"

    def test_client_from_x_forwarded_for(self):
        """Test getting client from X-Forwarded-For header."""
        request = Mock(spec=Request)
        request.headers.get.return_value = "203.0.113.1, 198.51.100.1"

        identifier = get_client_identifier(request)

        # Should use first IP
        assert identifier == "203.0.113.1"

    def test_client_from_x_forwarded_for_single(self):
        """Test X-Forwarded-For with single IP."""
        request = Mock(spec=Request)
        request.headers.get.return_value = "203.0.113.1"

        identifier = get_client_identifier(request)

        assert identifier == "203.0.113.1"

    def test_client_from_x_forwarded_for_with_spaces(self):
        """Test X-Forwarded-For with spaces."""
        request = Mock(spec=Request)
        request.headers.get.return_value = "203.0.113.1 , 198.51.100.1"

        identifier = get_client_identifier(request)

        # Should strip spaces
        assert identifier == "203.0.113.1"

    def test_client_no_client_info(self):
        """Test when no client info available."""
        request = Mock(spec=Request)
        request.headers.get.return_value = None
        request.client = None

        identifier = get_client_identifier(request)

        assert identifier == "unknown"


class TestGlobalRateLimitManager:
    """Test global rate limit manager."""

    def test_get_global_manager(self):
        """Test getting global manager instance."""
        manager1 = get_rate_limit_manager()
        manager2 = get_rate_limit_manager()

        # Should be same instance
        assert manager1 is manager2

    def test_global_manager_state_persists(self):
        """Test that global manager state persists."""
        manager = get_rate_limit_manager()
        manager.add_limiter("persistent", max_requests=5, window_seconds=60)

        # Get manager again
        manager2 = get_rate_limit_manager()

        # Should have the same limiter
        assert "persistent" in manager2.limiters


class TestRateLimitIntegration:
    """Integration tests for rate limiting."""

    def test_complete_rate_limit_flow(self):
        """Test complete rate limiting flow."""
        manager = RateLimitManager()
        manager.add_limiter("api", max_requests=3, window_seconds=60)

        # Simulate requests
        client_id = "192.168.1.100"

        # First 3 should succeed
        for i in range(3):
            assert manager.check_limit("api", client_id) is True

        # 4th should fail
        with pytest.raises(HTTPException) as exc_info:
            manager.check_limit("api", client_id)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    def test_multiple_clients_rate_limiting(self):
        """Test rate limiting with multiple clients."""
        manager = RateLimitManager()
        manager.add_limiter("api", max_requests=2, window_seconds=60)

        # Client 1 uses their limit
        manager.check_limit("api", "client1")
        manager.check_limit("api", "client1")
        with pytest.raises(HTTPException):
            manager.check_limit("api", "client1")

        # Client 2 should still have their limit
        manager.check_limit("api", "client2")
        manager.check_limit("api", "client2")
        with pytest.raises(HTTPException):
            manager.check_limit("api", "client2")

    def test_different_limits_per_endpoint(self):
        """Test different limits for different endpoints."""
        manager = RateLimitManager()
        manager.add_limiter("strict", max_requests=1, window_seconds=60)
        manager.add_limiter("relaxed", max_requests=100, window_seconds=60)

        client_id = "client1"

        # Strict endpoint
        manager.check_limit("strict", client_id)
        with pytest.raises(HTTPException):
            manager.check_limit("strict", client_id)

        # Relaxed endpoint should still work
        for _ in range(10):
            manager.check_limit("relaxed", client_id)

    def test_rate_limit_with_sliding_window(self):
        """Test rate limiting with sliding window."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=3, window_seconds=1)

        client_id = "client1"

        # Use up limit
        for _ in range(3):
            manager.check_limit("test", client_id)

        # Should be blocked
        with pytest.raises(HTTPException):
            manager.check_limit("test", client_id)

        # Wait for window to slide
        time.sleep(1.1)

        # Should work again
        manager.check_limit("test", client_id)

    def test_rate_limit_headers_in_flow(self):
        """Test rate limit headers throughout flow."""
        manager = RateLimitManager()
        manager.add_limiter("test", max_requests=5, window_seconds=60)

        client_id = "client1"

        # Make requests and check headers
        for i in range(5):
            manager.check_limit("test", client_id)
            headers = manager.get_rate_limit_headers("test", client_id)

            assert headers["X-RateLimit-Limit"] == "5"
            assert int(headers["X-RateLimit-Remaining"]) == 5 - i - 1

        # Final headers should show 0 remaining
        headers = manager.get_rate_limit_headers("test", client_id)
        assert headers["X-RateLimit-Remaining"] == "0"

    def test_concurrent_burst_requests(self):
        """Test handling burst of concurrent requests."""
        manager = RateLimitManager()
        manager.add_limiter("burst", max_requests=10, window_seconds=60)

        client_id = "burst_client"

        # Simulate burst of requests
        allowed_count = 0
        blocked_count = 0

        for _ in range(15):
            try:
                manager.check_limit("burst", client_id)
                allowed_count += 1
            except HTTPException:
                blocked_count += 1

        # Should allow exactly 10 and block 5
        assert allowed_count == 10
        assert blocked_count == 5


class TestRateLimitEdgeCases:
    """Test edge cases in rate limiting."""

    def test_zero_rate_limit(self):
        """Test rate limiter with zero requests allowed."""
        limiter = SlidingWindowRateLimiter(max_requests=0, window_seconds=60)

        # Should always be blocked
        assert limiter.is_allowed("user1") is False

    def test_very_short_window(self):
        """Test very short time window."""
        limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=0)

        # Should allow requests (0 second window)
        assert limiter.is_allowed("user1") is True

    def test_very_large_limit(self):
        """Test very large request limit."""
        limiter = SlidingWindowRateLimiter(max_requests=1000000, window_seconds=60)

        # Should allow many requests
        for _ in range(100):
            assert limiter.is_allowed("user1") is True

    def test_special_characters_in_key(self):
        """Test rate limiting with special characters in key."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        special_key = "user@example.com:192.168.1.1"
        assert limiter.is_allowed(special_key) is True
        assert limiter.is_allowed(special_key) is True
        assert limiter.is_allowed(special_key) is False

    def test_empty_string_key(self):
        """Test rate limiting with empty string key."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        assert limiter.is_allowed("") is True
        assert limiter.is_allowed("") is True
        assert limiter.is_allowed("") is False
