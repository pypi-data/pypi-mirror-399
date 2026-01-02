"""RBAC policy fetching and management."""

from __future__ import annotations

from typing import Any

import httpx

from astha_client._internal.async_utils import run_sync
from astha_client.exceptions import PolicyFetchError, PolicyValidationError
from astha_client.types import AsthaConfig, Policy


class PolicyClient:
    """Client for fetching and managing RBAC policies.

    Example:
        >>> config = AsthaConfig(user_access_token="...", aztp_id="...")
        >>> client = PolicyClient(config)
        >>> policy = await client.fetch_policy_async()
        >>> print(policy.mcp_url)
    """

    def __init__(self, config: AsthaConfig) -> None:
        """Initialize policy client with configuration.

        Args:
            config: Astha configuration containing credentials.
        """
        self._config = config
        self._cached_policy: Policy | None = None

    async def fetch_policy_async(self) -> Policy:
        """Fetch RBAC policy from Astha policy service (async).

        Returns:
            Policy object containing version, mcp_url, tools, and metadata.

        Raises:
            PolicyFetchError: If HTTP request fails.
            PolicyValidationError: If response is invalid.
        """
        headers = {
            "user_access_token": self._config.user_access_token,
            "Content-Type": "application/json",
        }

        if self._config.api_access:
            headers["api_access"] = self._config.api_access
        if self._config.api_access_key:
            headers["api_access_key"] = self._config.api_access_key

        request_body = {"aztpId": self._config.aztp_id}

        try:
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                response = await client.post(
                    self._config.policy_service_url,
                    headers=headers,
                    json=request_body,
                )

                if response.status_code != 200:
                    raise PolicyFetchError(
                        f"Policy service returned status {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )

                try:
                    data = response.json().get("data", {})
                except Exception as e:
                    raise PolicyValidationError(
                        f"Invalid JSON response from policy service: {e}"
                    ) from e

                self._validate_policy(data)
                self._cached_policy = Policy.from_dict(data)
                return self._cached_policy

        except httpx.TimeoutException as e:
            raise PolicyFetchError(
                f"Timeout fetching policy from {self._config.policy_service_url}"
            ) from e

        except httpx.ConnectError as e:
            raise PolicyFetchError(
                f"Failed to connect to policy service at {self._config.policy_service_url}"
            ) from e

        except (PolicyFetchError, PolicyValidationError):
            raise

        except Exception as e:
            raise PolicyFetchError(f"Unexpected error fetching policy: {e}") from e

    def fetch_policy(self) -> Policy:
        """Fetch RBAC policy (sync wrapper with Jupyter compatibility).

        Returns:
            Policy object containing version, mcp_url, tools, and metadata.

        Raises:
            PolicyFetchError: If HTTP request fails.
            PolicyValidationError: If response is invalid.
        """
        return run_sync(self.fetch_policy_async())

    @property
    def policy(self) -> Policy | None:
        """Get cached policy, if available."""
        return self._cached_policy

    def clear_cache(self) -> None:
        """Clear the cached policy."""
        self._cached_policy = None

    @staticmethod
    def _validate_policy(data: Any) -> None:
        """Validate policy structure, raising PolicyValidationError on failure."""
        if not isinstance(data, dict):
            raise PolicyValidationError("Policy response must be a JSON object")

        if "version" not in data:
            raise PolicyValidationError(
                "Policy response missing required 'version' field"
            )

        if "mcp_url" not in data:
            raise PolicyValidationError(
                "Policy response missing required 'mcp_url' field"
            )
