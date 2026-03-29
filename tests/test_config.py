"""Tests for the MarketoConfig class."""

import os
import pytest
from marketo_api.config import MarketoConfig


class TestMarketoConfig:
    """Tests for MarketoConfig."""

    def test_basic_construction(self):
        config = MarketoConfig(
            munchkin_id="123-ABC-456",
            client_id="test-id",
            client_secret="test-secret",
        )
        assert config.munchkin_id == "123-ABC-456"
        assert config.client_id == "test-id"
        assert config.client_secret == "test-secret"

    def test_base_url(self):
        config = MarketoConfig(munchkin_id="123-ABC-456")
        assert config.base_url == "https://123-ABC-456.mktorest.com"

    def test_identity_url(self):
        config = MarketoConfig(munchkin_id="123-ABC-456")
        assert config.identity_url == "https://123-ABC-456.mktorest.com/identity"

    def test_defaults(self):
        config = MarketoConfig()
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 2.0
        assert config.timeout == 30
        assert config.rate_limit_calls_per_20s == 80
        assert config.rate_limit_daily_max == 45000
        assert config.log_level == "INFO"
        assert config.token_refresh_buffer == 60

    def test_validate_missing_munchkin_id(self):
        config = MarketoConfig(client_id="id", client_secret="secret")
        with pytest.raises(ValueError, match="munchkin_id"):
            config.validate()

    def test_validate_missing_client_id(self):
        config = MarketoConfig(munchkin_id="123-ABC-456", client_secret="secret")
        with pytest.raises(ValueError, match="client_id"):
            config.validate()

    def test_validate_missing_client_secret(self):
        config = MarketoConfig(munchkin_id="123-ABC-456", client_id="id")
        with pytest.raises(ValueError, match="client_secret"):
            config.validate()

    def test_validate_success(self):
        config = MarketoConfig(
            munchkin_id="123-ABC-456",
            client_id="id",
            client_secret="secret",
        )
        config.validate()  # Should not raise

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("MARKETO_MUNCHKIN_ID", "ENV-123-456")
        monkeypatch.setenv("MARKETO_CLIENT_ID", "env-client-id")
        monkeypatch.setenv("MARKETO_CLIENT_SECRET", "env-secret")

        config = MarketoConfig.from_env()
        assert config.munchkin_id == "ENV-123-456"
        assert config.client_id == "env-client-id"
        assert config.client_secret == "env-secret"

    def test_from_env_missing_vars(self, monkeypatch):
        monkeypatch.delenv("MARKETO_MUNCHKIN_ID", raising=False)
        monkeypatch.delenv("MARKETO_CLIENT_ID", raising=False)
        monkeypatch.delenv("MARKETO_CLIENT_SECRET", raising=False)

        with pytest.raises(ValueError, match="Missing required"):
            MarketoConfig.from_env()
