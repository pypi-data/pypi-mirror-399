"""
Exception classes for pychronotab.
Maintains croniter API compatibility.
"""


class CroniterError(Exception):
    """Base exception for all pychronotab errors."""
    pass


class CroniterBadCronError(CroniterError):
    """Raised when a cron expression is invalid."""
    pass


class CroniterBadDateError(CroniterError):
    """Raised when a date/time value is invalid."""
    pass
