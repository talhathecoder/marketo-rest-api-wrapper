"""Rate limiter implementing Marketo's dual rate limit tiers.

- Short-term: 100 calls per 20-second sliding window
- Daily: 50,000 calls per calendar day

Uses a sliding window approach for short-term limiting and a simple
counter with daily reset for the daily quota.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Optional

logger = logging.getLogger("marketo_api.rate_limiter")


class RateLimiter:
    """Thread-safe dual-tier rate limiter for Marketo API calls.

    Args:
        calls_per_20s: Maximum calls allowed in a 20-second window.
        daily_max: Maximum calls allowed per day.
        daily_warning_threshold: Fraction of daily_max that triggers a warning.
    """

    WINDOW_SIZE = 20.0  # seconds

    def __init__(
        self,
        calls_per_20s: int = 80,
        daily_max: int = 45000,
        daily_warning_threshold: float = 0.9,
    ) -> None:
        self.calls_per_20s = calls_per_20s
        self.daily_max = daily_max
        self.daily_warning_threshold = daily_warning_threshold

        # Sliding window for short-term rate tracking
        self._window: deque[float] = deque()
        self._lock = threading.Lock()

        # Daily counter
        self._daily_count: int = 0
        self._daily_reset_time: float = self._next_midnight()

        self._warned_daily = False

    def wait_if_needed(self) -> None:
        """Block the calling thread if a rate limit would be exceeded.

        Call this before every API request. It will sleep if the short-term
        window is full, and raise an error if the daily limit is reached.

        Raises:
            RuntimeError: If the daily quota has been exhausted.
        """
        with self._lock:
            self._check_daily_reset()
            self._enforce_daily_limit()
            self._enforce_window_limit()
            self._record_call()

    def _enforce_window_limit(self) -> None:
        """Sleep if the 20-second window is full."""
        now = time.time()

        # Purge entries outside the window
        while self._window and self._window[0] < now - self.WINDOW_SIZE:
            self._window.popleft()

        if len(self._window) >= self.calls_per_20s:
            # Calculate how long to sleep until the oldest entry exits the window
            sleep_time = self._window[0] + self.WINDOW_SIZE - now + 0.1
            if sleep_time > 0:
                logger.info(
                    "Short-term rate limit reached (%d/%d in window). "
                    "Sleeping %.1fs...",
                    len(self._window),
                    self.calls_per_20s,
                    sleep_time,
                )
                time.sleep(sleep_time)

                # Purge again after sleeping
                now = time.time()
                while self._window and self._window[0] < now - self.WINDOW_SIZE:
                    self._window.popleft()

    def _enforce_daily_limit(self) -> None:
        """Check and enforce the daily quota."""
        if self._daily_count >= self.daily_max:
            seconds_until_reset = max(0, self._daily_reset_time - time.time())
            raise RuntimeError(
                f"Daily API quota exhausted ({self.daily_max} calls). "
                f"Resets in {seconds_until_reset:.0f}s."
            )

        # Warn if approaching the limit
        threshold = int(self.daily_max * self.daily_warning_threshold)
        if self._daily_count >= threshold and not self._warned_daily:
            logger.warning(
                "Approaching daily API limit: %d / %d calls used (%.0f%%)",
                self._daily_count,
                self.daily_max,
                (self._daily_count / self.daily_max) * 100,
            )
            self._warned_daily = True

    def _record_call(self) -> None:
        """Record that an API call is being made."""
        self._window.append(time.time())
        self._daily_count += 1

    def _check_daily_reset(self) -> None:
        """Reset the daily counter if a new day has started."""
        if time.time() >= self._daily_reset_time:
            logger.info("Daily rate limit counter reset.")
            self._daily_count = 0
            self._daily_reset_time = self._next_midnight()
            self._warned_daily = False

    @staticmethod
    def _next_midnight() -> float:
        """Calculate the Unix timestamp of the next midnight (UTC)."""
        import datetime

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(
            days=1
        )
        return tomorrow.timestamp()

    @property
    def daily_calls_remaining(self) -> int:
        """Return the number of API calls remaining for the day."""
        with self._lock:
            self._check_daily_reset()
            return max(0, self.daily_max - self._daily_count)

    @property
    def window_calls_remaining(self) -> int:
        """Return the number of API calls remaining in the current 20s window."""
        with self._lock:
            now = time.time()
            while self._window and self._window[0] < now - self.WINDOW_SIZE:
                self._window.popleft()
            return max(0, self.calls_per_20s - len(self._window))
