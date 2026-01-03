"""
Tests for cron field parsing and iteration.
"""

import pytest

from pychronotab.exceptions import CroniterBadCronError
from pychronotab.fields import DAY_NAMES, MONTH_NAMES, CronField, parse_cron_expression


class TestCronField:
    """Test CronField parsing and value iteration."""

    def test_wildcard(self):
        field = CronField("*", 0, 59)
        assert len(field.values) == 60
        assert field.min() == 0
        assert field.max() == 59

    def test_single_value(self):
        field = CronField("5", 0, 59)
        assert field.values == [5]
        assert field.contains(5)
        assert not field.contains(4)

    def test_range(self):
        field = CronField("10-15", 0, 59)
        assert field.values == [10, 11, 12, 13, 14, 15]

    def test_list(self):
        field = CronField("1,5,10", 0, 59)
        assert field.values == [1, 5, 10]

    def test_step_from_wildcard(self):
        field = CronField("*/15", 0, 59)
        assert field.values == [0, 15, 30, 45]

    def test_step_from_range(self):
        field = CronField("10-30/5", 0, 59)
        assert field.values == [10, 15, 20, 25, 30]

    def test_month_names(self):
        field = CronField("JAN,MAR,DEC", 1, 12, MONTH_NAMES)
        assert field.values == [1, 3, 12]

    def test_day_names(self):
        field = CronField("MON-FRI", 0, 6, DAY_NAMES)
        assert field.values == [1, 2, 3, 4, 5]

    def test_next_value(self):
        field = CronField("0,15,30,45", 0, 59)
        assert field.next_value(0) == 15
        assert field.next_value(15) == 30
        assert field.next_value(30) == 45
        assert field.next_value(45) is None  # Wrap

    def test_prev_value(self):
        field = CronField("0,15,30,45", 0, 59)
        assert field.prev_value(45) == 30
        assert field.prev_value(30) == 15
        assert field.prev_value(15) == 0
        assert field.prev_value(0) is None  # Wrap

    def test_invalid_range(self):
        with pytest.raises(CroniterBadCronError):
            CronField("30-10", 0, 59)

    def test_out_of_bounds(self):
        with pytest.raises(CroniterBadCronError):
            CronField("70", 0, 59)

    def test_empty_field(self):
        with pytest.raises(CroniterBadCronError):
            CronField("", 0, 59)


class TestParseCronExpression:
    """Test full cron expression parsing."""

    def test_5_field_cron(self):
        fields = parse_cron_expression("*/5 * * * *")
        assert len(fields) == 6
        # Second should default to 0
        assert fields[0].values == [0]
        # Minute should be */5
        assert fields[1].values == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

    def test_6_field_cron(self):
        fields = parse_cron_expression("*/30 */5 * * * *")
        assert len(fields) == 6
        # Second should be */30
        assert fields[0].values == [0, 30]
        # Minute should be */5
        assert fields[1].values == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

    def test_complex_expression(self):
        fields = parse_cron_expression("0 0 1,15 * MON-FRI")
        assert fields[1].values == [0]  # minute
        assert fields[2].values == [0]  # hour
        assert fields[3].values == [1, 15]  # day
        assert fields[5].values == [1, 2, 3, 4, 5]  # dow (MON-FRI)

    def test_invalid_field_count(self):
        with pytest.raises(CroniterBadCronError):
            parse_cron_expression("* * *")

        with pytest.raises(CroniterBadCronError):
            parse_cron_expression("* * * * * * *")
