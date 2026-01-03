"""Authentication and credential management with security best practices."""

import os
from pathlib import Path
from types import ModuleType
from typing import Protocol

from dotenv import load_dotenv


class RedactedString:
    """String wrapper that redacts value in repr and str for security."""

    def __init__(self, value: str):
        self._value = value

    def get(self) -> str:
        """Get the actual value."""
        return self._value

    def __str__(self) -> str:
        """Return redacted string."""
        return "***REDACTED***"

    def __repr__(self) -> str:
        """Return redacted repr."""
        return "RedactedString(***REDACTED***)"

    def __eq__(self, other: object) -> bool:
        """Compare values."""
        if isinstance(other, RedactedString):
            return self._value == other._value
        return False


class CredentialProvider(Protocol):
    """Protocol for pluggable credential providers."""

    def get_api_key(self) -> str | None:
        """Get API key from this provider.

        Returns:
            API key if available, None otherwise
        """
        ...


class EnvCredentialProvider:
    """Load credentials from environment variables."""

    def __init__(self, env_var: str = "ENTSOE_API_KEY"):
        self.env_var = env_var

    def get_api_key(self) -> str | None:
        """Get API key from environment variable."""
        return os.getenv(self.env_var)


class DotEnvCredentialProvider:
    """Load credentials from .env file (dev only)."""

    def __init__(self, env_file: Path | str = ".env", env_var: str = "ENTSOE_API_KEY"):
        self.env_file = Path(env_file)
        self.env_var = env_var

    def get_api_key(self) -> str | None:
        """Get API key from .env file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            return os.getenv(self.env_var)
        return None


class KeyringCredentialProvider:
    """Load credentials from OS keyring (optional)."""

    def __init__(self, service_name: str = "entsoe", username: str = "api_key"):
        self.service_name = service_name
        self.username = username
        self._keyring: ModuleType | None = None

    def get_api_key(self) -> str | None:
        """Get API key from OS keyring."""
        try:
            import keyring

            self._keyring = keyring
            return keyring.get_password(self.service_name, self.username)
        except ImportError:
            # keyring is optional
            return None
        except Exception:
            # Keyring access failed
            return None


class CredentialManager:
    """Manage API credentials with multiple sources and security best practices."""

    def __init__(
        self,
        api_key: str | None = None,
        providers: list[CredentialProvider] | None = None,
    ):
        """Initialize credential manager.

        Args:
            api_key: Explicit API key (highest priority)
            providers: List of credential providers to try in order
        """
        self._api_key = RedactedString(api_key) if api_key else None

        # Default providers in priority order
        if providers is None:
            providers = [
                EnvCredentialProvider(),
                DotEnvCredentialProvider(),
                KeyringCredentialProvider(),
            ]
        self._providers = providers

    def get_api_key(self) -> str:
        """Get API key from highest priority source.

        Returns:
            API key string

        Raises:
            ValueError: If no API key is found
        """
        # Priority 1: Explicit API key
        if self._api_key:
            return self._api_key.get()

        # Priority 2-N: Try providers in order
        for provider in self._providers:
            api_key = provider.get_api_key()
            if api_key:
                return api_key

        raise ValueError(
            "No API key found. Please provide via:\n"
            "  1. api_key= argument\n"
            "  2. ENTSOE_API_KEY environment variable\n"
            "  3. .env file with ENTSOE_API_KEY\n"
            "  4. OS keyring (optional)"
        )

    def set_api_key(self, api_key: str) -> None:
        """Update API key (for credential rotation).

        Args:
            api_key: New API key
        """
        self._api_key = RedactedString(api_key)


def sanitize_params(params: dict) -> dict:
    """Sanitize query parameters by redacting sensitive values.

    Args:
        params: Dictionary of parameters

    Returns:
        Sanitized copy with API keys redacted
    """
    sanitized = params.copy()
    sensitive_keys = {"api_key", "securityToken", "security_token", "token"}

    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = "***REDACTED***"

    return sanitized
