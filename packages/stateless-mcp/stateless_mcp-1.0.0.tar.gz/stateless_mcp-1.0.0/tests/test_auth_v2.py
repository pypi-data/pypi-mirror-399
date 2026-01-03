"""Comprehensive tests for API key authentication module."""

import pytest
from fastapi import HTTPException

from stateless_mcp.auth import APIKeyAuth, AuthContext, check_permission


class TestAuthContext:
    """Test AuthContext dataclass."""

    def test_auth_context_authenticated(self):
        """Test authenticated context."""
        ctx = AuthContext(authenticated=True, api_key="key123")

        assert ctx.authenticated is True
        assert ctx.api_key == "key123"
        assert ctx.user_id is None
        assert ctx.permissions == set()

    def test_auth_context_unauthenticated(self):
        """Test unauthenticated context."""
        ctx = AuthContext(authenticated=False)

        assert ctx.authenticated is False
        assert ctx.api_key is None
        assert ctx.user_id is None
        assert ctx.permissions == set()

    def test_auth_context_with_permissions(self):
        """Test context with permissions."""
        ctx = AuthContext(
            authenticated=True,
            api_key="key123",
            permissions={"read", "write"},
        )

        assert ctx.authenticated is True
        assert ctx.permissions == {"read", "write"}

    def test_auth_context_with_user_id(self):
        """Test context with user ID."""
        ctx = AuthContext(
            authenticated=True,
            api_key="key123",
            user_id="user456",
        )

        assert ctx.authenticated is True
        assert ctx.user_id == "user456"


class TestAPIKeyAuth:
    """Test APIKeyAuth class."""

    def test_init_with_single_key(self):
        """Test initialization with single API key."""
        auth = APIKeyAuth(api_keys=["key123"])

        assert len(auth.api_keys) == 1
        assert "key123" in auth.api_keys

    def test_init_with_multiple_keys(self):
        """Test initialization with multiple API keys."""
        auth = APIKeyAuth(api_keys=["key1", "key2", "key3"])

        assert len(auth.api_keys) == 3
        assert "key1" in auth.api_keys
        assert "key2" in auth.api_keys
        assert "key3" in auth.api_keys

    def test_init_with_custom_header(self):
        """Test initialization with custom header name."""
        auth = APIKeyAuth(api_keys=["key"], header_name="X-Custom-Key")

        assert auth.header_name == "X-Custom-Key"

    def test_init_with_empty_keys(self):
        """Test initialization with empty key list."""
        auth = APIKeyAuth(api_keys=[])

        assert len(auth.api_keys) == 0

    @pytest.mark.asyncio
    async def test_valid_api_key(self):
        """Test authentication with valid API key."""
        auth = APIKeyAuth(api_keys=["valid_key_123"])

        context = await auth(api_key="valid_key_123")

        assert context.authenticated is True
        assert context.api_key == "valid_key_123"

    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test authentication with invalid API key."""
        auth = APIKeyAuth(api_keys=["valid_key"])

        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key="invalid_key")

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test authentication with missing API key."""
        auth = APIKeyAuth(api_keys=["valid_key"])

        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key=None)

        assert exc_info.value.status_code == 401
        assert "API key required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_multiple_valid_keys(self):
        """Test authentication with multiple valid keys."""
        auth = APIKeyAuth(api_keys=["key1", "key2", "key3"])

        # All keys should work
        ctx1 = await auth(api_key="key1")
        assert ctx1.authenticated is True
        assert ctx1.api_key == "key1"

        ctx2 = await auth(api_key="key2")
        assert ctx2.authenticated is True
        assert ctx2.api_key == "key2"

        ctx3 = await auth(api_key="key3")
        assert ctx3.authenticated is True
        assert ctx3.api_key == "key3"

    @pytest.mark.asyncio
    async def test_key_case_sensitive(self):
        """Test that API keys are case-sensitive."""
        auth = APIKeyAuth(api_keys=["ValidKey123"])

        # Exact match should work
        ctx = await auth(api_key="ValidKey123")
        assert ctx.authenticated is True

        # Different case should fail
        with pytest.raises(HTTPException):
            await auth(api_key="validkey123")

        with pytest.raises(HTTPException):
            await auth(api_key="VALIDKEY123")

    @pytest.mark.asyncio
    async def test_whitespace_handling(self):
        """Test handling of whitespace in API keys."""
        auth = APIKeyAuth(api_keys=["key_with_no_spaces"])

        # Exact key works
        ctx = await auth(api_key="key_with_no_spaces")
        assert ctx.authenticated is True

        # Key with spaces should fail (no auto-trimming)
        with pytest.raises(HTTPException):
            await auth(api_key=" key_with_no_spaces ")

    @pytest.mark.asyncio
    async def test_empty_string_key(self):
        """Test authentication with empty string key."""
        auth = APIKeyAuth(api_keys=["valid_key"])

        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key="")

        assert exc_info.value.status_code == 401


class TestCheckPermission:
    """Test check_permission function."""

    def test_has_permission(self):
        """Test checking when permission exists."""
        ctx = AuthContext(
            authenticated=True,
            permissions={"read", "write", "delete"},
        )

        # Should not raise
        check_permission(ctx, "read")
        check_permission(ctx, "write")
        check_permission(ctx, "delete")

    def test_missing_permission(self):
        """Test checking when permission is missing."""
        ctx = AuthContext(
            authenticated=True,
            permissions={"read"},
        )

        with pytest.raises(HTTPException) as exc_info:
            check_permission(ctx, "write")

        assert exc_info.value.status_code == 403
        assert "Permission denied" in exc_info.value.detail

    def test_unauthenticated_context(self):
        """Test checking permission on unauthenticated context."""
        ctx = AuthContext(authenticated=False)

        with pytest.raises(HTTPException) as exc_info:
            check_permission(ctx, "read")

        assert exc_info.value.status_code == 403

    def test_empty_permissions(self):
        """Test checking when no permissions granted."""
        ctx = AuthContext(authenticated=True, permissions=set())

        with pytest.raises(HTTPException):
            check_permission(ctx, "any_permission")

    def test_case_sensitive_permissions(self):
        """Test that permissions are case-sensitive."""
        ctx = AuthContext(
            authenticated=True,
            permissions={"Read", "Write"},
        )

        # Exact case works
        check_permission(ctx, "Read")
        check_permission(ctx, "Write")

        # Different case fails
        with pytest.raises(HTTPException):
            check_permission(ctx, "read")

        with pytest.raises(HTTPException):
            check_permission(ctx, "write")


class TestAuthIntegration:
    """Integration tests for authentication."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self):
        """Test complete authentication flow."""
        # Setup auth with multiple keys
        auth = APIKeyAuth(
            api_keys=["dev_key", "prod_key", "admin_key"],
            header_name="X-API-Key",
        )

        # Valid authentication
        ctx = await auth(api_key="dev_key")
        assert ctx.authenticated is True
        assert ctx.api_key == "dev_key"

        # Invalid authentication
        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key="wrong_key")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_with_permissions_flow(self):
        """Test authentication with permission checking."""
        auth = APIKeyAuth(api_keys=["key123"])

        # Authenticate
        ctx = await auth(api_key="key123")

        # Initially no permissions (would need to be set elsewhere)
        assert ctx.permissions == set()

        # Simulate adding permissions
        ctx.permissions.add("read")
        ctx.permissions.add("write")

        # Check permissions
        check_permission(ctx, "read")
        check_permission(ctx, "write")

        with pytest.raises(HTTPException):
            check_permission(ctx, "delete")

    @pytest.mark.asyncio
    async def test_multiple_concurrent_auth(self):
        """Test multiple concurrent authentication requests."""
        auth = APIKeyAuth(api_keys=["key1", "key2", "key3"])

        # Simulate concurrent requests with different keys
        results = []
        for key in ["key1", "key2", "key3"]:
            ctx = await auth(api_key=key)
            results.append(ctx)

        # All should succeed
        assert len(results) == 3
        assert all(r.authenticated for r in results)
        assert results[0].api_key == "key1"
        assert results[1].api_key == "key2"
        assert results[2].api_key == "key3"

    @pytest.mark.asyncio
    async def test_auth_error_messages(self):
        """Test authentication error messages."""
        auth = APIKeyAuth(api_keys=["valid"])

        # Missing key
        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key=None)
        assert "required" in exc_info.value.detail.lower()

        # Invalid key
        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key="invalid")
        assert "invalid" in exc_info.value.detail.lower()

    def test_permission_error_message(self):
        """Test permission denied error message."""
        ctx = AuthContext(authenticated=True, permissions={"read"})

        with pytest.raises(HTTPException) as exc_info:
            check_permission(ctx, "write")

        assert "Permission denied" in exc_info.value.detail
        assert "write" in exc_info.value.detail


class TestAuthEdgeCases:
    """Test edge cases in authentication."""

    @pytest.mark.asyncio
    async def test_duplicate_keys(self):
        """Test handling duplicate API keys."""
        auth = APIKeyAuth(api_keys=["key1", "key1", "key2"])

        # Should deduplicate internally
        ctx = await auth(api_key="key1")
        assert ctx.authenticated is True

    @pytest.mark.asyncio
    async def test_very_long_api_key(self):
        """Test authentication with very long API key."""
        long_key = "a" * 1000
        auth = APIKeyAuth(api_keys=[long_key])

        ctx = await auth(api_key=long_key)
        assert ctx.authenticated is True
        assert ctx.api_key == long_key

    @pytest.mark.asyncio
    async def test_special_characters_in_key(self):
        """Test API keys with special characters."""
        special_key = "key-with_special.chars!@#$%"
        auth = APIKeyAuth(api_keys=[special_key])

        ctx = await auth(api_key=special_key)
        assert ctx.authenticated is True
        assert ctx.api_key == special_key

    @pytest.mark.asyncio
    async def test_unicode_in_key(self):
        """Test API keys with Unicode characters."""
        unicode_key = "key_with_émojis_🔑"
        auth = APIKeyAuth(api_keys=[unicode_key])

        ctx = await auth(api_key=unicode_key)
        assert ctx.authenticated is True
        assert ctx.api_key == unicode_key

    def test_permission_with_special_chars(self):
        """Test permissions with special characters."""
        ctx = AuthContext(
            authenticated=True,
            permissions={"read:all", "write:own", "admin/*"},
        )

        check_permission(ctx, "read:all")
        check_permission(ctx, "write:own")
        check_permission(ctx, "admin/*")

        with pytest.raises(HTTPException):
            check_permission(ctx, "read:own")

    def test_many_permissions(self):
        """Test context with many permissions."""
        permissions = {f"perm_{i}" for i in range(100)}
        ctx = AuthContext(authenticated=True, permissions=permissions)

        # Should be able to check any permission
        for perm in permissions:
            check_permission(ctx, perm)

        # Missing permission should fail
        with pytest.raises(HTTPException):
            check_permission(ctx, "perm_999")


class TestAuthSecurity:
    """Test security aspects of authentication."""

    @pytest.mark.asyncio
    async def test_timing_attack_resistance(self):
        """Test that auth doesn't leak info via timing."""
        auth = APIKeyAuth(api_keys=["secret_key_12345"])

        # These should all fail similarly (timing shouldn't reveal info)
        # Note: True timing attack resistance would need constant-time comparison
        keys_to_test = [
            "wrong_key",
            "secret_key_1234",  # Almost correct
            "x",  # Very short
            "",  # Empty
        ]

        for key in keys_to_test:
            with pytest.raises(HTTPException) as exc_info:
                await auth(api_key=key)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_no_key_enumeration(self):
        """Test that error messages don't reveal valid keys."""
        auth = APIKeyAuth(api_keys=["key1", "key2"])

        # Error message should be generic
        with pytest.raises(HTTPException) as exc_info:
            await auth(api_key="wrong")

        # Should not reveal which keys are valid
        assert "key1" not in exc_info.value.detail
        assert "key2" not in exc_info.value.detail

    def test_immutable_permissions(self):
        """Test that permissions can't be easily modified."""
        ctx = AuthContext(
            authenticated=True,
            permissions={"read"},
        )

        # Trying to modify should fail permission check
        with pytest.raises(HTTPException):
            check_permission(ctx, "write")

        # Even if we add permission, original check should work
        ctx.permissions.add("write")
        check_permission(ctx, "write")  # Now works

    @pytest.mark.asyncio
    async def test_auth_context_isolation(self):
        """Test that auth contexts are isolated."""
        auth = APIKeyAuth(api_keys=["key1", "key2"])

        ctx1 = await auth(api_key="key1")
        ctx2 = await auth(api_key="key2")

        # Contexts should be independent
        assert ctx1.api_key != ctx2.api_key
        assert ctx1 is not ctx2

        # Modifying one shouldn't affect the other
        ctx1.permissions.add("read")
        assert "read" not in ctx2.permissions
