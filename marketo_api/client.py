"""Main client class — the primary entry point for the Marketo API wrapper.

Usage:
    from marketo_api import MarketoClient

    client = MarketoClient(
        munchkin_id="123-ABC-456",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )

    lead = client.leads.get_by_email("john@example.com")
"""

from __future__ import annotations

import logging
from typing import Optional

from marketo_api.auth import MarketoAuth
from marketo_api.config import MarketoConfig
from marketo_api.resources.activities import ActivitiesResource
from marketo_api.resources.bulk_extract import BulkExtractResource
from marketo_api.resources.bulk_import import BulkImportResource
from marketo_api.resources.campaigns import CampaignsResource
from marketo_api.resources.custom_objects import CustomObjectsResource
from marketo_api.resources.folders import FoldersResource
from marketo_api.resources.leads import LeadsResource
from marketo_api.resources.lists import ListsResource
from marketo_api.resources.programs import ProgramsResource
from marketo_api.resources.tokens import TokensResource
from marketo_api.transport import HttpTransport
from marketo_api.utils.rate_limiter import RateLimiter

logger = logging.getLogger("marketo_api")


class MarketoClient:
    """The main Marketo REST API client.

    Provides access to all API resources through a clean, resource-based
    interface. Handles authentication, rate limiting, and retry logic
    transparently.

    Args:
        munchkin_id: Your Marketo Munchkin Account ID.
        client_id: OAuth 2.0 Client ID.
        client_secret: OAuth 2.0 Client Secret.
        config: Optional MarketoConfig for advanced configuration.
            If provided, munchkin_id/client_id/client_secret are ignored.

    Example:
        >>> client = MarketoClient(
        ...     munchkin_id="123-ABC-456",
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret"
        ... )
        >>> lead = client.leads.get_by_email("test@example.com")
    """

    def __init__(
        self,
        munchkin_id: str = "",
        client_id: str = "",
        client_secret: str = "",
        config: MarketoConfig | None = None,
    ) -> None:
        if config:
            self._config = config
        else:
            self._config = MarketoConfig(
                munchkin_id=munchkin_id,
                client_id=client_id,
                client_secret=client_secret,
            )

        self._config.validate()
        self._setup_logging()

        # Core infrastructure
        self._auth = MarketoAuth(self._config)
        self._rate_limiter = RateLimiter(
            calls_per_20s=self._config.rate_limit_calls_per_20s,
            daily_max=self._config.rate_limit_daily_max,
            daily_warning_threshold=self._config.daily_warning_threshold,
        )
        self._transport = HttpTransport(self._config, self._auth, self._rate_limiter)

        # API Resources
        self.leads = LeadsResource(self._transport)
        self.activities = ActivitiesResource(self._transport)
        self.campaigns = CampaignsResource(self._transport)
        self.programs = ProgramsResource(self._transport)
        self.lists = ListsResource(self._transport)
        self.folders = FoldersResource(self._transport)
        self.tokens = TokensResource(self._transport)
        self.custom_objects = CustomObjectsResource(self._transport)
        self.bulk_import = BulkImportResource(self._transport)
        self.bulk_extract = BulkExtractResource(self._transport)

    @classmethod
    def from_env(cls) -> MarketoClient:
        """Create a client from environment variables.

        Required env vars:
            MARKETO_MUNCHKIN_ID
            MARKETO_CLIENT_ID
            MARKETO_CLIENT_SECRET

        Returns:
            A configured MarketoClient instance.
        """
        config = MarketoConfig.from_env()
        return cls(config=config)

    def _setup_logging(self) -> None:
        """Configure logging based on the config log level."""
        log_level = getattr(logging, self._config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger.setLevel(log_level)

    @property
    def config(self) -> MarketoConfig:
        """Access the client configuration."""
        return self._config

    @property
    def daily_calls_remaining(self) -> int:
        """Check how many API calls remain for the day."""
        return self._rate_limiter.daily_calls_remaining

    @property
    def window_calls_remaining(self) -> int:
        """Check how many API calls remain in the current 20s window."""
        return self._rate_limiter.window_calls_remaining

    def __repr__(self) -> str:
        return f"MarketoClient(munchkin_id='{self._config.munchkin_id}')"
