"""Tests for the exceptions module."""

import pytest
from marketo_api.exceptions import (
    MarketoAPIError,
    MarketoAuthError,
    MarketoNotFoundError,
    MarketoRateLimitError,
    MarketoValidationError,
    raise_for_error,
)


class TestRaiseForError:
    """Tests for the raise_for_error function."""

    def test_success_response_no_raise(self):
        data = {"success": True, "result": [{"id": 1}]}
        raise_for_error(data)  # Should not raise

    def test_auth_error_601(self):
        data = {
            "success": False,
            "errors": [{"code": "601", "message": "Access token invalid"}],
        }
        with pytest.raises(MarketoAuthError) as exc_info:
            raise_for_error(data)
        assert exc_info.value.error_code == "601"

    def test_auth_error_602(self):
        data = {
            "success": False,
            "errors": [{"code": "602", "message": "Access token expired"}],
        }
        with pytest.raises(MarketoAuthError):
            raise_for_error(data)

    def test_rate_limit_error_606(self):
        data = {
            "success": False,
            "errors": [{"code": "606", "message": "Max rate limit exceeded"}],
        }
        with pytest.raises(MarketoRateLimitError) as exc_info:
            raise_for_error(data)
        assert exc_info.value.retry_after == 20

    def test_rate_limit_error_607(self):
        data = {
            "success": False,
            "errors": [{"code": "607", "message": "Daily quota reached"}],
        }
        with pytest.raises(MarketoRateLimitError) as exc_info:
            raise_for_error(data)
        assert exc_info.value.retry_after == 86400

    def test_not_found_error(self):
        data = {
            "success": False,
            "errors": [{"code": "610", "message": "Resource not found"}],
        }
        with pytest.raises(MarketoNotFoundError):
            raise_for_error(data)

    def test_validation_error(self):
        data = {
            "success": False,
            "errors": [{"code": "611", "message": "Missing required field"}],
        }
        with pytest.raises(MarketoValidationError):
            raise_for_error(data)

    def test_unknown_error_code(self):
        data = {
            "success": False,
            "errors": [{"code": "999", "message": "Something weird"}],
        }
        with pytest.raises(MarketoAPIError):
            raise_for_error(data)

    def test_no_errors_array(self):
        data = {"success": False}
        with pytest.raises(MarketoAPIError, match="Unknown error"):
            raise_for_error(data)

    def test_request_id_preserved(self):
        data = {
            "success": False,
            "errors": [{"code": "601", "message": "Invalid"}],
            "requestId": "abc123",
        }
        with pytest.raises(MarketoAuthError) as exc_info:
            raise_for_error(data, request_id="abc123")
        assert exc_info.value.request_id == "abc123"
