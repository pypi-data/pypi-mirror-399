"""Example script to test policy fetching.

This script demonstrates how to fetch RBAC policy from the Astha service
without initializing MCP connections.

Run with: uv run python example_fetch_policy.py
"""

import asyncio
import json
import os
from pprint import pprint

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from astha_client import (
    Astha,
    AsthaError,
    PolicyFetchError,
    PolicyValidationError,
)

# Default credentials (can be overridden by environment variables)
DEFAULT_USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
DEFAULT_AZTP_ID = os.getenv("AZTP_ID")

async def test_policy_fetch():
    """Test fetching RBAC policy without MCP initialization."""
    print("=" * 70)
    print("Astha Policy Fetch Test")
    print("=" * 70)

    # Get credentials from environment or use defaults
    user_access_token = os.getenv("ASTHA_USER_ACCESS_TOKEN", DEFAULT_USER_ACCESS_TOKEN)
    aztp_id = os.getenv("ASTHA_AZTP_ID", DEFAULT_AZTP_ID)

    print(f"\nUsing credentials:")
    print(f"  Token: {user_access_token[:20]}...")
    print(f"  AZTP ID: {aztp_id}")
    print()

    try:
        # Create Astha client (no MCP config needed for policy fetch)
        astha = Astha(
            user_access_token=user_access_token,
            aztp_id=aztp_id,
        )

        print("✓ Astha client created successfully")
        print(f"  Initialized: {astha.is_initialized}")

        # Fetch policy using the internal policy client directly
        print("\n" + "-" * 70)
        print("Fetching RBAC policy from service...")
        print("-" * 70)

        policy = await astha._policy_client.fetch_policy_async()

        print("\n✅ Policy fetched successfully!")
        print("\n" + "=" * 70)
        print("Policy Details")
        print("=" * 70)

        # Display policy metadata
        print(f"\nMetadata:")
        print(f"  Name: {policy.metadata.name}")
        print(f"  Description: {policy.metadata.description or 'N/A'}")

        # Display policy version and URL
        print(f"\nVersion: {policy.version}")
        print(f"MCP URL: {policy.mcp_url}")

        # Display allowed tools
        print(f"\nAllowed Tools ({len(policy.tools.allowed_tools)}):")
        if policy.tools.allowed_tools:
            for tool in sorted(policy.tools.allowed_tools):
                print(f"  ✓ {tool}")
        else:
            print("  (none)")

        # Display denied tools
        print(f"\nDenied Tools ({len(policy.tools.denied_tools)}):")
        if policy.tools.denied_tools:
            for tool in sorted(policy.tools.denied_tools):
                print(f"  ✗ {tool}")
        else:
            print("  (none)")

        # Display raw policy (optional)
        print("\n" + "=" * 70)
        print("Raw Policy Data")
        print("=" * 70)
        print(json.dumps(policy.raw, indent=2))

        # Test accessing policy through Astha properties
        print("\n" + "=" * 70)
        print("Accessing Policy via Astha Properties")
        print("=" * 70)
        print(f"astha.policy: {astha.policy is not None}")
        print(f"astha.mcp_url: {astha.mcp_url}")
        print(f"astha.allowed_tools: {sorted(astha.allowed_tools)}")
        print(f"astha.denied_tools: {sorted(astha.denied_tools)}")

    except PolicyFetchError as e:
        print(f"\n❌ Policy Fetch Error:")
        print(f"  Message: {e}")
        if e.status_code:
            print(f"  HTTP Status Code: {e.status_code}")
        print("\nPossible causes:")
        print("  - Invalid or expired access token")
        print("  - Network connectivity issues")
        print("  - Policy service is down")
        print("  - Invalid AZTP ID")

    except PolicyValidationError as e:
        print(f"\n❌ Policy Validation Error:")
        print(f"  Message: {e}")
        print("\nPossible causes:")
        print("  - Invalid policy response format")
        print("  - Missing required fields in policy")
        print("  - Policy service returned malformed data")

    except ValueError as e:
        print(f"\n❌ Input Validation Error:")
        print(f"  Message: {e}")
        print("\nPlease check your credentials and try again.")

    except AsthaError as e:
        print(f"\n❌ Astha Error:")
        print(f"  Message: {e}")

    except Exception as e:
        print(f"\n❌ Unexpected Error:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {e}")
        raise


async def test_invalid_credentials():
    """Test error handling with invalid credentials."""
    print("\n" + "=" * 70)
    print("Testing Error Handling with Invalid Credentials")
    print("=" * 70)

    try:
        astha = Astha(
            user_access_token="invalid_token",
            aztp_id="invalid_aztp_id",
        )

        print("\n⏳ Attempting to fetch policy with invalid credentials...")
        policy = await astha._policy_client.fetch_policy_async()
        print(f"❌ Unexpected success: {policy}")

    except PolicyFetchError as e:
        print(f"✅ Correctly caught PolicyFetchError:")
        print(f"   Message: {e}")
        if e.status_code:
            print(f"   HTTP Status: {e.status_code}")

    except Exception as e:
        print(f"⚠️  Caught unexpected exception: {type(e).__name__}: {e}")


async def main():
    """Run all test scenarios."""
    # Test 1: Fetch policy with valid credentials
    await test_policy_fetch()

    # Test 2: Test error handling with invalid credentials
    await test_invalid_credentials()

    print("\n" + "=" * 70)
    print("Tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
