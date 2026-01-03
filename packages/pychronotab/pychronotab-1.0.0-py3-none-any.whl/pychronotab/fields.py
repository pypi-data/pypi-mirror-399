"""
Cron field parsing and value iteration.

Each field (second, minute, hour, day, month, day_of_week) is parsed
into a sorted list of allowed values, enabling efficient next/prev lookups.
"""

from __future__ import annotations

from .exceptions import CroniterBadCronError

# Month and day name aliases
MONTH_NAMES = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

DAY_NAMES = {
    'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6
}


class CronField:
    """
    Represents a single cron field (second, minute, hour, etc.).

    Parses cron syntax and provides next/prev value lookups.
    """

    def __init__(
        self,
        field_str: str,
        min_value: int,
        max_value: int,
        aliases: dict[str, int] | None = None
    ):
        self.field_str = field_str
        self.min_value = min_value
        self.max_value = max_value
        self.aliases = aliases or {}
        self.values = self._parse(field_str)

    def _parse(self, field_str: str) -> list[int]:
        """Parse cron field string into sorted list of allowed values."""
        if not field_str or not field_str.strip():
            raise CroniterBadCronError(f"Empty field: '{field_str}'")

        field_str = field_str.strip().upper()
        values = set()

        # Split by comma for lists
        for part in field_str.split(','):
            part = part.strip()
            if not part:
                continue

            # Handle step values (*/5 or 1-10/2)
            if '/' in part:
                range_part, step_part = part.split('/', 1)
                try:
                    step = int(step_part)
                    if step <= 0:
                        raise CroniterBadCronError(f"Step must be positive: {part}")
                except ValueError as e:
                    raise CroniterBadCronError(f"Invalid step value: {part}") from e

                # Determine range
                if range_part == '*':
                    start, end = self.min_value, self.max_value
                elif '-' in range_part:
                    start_str, end_str = range_part.split('-', 1)
                    start = self._parse_value(start_str)
                    end = self._parse_value(end_str)
                else:
                    start = self._parse_value(range_part)
                    end = self.max_value

                # Add stepped values
                for val in range(start, end + 1, step):
                    if self.min_value <= val <= self.max_value:
                        values.add(val)

            # Handle ranges (1-5)
            elif '-' in part:
                start_str, end_str = part.split('-', 1)
                start = self._parse_value(start_str)
                end = self._parse_value(end_str)

                if start > end:
                    raise CroniterBadCronError(f"Invalid range (start > end): {part}")

                for val in range(start, end + 1):
                    if self.min_value <= val <= self.max_value:
                        values.add(val)

            # Handle wildcard
            elif part == '*':
                for val in range(self.min_value, self.max_value + 1):
                    values.add(val)

            # Handle single value
            else:
                val = self._parse_value(part)
                if self.min_value <= val <= self.max_value:
                    values.add(val)
                else:
                    raise CroniterBadCronError(
                        f"Value {val} out of range [{self.min_value}, {self.max_value}]"
                    )

        if not values:
            raise CroniterBadCronError(f"No valid values in field: '{field_str}'")

        return sorted(values)

    def _parse_value(self, value_str: str) -> int:
        """Parse a single value, handling aliases."""
        value_str = value_str.strip().upper()

        # Check aliases (month/day names)
        if value_str in self.aliases:
            return self.aliases[value_str]

        # Parse as integer
        try:
            return int(value_str)
        except ValueError as e:
            raise CroniterBadCronError(f"Invalid value: '{value_str}'") from e

    def next_value(self, current: int) -> int | None:
        """
        Return the next allowed value strictly greater than current.
        Returns None if we need to wrap (no value > current in this field).
        """
        for val in self.values:
            if val > current:
                return val
        return None

    def prev_value(self, current: int) -> int | None:
        """
        Return the previous allowed value strictly less than current.
        Returns None if we need to wrap (no value < current in this field).
        """
        for val in reversed(self.values):
            if val < current:
                return val
        return None

    def min(self) -> int:
        """Return the minimum allowed value."""
        return self.values[0]

    def max(self) -> int:
        """Return the maximum allowed value."""
        return self.values[-1]

    def contains(self, value: int) -> bool:
        """Check if value is allowed by this field."""
        return value in self.values

    def __repr__(self) -> str:
        return f"CronField('{self.field_str}', values={self.values})"


def parse_cron_expression(expr: str) -> tuple[CronField, ...]:
    """
    Parse a cron expression into field objects.

    Supports:
    - 5-field: minute hour day month day_of_week
    - 6-field: second minute hour day month day_of_week

    Returns tuple of (second, minute, hour, day, month, day_of_week).
    For 5-field cron, second will be a field matching only 0.
    """
    parts = expr.strip().split()

    if len(parts) == 5:
        # Standard 5-field cron (no seconds)
        minute, hour, day, month, dow = parts
        second = '0'  # Default to 0 seconds
    elif len(parts) == 6:
        # 6-field cron with seconds
        second, minute, hour, day, month, dow = parts
    else:
        raise CroniterBadCronError(
            f"Invalid cron expression (expected 5 or 6 fields, got {len(parts)}): '{expr}'"
        )

    # Parse each field with appropriate bounds and aliases
    second_field = CronField(second, 0, 59)
    minute_field = CronField(minute, 0, 59)
    hour_field = CronField(hour, 0, 23)
    day_field = CronField(day, 1, 31)
    month_field = CronField(month, 1, 12, MONTH_NAMES)
    dow_field = CronField(dow, 0, 6, DAY_NAMES)

    return (second_field, minute_field, hour_field, day_field, month_field, dow_field)
