"""Configuration for the Marketo API client."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MarketoConfig:
    """Configuration object for MarketoClient.

    Can be constructed directly or loaded from environment variables
    using MarketoConfig.from_env().

    Attributes:
        munchkin_id: Your Marketo Munchkin Account ID (e.g., "123-ABC-456").
        client_id: OAuth 2.0 Client ID from your Marketo LaunchPoint service.
        client_secret: OAuth 2.0 Client Secret from your LaunchPoint service.
        max_retries: Maximum number of retries for transient errors.
        retry_backoff_factor: Multiplier for exponential backoff between retries.
        timeout: Request timeout in seconds.
        rate_limit_calls_per_20s: Max API calls per 20-second window (Marketo hard limit: 100).
        rate_limit_daily_max: Max API calls per day (Marketo hard limit: 50,000).
        daily_warning_threshold: Percentage of daily limit that triggers a warning log.
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR).
        token_refresh_buffer: Seconds before token expiry to trigger a refresh.
    """

    munchkin_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    timeout: int = 30
    rate_limit_calls_per_20s: int = 80
    rate_limit_daily_max: int = 45000
    daily_warning_threshold: float = 0.9
    log_level: str = "INFO"
    token_refresh_buffer: int = 60

    @property
    def base_url(self) -> str:
        """Construct the REST API base URL from the Munchkin ID."""
        return f"https://{self.munchkin_id}.mktorest.com"

    @property
    def identity_url(self) -> str:
        """Construct the identity/authentication URL from the Munchkin ID."""
        return f"https://{self.munchkin_id}.mktorest.com/identity"

    @classmethod
    def from_env(cls) -> MarketoConfig:
        """Create a config instance from environment variables.

        Required env vars:
            MARKETO_MUNCHKIN_ID
            MARKETO_CLIENT_ID
            MARKETO_CLIENT_SECRET

        Optional env vars:
            MARKETO_MAX_RETRIES (default: 3)
            MARKETO_TIMEOUT (default: 30)
            MARKETO_LOG_LEVEL (default: INFO)
        """
        munchkin_id = os.environ.get("MARKETO_MUNCHKIN_ID", "")
        client_id = os.environ.get("MARKETO_CLIENT_ID", "")
        client_secret = os.environ.get("MARKETO_CLIENT_SECRET", "")

        if not all([munchkin_id, client_id, client_secret]):
            missing = []
            if not munchkin_id:
                missing.append("MARKETO_MUNCHKIN_ID")
            if not client_id:
                missing.append("MARKETO_CLIENT_ID")
            if not client_secret:
                missing.append("MARKETO_CLIENT_SECRET")
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            munchkin_id=munchkin_id,
            client_id=client_id,
            client_secret=client_secret,
            max_retries=int(os.environ.get("MARKETO_MAX_RETRIES", "3")),
            timeout=int(os.environ.get("MARKETO_TIMEOUT", "30")),
            log_level=os.environ.get("MARKETO_LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """Validate that all required fields are set."""
        if not self.munchkin_id:
            raise ValueError("munchkin_id is required")
        if not self.client_id:
            raise ValueError("client_id is required")
        if not self.client_secret:
            raise ValueError("client_secret is required")
