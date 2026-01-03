"""Main Astha client - the primary entry point."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from astha_client._internal.async_utils import run_sync
from astha_client.exceptions import InitializationError
from astha_client.policy import PolicyClient
from astha_client.types import AsthaConfig, Policy

if TYPE_CHECKING:
    from langchain_core.language_models import BaseLanguageModel
    from mcp_use import MCPAgent, MCPClient


def _sanitize_schema_field_names(schema: Any) -> Any:
    """Sanitize JSON schema field names to be Pydantic v2 compatible.

    Pydantic v2 doesn't allow field names with leading underscores.
    This function renames such fields by removing the leading underscore.

    Args:
        schema: The JSON schema to sanitize.

    Returns:
        The sanitized JSON schema.
    """
    if isinstance(schema, dict):
        new_schema = {}
        for key, value in schema.items():
            # Sanitize the value recursively
            sanitized_value = _sanitize_schema_field_names(value)

            # If this is a "properties" dict, sanitize property names
            if key == "properties" and isinstance(sanitized_value, dict):
                new_properties = {}
                for prop_name, prop_value in sanitized_value.items():
                    # Remove leading underscores from property names
                    if prop_name.startswith("_"):
                        new_name = prop_name.lstrip("_")
                        # Ensure we don't create empty names
                        if not new_name:
                            new_name = "param"
                        new_properties[new_name] = prop_value
                    else:
                        new_properties[prop_name] = prop_value
                sanitized_value = new_properties

            # If this is a "required" list, sanitize field names there too
            if key == "required" and isinstance(sanitized_value, list):
                sanitized_value = [
                    name.lstrip("_") if name.startswith("_") else name
                    for name in sanitized_value
                ]

            new_schema[key] = sanitized_value
        return new_schema
    elif isinstance(schema, list):
        return [_sanitize_schema_field_names(item) for item in schema]
    return schema


def _patch_mcp_use_schema_handler() -> None:
    """Patch the mcp_use library to handle underscore-prefixed field names."""
    try:
        from mcp_use.agents.adapters.base import BaseAdapter

        original_fix_schema = BaseAdapter.fix_schema
        def patched_fix_schema(self: Any, schema: Any) -> Any:
            # First apply the original fixes
            fixed = original_fix_schema(self, schema)
            # Then sanitize field names
            return _sanitize_schema_field_names(fixed)

        BaseAdapter.fix_schema = patched_fix_schema
    except ImportError:
        pass  # mcp_use not installed, nothing to patch


class Astha:
    """Main Astha client for RBAC-controlled MCP access.

    Provides a clean API for accessing MCP tools with automatic RBAC
    policy enforcement. Tools are filtered based on the user's permissions.

    Example with MCP config dict:
        >>> mcp_config = {
        ...     "mcpServers": {
        ...         "my-server": {
        ...             "command": "uvx",
        ...             "args": ["mcp-proxy", "http://mcp.astha.ai/sse", ...]
        ...         }
        ...     }
        ... }
        >>> astha = Astha(
        ...     user_access_token="...",
        ...     aztp_id="...",
        ...     mcp_config=mcp_config,
        ... )
        >>> await astha.initialize()
        >>> agent = await astha.create_agent(llm=llm)

    Example with MCP config file:
        >>> astha = Astha(
        ...     user_access_token="...",
        ...     aztp_id="...",
        ...     mcp_config_file="mcp_config.json",
        ... )

    Context Manager Example:
        >>> async with Astha(...) as astha:
        ...     agent = await astha.create_agent(llm=llm)
        ...     result = await agent.run("List tools")
    """

    def __init__(
        self,
        user_access_token: str,
        aztp_id: str,
        *,
        mcp_config: dict[str, Any] | None = None,
        mcp_config_file: str | Path | None = None,
        policy_service_url: str = "https://api.astha.ai/astha/v1/user-workload/access-token/rbac",
        api_access: str | None = None,
        api_access_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize Astha client.

        Args:
            user_access_token: User access token for authentication.
            aztp_id: AZTP ID identifying the workload/node.
            mcp_config: MCP server configuration dict (mcpServers format).
            mcp_config_file: Path to MCP config JSON file.
            policy_service_url: URL of the RBAC policy service.
            api_access: Optional API access token.
            api_access_key: Optional API access key.
            timeout: HTTP request timeout in seconds.

        Note:
            Either mcp_config or mcp_config_file should be provided.
            If neither is provided, a default config using the Astha gateway
            will be generated.
        """
        self._config = AsthaConfig(
            user_access_token=user_access_token,
            aztp_id=aztp_id,
            policy_service_url=policy_service_url,
            api_access=api_access,
            api_access_key=api_access_key,
            timeout=timeout,
        )
        self._policy_client = PolicyClient(self._config)
        self._mcp_config = mcp_config
        self._mcp_config_file = mcp_config_file
        self._mcp_client: MCPClient | None = None
        self._initialized: bool = False

    # === Async API ===

    async def initialize(self) -> None:
        """Initialize Astha: fetch policy and create MCP sessions.

        This method:
        1. Fetches the RBAC policy from the policy service
        2. Loads MCP configuration (from dict, file, or generates default)
        3. Creates MCPClient and establishes sessions

        Raises:
            InitializationError: If initialization fails.
        """
        if self._initialized:
            return

        # Apply patch to handle underscore-prefixed field names in tool schemas
        _patch_mcp_use_schema_handler()

        try:
            # 1. Fetch RBAC policy
            await self._policy_client.fetch_policy_async()

            # 2. Load or generate MCP configuration
            mcp_config = self._get_mcp_config()

            # 3. Create MCP client and sessions
            from mcp_use import MCPClient

            self._mcp_client = MCPClient.from_dict(mcp_config)
            await self._mcp_client.create_all_sessions()

            self._initialized = True

        except Exception as e:
            raise InitializationError(f"Failed to initialize Astha: {e}") from e

    async def get_tools_async(self) -> list[str]:
        """Get RBAC-allowed tool names (async).

        Returns:
            List of tool names that are allowed by RBAC policy.

        Raises:
            InitializationError: If not initialized.
        """
        if not self._initialized:
            await self.initialize()

        policy = self._policy_client.policy
        if policy and policy.tools.allowed_tools:
            return list(policy.tools.allowed_tools)
        return []

    async def create_agent(
        self,
        llm: BaseLanguageModel,
        max_steps: int = 15,
        memory_enabled: bool = True,
        **kwargs: Any,
    ) -> MCPAgent:
        """Create an MCPAgent with RBAC-filtered tools.

        Args:
            llm: LangChain language model to use.
            max_steps: Maximum steps for agent execution.
            memory_enabled: Enable conversation memory.
            **kwargs: Additional MCPAgent arguments.

        Returns:
            Configured MCPAgent ready for use.

        Raises:
            InitializationError: If not initialized.
        """
        if not self._initialized:
            await self.initialize()

        if self._mcp_client is None:
            raise InitializationError("MCP client not initialized")

        from mcp_use import MCPAgent

        # Compute disallowed tools from policy
        policy = self._policy_client.policy
        disallowed_tools = self._get_disallowed_tools(policy) if policy else []

        agent = MCPAgent(
            llm=llm,
            client=self._mcp_client,
            max_steps=max_steps,
            memory_enabled=memory_enabled,
            disallowed_tools=disallowed_tools,
            **kwargs,
        )

        return agent

    async def close(self) -> None:
        """Close all MCP sessions and clean up resources."""
        if self._mcp_client is not None:
            await self._mcp_client.close_all_sessions()
            self._mcp_client = None
        self._initialized = False

    # === Sync API ===

    def get_tools(self) -> list[str]:
        """Get RBAC-allowed tool names (sync wrapper).

        Returns:
            List of tool names that are allowed by RBAC policy.
        """
        return run_sync(self.get_tools_async())

    # === Properties ===

    @property
    def policy(self) -> Policy | None:
        """Get the current RBAC policy."""
        return self._policy_client.policy

    @property
    def mcp_url(self) -> str | None:
        """Get the MCP server URL from policy."""
        return self.policy.mcp_url if self.policy else None

    @property
    def allowed_tools(self) -> frozenset[str]:
        """Get set of allowed tool names."""
        return self.policy.tools.allowed_tools if self.policy else frozenset()

    @property
    def denied_tools(self) -> frozenset[str]:
        """Get set of denied tool names."""
        return self.policy.tools.denied_tools if self.policy else frozenset()

    @property
    def is_initialized(self) -> bool:
        """Check if Astha is fully initialized."""
        return self._initialized

    @property
    def client(self) -> MCPClient | None:
        """Get the underlying MCPClient instance."""
        return self._mcp_client

    # === Context Manager Support ===

    async def __aenter__(self) -> Astha:
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    # === Private Methods ===

    def _get_mcp_config(self) -> dict[str, Any]:
        """Get MCP configuration from provided source or generate default.

        Returns:
            MCP configuration dict.

        Raises:
            InitializationError: If config file cannot be loaded.
        """
        # Use provided config dict
        if self._mcp_config is not None:
            return self._mcp_config

        # Load from config file
        if self._mcp_config_file is not None:
            try:
                config_path = Path(self._mcp_config_file)
                with open(config_path) as f:
                    return json.load(f)
            except Exception as e:
                raise InitializationError(
                    f"Failed to load MCP config from {self._mcp_config_file}: {e}"
                ) from e

        # Generate default config using Astha gateway
        return self._build_default_config()

    def _build_default_config(self) -> dict[str, Any]:
        """Build default MCP config using Astha gateway.

        Returns:
            Default MCP configuration dict.
        """
        return {
            "mcpServers": {
                "astha-mcp": {
                    "command": "uvx",
                    "args": [
                        "mcp-proxy",
                        "http://mcp.astha.ai/sse",
                        "--headers",
                        "X-User-Access-Token",
                        self._config.user_access_token,
                        "--headers",
                        "X-Aztp-ID",
                        self._config.aztp_id,
                    ],
                }
            }
        }

    def _get_disallowed_tools(self, policy: Policy) -> list[str]:
        """Get list of disallowed tool names for MCPAgent.

        Args:
            policy: RBAC policy.

        Returns:
            List of tool names to disallow in MCPAgent.
        """
        return list(policy.tools.denied_tools)
