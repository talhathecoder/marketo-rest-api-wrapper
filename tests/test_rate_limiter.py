"""Tests for the RateLimiter utility."""

import time
import pytest
from marketo_api.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    def test_initial_state(self):
        limiter = RateLimiter(calls_per_20s=10, daily_max=100)
        assert limiter.daily_calls_remaining == 100
        assert limiter.window_calls_remaining == 10

    def test_records_calls(self):
        limiter = RateLimiter(calls_per_20s=10, daily_max=100)
        limiter.wait_if_needed()
        assert limiter.daily_calls_remaining == 99
        assert limiter.window_calls_remaining == 9

    def test_multiple_calls(self):
        limiter = RateLimiter(calls_per_20s=10, daily_max=100)
        for _ in range(5):
            limiter.wait_if_needed()
        assert limiter.daily_calls_remaining == 95
        assert limiter.window_calls_remaining == 5

    def test_daily_limit_exhaustion(self):
        limiter = RateLimiter(calls_per_20s=1000, daily_max=3)
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        with pytest.raises(RuntimeError, match="Daily API quota exhausted"):
            limiter.wait_if_needed()

    def test_thread_safety(self):
        """Basic check that the limiter doesn't crash under threading."""
        import threading

        limiter = RateLimiter(calls_per_20s=100, daily_max=1000)
        errors = []

        def make_calls():
            try:
                for _ in range(10):
                    limiter.wait_if_needed()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=make_calls) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert limiter.daily_calls_remaining == 950
