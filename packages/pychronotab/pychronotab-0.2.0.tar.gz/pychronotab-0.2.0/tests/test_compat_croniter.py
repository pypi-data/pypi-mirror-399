"""
Tests for croniter API compatibility.
"""

from datetime import UTC, datetime

import pytest

from pychronotab import croniter
from pychronotab.exceptions import CroniterBadDateError


class TestCroniterCompat:
    """Test croniter-compatible API."""

    def test_basic_get_next(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        next1 = it.get_next(datetime)
        assert next1 == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

        next2 = it.get_next(datetime)
        assert next2 == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)

    def test_get_next_float(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        next1 = it.get_next(float)
        assert isinstance(next1, float)

        # Convert back to datetime to verify
        dt = datetime.fromtimestamp(next1, tz=UTC)
        assert dt == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

    def test_get_prev(self):
        base = datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        prev1 = it.get_prev(datetime)
        assert prev1 == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

        prev2 = it.get_prev(datetime)
        assert prev2 == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_get_current(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        # Should raise before first get_next/get_prev
        with pytest.raises(CroniterBadDateError):
            it.get_current(datetime)

        next1 = it.get_next(datetime)
        current = it.get_current(datetime)
        assert current == next1

    def test_all_next(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/10 * * * *", base)

        iterator = it.all_next(datetime)

        assert next(iterator) == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 20, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC)

    def test_all_prev(self):
        base = datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC)
        it = croniter("*/10 * * * *", base)

        iterator = it.all_prev(datetime)

        assert next(iterator) == datetime(2024, 1, 1, 12, 20, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_set_current(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        # Set to a different time
        new_time = datetime(2024, 1, 1, 15, 0, 0, tzinfo=UTC)
        it.set_current(new_time)

        next1 = it.get_next(datetime)
        assert next1 == datetime(2024, 1, 1, 15, 5, 0, tzinfo=UTC)

    def test_6_field_cron(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/30 * * * * *", base)

        next1 = it.get_next(datetime)
        assert next1 == datetime(2024, 1, 1, 12, 0, 30, tzinfo=UTC)

        next2 = it.get_next(datetime)
        assert next2 == datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC)

    def test_no_start_time(self):
        # Should use current time
        it = croniter("*/5 * * * *")

        next1 = it.get_next(datetime)
        assert isinstance(next1, datetime)
        assert next1.tzinfo is not None

    def test_cur_property(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/5 * * * *", base)

        # Before first call
        assert it.cur is None

        next1 = it.get_next(datetime)
        assert it.cur is not None
        assert isinstance(it.cur, float)
        assert it.cur == next1.timestamp()

    def test_iter_protocol(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        it = croniter("*/10 * * * *", base)

        iterator = iter(it)

        assert next(iterator) == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 20, 0, tzinfo=UTC)
