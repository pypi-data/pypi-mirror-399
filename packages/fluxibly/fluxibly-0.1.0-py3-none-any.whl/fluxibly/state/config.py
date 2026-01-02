"""Configuration for state management and database persistence.

This module provides configuration classes for database backends,
loading settings from environment variables.
"""

import os
from typing import Literal

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration settings.

    Attributes:
        backend: Database backend type (mock or postgresql)
        host: Database host
        port: Database port
        database: Database name
        user: Database username
        password: Database password
        pool_size: Connection pool size
        max_overflow: Maximum connection pool overflow
    """

    backend: Literal["mock", "postgresql"] = Field(default="mock")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="fluxibly")
    user: str = Field(default="postgres")
    password: str = Field(default="")
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables.

        Environment variables:
            DB_BACKEND: Database backend (mock or postgresql)
            DB_HOST: Database host
            DB_PORT: Database port
            DB_NAME: Database name
            DB_USER: Database username
            DB_PASSWORD: Database password
            DB_POOL_SIZE: Connection pool size
            DB_MAX_OVERFLOW: Maximum pool overflow

        Returns:
            DatabaseConfig instance
        """
        return cls(
            backend=os.getenv("DB_BACKEND", "mock"),  # type: ignore
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "fluxibly"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        )

    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string.

        Returns:
            PostgreSQL connection URL
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class StateConfig(BaseModel):
    """State management configuration.

    Attributes:
        enable_persistence: Whether to enable database persistence
        user_id: Default user ID for conversation threads
        org_id: Default organization ID for conversation threads
        database: Database configuration
    """

    enable_persistence: bool = Field(default=False)
    user_id: str = Field(default="default_user")
    org_id: str = Field(default="default_org")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @classmethod
    def from_env(cls) -> "StateConfig":
        """Load state configuration from environment variables.

        Environment variables:
            ENABLE_DB_PERSISTENCE: Enable database persistence (true/false)
            DEFAULT_USER_ID: Default user ID
            DEFAULT_ORG_ID: Default organization ID
            (Plus all DB_* variables from DatabaseConfig)

        Returns:
            StateConfig instance
        """
        enable_persistence = os.getenv("ENABLE_DB_PERSISTENCE", "false").lower() == "true"
        return cls(
            enable_persistence=enable_persistence,
            user_id=os.getenv("DEFAULT_USER_ID", "default_user"),
            org_id=os.getenv("DEFAULT_ORG_ID", "default_org"),
            database=DatabaseConfig.from_env(),
        )
