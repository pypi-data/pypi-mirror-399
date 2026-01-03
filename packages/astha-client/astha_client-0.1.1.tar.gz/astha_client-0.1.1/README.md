# Astha Client

RBAC-controlled MCP (Model Context Protocol) tool access for AI agents. A clean, simple Python package for integrating MCP tools with LangChain agents while enforcing role-based access control.

## Features

- **RBAC Policy Enforcement**: Automatically fetch and apply access policies from Astha API
- **LangChain Integration**: Seamless integration with LangChain and Anthropic models
- **Clean API**: Simple, Composio-like interface for MCP tool access
- **Flexible Configuration**: Support for custom MCP server configs (dict or file)
- **Async Context Manager**: Automatic resource cleanup

## Installation

```bash
uv sync
```

## Quick Start

```python
import asyncio
from astha_client import Astha
from langchain_anthropic import ChatAnthropic

MCP_CONFIG = {
    "mcpServers": {
        "my-server": {
            "command": "uvx",
            "args": [
                "mcp-proxy",
                "http://mcp.astha.ai/sse",
                "--headers", "X-User-Access-Token", "your-token",
                "--headers", "X-Aztp-ID", "aztp://your-aztp-id",
            ],
        }
    }
}

async def main():
    async with Astha(
        user_access_token="your-token",
        aztp_id="aztp://your-aztp-id",
        mcp_config=MCP_CONFIG,
    ) as astha:
        # View allowed tools from RBAC policy
        print(f"Allowed tools: {astha.get_tools()}")

        # Create agent with RBAC-filtered tools
        llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
        agent = await astha.create_agent(llm=llm)

        # Run queries
        result = await agent.run("Send SMS to +1234567890")
        print(result)

asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your-anthropic-api-key
ASTHA_USER_ACCESS_TOKEN=your-user-access-token
ASTHA_AZTP_ID=aztp://aztp.network/workload/your-workload
```

### MCP Server Configuration

You can provide MCP config in three ways:

**1. Dictionary:**
```python
Astha(
    user_access_token="...",
    aztp_id="...",
    mcp_config={"mcpServers": {...}}
)
```

**2. Config file:**
```python
Astha(
    user_access_token="...",
    aztp_id="...",
    mcp_config_file="mcp_config.json"
)
```

**3. Default (uses Astha gateway):**
```python
Astha(
    user_access_token="...",
    aztp_id="..."
)
```

## API Reference

### Astha

```python
class Astha:
    def __init__(
        self,
        user_access_token: str,
        aztp_id: str,
        *,
        mcp_config: dict | None = None,
        mcp_config_file: str | Path | None = None,
        policy_service_url: str = "https://api.astha.ai/...",
    )

    async def initialize(self) -> None
    async def create_agent(self, llm, max_steps=15, memory_enabled=True) -> MCPAgent
    def get_tools(self) -> list[str]
    async def close(self) -> None

    # Properties
    policy: Policy | None
    mcp_url: str | None
    allowed_tools: frozenset[str]
    denied_tools: frozenset[str]
```

### Context Manager

```python
async with Astha(...) as astha:
    agent = await astha.create_agent(llm=llm)
    result = await agent.run("your query")
# Resources automatically cleaned up
```

## How It Works

1. **Policy Fetch**: Astha fetches RBAC policy from `api.astha.ai` using your credentials
2. **Tool Filtering**: Only tools allowed by your policy are exposed to the agent
3. **MCP Connection**: Connects to MCP server via `mcp-proxy` using stdio transport
4. **Agent Creation**: Creates a LangChain-compatible MCPAgent with filtered tools

## Requirements

- Python 3.11+
- `uv` package manager
- Anthropic API key
- Astha user access token and AZTP ID

## License

MIT
