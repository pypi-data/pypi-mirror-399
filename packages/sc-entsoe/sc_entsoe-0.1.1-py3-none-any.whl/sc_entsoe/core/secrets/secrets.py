"""Secrets management interface and factory."""

from typing import Any

from sc_entsoe.core.env import GetString, SecretsMode

from .envvar import EnvVarSecret
from .secretsmanager import SecretsManagerSecret


class SecretGetter:
    """Interface for getting secrets."""

    async def get_secrets(self, secret_ref: str | None = None) -> dict[str, str]:
        """
        Get secrets.

        Args:
            secret_ref: Reference to the secret (e.g., ARN for Secrets Manager)

        Returns:
            Dictionary of secret key-value pairs
        """
        raise NotImplementedError


def NewSecret(ctx: dict[str, Any] | None = None) -> SecretGetter:
    """
    Create a new secret getter based on SECRETS_MODE environment variable.

    Args:
        ctx: Context dictionary (unused but kept for API compatibility)

    Returns:
        SecretGetter instance

    Raises:
        ValueError: If SECRETS_MODE is set to an unknown value
    """
    mode, err = GetString(SecretsMode)
    if err is not None:
        # Default to envvar if not set
        return EnvVarSecret()

    mode = mode.lower()

    if mode == "secretsmanager":
        return SecretsManagerSecret()
    elif mode == "envvar" or mode == "":
        return EnvVarSecret()
    else:
        raise ValueError(f"unknown secrets mode: {mode}")
