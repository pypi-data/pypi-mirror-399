"""Authentication and authorization for stateless MCP."""

from typing import Optional, List, Set
from fastapi import HTTPException, Security, Header
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import secrets


class AuthContext(BaseModel):
    """Authentication context for requests."""

    authenticated: bool = False
    api_key: Optional[str] = None
    user_id: Optional[str] = None
    roles: Set[str] = set()
    permissions: Set[str] = set()


class APIKeyAuth:
    """API Key authentication handler."""

    def __init__(self, api_keys: List[str], header_name: str = "X-API-Key"):
        """
        Initialize API key authentication.

        Args:
            api_keys: List of valid API keys
            header_name: HTTP header name for API key
        """
        self.api_keys = set(api_keys) if api_keys else set()
        self.header_name = header_name
        self.security = APIKeyHeader(name=header_name, auto_error=False)

    async def __call__(self, api_key: Optional[str] = Security(APIKeyHeader(name="X-API-Key", auto_error=False))) -> AuthContext:
        """
        Validate API key from request header.

        Args:
            api_key: API key from header

        Returns:
            AuthContext with authentication status

        Raises:
            HTTPException: If auth is required but invalid
        """
        if not self.api_keys:
            # Auth not configured, allow all
            return AuthContext(authenticated=True)

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing API key",
                headers={"WWW-Authenticate": f'{self.header_name}'},
            )

        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key",
                headers={"WWW-Authenticate": f'{self.header_name}'},
            )

        return AuthContext(
            authenticated=True,
            api_key=api_key,
            user_id=f"user_{hash(api_key) % 10000}",  # Simple user ID from key
        )


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure random API key.

    Args:
        length: Length of the API key

    Returns:
        Random API key string
    """
    return secrets.token_urlsafe(length)


class ToolPermissions:
    """Permission checker for tools."""

    def __init__(self):
        self.tool_permissions: dict = {}
        self.tool_roles: dict = {}

    def register_tool_permissions(self, tool_name: str, permissions: Set[str], roles: Set[str]):
        """Register permissions for a tool."""
        self.tool_permissions[tool_name] = permissions
        self.tool_roles[tool_name] = roles

    def check_permissions(self, tool_name: str, auth_context: AuthContext) -> bool:
        """
        Check if user has permission to access tool.

        Args:
            tool_name: Name of the tool
            auth_context: Authentication context

        Returns:
            True if authorized, False otherwise
        """
        if not auth_context.authenticated:
            return False

        # Check role-based access
        required_roles = self.tool_roles.get(tool_name, set())
        if required_roles:
            if not auth_context.roles.intersection(required_roles):
                return False

        # Check permission-based access
        required_permissions = self.tool_permissions.get(tool_name, set())
        if required_permissions:
            if not auth_context.permissions.intersection(required_permissions):
                return False

        return True


# Global permission checker
_permission_checker = ToolPermissions()


def get_permission_checker() -> ToolPermissions:
    """Get global permission checker."""
    return _permission_checker


def check_permission(auth_context: AuthContext, permission: str):
    """
    Check if auth context has a specific permission.

    Args:
        auth_context: Authentication context
        permission: Permission to check

    Raises:
        HTTPException: If permission not granted
    """
    if not auth_context.authenticated or permission not in auth_context.permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission} required"
        )
