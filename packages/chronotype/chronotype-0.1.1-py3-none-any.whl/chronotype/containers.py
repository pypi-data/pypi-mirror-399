"""Temporal container types."""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Any, Dict, Generic, Iterator, List, Optional, Tuple, TypeVar

from chronotype.base import Temporal
from chronotype.exceptions import EmptyTemporalError
from chronotype.interpolation import StepInterpolation
from chronotype.query import TemporalQuery
from chronotype.utils import TimestampType, normalize_timestamp, now

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class TemporalList(Temporal[List[T]]):
    """
    Temporal list that tracks history of list changes.
    """

    def __init__(
        self,
        initial: Optional[List[T]] = None,
        initial_time: Optional[TimestampType] = None,
    ) -> None:
        super().__init__(
            list(initial) if initial else None,
            initial_time,
            StepInterpolation(),
        )

    def set(self, timestamp: TimestampType, value: List[T]) -> None:
        """Set list at timestamp, storing a copy."""
        super().set(timestamp, list(value))

    def append(self, value: T, timestamp: Optional[TimestampType] = None) -> None:
        """Append value to list, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            self.set(ts, [value])
        else:
            current = list(self.current())
            current.append(value)
            self.set(ts, current)

    def extend(self, values: List[T], timestamp: Optional[TimestampType] = None) -> None:
        """Extend list with values, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            self.set(ts, list(values))
        else:
            current = list(self.current())
            current.extend(values)
            self.set(ts, current)

    def insert(self, index: int, value: T, timestamp: Optional[TimestampType] = None) -> None:
        """Insert value at index, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            self.set(ts, [value])
        else:
            current = list(self.current())
            current.insert(index, value)
            self.set(ts, current)

    def remove(self, value: T, timestamp: Optional[TimestampType] = None) -> None:
        """Remove value from list, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            raise ValueError(f"{value} not in list")

        current = list(self.current())
        current.remove(value)
        self.set(ts, current)

    def pop(
        self, index: int = -1, timestamp: Optional[TimestampType] = None
    ) -> T:
        """Pop value from list, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            raise IndexError("pop from empty list")

        current = list(self.current())
        value = current.pop(index)
        self.set(ts, current)
        return value

    def clear_list(self, timestamp: Optional[TimestampType] = None) -> None:
        """Clear the list contents (not the history)."""
        ts = normalize_timestamp(timestamp) if timestamp else now()
        self.set(ts, [])

    def current_len(self) -> int:
        """Get length of current list."""
        if not self._timeline:
            raise EmptyTemporalError()
        return len(self.current())

    def len_at(self, timestamp: TimestampType) -> Optional[int]:
        """Get length of list at timestamp."""
        value = self.at(timestamp)
        return len(value) if value is not None else None

    def contains_at(self, timestamp: TimestampType, value: T) -> bool:
        """Check if value is in list at timestamp."""
        lst = self.at(timestamp)
        return value in lst if lst is not None else False

    def get_item_at(self, timestamp: TimestampType, index: int) -> Optional[T]:
        """Get item at index from list at timestamp."""
        lst = self.at(timestamp)
        if lst is not None and -len(lst) <= index < len(lst):
            return lst[index]
        return None

    def copy(self) -> TemporalList[T]:
        """Create a deep copy."""
        new = TemporalList[T]()
        new._timeline = [(ts, list(v)) for ts, v in self._timeline]
        return new


class TemporalDict(Temporal[Dict[K, V]]):
    """
    Temporal dictionary that tracks history of dict changes.
    """

    def __init__(
        self,
        initial: Optional[Dict[K, V]] = None,
        initial_time: Optional[TimestampType] = None,
    ) -> None:
        super().__init__(
            dict(initial) if initial else None,
            initial_time,
            StepInterpolation(),
        )

    def set(self, timestamp: TimestampType, value: Dict[K, V]) -> None:
        """Set dict at timestamp, storing a copy."""
        super().set(timestamp, dict(value))

    def set_item(
        self, key: K, value: V, timestamp: Optional[TimestampType] = None
    ) -> None:
        """Set key-value pair, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            self.set(ts, {key: value})
        else:
            current = dict(self.current())
            current[key] = value
            self.set(ts, current)

    def delete_item(self, key: K, timestamp: Optional[TimestampType] = None) -> None:
        """Delete key, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            raise KeyError(key)

        current = dict(self.current())
        del current[key]
        self.set(ts, current)

    def update_dict(
        self, other: Dict[K, V], timestamp: Optional[TimestampType] = None
    ) -> None:
        """Update dict with another dict, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            self.set(ts, dict(other))
        else:
            current = dict(self.current())
            current.update(other)
            self.set(ts, current)

    def pop_item(
        self, key: K, timestamp: Optional[TimestampType] = None, default: Optional[V] = None
    ) -> Optional[V]:
        """Pop key from dict, creating new historical entry."""
        ts = normalize_timestamp(timestamp) if timestamp else now()

        if not self._timeline:
            return default

        current = dict(self.current())
        value = current.pop(key, default)
        self.set(ts, current)
        return value

    def clear_dict(self, timestamp: Optional[TimestampType] = None) -> None:
        """Clear the dict contents (not the history)."""
        ts = normalize_timestamp(timestamp) if timestamp else now()
        self.set(ts, {})

    def get_item_at(self, timestamp: TimestampType, key: K) -> Optional[V]:
        """Get value for key from dict at timestamp."""
        dct = self.at(timestamp)
        return dct.get(key) if dct is not None else None

    def contains_key_at(self, timestamp: TimestampType, key: K) -> bool:
        """Check if key exists in dict at timestamp."""
        dct = self.at(timestamp)
        return key in dct if dct is not None else False

    def keys_at(self, timestamp: TimestampType) -> Optional[List[K]]:
        """Get keys of dict at timestamp."""
        dct = self.at(timestamp)
        return list(dct.keys()) if dct is not None else None

    def values_at(self, timestamp: TimestampType) -> Optional[List[V]]:
        """Get values of dict at timestamp."""
        dct = self.at(timestamp)
        return list(dct.values()) if dct is not None else None

    def items_at(self, timestamp: TimestampType) -> Optional[List[Tuple[K, V]]]:
        """Get items of dict at timestamp."""
        dct = self.at(timestamp)
        return list(dct.items()) if dct is not None else None

    def len_at(self, timestamp: TimestampType) -> Optional[int]:
        """Get length of dict at timestamp."""
        dct = self.at(timestamp)
        return len(dct) if dct is not None else None

    def key_history(self, key: K) -> List[Tuple[datetime, Optional[V]]]:
        """Get history of a specific key's values."""
        history = []
        prev_value: Optional[V] = None
        key_existed = False

        for ts, dct in self._timeline:
            current_value = dct.get(key)
            currently_exists = key in dct

            if currently_exists != key_existed or current_value != prev_value:
                history.append((ts, current_value if currently_exists else None))
                prev_value = current_value
                key_existed = currently_exists

        return history

    def copy(self) -> TemporalDict[K, V]:
        """Create a deep copy."""
        new = TemporalDict[K, V]()
        new._timeline = [(ts, dict(v)) for ts, v in self._timeline]
        return new