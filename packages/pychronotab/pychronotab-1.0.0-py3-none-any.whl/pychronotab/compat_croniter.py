"""
croniter API compatibility layer.

Provides a drop-in replacement for the abandoned croniter library.
All functionality is backed by pychronotab's CronExpression.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from .core import CronExpression
from .exceptions import CroniterBadDateError


class croniter:  # noqa: N801
    """
    croniter-compatible interface backed by CronExpression.

    This class provides full API compatibility with the original croniter
    library, allowing it to be used as a drop-in replacement.

    Example:
        >>> from datetime import datetime
        >>> from pychronotab import croniter
        >>>
        >>> it = croniter("*/5 * * * *", datetime(2024, 1, 1, 12, 0))
        >>> print(it.get_next(datetime))
        >>> print(it.get_next(datetime))
    """

    def __init__(
        self,
        expr_format: str,
        start_time: datetime | None = None,
        day_or: bool = True,
        max_years_between_matches: int | None = None,
        **kwargs: Any
    ):
        """
        Initialize croniter.

        Args:
            expr_format: Cron expression (5 or 6 fields)
            start_time: Starting datetime (default: now)
            day_or: If True, day_of_month and day_of_week are OR'd (standard behavior)
            max_years_between_matches: Not used (for API compatibility)
            **kwargs: Additional args for compatibility (ignored)
        """
        self._expr_format = expr_format
        self._day_or = day_or

        # Determine timezone from start_time
        tz: timezone | ZoneInfo | None = None
        if start_time is not None and start_time.tzinfo is not None:
            tz = start_time.tzinfo  # type: ignore[assignment]

        # Create underlying CronExpression
        self._cron_expr = CronExpression(expr_format, tz=tz)

        # Track current position
        self._start_time = start_time
        self._current: datetime | None = None
        self._initialized = False

    def get_next(self, ret_type: type = datetime) -> Any:
        """
        Get the next occurrence.

        Args:
            ret_type: Return type (datetime or float for timestamp)

        Returns:
            Next occurrence as datetime or float timestamp
        """
        if not self._initialized:
            # First call - use start_time or now
            base = self._start_time if self._start_time is not None else None
            self._current = self._cron_expr.next(base, inclusive=False)
            self._initialized = True
        else:
            # Get next after current
            self._current = self._cron_expr.next(self._current, inclusive=False)

        return self._convert_return_type(self._current, ret_type)

    def get_prev(self, ret_type: type = datetime) -> Any:
        """
        Get the previous occurrence.

        Args:
            ret_type: Return type (datetime or float for timestamp)

        Returns:
            Previous occurrence as datetime or float timestamp
        """
        if not self._initialized:
            # First call - use start_time or now
            base = self._start_time if self._start_time is not None else None
            self._current = self._cron_expr.prev(base, inclusive=False)
            self._initialized = True
        else:
            # Get previous before current
            self._current = self._cron_expr.prev(self._current, inclusive=False)

        return self._convert_return_type(self._current, ret_type)

    def get_current(self, ret_type: type = datetime) -> Any:
        """
        Get the current occurrence (last returned by get_next/get_prev).

        Args:
            ret_type: Return type (datetime or float for timestamp)

        Returns:
            Current occurrence as datetime or float timestamp

        Raises:
            CroniterBadDateError: If get_next/get_prev hasn't been called yet
        """
        if not self._initialized or self._current is None:
            raise CroniterBadDateError(
                "get_current() called before get_next() or get_prev()"
            )

        return self._convert_return_type(self._current, ret_type)

    def all_next(self, ret_type: type = datetime) -> Iterator[Any]:
        """
        Iterate over all future occurrences.

        Args:
            ret_type: Return type (datetime or float for timestamp)

        Yields:
            Future occurrences
        """
        while True:
            yield self.get_next(ret_type)

    def all_prev(self, ret_type: type = datetime) -> Iterator[Any]:
        """
        Iterate over all past occurrences.

        Args:
            ret_type: Return type (datetime or float for timestamp)

        Yields:
            Past occurrences
        """
        while True:
            yield self.get_prev(ret_type)

    def set_current(self, dt: datetime) -> None:
        """
        Set the current position.

        Args:
            dt: New current datetime
        """
        self._start_time = dt
        self._current = None
        self._initialized = False

    def get_schedule(self, ret_type: type = datetime) -> Any:
        """
        Alias for get_current() for compatibility.

        Args:
            ret_type: Return type

        Returns:
            Current occurrence
        """
        return self.get_current(ret_type)

    @staticmethod
    def _convert_return_type(dt: datetime, ret_type: type) -> Any:
        """Convert datetime to requested return type."""
        if ret_type is datetime:
            return dt
        elif ret_type is float:
            return dt.timestamp()
        elif ret_type is int:
            return int(dt.timestamp())
        else:
            raise TypeError(f"Unsupported return type: {ret_type}")

    @property
    def cur(self) -> float | None:
        """
        Current position as timestamp (for compatibility).

        Returns:
            Current timestamp or None
        """
        if self._current is None:
            return None
        return self._current.timestamp()

    def __iter__(self) -> Iterator[datetime]:
        """Iterate forward over occurrences."""
        return self.all_next(datetime)

    def __repr__(self) -> str:
        return f"croniter('{self._expr_format}', {self._current})"


# Alias for compatibility
Croniter = croniter
