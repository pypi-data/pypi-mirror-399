"""
Environment Variable Helpers

Provides convenient functions for reading environment variables
used by Gnosari Engine, with sensible defaults and validation.
"""

import os
from typing import Optional


def get_database_url(default: Optional[str] = None) -> Optional[str]:
    """
    Get database URL from GNOSARI_DATABASE_URL environment variable.

    Args:
        default: Default value if environment variable is not set

    Returns:
        Database URL string or None

    Example:
        >>> database_url = get_database_url()
        >>> # Or with explicit default
        >>> database_url = get_database_url("postgresql+asyncpg://localhost/gnosari")
    """
    return os.getenv("GNOSARI_DATABASE_URL", default)


def get_account_id(default: Optional[int] = None) -> Optional[int]:
    """
    Get account ID from GNOSARI_ACCOUNT_ID environment variable.

    Args:
        default: Default value if environment variable is not set

    Returns:
        Account ID as integer or None

    Raises:
        ValueError: If GNOSARI_ACCOUNT_ID is set but not a valid integer

    Example:
        >>> account_id = get_account_id()
        >>> # Or with explicit default
        >>> account_id = get_account_id(default=1)
    """
    value = os.getenv("GNOSARI_ACCOUNT_ID")

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Invalid GNOSARI_ACCOUNT_ID: '{value}'. Must be an integer."
        )


def get_openai_api_key(default: Optional[str] = None) -> Optional[str]:
    """
    Get OpenAI API key from OPENAI_API_KEY environment variable.

    Args:
        default: Default value if environment variable is not set

    Returns:
        OpenAI API key string or None

    Example:
        >>> api_key = get_openai_api_key()
    """
    return os.getenv("OPENAI_API_KEY", default)


def get_anthropic_api_key(default: Optional[str] = None) -> Optional[str]:
    """
    Get Anthropic API key from ANTHROPIC_API_KEY environment variable.

    Args:
        default: Default value if environment variable is not set

    Returns:
        Anthropic API key string or None

    Example:
        >>> api_key = get_anthropic_api_key()
    """
    return os.getenv("ANTHROPIC_API_KEY", default)


def get_provider_api_key(provider: str) -> Optional[str]:
    """
    Get API key for specified provider from environment variable.

    Supports: openai, anthropic, deepseek, google, etc.

    Args:
        provider: Provider name (e.g., "openai", "anthropic")

    Returns:
        API key string or None

    Example:
        >>> api_key = get_provider_api_key("openai")
        >>> api_key = get_provider_api_key("anthropic")
    """
    provider_upper = provider.upper()

    # Common provider environment variable patterns
    env_var_patterns = [
        f"{provider_upper}_API_KEY",
        f"{provider_upper}API_KEY",
        f"{provider_upper}_KEY",
    ]

    for env_var in env_var_patterns:
        value = os.getenv(env_var)
        if value:
            return value

    return None


def require_database_url() -> str:
    """
    Get database URL from environment variable, raising error if not set.

    Returns:
        Database URL string

    Raises:
        ValueError: If GNOSARI_DATABASE_URL is not set

    Example:
        >>> database_url = require_database_url()
    """
    database_url = get_database_url()

    if not database_url:
        raise ValueError(
            "GNOSARI_DATABASE_URL environment variable is required. "
            "Set it to your PostgreSQL connection string, e.g., "
            "postgresql+asyncpg://user:pass@localhost/gnosari"
        )

    return database_url


def require_account_id() -> int:
    """
    Get account ID from environment variable, raising error if not set.

    Returns:
        Account ID as integer

    Raises:
        ValueError: If GNOSARI_ACCOUNT_ID is not set or invalid

    Example:
        >>> account_id = require_account_id()
    """
    account_id = get_account_id()

    if account_id is None:
        raise ValueError(
            "GNOSARI_ACCOUNT_ID environment variable is required. "
            "Set it to your account identifier (integer)."
        )

    return account_id


def get_all_gnosari_env_vars() -> dict:
    """
    Get all GNOSARI_* environment variables as a dictionary.

    Returns:
        Dictionary of environment variable names to values

    Example:
        >>> env_vars = get_all_gnosari_env_vars()
        >>> print(env_vars)
        {'GNOSARI_DATABASE_URL': '...', 'GNOSARI_ACCOUNT_ID': '1'}
    """
    return {
        key: value
        for key, value in os.environ.items()
        if key.startswith("GNOSARI_")
    }


__all__ = [
    "get_database_url",
    "get_account_id",
    "get_openai_api_key",
    "get_anthropic_api_key",
    "get_provider_api_key",
    "require_database_url",
    "require_account_id",
    "get_all_gnosari_env_vars",
]
