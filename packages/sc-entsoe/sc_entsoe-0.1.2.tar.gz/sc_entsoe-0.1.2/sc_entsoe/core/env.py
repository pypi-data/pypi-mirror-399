"""Environment variable handling with Go-style error returns."""

import os

# Environment variable names
SecretsMode = "SECRETS_MODE"
PostgresHost = "POSTGRES_HOST"
PostgresPort = "POSTGRES_PORT"
PostgresUser = "POSTGRES_USER"
PostgresPassword = "POSTGRES_PASSWORD"
PostgresDB = "POSTGRES_DB"
PostgresSSLMode = "POSTGRES_SSL_MODE"
PostgresMaxConnections = "POSTGRES_MAX_CONNECTIONS"
PostgresMinConnections = "POSTGRES_MIN_CONNECTIONS"


def GetString(key: str) -> tuple[str | None, Exception | None]:
    """
    Get string value from environment variable.

    Args:
        key: Environment variable name

    Returns:
        Tuple of (value, error) - Go-style error handling
    """
    value = os.getenv(key)
    if value is None:
        return None, ValueError(f"environment variable {key} not set")
    return value, None


def GetStringOr(key: str, default: str) -> tuple[str, Exception | None]:
    """
    Get string value from environment variable with default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Tuple of (value, error) - Go-style error handling
    """
    value = os.getenv(key, default)
    return value, None


def GetInt32Or(key: str, default: int) -> tuple[int, Exception | None]:
    """
    Get int32 value from environment variable with default.

    Args:
        key: Environment variable name
        default: Default value if not set

    Returns:
        Tuple of (value, error) - Go-style error handling
    """
    value_str = os.getenv(key)
    if value_str is None:
        return default, None

    try:
        value = int(value_str)
        return value, None
    except ValueError:
        return default, ValueError(f"invalid integer value for {key}: {value_str}")
