"""Utility functions for chronotype."""

from datetime import date, datetime, timezone
from typing import Union

TimestampType = Union[datetime, date]


def normalize_timestamp(ts: TimestampType) -> datetime:
    """Convert any timestamp to datetime for consistent handling."""
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts
        return ts
    elif isinstance(ts, date):
        return datetime(ts.year, ts.month, ts.day)
    else:
        raise TypeError(f"Expected datetime or date, got {type(ts).__name__}")


def timestamp_to_seconds(ts: datetime) -> float:
    """Convert datetime to seconds since epoch."""
    return ts.timestamp()


def seconds_to_timedelta_total(start: datetime, end: datetime) -> float:
    """Get total seconds between two datetimes."""
    return (end - start).total_seconds()


def now() -> datetime:
    """Get current datetime."""
    return datetime.now()


def ensure_datetime(ts: TimestampType) -> datetime:
    """Ensure timestamp is a datetime object."""
    return normalize_timestamp(ts)