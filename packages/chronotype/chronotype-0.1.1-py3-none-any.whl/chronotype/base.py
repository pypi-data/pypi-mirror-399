"""Base temporal class for generic types."""

from __future__ import annotations

import bisect
import copy
import json
import pickle
from datetime import date, datetime
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from chronotype.exceptions import EmptyTemporalError, InvalidTimestampError
from chronotype.interpolation import InterpolationStrategy, StepInterpolation
from chronotype.query import TemporalQuery
from chronotype.utils import TimestampType, normalize_timestamp, now

T = TypeVar("T")


class Temporal(Generic[T]):
    """
    A temporal value that tracks its history over time.

    Every assignment is stored with its timestamp, allowing queries
    at any point in time and analysis over time ranges.
    """

    def __init__(
        self,
        initial: Optional[T] = None,
        initial_time: Optional[TimestampType] = None,
        interpolation: Optional[InterpolationStrategy[T]] = None,
    ) -> None:
        """
        Initialize a temporal value.

        Args:
            initial: Optional initial value
            initial_time: Timestamp for initial value (defaults to now)
            interpolation: Strategy for interpolating between values
        """
        self._timeline: List[Tuple[datetime, T]] = []
        self._interpolation: InterpolationStrategy[T] = interpolation or StepInterpolation()

        if initial is not None:
            ts = normalize_timestamp(initial_time) if initial_time else now()
            self._timeline.append((ts, initial))

    def _find_index(self, ts: datetime) -> int:
        """Find insertion index for timestamp using binary search."""
        timestamps = [t for t, _ in self._timeline]
        return bisect.bisect_right(timestamps, ts)

    def _find_index_left(self, ts: datetime) -> int:
        """Find leftmost insertion index for timestamp."""
        timestamps = [t for t, _ in self._timeline]
        return bisect.bisect_left(timestamps, ts)

    def set(self, timestamp: TimestampType, value: T) -> None:
        """Set value at a specific timestamp."""
        ts = normalize_timestamp(timestamp)
        idx = self._find_index_left(ts)

        if idx < len(self._timeline) and self._timeline[idx][0] == ts:
            self._timeline[idx] = (ts, value)
        else:
            self._timeline.insert(idx, (ts, value))

    def __setitem__(self, timestamp: TimestampType, value: T) -> None:
        """Set value at timestamp using bracket notation."""
        self.set(timestamp, value)

    def at(self, timestamp: TimestampType) -> Optional[T]:
        """
        Get value at a specific timestamp.

        Returns the value that was active at the given time,
        using the interpolation strategy if needed.
        """
        if not self._timeline:
            return None

        ts = normalize_timestamp(timestamp)

        idx = self._find_index(ts)

        if idx == 0:
            after = self._timeline[0] if self._timeline else None
            return self._interpolation.interpolate(ts, None, after)

        before = self._timeline[idx - 1]

        if idx < len(self._timeline):
            after = self._timeline[idx]
        else:
            after = None

        return self._interpolation.interpolate(ts, before, after)

    def __getitem__(self, timestamp: TimestampType) -> Optional[T]:
        """Get value at timestamp using bracket notation."""
        return self.at(timestamp)

    def current(self) -> T:
        """Get the most recent value."""
        if not self._timeline:
            raise EmptyTemporalError("No values in temporal")
        return self._timeline[-1][1]

    def current_entry(self) -> Tuple[datetime, T]:
        """Get the most recent entry as (timestamp, value)."""
        if not self._timeline:
            raise EmptyTemporalError("No values in temporal")
        return self._timeline[-1]

    def first(self) -> T:
        """Get the first (oldest) value."""
        if not self._timeline:
            raise EmptyTemporalError("No values in temporal")
        return self._timeline[0][1]

    def first_entry(self) -> Tuple[datetime, T]:
        """Get the first entry as (timestamp, value)."""
        if not self._timeline:
            raise EmptyTemporalError("No values in temporal")
        return self._timeline[0]

    def between(
        self,
        start: TimestampType,
        end: TimestampType,
        include_start: bool = True,
        include_end: bool = True,
    ) -> TemporalQuery[T]:
        """
        Query values between two timestamps.

        Args:
            start: Start of range
            end: End of range
            include_start: Include entries at exactly start time
            include_end: Include entries at exactly end time

        Returns:
            TemporalQuery object for further operations
        """
        start_dt = normalize_timestamp(start)
        end_dt = normalize_timestamp(end)

        if start_dt > end_dt:
            raise InvalidTimestampError("Start must be before or equal to end")

        entries = []
        for ts, value in self._timeline:
            if include_start and include_end:
                if start_dt <= ts <= end_dt:
                    entries.append((ts, value))
            elif include_start:
                if start_dt <= ts < end_dt:
                    entries.append((ts, value))
            elif include_end:
                if start_dt < ts <= end_dt:
                    entries.append((ts, value))
            else:
                if start_dt < ts < end_dt:
                    entries.append((ts, value))

        return TemporalQuery(entries, start_dt, end_dt, include_start, include_end)

    def history(self) -> List[Tuple[datetime, T]]:
        """Get full history as list of (timestamp, value) tuples."""
        return list(self._timeline)

    def changes(self) -> List[Tuple[datetime, Optional[T], T]]:
        """
        Get list of changes as (timestamp, old_value, new_value) tuples.
        First entry has None as old_value.
        """
        if not self._timeline:
            return []

        changes: List[Tuple[datetime, Optional[T], T]] = [
            (self._timeline[0][0], None, self._timeline[0][1])
        ]

        for i in range(1, len(self._timeline)):
            ts, new_val = self._timeline[i]
            old_val = self._timeline[i - 1][1]
            changes.append((ts, old_val, new_val))

        return changes

    def rollback(self, to: Optional[TimestampType] = None, steps: int = 1) -> None:
        """
        Rollback changes.

        Args:
            to: If provided, remove all entries after this timestamp
            steps: If 'to' not provided, remove this many recent entries
        """
        if to is not None:
            ts = normalize_timestamp(to)
            self._timeline = [(t, v) for t, v in self._timeline if t <= ts]
        else:
            if steps > 0:
                self._timeline = self._timeline[:-steps] if steps < len(self._timeline) else []

    def clear(self) -> None:
        """Remove all entries."""
        self._timeline.clear()

    def __len__(self) -> int:
        """Number of entries in history."""
        return len(self._timeline)

    def __bool__(self) -> bool:
        """True if there are any entries."""
        return len(self._timeline) > 0

    def __iter__(self) -> Iterator[Tuple[datetime, T]]:
        """Iterate over (timestamp, value) pairs."""
        return iter(self._timeline)

    def __contains__(self, timestamp: TimestampType) -> bool:
        """Check if there's an entry at exactly this timestamp."""
        ts = normalize_timestamp(timestamp)
        return any(t == ts for t, _ in self._timeline)

    def __repr__(self) -> str:
        if not self._timeline:
            return f"{self.__class__.__name__}(empty)"
        return f"{self.__class__.__name__}(entries={len(self._timeline)}, current={self._timeline[-1][1]!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temporal):
            return NotImplemented
        return self._timeline == other._timeline

    def copy(self) -> "Temporal[T]":
        """Create a shallow copy."""
        new = Temporal[T]()
        new._timeline = list(self._timeline)
        new._interpolation = self._interpolation
        return new

    def deepcopy(self) -> "Temporal[T]":
        """Create a deep copy."""
        new = Temporal[T]()
        new._timeline = [(ts, copy.deepcopy(v)) for ts, v in self._timeline]
        new._interpolation = self._interpolation
        return new

    def timestamps(self) -> List[datetime]:
        """Get all timestamps."""
        return [ts for ts, _ in self._timeline]

    def values(self) -> List[T]:
        """Get all values."""
        return [v for _, v in self._timeline]

    def slice(self, start: TimestampType, end: TimestampType) -> "Temporal[T]":
        """Create a new Temporal containing only entries in the range."""
        query = self.between(start, end)
        new = Temporal[T]()
        new._timeline = list(query.entries())
        new._interpolation = self._interpolation
        return new

    def merge(self, other: "Temporal[T]", prefer_self: bool = True) -> "Temporal[T]":
        """
        Merge with another temporal.

        Args:
            other: Another temporal to merge with
            prefer_self: If True, prefer this temporal's values on conflict

        Returns:
            New merged Temporal
        """
        new = Temporal[T]()
        new._interpolation = self._interpolation

        all_entries: Dict[datetime, T] = {}

        if prefer_self:
            for ts, v in other._timeline:
                all_entries[ts] = v
            for ts, v in self._timeline:
                all_entries[ts] = v
        else:
            for ts, v in self._timeline:
                all_entries[ts] = v
            for ts, v in other._timeline:
                all_entries[ts] = v

        new._timeline = sorted(all_entries.items(), key=lambda x: x[0])
        return new

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entries": [(ts.isoformat(), v) for ts, v in self._timeline],
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Temporal[T]":
        """Create from dictionary."""
        new = cls()
        for ts_str, value in data.get("entries", []):
            ts = datetime.fromisoformat(ts_str)
            new._timeline.append((ts, value))
        return new

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "Temporal[T]":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def __getstate__(self) -> Dict[str, Any]:
        """Support for pickle serialization."""
        return {
            "timeline": self._timeline,
            "interpolation": self._interpolation,
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Support for pickle deserialization."""
        self._timeline = state["timeline"]
        self._interpolation = state["interpolation"]