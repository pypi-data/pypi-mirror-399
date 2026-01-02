"""MCP server configuration builder."""

from __future__ import annotations

from typing import Any

from astha_client.types import Policy


# Default Astha MCP gateway URL
ASTHA_GATEWAY_URL = "http://mcp.astha.ai/sse"


class MCPConfigBuilder:
    """Builds MCP server configuration from RBAC policy.

    This class generates configuration dictionaries compatible with
    mcp_use.MCPClient.from_dict() method.

    Example:
        >>> builder = MCPConfigBuilder(
        ...     user_access_token="token",
        ...     aztp_id="aztp://...",
        ... )
        >>> config = builder.build_from_policy(policy)
        >>> client = MCPClient.from_dict(config)
    """

    def __init__(
        self,
        user_access_token: str,
        aztp_id: str,
        server_name: str = "astha-mcp",
        gateway_url: str = ASTHA_GATEWAY_URL,
    ) -> None:
        """Initialize config builder.

        Args:
            user_access_token: User access token for MCP authentication.
            aztp_id: AZTP ID for MCP authentication.
            server_name: Name to use for the MCP server in config.
            gateway_url: Astha MCP gateway URL (default: http://mcp.astha.ai/sse).
        """
        self._user_access_token = user_access_token
        self._aztp_id = aztp_id
        self._server_name = server_name
        self._gateway_url = gateway_url

    def build_from_policy(self, _policy: Policy) -> dict[str, Any]:
        """Build MCP server config dict from policy.

        Uses the Astha gateway URL (not the policy's mcp_url) since the
        gateway handles routing to the appropriate backend MCP server.

        Args:
            _policy: RBAC policy (kept for API consistency; gateway URL is used).

        Returns:
            Configuration dict compatible with mcp_use.MCPClient.from_dict()
        """
        # Use Astha gateway, not the policy's mcp_url
        # The gateway routes based on the aztp_id header
        return self.build_stdio_config(self._gateway_url)

    def build_stdio_config(self, mcp_url: str) -> dict[str, Any]:
        """Build stdio-based config using mcp-proxy.

        This creates a configuration that uses uvx + mcp-proxy to connect
        to the MCP server via stdio transport.

        Args:
            mcp_url: URL of the MCP server (SSE endpoint).

        Returns:
            Configuration dict with mcpServers entry.
        """
        return {
            "mcpServers": {
                self._server_name: {
                    "command": "uvx",
                    "args": [
                        "mcp-proxy",
                        mcp_url,
                        "--headers",
                        "X-User-Access-Token",
                        self._user_access_token,
                        "--headers",
                        "X-Aztp-ID",
                        self._aztp_id,
                    ],
                }
            }
        }

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for direct HTTP connections.

        Returns:
            Dictionary of headers for MCP server authentication.
        """
        return {
            "X-User-Access-Token": self._user_access_token,
            "X-Aztp-ID": self._aztp_id,
        }
