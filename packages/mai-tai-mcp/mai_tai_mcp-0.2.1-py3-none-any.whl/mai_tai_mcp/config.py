"""Configuration management for mai-tai MCP server (v3 - workspace edition).

v3 Config Model:
- Three required environment variables: MAI_TAI_API_URL, MAI_TAI_API_KEY, MAI_TAI_WORKSPACE_ID
- No legacy fallbacks or alternate variable names
- Fail fast with a clear error if any are missing
- Users can set these via any method (env.sh, .env, .env.mai-tai, editor config, etc.)
"""

import os
from typing import List

from pydantic import BaseModel, Field

from mai_tai_mcp import __version__


class ConfigurationError(Exception):
    """Raised when Mai-Tai MCP configuration is invalid or incomplete."""

    pass


class MaiTaiConfig(BaseModel):
    """Mai-tai connection configuration (v3 - workspace edition).

    All three fields are required. There are no defaults or fallbacks.
    """

    api_url: str = Field(
        ..., description="Mai-tai backend URL (e.g., https://mai-tai-backend.example.com)"
    )
    api_key: str = Field(
        ..., description="Mai-tai API key (workspace-scoped, starts with mt_)"
    )
    workspace_id: str = Field(
        ..., description="Mai-tai workspace ID (from workspace settings)"
    )

    @classmethod
    def from_env(cls) -> "MaiTaiConfig":
        """Load configuration from environment variables.

        Required environment variables:
        - MAI_TAI_API_URL: Backend URL
        - MAI_TAI_API_KEY: Workspace-scoped API key
        - MAI_TAI_WORKSPACE_ID: Workspace ID for this repo

        Raises:
            ConfigurationError: If any required variable is missing or empty.
        """
        required_vars = ["MAI_TAI_API_URL", "MAI_TAI_API_KEY", "MAI_TAI_WORKSPACE_ID"]
        missing: List[str] = []

        api_url = os.getenv("MAI_TAI_API_URL", "").strip()
        api_key = os.getenv("MAI_TAI_API_KEY", "").strip()
        workspace_id = os.getenv("MAI_TAI_WORKSPACE_ID", "").strip()

        if not api_url:
            missing.append("MAI_TAI_API_URL")
        if not api_key:
            missing.append("MAI_TAI_API_KEY")
        if not workspace_id:
            missing.append("MAI_TAI_WORKSPACE_ID")

        if missing:
            raise ConfigurationError(_build_config_error_message(missing))

        return cls(api_url=api_url, api_key=api_key, workspace_id=workspace_id)


def _build_config_error_message(missing_vars: List[str]) -> str:
    """Build a clear, actionable error message for missing config."""
    vars_list = ", ".join(missing_vars)
    return (
        f"mai-tai-mcp v{__version__}\n"
        f"\n"
        f"Configuration error: missing required environment variable(s): {vars_list}\n"
        f"\n"
        f"Required variables:\n"
        f"  MAI_TAI_API_URL       - Backend URL (e.g., https://mai-tai-backend.example.com)\n"
        f"  MAI_TAI_API_KEY       - Your workspace-scoped API key\n"
        f"  MAI_TAI_WORKSPACE_ID  - Workspace ID (from workspace settings)\n"
        f"\n"
        f"You can get these values from the Mai-Tai workspace settings page.\n"
        f"Add them to your environment (env.sh, .env, editor config, etc.) before starting mai-tai-mcp."
    )


def get_config() -> MaiTaiConfig:
    """Get mai-tai configuration from environment.

    This is the main entry point for loading config. It reads from environment
    variables only - no file-specific logic. Users are free to populate their
    environment however they prefer.

    Raises:
        ConfigurationError: If required variables are missing.
    """
    return MaiTaiConfig.from_env()

