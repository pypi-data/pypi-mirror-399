"""Type definitions for the Astha package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolPolicy:
    """RBAC tool access policy.

    Attributes:
        allowed_tools: Set of tool names explicitly allowed.
        denied_tools: Set of tool names explicitly denied.
    """

    allowed_tools: frozenset[str] = field(default_factory=frozenset)
    denied_tools: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolPolicy:
        """Create ToolPolicy from dictionary."""
        return cls(
            allowed_tools=frozenset(data.get("allowed_tools", [])),
            denied_tools=frozenset(data.get("denied_tools", [])),
        )


@dataclass(frozen=True)
class PolicyMetadata:
    """Metadata associated with an RBAC policy.

    Attributes:
        name: Human-readable name of the policy.
        description: Optional description.
    """

    name: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyMetadata:
        """Create PolicyMetadata from dictionary."""
        return cls(
            name=data.get("name", "Unknown"),
            description=data.get("description"),
        )


@dataclass(frozen=True)
class Policy:
    """Complete RBAC policy structure.

    Attributes:
        version: Policy version string (e.g., "1.0", "2.0").
        mcp_url: Upstream MCP server URL to connect to.
        tools: Tool access rules.
        metadata: Policy metadata.
        raw: Raw policy dictionary for debugging.
    """

    version: str
    mcp_url: str
    tools: ToolPolicy
    metadata: PolicyMetadata
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Policy:
        """Create Policy from dictionary."""
        return cls(
            version=data.get("version", "unknown"),
            mcp_url=data.get("mcp_url", ""),
            tools=ToolPolicy.from_dict(data.get("tools", {})),
            metadata=PolicyMetadata.from_dict(data.get("metadata", {})),
            raw=data,
        )


@dataclass
class AsthaConfig:
    """Configuration for Astha client.

    Attributes:
        user_access_token: User access token for authentication.
        aztp_id: AZTP ID identifying the workload/node.
        policy_service_url: URL of the RBAC policy service.
        api_access: Optional API access token.
        api_access_key: Optional API access key.
        timeout: HTTP request timeout in seconds.
    """

    user_access_token: str
    aztp_id: str
    policy_service_url: str = (
        "https://api.astha.ai/astha/v1/user-workload/access-token/rbac"
    )
    api_access: str | None = None
    api_access_key: str | None = None
    timeout: float = 30.0
