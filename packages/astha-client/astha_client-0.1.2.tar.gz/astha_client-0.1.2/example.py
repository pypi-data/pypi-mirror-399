"""Example usage of the Astha package.

This example demonstrates how to use the Astha package for RBAC-controlled
MCP tool access with LangChain. It fetches the policy first and uses the
MCP configuration provided by the policy service.

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
DEFAULT_USER_ACCESS_TOKEN = os.getenv("ASTHA_USER_ACCESS_TOKEN")
DEFAULT_AZTP_ID = os.getenv("ASTHA_AZTP_ID")


async def main():
    """Main example demonstrating Astha package usage."""
    print("=" * 60)
    print("Astha Package Example")
    print("=" * 60)

    # Get credentials (use defaults or environment variables)
    user_access_token = os.getenv("USER_ACCESS_TOKEN", DEFAULT_USER_ACCESS_TOKEN)
    aztp_id = os.getenv("AZTP_ID", DEFAULT_AZTP_ID)
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        return

    # Step 1: Fetch policy to get MCP configuration
    print("\nStep 1: Fetching RBAC policy...")
    astha_temp = Astha(
        user_access_token=user_access_token,
        aztp_id=aztp_id,
    )

    try:
        policy = await astha_temp._policy_client.fetch_policy_async()
        print(f"✓ Policy fetched: {policy.metadata.name}")
        print(f"  MCP URL: {policy.mcp_url}")
        print(f"  Allowed tools: {list(policy.tools.allowed_tools)}")

        # Extract MCP config from policy
        mcp_config = policy.raw.get("mcp_json", {})
        if not mcp_config or "mcpServers" not in mcp_config:
            print("\n⚠️  No MCP configuration found in policy, using default")
            mcp_config = None
        else:
            print(f"\n✓ MCP configuration found in policy")
            print(f"  Servers: {list(mcp_config['mcpServers'].keys())}")

    except AsthaError as e:
        print(f"❌ Failed to fetch policy: {e}")
        return

    # Step 2: Initialize Astha with MCP config from policy
    print("\nStep 2: Initializing Astha with MCP servers...")

    try:
        # Use async context manager for automatic cleanup
        # Using MCP config from policy for optimal compatibility
        async with Astha(
            user_access_token=user_access_token,
            aztp_id=aztp_id,
            mcp_config=mcp_config,  # Use config from policy
        ) as astha:
            print("✓ Astha initialized successfully")

            # Print policy info
            print(f"\nPolicy Details:")
            print(f"  Name: {astha.policy.metadata.name}")
            print(f"  MCP URL: {astha.mcp_url}")
            print(f"  Allowed tools: {list(astha.allowed_tools)}")
            print(f"  Denied tools: {list(astha.denied_tools)}")

            # Get allowed tool names from RBAC policy
            tools = astha.get_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool_name in tools:
                print(f"  ✓ {tool_name}")

            # Create LLM and agent
            print("\nStep 3: Creating MCP agent...")
            llm = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
                api_key=anthropic_api_key,
            )

            agent = await astha.create_agent(
                llm=llm,
                max_steps=15,
                memory_enabled=True,
            )
            print("✓ MCP agent initialized with memory enabled")

            # Run a simple query
            print("\n" + "=" * 60)
            print("Step 4: Running agent query")
            print("=" * 60)
            print("\nQuery: List all the tools")
            print("-" * 60)

            result = await agent.run("Hello, list all the tools available.")
            print(f"Result: {result}")

            print("\n" + "=" * 60)
            print("✅ Query completed successfully!")
            print("=" * 60)

            result = await agent.run("run get_all_posts_summary tool'")
            print(f"Result: {result}")



    except AsthaError as e:
        print(f"\n❌ Astha error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
