"""Astha - RBAC-controlled MCP tool access for AI agents.

This package provides a clean API for accessing MCP (Model Context Protocol)
tools with automatic RBAC (Role-Based Access Control) policy enforcement.

Example:
    >>> from astha_client import Astha
    >>> from langchain_anthropic import ChatAnthropic
    >>>
    >>> # Initialize client with credentials
    >>> astha = Astha(
    ...     user_access_token="your-token",
    ...     aztp_id="aztp://your-workload-id",
    ... )
    >>>
    >>> # Initialize and get tools
    >>> await astha.initialize()
    >>> tools = astha.get_tools()
    >>> print(f"Available tools: {[t.name for t in tools]}")
    >>>
    >>> # Create an agent with LLM
    >>> llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
    >>> agent = await astha.create_agent(llm=llm)
    >>> result = await agent.run("Send an SMS to +1234567890")
    >>>
    >>> # Clean up
    >>> await astha.close()

Context Manager Example:
    >>> async with Astha(user_access_token="...", aztp_id="...") as astha:
    ...     agent = await astha.create_agent(llm=llm)
    ...     result = await agent.run("List all available tools")
    ...     print(result)
"""

from astha_client.client import Astha
from astha_client.exceptions import (
    AsthaError,
    ConnectionError,
    InitializationError,
    PolicyFetchError,
    PolicyValidationError,
    ToolAccessDeniedError,
)
from astha_client.types import AsthaConfig, Policy, PolicyMetadata, ToolPolicy

__version__ = "0.1.0"

__all__ = [
    # Main class
    "Astha",
    # Types
    "Policy",
    "ToolPolicy",
    "PolicyMetadata",
    "AsthaConfig",
    # Exceptions
    "AsthaError",
    "PolicyFetchError",
    "PolicyValidationError",
    "ConnectionError",
    "ToolAccessDeniedError",
    "InitializationError",
]
