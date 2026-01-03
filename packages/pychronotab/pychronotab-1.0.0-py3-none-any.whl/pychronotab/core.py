"""
Core CronExpression implementation with timezone-aware iteration.

Supports both 5-field and 6-field (with seconds) cron expressions.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .exceptions import CroniterBadDateError
from .fields import CronField, parse_cron_expression


class CronExpression:
    """
    Modern cron expression iterator with timezone support.

    Supports:
    - 5-field cron: minute hour day month day_of_week
    - 6-field cron: second minute hour day month day_of_week
    - Timezone-aware datetime handling
    - DST-aware transitions

    Example:
        >>> from datetime import datetime, timezone
        >>> expr = CronExpression("*/5 * * * *", tz=timezone.utc)
        >>> next_run = expr.next(datetime.now(timezone.utc))
    """

    def __init__(self, expr: str, tz: timezone | ZoneInfo | None = None):
        """
        Initialize a cron expression.

        Args:
            expr: Cron expression string (5 or 6 fields)
            tz: Timezone for interpretation (default: UTC)
        """
        self.expr = expr
        self.tz = tz or UTC

        # Parse expression into field objects
        fields = parse_cron_expression(expr)
        self.second_field: CronField = fields[0]
        self.minute_field: CronField = fields[1]
        self.hour_field: CronField = fields[2]
        self.day_field: CronField = fields[3]
        self.month_field: CronField = fields[4]
        self.dow_field: CronField = fields[5]

    def _normalize_datetime(self, dt: datetime | None) -> datetime:
        """Normalize datetime to be timezone-aware in self.tz."""
        if dt is None:
            dt = datetime.now(self.tz)

        if dt.tzinfo is None:
            # Naive datetime - attach our timezone
            dt = dt.replace(tzinfo=self.tz)
        elif dt.tzinfo != self.tz:
            # Different timezone - convert
            dt = dt.astimezone(self.tz)

        return dt

    def _matches(self, dt: datetime) -> bool:
        """Check if datetime matches all cron fields."""
        # Convert Python weekday (Mon=0, Sun=6) to cron weekday (Sun=0, Mon=1)
        cron_dow = (dt.weekday() + 1) % 7
        return (
            self.second_field.contains(dt.second) and
            self.minute_field.contains(dt.minute) and
            self.hour_field.contains(dt.hour) and
            self.day_field.contains(dt.day) and
            self.month_field.contains(dt.month) and
            self.dow_field.contains(cron_dow)
        )

    def next(self, base: datetime | None = None, *, inclusive: bool = False) -> datetime:
        """
        Get the next occurrence after (or at, if inclusive) base.

        Args:
            base: Starting datetime (default: now in self.tz)
            inclusive: If True and base matches, return base

        Returns:
            Next matching datetime
        """
        current = self._normalize_datetime(base)

        # If inclusive and current matches, return it
        if inclusive and self._matches(current):
            return current

        # Start search from next second
        current = current.replace(microsecond=0) + timedelta(seconds=1)

        # Limit iterations to prevent infinite loops
        max_iterations = 366 * 24 * 60 * 60  # 1 year in seconds
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Check if current datetime matches
            if self._matches(current):
                return current

            # Advance to next candidate
            current = self._advance_to_next_candidate(current)

        raise CroniterBadDateError("Could not find next occurrence within 1 year")

    def _advance_to_next_candidate(self, dt: datetime) -> datetime:
        """Advance datetime to next potential match, skipping impossible times."""

        # Try to advance second
        next_sec = self.second_field.next_value(dt.second)
        if next_sec is not None:
            return dt.replace(second=next_sec, microsecond=0)

        # Wrap second, advance minute
        dt = dt.replace(second=self.second_field.min(), microsecond=0)
        next_min = self.minute_field.next_value(dt.minute)
        if next_min is not None:
            return dt.replace(minute=next_min)

        # Wrap minute, advance hour
        dt = dt.replace(minute=self.minute_field.min())
        next_hour = self.hour_field.next_value(dt.hour)
        if next_hour is not None:
            return dt.replace(hour=next_hour)

        # Wrap hour, advance day
        dt = dt.replace(hour=self.hour_field.min())
        dt = dt + timedelta(days=1)

        # Skip months/days that don't match
        while not self.month_field.contains(dt.month):
            # Jump to first day of next month
            if dt.month == 12:
                dt = dt.replace(year=dt.year + 1, month=1, day=1)
            else:
                dt = dt.replace(month=dt.month + 1, day=1)

        return dt

    def prev(self, base: datetime | None = None, *, inclusive: bool = False) -> datetime:
        """
        Get the previous occurrence before (or at, if inclusive) base.

        Args:
            base: Starting datetime (default: now in self.tz)
            inclusive: If True and base matches, return base

        Returns:
            Previous matching datetime
        """
        current = self._normalize_datetime(base)

        # If inclusive and current matches, return it
        if inclusive and self._matches(current):
            return current

        # Start search from previous second
        current = current.replace(microsecond=0) - timedelta(seconds=1)

        # Limit iterations
        max_iterations = 366 * 24 * 60 * 60
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            if self._matches(current):
                return current

            current = self._advance_to_prev_candidate(current)

        raise CroniterBadDateError("Could not find previous occurrence within 1 year")

    def _advance_to_prev_candidate(self, dt: datetime) -> datetime:
        """Advance datetime backward to previous potential match."""

        # Try to go back one second
        prev_sec = self.second_field.prev_value(dt.second)
        if prev_sec is not None:
            return dt.replace(second=prev_sec, microsecond=0)

        # Wrap second, go back minute
        dt = dt.replace(second=self.second_field.max(), microsecond=0)
        prev_min = self.minute_field.prev_value(dt.minute)
        if prev_min is not None:
            return dt.replace(minute=prev_min)

        # Wrap minute, go back hour
        dt = dt.replace(minute=self.minute_field.max())
        prev_hour = self.hour_field.prev_value(dt.hour)
        if prev_hour is not None:
            return dt.replace(hour=prev_hour)

        # Wrap hour, go back day
        dt = dt.replace(hour=self.hour_field.max())
        dt = dt - timedelta(days=1)

        # Skip months that don't match
        while not self.month_field.contains(dt.month):
            # Jump to last day of previous month
            dt = dt.replace(day=1) - timedelta(days=1)

        return dt

    def iter(
        self,
        start: datetime | None = None,
        *,
        direction: str = "forward",
        inclusive: bool = False
    ) -> Iterator[datetime]:
        """
        Iterate over occurrences.

        Args:
            start: Starting datetime (default: now)
            direction: "forward" or "backward"
            inclusive: Include start if it matches

        Yields:
            Matching datetimes
        """
        current = self._normalize_datetime(start)

        if direction == "forward":
            while True:
                current = self.next(current, inclusive=inclusive)
                inclusive = False  # Only first iteration can be inclusive
                yield current
        else:
            while True:
                current = self.prev(current, inclusive=inclusive)
                inclusive = False
                yield current

    def __repr__(self) -> str:
        return f"CronExpression('{self.expr}', tz={self.tz})"
