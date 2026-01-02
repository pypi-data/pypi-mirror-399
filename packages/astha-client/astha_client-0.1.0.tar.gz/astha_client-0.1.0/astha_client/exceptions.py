"""Custom exceptions for the Astha package."""

from __future__ import annotations


class AsthaError(Exception):
    """Base exception for all Astha errors."""

    pass


class PolicyFetchError(AsthaError):
    """Error fetching RBAC policy from the policy service.

    Attributes:
        status_code: HTTP status code if available.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class PolicyValidationError(AsthaError):
    """Error validating policy structure."""

    pass


class ConnectionError(AsthaError):
    """Error connecting to MCP server."""

    pass


class ToolAccessDeniedError(AsthaError):
    """Attempted to access a denied tool.

    Attributes:
        tool_name: Name of the denied tool.
    """

    def __init__(self, tool_name: str) -> None:
        super().__init__(f"Access denied for tool: {tool_name}")
        self.tool_name = tool_name


class InitializationError(AsthaError):
    """Error during Astha initialization."""

    pass
