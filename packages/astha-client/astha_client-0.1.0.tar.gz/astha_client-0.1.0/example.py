"""Example usage of the Astha package.

This example demonstrates how to use the Astha package for RBAC-controlled
MCP tool access with LangChain.

Run with: uv run python example.py
"""

import asyncio
import os
import warnings

# Suppress asyncio cleanup warnings (harmless noise from event loop shutdown)
warnings.filterwarnings("ignore", message=".*_UnixSelectorEventLoop.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file
load_dotenv()

from astha_client import Astha, AsthaError

# Default credentials (can be overridden by environment variables)
DEFAULT_USER_ACCESS_TOKEN = "qLUOhv+OUxKsdtvX6HZBVw==.miU1K6bmQXCrJ8M1rKFFeM6ItFm3IBKP+vEoNT+SBRecKTia/yPnX68zEYx/J31Oj2OJjfwixzZ8ElI9P9bErVCPbxXfhTR+QPNeKzlkso5IVULnsv6XlTlpW94VlBG7S07JEm3Itq+cDE9KQwQeEA=="
DEFAULT_AZTP_ID = "aztp://aztp.network/workload/development/node/sunday-hackathon/infobip-sms"

# MCP server configuration - defines how to connect to MCP servers
# This can be customized for different servers (Infobip SMS, Notion, Linear, etc.)
MCP_CONFIG = {
    "mcpServers": {
        "infobip-sms": {
            "command": "uvx",
            "args": [
                "mcp-proxy",
                "http://mcp.astha.ai/sse",
                "--headers",
                "X-User-Access-Token",
                DEFAULT_USER_ACCESS_TOKEN,
                "--headers",
                "X-Aztp-ID",
                DEFAULT_AZTP_ID,
            ],
        }
    }
}


async def main():
    """Main example demonstrating Astha package usage."""
    print("=" * 60)
    print("Astha Package Example")
    print("=" * 60)

    # Get credentials (use defaults or environment variables)
    user_access_token = os.getenv("ASTHA_USER_ACCESS_TOKEN", DEFAULT_USER_ACCESS_TOKEN)
    aztp_id = os.getenv("ASTHA_AZTP_ID", DEFAULT_AZTP_ID)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        return

    try:
        # Use async context manager for automatic cleanup
        # You can provide mcp_config dict, mcp_config_file path, or let it use defaults
        async with Astha(
            user_access_token=user_access_token,
            aztp_id=aztp_id,
            mcp_config=MCP_CONFIG,  # Pass custom MCP config
        ) as astha:
            # Print policy info
            print(f"\nPolicy: {astha.policy.metadata.name}")
            print(f"MCP URL: {astha.mcp_url}")
            print(f"Allowed tools: {list(astha.allowed_tools)}")

            # Get allowed tool names from RBAC policy
            tools = astha.get_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool_name in tools:
                print(f"  - {tool_name}")

            # Create LLM and agent
            llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
                api_key=anthropic_api_key,
            )

            agent = await astha.create_agent(
                llm=llm,
                max_steps=15,
                memory_enabled=True,
            )
            print("\nMCP agent initialized with memory enabled")

            # Run a simple query
            print("\n" + "=" * 60)
            print("Running agent query: 'Hello, list all the tools?'")
            print("=" * 60)

            result = await agent.run("Hello, list all the tools?")
            print(f"\nResult:\n{result}")

    except AsthaError as e:
        print(f"Astha error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
