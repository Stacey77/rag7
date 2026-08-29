"""API key and secret management using environment variables only."""

from __future__ import annotations

import os
from typing import Any

from loguru import logger


class SecretNotFoundError(KeyError):
    """Raised when a requested secret is not available."""


class SecretManager:
    """API key and secret management via environment variables.

    Reads secrets exclusively from environment variables — never from
    code, configuration files, or hard-coded values.  Provides a
    consistent interface for retrieving and validating secrets.

    Attributes:
        _secret_registry: Mapping of logical name to environment variable name.
        _required_secrets: Set of secrets that must be present at startup.
    """

    def __init__(self) -> None:
        """Initialise the secret manager with an empty registry."""
        self._secret_registry: dict[str, str] = {}
        self._required_secrets: set[str] = set()
        logger.info("SecretManager initialised")

    def register(
        self,
        name: str,
        env_var: str,
        required: bool = False,
    ) -> None:
        """Register a secret by mapping a logical name to an env variable.

        Args:
            name: Logical name used to retrieve the secret.
            env_var: Environment variable name where the secret is stored.
            required: If ``True``, the secret is validated at startup.
        """
        self._secret_registry[name] = env_var
        if required:
            self._required_secrets.add(name)
        logger.debug("Secret '{}' registered → env var '{}'", name, env_var)

    def get(self, name: str, default: str | None = None) -> str | None:
        """Retrieve a secret value from the environment.

        Args:
            name: Logical secret name (must be registered first).
            default: Fallback value if the env variable is not set.

        Returns:
            Secret value string, or ``default`` if not found.

        Raises:
            SecretNotFoundError: If ``name`` is not registered.
        """
        if name not in self._secret_registry:
            raise SecretNotFoundError(
                f"Secret '{name}' is not registered. Call register() first."
            )
        env_var = self._secret_registry[name]
        value = os.environ.get(env_var, default)
        if value is None:
            logger.debug("Secret '{}' not set (env var: {})", name, env_var)
        return value

    def require(self, name: str) -> str:
        """Retrieve a required secret; raises if not set.

        Args:
            name: Logical secret name.

        Returns:
            Secret value string.

        Raises:
            SecretNotFoundError: If not registered or env variable not set.
        """
        value = self.get(name)
        if value is None:
            env_var = self._secret_registry.get(name, "?")
            raise SecretNotFoundError(
                f"Required secret '{name}' is not set. "
                f"Set environment variable '{env_var}'."
            )
        return value

    def validate_required(self) -> list[str]:
        """Check that all required secrets are present.

        Returns:
            List of missing required secret names (empty if all present).
        """
        missing: list[str] = []
        for name in self._required_secrets:
            if self.get(name) is None:
                missing.append(name)
        if missing:
            logger.error("Missing required secrets: {}", missing)
        else:
            logger.info("All {} required secrets validated", len(self._required_secrets))
        return missing

    def is_set(self, name: str) -> bool:
        """Check whether a registered secret is currently available.

        Args:
            name: Logical secret name.

        Returns:
            ``True`` if the secret is registered and the env variable is set.
        """
        try:
            return self.get(name) is not None
        except SecretNotFoundError:
            return False

    def list_registered(self) -> dict[str, dict[str, Any]]:
        """List all registered secrets with their status.

        Returns:
            Mapping of secret name to metadata dict with ``"env_var"``,
            ``"required"``, and ``"is_set"`` keys.
        """
        return {
            name: {
                "env_var": env_var,
                "required": name in self._required_secrets,
                "is_set": self.is_set(name),
            }
            for name, env_var in self._secret_registry.items()
        }
