# Astha Client

RBAC-controlled MCP (Model Context Protocol) tool access for AI agents. A clean, simple Python package for integrating MCP tools with LangChain agents while enforcing role-based access control.

## Features

- **RBAC Policy Enforcement**: Automatically fetch and apply access policies from Astha API
- **LangChain Integration**: Seamless integration with LangChain and Anthropic models
- **Clean API**: Simple, Composio-like interface for MCP tool access
- **Flexible Configuration**: Support for custom MCP server configs (dict or file)
- **Async Context Manager**: Automatic resource cleanup
- **Comprehensive Error Handling**: Robust input validation and error messages
- **Type Safety**: Full type hints with MyPy support
- **Testing**: Complete unit and integration test coverage

## Installation

### From PyPI (recommended)

```bash
pip install astha-client
```

### From source

```bash
git clone https://github.com/AsthaAi/astha-client-py.git
cd astha-client-py
uv sync
```

## Quick Start

### Basic Usage

```python
import asyncio
import os
from astha_client import Astha
from langchain_anthropic import ChatAnthropic

async def main():
    # Credentials from environment variables
    async with Astha(
        user_access_token=os.getenv("ASTHA_USER_ACCESS_TOKEN"),
        aztp_id=os.getenv("ASTHA_AZTP_ID"),
    ) as astha:
        # View allowed tools from RBAC policy
        print(f"Policy: {astha.policy.metadata.name}")
        print(f"Allowed tools: {astha.get_tools()}")

        # Create agent with RBAC-filtered tools
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        agent = await astha.create_agent(llm=llm)

        # Run queries
        result = await agent.run("List all available tools")
        print(result)

asyncio.run(main())
```

### With Custom MCP Configuration

```python
import asyncio
import os
from astha_client import Astha
from langchain_anthropic import ChatAnthropic

# Option 1: Fetch policy and use its MCP configuration
async def main():
    # First fetch the policy to get MCP config
    astha_temp = Astha(
        user_access_token=os.getenv("ASTHA_USER_ACCESS_TOKEN"),
        aztp_id=os.getenv("ASTHA_AZTP_ID"),
    )

    policy = await astha_temp._policy_client.fetch_policy_async()
    mcp_config = policy.raw.get("mcp_json", {})

    # Use the policy's MCP configuration
    async with Astha(
        user_access_token=os.getenv("ASTHA_USER_ACCESS_TOKEN"),
        aztp_id=os.getenv("ASTHA_AZTP_ID"),
        mcp_config=mcp_config,
    ) as astha:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        agent = await astha.create_agent(llm=llm)
        result = await agent.run("Your query here")
        print(result)

asyncio.run(main())
```

See [example.py](example.py) and [example_fetch_policy.py](example_fetch_policy.py) for complete working examples.

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

**1. From Policy (Recommended):**
```python
# Fetch policy first to get MCP configuration
policy = await astha._policy_client.fetch_policy_async()
mcp_config = policy.raw.get("mcp_json", {})

Astha(
    user_access_token="...",
    aztp_id="...",
    mcp_config=mcp_config
)
```

**2. Custom Dictionary:**
```python
Astha(
    user_access_token="...",
    aztp_id="...",
    mcp_config={"mcpServers": {...}}
)
```

**3. Config File:**
```python
Astha(
    user_access_token="...",
    aztp_id="...",
    mcp_config_file="mcp_config.json"
)
```

**4. Default (minimal setup):**
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
        policy_service_url: str = "https://api.astha.ai/v1/rbac/policy",
        timeout: int = 30,
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
    is_initialized: bool
```

### Exceptions

The package provides specific exception types for better error handling:

```python
from astha_client import (
    AsthaError,              # Base exception
    PolicyFetchError,        # Failed to fetch policy from service
    PolicyValidationError,   # Invalid policy response
    ConfigurationError,      # Configuration issues
    ConnectionError,         # MCP connection issues
    InitializationError,     # Initialization failures
    ToolAccessDeniedError,   # Attempted to use denied tool
)
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

## Error Handling

The package includes comprehensive error handling:

```python
from astha_client import Astha, PolicyFetchError, InitializationError

try:
    async with Astha(
        user_access_token=token,
        aztp_id=aztp_id,
    ) as astha:
        agent = await astha.create_agent(llm=llm)
        result = await agent.run("query")

except PolicyFetchError as e:
    print(f"Failed to fetch policy: {e}")
    # Handle invalid credentials, network issues, etc.

except InitializationError as e:
    print(f"Failed to initialize: {e}")
    # Handle MCP connection issues, config errors, etc.

except ValueError as e:
    print(f"Invalid input: {e}")
    # Handle validation errors (empty tokens, invalid timeout, etc.)
```

## Testing

The package includes comprehensive tests:

```bash
# Run unit tests
uv run pytest

# Run with coverage
uv run pytest --cov=astha_client

# Run specific test file
uv run pytest test_error_handling.py

# Run example scripts
uv run python example.py
uv run python example_fetch_policy.py
```

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run type checking
uv run mypy astha_client

# Run linting
uv run ruff check astha_client

# Format code
uv run black astha_client
```

## Requirements

- Python 3.11+
- Dependencies:
  - `mcp-use>=1.5.1`
  - `langchain-anthropic>=1.3.0`
  - `httpx>=0.27.0`
  - `mcp>=0.9.0`
  - `python-dotenv>=1.2.1`
- Anthropic API key
- Astha user access token and AZTP ID

## Examples

See the following example files for complete usage:

- [example.py](example.py) - Complete workflow with policy-provided MCP config
- [example_fetch_policy.py](example_fetch_policy.py) - Policy fetching without MCP connections

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
