"""Query objects for temporal range operations."""

from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from chronotype.exceptions import EmptyTemporalError

T = TypeVar("T")
N = TypeVar("N", int, float)


class TemporalQuery(Generic[T]):
    """
    Query object for temporal range operations.
    Provides aggregation and analysis over a time range.
    """

    def __init__(
        self,
        entries: List[Tuple[datetime, T]],
        start: datetime,
        end: datetime,
        include_start: bool = True,
        include_end: bool = True,
    ) -> None:
        self._entries = entries
        self._start = start
        self._end = end
        self._include_start = include_start
        self._include_end = include_end

    @property
    def start(self) -> datetime:
        """Start of the query range."""
        return self._start

    @property
    def end(self) -> datetime:
        """End of the query range."""
        return self._end

    def entries(self) -> List[Tuple[datetime, T]]:
        """Get all entries in the range as (timestamp, value) tuples."""
        return list(self._entries)

    def values(self) -> List[T]:
        """Get all values in the range."""
        return [v for _, v in self._entries]

    def timestamps(self) -> List[datetime]:
        """Get all timestamps in the range."""
        return [ts for ts, _ in self._entries]

    def count(self) -> int:
        """Count of entries in the range."""
        return len(self._entries)

    def is_empty(self) -> bool:
        """Check if the query result is empty."""
        return len(self._entries) == 0

    def first(self) -> Optional[Tuple[datetime, T]]:
        """Get the first entry in the range."""
        if self._entries:
            return self._entries[0]
        return None

    def last(self) -> Optional[Tuple[datetime, T]]:
        """Get the last entry in the range."""
        if self._entries:
            return self._entries[-1]
        return None

    def first_value(self) -> Optional[T]:
        """Get the first value in the range."""
        entry = self.first()
        return entry[1] if entry else None

    def last_value(self) -> Optional[T]:
        """Get the last value in the range."""
        entry = self.last()
        return entry[1] if entry else None

    def filter(self, predicate: Callable[[T], bool]) -> "TemporalQuery[T]":
        """Filter entries by a predicate function."""
        filtered = [(ts, v) for ts, v in self._entries if predicate(v)]
        return TemporalQuery(
            filtered,
            self._start,
            self._end,
            self._include_start,
            self._include_end,
        )

    def map(self, func: Callable[[T], T]) -> "TemporalQuery[T]":
        """Apply a function to all values."""
        mapped = [(ts, func(v)) for ts, v in self._entries]
        return TemporalQuery(
            mapped,
            self._start,
            self._end,
            self._include_start,
            self._include_end,
        )

    def __iter__(self) -> Iterator[Tuple[datetime, T]]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return len(self._entries) > 0


class NumericTemporalQuery(TemporalQuery[N]):
    """Query with numeric aggregation methods."""

    def __init__(
        self,
        entries: List[Tuple[datetime, N]],
        start: datetime,
        end: datetime,
        include_start: bool = True,
        include_end: bool = True,
        value_before_range: Optional[N] = None,
    ) -> None:
        super().__init__(entries, start, end, include_start, include_end)  # type: ignore[arg-type]
        self._value_before_range: Optional[N] = value_before_range

    def min(self) -> N:
        """Get the minimum value in the range."""
        if not self._entries:
            raise EmptyTemporalError("Cannot compute min of empty query result")
        return min(v for _, v in self._entries)

    def max(self) -> N:
        """Get the maximum value in the range."""
        if not self._entries:
            raise EmptyTemporalError("Cannot compute max of empty query result")
        return max(v for _, v in self._entries)

    def sum(self) -> N:
        """Get the sum of all values in the range."""
        if not self._entries:
            return cast(N, 0)
        return cast(N, sum(v for _, v in self._entries))

    def average(self) -> float:
        """
        Get the time-weighted average of values in the range.
        Each value is weighted by how long it was active.
        """
        if not self._entries:
            raise EmptyTemporalError("Cannot compute average of empty query result")

        if len(self._entries) == 1:
            return float(self._entries[0][1])

        total_weight = 0.0
        weighted_sum = 0.0

        effective_entries: List[Tuple[datetime, N]] = []

        if self._value_before_range is not None:
            effective_entries.append((self._start, self._value_before_range))

        effective_entries.extend(self._entries)

        for i in range(len(effective_entries)):
            ts, value = effective_entries[i]

            if i + 1 < len(effective_entries):
                next_ts = effective_entries[i + 1][0]
            else:
                next_ts = self._end

            start_time = max(ts, self._start)
            end_time = min(next_ts, self._end)

            if end_time > start_time:
                duration = (end_time - start_time).total_seconds()
                weighted_sum += value * duration
                total_weight += duration

        if total_weight == 0:
            return float(self._entries[-1][1]) if self._entries else 0.0

        return float(weighted_sum / total_weight)

    def simple_average(self) -> float:
        """Get simple (non-weighted) average of values."""
        if not self._entries:
            raise EmptyTemporalError("Cannot compute average of empty query result")
        return sum(v for _, v in self._entries) / len(self._entries)

    def median(self) -> N:
        """Get the median value in the range."""
        if not self._entries:
            raise EmptyTemporalError("Cannot compute median of empty query result")
        sorted_values = sorted(v for _, v in self._entries)
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2  # type: ignore[return-value]
        return sorted_values[mid]

    def variance(self) -> float:
        """Get the variance of values in the range."""
        if not self._entries:
            raise EmptyTemporalError("Cannot compute variance of empty query result")
        avg = self.simple_average()
        return float(sum((v - avg) ** 2 for _, v in self._entries) / len(self._entries))

    def std_dev(self) -> float:
        """Get the standard deviation of values in the range."""
        return float(self.variance() ** 0.5)

    def delta(self) -> N:
        """Get the change from first to last value."""
        if len(self._entries) < 2:
            raise EmptyTemporalError("Need at least 2 entries to compute delta")
        return self._entries[-1][1] - self._entries[0][1]

    def rate_of_change(self) -> float:
        """Get the rate of change per second."""
        if len(self._entries) < 2:
            raise EmptyTemporalError("Need at least 2 entries to compute rate of change")
        time_delta = (self._entries[-1][0] - self._entries[0][0]).total_seconds()
        if time_delta == 0:
            return 0.0
        return float(self.delta()) / time_delta