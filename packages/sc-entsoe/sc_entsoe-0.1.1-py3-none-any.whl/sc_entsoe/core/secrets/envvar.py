"""Environment variable-based secret getter."""

import os

from .secrets import SecretGetter


class EnvVarSecret(SecretGetter):
    """Secret getter that reads from environment variables."""

    async def get_secrets(self, secret_ref: str | None = None) -> dict[str, str]:
        """
        Get all environment variables as secrets.

        Args:
            secret_ref: Not used for env var getter

        Returns:
            Dictionary of all environment variables
        """
        return dict(os.environ)
