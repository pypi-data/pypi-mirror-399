# pychronotab

A modern cron expression iterator with full croniter API compatibility, supporting both 5-field (standard) and 6-field (with seconds) cron expressions.

## Why pychronotab?

`pychronotab` was created to solve namespace conflicts when using multiple task schedulers (like `django-celery-beat` with `python-crontab` and `rq-scheduler` with `croniter`) in the same project. Both `python-crontab` and older cron libraries expose a top-level `crontab` module, causing import conflicts.

**pychronotab** provides:

- ✅ **Zero namespace conflicts** - all imports under `pychronotab`
- ✅ **Full croniter API compatibility** - drop-in replacement for abandoned croniter
- ✅ **6-field cron support** - includes seconds field for sub-minute scheduling
- ✅ **Modern timezone handling** - uses `zoneinfo` (Python 3.9+)
- ✅ **DST-aware** - handles daylight saving time transitions correctly
- ✅ **Active maintenance** - not abandoned

## Installation

```bash
pip install pychronotab
```

## Quick Start

### Modern API

```python
from datetime import datetime, timezone
from pychronotab import CronExpression

# 5-field cron (standard)
expr = CronExpression("*/5 * * * *", tz=timezone.utc)
now = datetime.now(timezone.utc)
next_run = expr.next(now)
print(f"Next run: {next_run}")

# 6-field cron (with seconds)
expr_seconds = CronExpression("*/30 */5 * * * *", tz=timezone.utc)
next_run = expr_seconds.next(now)
print(f"Next run (with seconds): {next_run}")
```

### croniter-Compatible API

Drop-in replacement for croniter (just change the import):

```python
from datetime import datetime
from pychronotab import croniter

# Standard 5-field cron
it = croniter("*/5 * * * *", datetime.now())
print(it.get_next(datetime))
print(it.get_next(datetime))

# 6-field cron with seconds
it_seconds = croniter("*/30 */5 * * * *", datetime.now())
print(it_seconds.get_next(datetime))
```

## Cron Expression Format

### 5-field format (standard Unix cron):
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── day of week (0-6, SUN-SAT)
│ │ │ └───── month (1-12, JAN-DEC)
│ │ └─────── day of month (1-31)
│ └───────── hour (0-23)
└─────────── minute (0-59)
```

### 6-field format (with seconds):
```
* * * * * *
│ │ │ │ │ │
│ │ │ │ │ └─── day of week (0-6, SUN-SAT)
│ │ │ │ └───── month (1-12, JAN-DEC)
│ │ │ └─────── day of month (1-31)
│ │ └───────── hour (0-23)
│ └─────────── minute (0-59)
└───────────── second (0-59)
```

### Supported syntax:

- `*` - any value
- `5` - specific value
- `1-5` - range of values
- `*/5` - step values (every 5)
- `1,3,5` - list of values
- `1-5/2` - range with step
- `JAN-DEC`, `SUN-SAT` - month/day names

## API Reference

### CronExpression (Modern API)

```python
class CronExpression:
    def __init__(self, expr: str, tz: timezone | None = None)
    def next(self, base: datetime | None = None, *, inclusive: bool = False) -> datetime
    def prev(self, base: datetime | None = None, *, inclusive: bool = False) -> datetime
    def iter(self, start: datetime, *, direction: str = "forward", inclusive: bool = False) -> Iterator[datetime]
```

### croniter (Compatibility API)

```python
class croniter:
    def __init__(self, expr_format: str, start_time: datetime | None = None, day_or: bool = True)
    def get_next(self, ret_type: Type = datetime) -> datetime | float
    def get_prev(self, ret_type: Type = datetime) -> datetime | float
    def get_current(self, ret_type: Type = datetime) -> datetime | float
    def all_next(self, ret_type: Type = datetime) -> Iterator[datetime | float]
    def all_prev(self, ret_type: Type = datetime) -> Iterator[datetime | float]
```

## Migration from croniter

Simply change your import:

```python
# Old
from croniter import croniter

# New
from pychronotab import croniter
```

Everything else stays the same!

## Avoiding Namespace Conflicts

Unlike `python-crontab` (which exposes `crontab` module) and old `croniter` dependencies, `pychronotab` keeps everything under its own namespace:

```python
# ✅ Safe - no conflicts
from pychronotab import CronExpression, croniter

# ❌ Never exposed - won't conflict with python-crontab
# from crontab import ...  # This won't exist in pychronotab
```

This means you can safely use:
- `django-celery-beat` (uses `python-crontab`)
- `rq-scheduler` (uses `pychronotab` instead of abandoned `croniter`)
- Any other `crontab`-based library

…all in the same project without import conflicts!

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.
