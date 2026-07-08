"""Time helpers (P-11 deprecated-API fix, P-07 shared overdue logic).

``datetime.utcnow()`` is deprecated from Python 3.12. ``now_utc`` uses the
sanctioned ``datetime.now(timezone.utc)`` and returns a naive value to match
the naive-UTC datetimes flask-sqlalchemy stores and reads back from SQLite,
preserving the original comparison behavior exactly.
"""
from datetime import datetime, timezone

from config.constants import TERMINAL_STATUSES


def now_utc():
    """Current UTC time as a naive datetime (matches DB-stored naive UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _as_naive_utc(value):
    if value is not None and value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def is_overdue(due_date, status):
    """A task is overdue if its due date passed and it is not in a terminal state.

    Single source of truth for the overdue rule that was previously copy-pasted
    across five handlers.
    """
    if not due_date:
        return False
    return _as_naive_utc(due_date) < now_utc() and status not in TERMINAL_STATUSES
