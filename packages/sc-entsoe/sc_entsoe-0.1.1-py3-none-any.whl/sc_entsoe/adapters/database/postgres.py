"""PostgreSQL database adapter using asyncpg."""

from typing import Any

import asyncpg

from sc_entsoe.core import env, log

DEFAULT_PORT = "5432"
DEFAULT_USER = "postgres"
DEFAULT_SSL_MODE = "disable"
DEFAULT_MAX_CONNECTIONS = 10
DEFAULT_MIN_CONNECTIONS = 2
DEFAULT_MAX_CONN_LIFETIME = 3600.0  # 1 hour in seconds
DEFAULT_MAX_CONN_IDLE_TIME = 1800.0  # 30 minutes in seconds
DEFAULT_HEALTH_CHECK_PERIOD = 30.0  # 30 seconds


class Config:
    """PostgreSQL connection configuration."""

    def __init__(
        self,
        host: str,
        port: str,
        user: str,
        password: str,
        database: str,
        ssl_mode: str = DEFAULT_SSL_MODE,
        max_connections: int = DEFAULT_MAX_CONNECTIONS,
        min_connections: int = DEFAULT_MIN_CONNECTIONS,
        max_conn_lifetime: float = DEFAULT_MAX_CONN_LIFETIME,
        max_conn_idle_time: float = DEFAULT_MAX_CONN_IDLE_TIME,
        health_check_period: float = DEFAULT_HEALTH_CHECK_PERIOD,
    ):
        """Initialize database configuration."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.ssl_mode = ssl_mode
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_conn_lifetime = max_conn_lifetime
        self.max_conn_idle_time = max_conn_idle_time
        self.health_check_period = health_check_period


def ConfigFromEnv() -> Config:
    """
    Load database configuration from environment variables.

    Returns:
        Config instance

    Raises:
        ValueError: If required environment variables are missing
    """
    # Required variables
    host, err = env.GetString(env.PostgresHost)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresHost}: {err}")

    pwd, err = env.GetString(env.PostgresPassword)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresPassword}: {err}")

    db, err = env.GetString(env.PostgresDB)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresDB}: {err}")

    # Optional variables with defaults
    port, err = env.GetStringOr(env.PostgresPort, DEFAULT_PORT)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresPort}: {err}")

    user, err = env.GetStringOr(env.PostgresUser, DEFAULT_USER)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresUser}: {err}")

    sslmode, err = env.GetStringOr(env.PostgresSSLMode, DEFAULT_SSL_MODE)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresSSLMode}: {err}")

    max_conns, err = env.GetInt32Or(env.PostgresMaxConnections, DEFAULT_MAX_CONNECTIONS)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresMaxConnections}: {err}")

    min_conns, err = env.GetInt32Or(env.PostgresMinConnections, DEFAULT_MIN_CONNECTIONS)
    if err is not None:
        raise ValueError(f"failed to get {env.PostgresMinConnections}: {err}")

    return Config(
        host=host,
        port=port,
        user=user,
        password=pwd,
        database=db,
        ssl_mode=sslmode,
        max_connections=max_conns,
        min_connections=min_conns,
        max_conn_lifetime=DEFAULT_MAX_CONN_LIFETIME,
        max_conn_idle_time=DEFAULT_MAX_CONN_IDLE_TIME,
        health_check_period=DEFAULT_HEALTH_CHECK_PERIOD,
    )


class Pool:
    """PostgreSQL connection pool wrapper."""

    def __init__(self, pool: asyncpg.Pool):
        """Initialize pool wrapper."""
        self._pool = pool

    @property
    def pool(self) -> asyncpg.Pool:
        """Get the underlying asyncpg pool."""
        return self._pool

    async def close(self, ctx: dict[str, Any] | None = None) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            if ctx:
                logger = log.Ctx(ctx)  # type: ignore[attr-defined]
                logger.info("PostgreSQL connection pool closed")


async def NewPool(ctx: dict[str, Any] | None, cfg: Config) -> Pool:
    """
    Create a new PostgreSQL connection pool.

    Args:
        ctx: Context dictionary for logging
        cfg: Database configuration

    Returns:
        Pool instance

    Raises:
        ValueError: If connection fails
    """
    if ctx is None:
        ctx = {}

    ctx = log.Str(ctx, "db_host", cfg.host)  # type: ignore[attr-defined]
    ctx = log.Str(ctx, "db_port", cfg.port)  # type: ignore[attr-defined]
    ctx = log.Str(ctx, "db_name", cfg.database)  # type: ignore[attr-defined]
    ctx = log.Str(ctx, "db_user", cfg.user)  # type: ignore[attr-defined]
    ctx = log.Int(ctx, "db_max_connections", cfg.max_connections)  # type: ignore[attr-defined]
    ctx = log.Int(ctx, "db_min_connections", cfg.min_connections)  # type: ignore[attr-defined]

    logger = log.Ctx(ctx)  # type: ignore[attr-defined]
    logger.info("creating PostgreSQL connection pool")

    # Build connection string
    dsn = f"postgresql://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}"

    try:
        pool = await asyncpg.create_pool(
            dsn,
            min_size=cfg.min_connections,
            max_size=cfg.max_connections,
            max_queries=50000,
            max_inactive_connection_lifetime=cfg.max_conn_idle_time,
            command_timeout=60,
        )

        # Verify the connection
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

        logger.info("PostgreSQL connection pool created successfully")

        return Pool(pool)
    except Exception as e:
        raise ValueError(f"failed to create connection pool: {e}") from e


async def PoolFromEnv(ctx: dict[str, Any] | None = None) -> Pool:
    """
    Create a new connection pool from environment variables.

    Args:
        ctx: Context dictionary for logging

    Returns:
        Pool instance

    Raises:
        ValueError: If configuration or connection fails
    """
    cfg = ConfigFromEnv()
    return await NewPool(ctx, cfg)
