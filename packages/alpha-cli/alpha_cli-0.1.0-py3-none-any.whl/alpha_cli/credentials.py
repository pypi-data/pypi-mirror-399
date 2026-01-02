"""Secure credential storage using OS keyring."""

import json
import os
from pathlib import Path

import keyring

from alpha_cli.types import AlphaCredentials, KalshiCredentials

SERVICE_NAME = "alpha-cli"

# Environment variable names for CI/headless environments
ENV_ALPHA_API_KEY = "ALPHA_API_KEY"
ENV_KALSHI_API_KEY = "KALSHI_API_KEY"
ENV_KALSHI_PRIVATE_KEY_PATH = "KALSHI_PRIVATE_KEY_PATH"


def store_alpha_credentials(creds: AlphaCredentials) -> None:
    """
    Store Alpha CLI credentials in OS keyring.

    Args:
        creds: Alpha credentials to store
    """
    keyring.set_password(
        SERVICE_NAME,
        "alpha_credentials",
        json.dumps(
            {
                "api_key": creds.api_key,
                "user_email": creds.user_email,
            }
        ),
    )


def get_alpha_credentials() -> AlphaCredentials | None:
    """
    Retrieve Alpha CLI credentials.

    Checks in order:
    1. Environment variables
    2. OS keyring

    Returns:
        AlphaCredentials if found, None otherwise
    """
    # Check environment first (for CI/automation)
    env_key = os.environ.get(ENV_ALPHA_API_KEY)
    if env_key:
        return AlphaCredentials(api_key=env_key)

    # Check keyring
    data = keyring.get_password(SERVICE_NAME, "alpha_credentials")
    if not data:
        return None

    try:
        parsed = json.loads(data)
        return AlphaCredentials(
            api_key=parsed["api_key"],
            user_email=parsed.get("user_email"),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def delete_alpha_credentials() -> None:
    """Remove Alpha CLI credentials from OS keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "alpha_credentials")
    except keyring.errors.PasswordDeleteError:
        pass  # Already deleted


def store_kalshi_credentials(creds: KalshiCredentials) -> None:
    """
    Store Kalshi credentials in OS keyring.

    Args:
        creds: Kalshi credentials to store
    """
    keyring.set_password(
        SERVICE_NAME,
        "kalshi_credentials",
        json.dumps(
            {
                "api_key": creds.api_key,
                "private_key_path": creds.private_key_path,
            }
        ),
    )


def get_kalshi_credentials() -> KalshiCredentials | None:
    """
    Retrieve Kalshi credentials.

    Checks in order:
    1. Environment variables
    2. OS keyring

    Returns:
        KalshiCredentials if found, None otherwise
    """
    # Check environment first
    env_key = os.environ.get(ENV_KALSHI_API_KEY)
    if env_key:
        return KalshiCredentials(
            api_key=env_key,
            private_key_path=os.environ.get(ENV_KALSHI_PRIVATE_KEY_PATH),
        )

    # Check keyring
    data = keyring.get_password(SERVICE_NAME, "kalshi_credentials")
    if not data:
        return None

    try:
        parsed = json.loads(data)
        return KalshiCredentials(
            api_key=parsed["api_key"],
            private_key_path=parsed.get("private_key_path"),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def delete_kalshi_credentials() -> None:
    """Remove Kalshi credentials from OS keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "kalshi_credentials")
    except keyring.errors.PasswordDeleteError:
        pass  # Already deleted


def get_config_dir() -> Path:
    """Get the Alpha CLI config directory."""
    config_dir = Path.home() / ".alpha"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the config file."""
    return get_config_dir() / "config.toml"


def mask_api_key(key: str) -> str:
    """
    Mask an API key for display.

    Example: alpha_live_abc123xyz → alpha_live_abc1...xyz
    """
    if len(key) <= 16:
        return key[:4] + "..." + key[-4:]
    return key[:16] + "..." + key[-4:]
