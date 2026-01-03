"""
Tests for CronExpression core functionality.
"""

from datetime import UTC, datetime

from pychronotab import CronExpression


class TestCronExpression:
    """Test CronExpression iteration."""

    def test_every_5_minutes(self):
        expr = CronExpression("*/5 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        next1 = expr.next(base)
        assert next1 == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

        next2 = expr.next(next1)
        assert next2 == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)

    def test_every_30_seconds(self):
        expr = CronExpression("*/30 * * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        next1 = expr.next(base)
        assert next1 == datetime(2024, 1, 1, 12, 0, 30, tzinfo=UTC)

        next2 = expr.next(next1)
        assert next2 == datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC)

    def test_specific_time(self):
        expr = CronExpression("0 0 * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC)

        next1 = expr.next(base)
        assert next1 == datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)

    def test_inclusive_match(self):
        expr = CronExpression("*/5 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

        # Without inclusive, should skip to next
        next1 = expr.next(base, inclusive=False)
        assert next1 == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)

        # With inclusive, should return base
        next2 = expr.next(base, inclusive=True)
        assert next2 == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

    def test_prev(self):
        expr = CronExpression("*/5 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)

        prev1 = expr.prev(base)
        assert prev1 == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)

        prev2 = expr.prev(prev1)
        assert prev2 == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_month_boundary(self):
        expr = CronExpression("0 0 1 * *", tz=UTC)
        base = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        next1 = expr.next(base)
        assert next1 == datetime(2024, 2, 1, 0, 0, 0, tzinfo=UTC)

    def test_year_boundary(self):
        expr = CronExpression("0 0 1 1 *", tz=UTC)
        base = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)

        next1 = expr.next(base)
        assert next1 == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    def test_iter_forward(self):
        expr = CronExpression("*/10 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

        iterator = expr.iter(base, direction="forward")

        assert next(iterator) == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 20, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC)

    def test_iter_backward(self):
        expr = CronExpression("*/10 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 30, 0, tzinfo=UTC)

        iterator = expr.iter(base, direction="backward")

        assert next(iterator) == datetime(2024, 1, 1, 12, 20, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 10, 0, tzinfo=UTC)
        assert next(iterator) == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_naive_datetime_gets_tz(self):
        expr = CronExpression("*/5 * * * *", tz=UTC)
        base = datetime(2024, 1, 1, 12, 0, 0)  # Naive

        next1 = expr.next(base)
        assert next1.tzinfo == UTC

    def test_complex_expression(self):
        # Every 15 minutes during business hours on weekdays
        expr = CronExpression("0 */15 9-17 * * MON-FRI", tz=UTC)
        base = datetime(2024, 1, 1, 8, 0, 0, tzinfo=UTC)  # Monday

        next1 = expr.next(base)
        assert next1 == datetime(2024, 1, 1, 9, 0, 0, tzinfo=UTC)

        next2 = expr.next(next1)
        assert next2 == datetime(2024, 1, 1, 9, 15, 0, tzinfo=UTC)
