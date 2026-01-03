"""Numeric temporal types with arithmetic operations."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, Iterator, List, Optional, Tuple, Union, overload

from chronotype.base import Temporal
from chronotype.exceptions import EmptyTemporalError
from chronotype.interpolation import InterpolationStrategy, LinearInterpolation, StepInterpolation
from chronotype.query import NumericTemporalQuery
from chronotype.utils import TimestampType, normalize_timestamp, now


class TemporalFloat(Temporal[float]):
    """
    Temporal float with arithmetic operations and optional interpolation.
    """

    def __init__(
        self,
        initial: Optional[float] = None,
        initial_time: Optional[TimestampType] = None,
        interpolate: bool = False,
    ) -> None:
        """
        Initialize a temporal float.

        Args:
            initial: Optional initial value
            initial_time: Timestamp for initial value
            interpolate: If True, use linear interpolation
        """
        interp: InterpolationStrategy[float] = (
            LinearInterpolation() if interpolate else StepInterpolation()
        )
        super().__init__(initial, initial_time, interp)
        self._interpolate = interpolate

    def between(
        self,
        start: TimestampType,
        end: TimestampType,
        include_start: bool = True,
        include_end: bool = True,
    ) -> NumericTemporalQuery[float]:
        """Query values between timestamps with numeric aggregations."""
        start_dt = normalize_timestamp(start)
        end_dt = normalize_timestamp(end)

        entries = []
        value_before: Optional[float] = None

        for ts, value in self._timeline:
            if ts < start_dt:
                value_before = value
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

        return NumericTemporalQuery(
            entries, start_dt, end_dt, include_start, include_end, value_before
        )

    def __add__(self, other: Union[TemporalFloat, float, int]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat(interpolate=self._interpolate)
            for ts, v in self._timeline:
                result[ts] = v + other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat(interpolate=self._interpolate)
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 + v2
        return result

    def __radd__(self, other: Union[float, int]) -> TemporalFloat:
        return self.__add__(other)

    def __sub__(self, other: Union[TemporalFloat, float, int]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat(interpolate=self._interpolate)
            for ts, v in self._timeline:
                result[ts] = v - other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat(interpolate=self._interpolate)
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 - v2
        return result

    def __rsub__(self, other: Union[float, int]) -> TemporalFloat:
        result = TemporalFloat(interpolate=self._interpolate)
        for ts, v in self._timeline:
            result[ts] = other - v
        return result

    def __mul__(self, other: Union[TemporalFloat, float, int]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat(interpolate=self._interpolate)
            for ts, v in self._timeline:
                result[ts] = v * other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat(interpolate=self._interpolate)
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 * v2
        return result

    def __rmul__(self, other: Union[float, int]) -> TemporalFloat:
        return self.__mul__(other)

    def __truediv__(self, other: Union[TemporalFloat, float, int]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat(interpolate=self._interpolate)
            for ts, v in self._timeline:
                result[ts] = v / other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat(interpolate=self._interpolate)
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None and v2 != 0:
                result[ts] = v1 / v2
        return result

    def __rtruediv__(self, other: Union[float, int]) -> TemporalFloat:
        result = TemporalFloat(interpolate=self._interpolate)
        for ts, v in self._timeline:
            if v != 0:
                result[ts] = other / v
        return result

    def __pow__(self, other: Union[TemporalFloat, float, int]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat(interpolate=self._interpolate)
            for ts, v in self._timeline:
                result[ts] = v**other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat(interpolate=self._interpolate)
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1**v2
        return result

    def __neg__(self) -> TemporalFloat:
        result = TemporalFloat(interpolate=self._interpolate)
        for ts, v in self._timeline:
            result[ts] = -v
        return result

    def __abs__(self) -> TemporalFloat:
        result = TemporalFloat(interpolate=self._interpolate)
        for ts, v in self._timeline:
            result[ts] = abs(v)
        return result

    def __lt__(self, other: Union[TemporalFloat, float, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a < b)

    def __le__(self, other: Union[TemporalFloat, float, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a <= b)

    def __gt__(self, other: Union[TemporalFloat, float, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a > b)

    def __ge__(self, other: Union[TemporalFloat, float, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a >= b)

    def _compare(
        self, other: Union[TemporalFloat, float, int], op: Callable[[float, float], bool]
    ) -> "TemporalBool":
        from chronotype.numeric import TemporalBool

        if isinstance(other, (int, float)):
            result = TemporalBool()
            for ts, v in self._timeline:
                result[ts] = op(v, other)
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalBool()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = op(v1, v2)
        return result

    def copy(self) -> TemporalFloat:
        """Create a copy."""
        new = TemporalFloat(interpolate=self._interpolate)
        new._timeline = list(self._timeline)
        return new


class TemporalInt(Temporal[int]):
    """
    Temporal integer with arithmetic operations.
    """

    def __init__(
        self,
        initial: Optional[int] = None,
        initial_time: Optional[TimestampType] = None,
    ) -> None:
        super().__init__(initial, initial_time, StepInterpolation())

    def between(
        self,
        start: TimestampType,
        end: TimestampType,
        include_start: bool = True,
        include_end: bool = True,
    ) -> NumericTemporalQuery[int]:
        """Query values between timestamps with numeric aggregations."""
        start_dt = normalize_timestamp(start)
        end_dt = normalize_timestamp(end)

        entries = []
        value_before: Optional[int] = None

        for ts, value in self._timeline:
            if ts < start_dt:
                value_before = value
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

        return NumericTemporalQuery(
            entries, start_dt, end_dt, include_start, include_end, value_before
        )

    def __add__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v + other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 + v2
        return result

    def __radd__(self, other: int) -> TemporalInt:
        return self.__add__(other)

    def __sub__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v - other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 - v2
        return result

    def __rsub__(self, other: int) -> TemporalInt:
        result = TemporalInt()
        for ts, v in self._timeline:
            result[ts] = other - v
        return result

    def __mul__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v * other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 * v2
        return result

    def __rmul__(self, other: int) -> TemporalInt:
        return self.__mul__(other)

    def __truediv__(self, other: Union[TemporalInt, TemporalFloat, int, float]) -> TemporalFloat:
        if isinstance(other, (int, float)):
            result = TemporalFloat()
            for ts, v in self._timeline:
                result[ts] = v / other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalFloat()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None and v2 != 0:
                result[ts] = v1 / v2
        return result

    def __floordiv__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v // other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None and v2 != 0:
                result[ts] = v1 // v2
        return result

    def __mod__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v % other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None and v2 != 0:
                result[ts] = v1 % v2
        return result

    def __pow__(self, other: Union[TemporalInt, int]) -> TemporalInt:
        if isinstance(other, int):
            result = TemporalInt()
            for ts, v in self._timeline:
                result[ts] = v**other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalInt()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1**v2
        return result

    def __neg__(self) -> TemporalInt:
        result = TemporalInt()
        for ts, v in self._timeline:
            result[ts] = -v
        return result

    def __abs__(self) -> TemporalInt:
        result = TemporalInt()
        for ts, v in self._timeline:
            result[ts] = abs(v)
        return result

    def __lt__(self, other: Union[TemporalInt, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a < b)

    def __le__(self, other: Union[TemporalInt, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a <= b)

    def __gt__(self, other: Union[TemporalInt, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a > b)

    def __ge__(self, other: Union[TemporalInt, int]) -> "TemporalBool":
        return self._compare(other, lambda a, b: a >= b)

    def _compare(self, other: Union[TemporalInt, int], op: Callable[[int, int], bool]) -> "TemporalBool":
        if isinstance(other, int):
            result = TemporalBool()
            for ts, v in self._timeline:
                result[ts] = op(v, other)
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalBool()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = op(v1, v2)
        return result

    def to_float(self) -> TemporalFloat:
        """Convert to TemporalFloat."""
        result = TemporalFloat()
        for ts, v in self._timeline:
            result[ts] = float(v)
        return result

    def copy(self) -> TemporalInt:
        """Create a copy."""
        new = TemporalInt()
        new._timeline = list(self._timeline)
        return new


class TemporalBool(Temporal[bool]):
    """
    Temporal boolean with logical operations.
    """

    def __init__(
        self,
        initial: Optional[bool] = None,
        initial_time: Optional[TimestampType] = None,
    ) -> None:
        super().__init__(initial, initial_time, StepInterpolation())

    def __and__(self, other: Union[TemporalBool, bool]) -> TemporalBool:
        if isinstance(other, bool):
            result = TemporalBool()
            for ts, v in self._timeline:
                result[ts] = v and other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalBool()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 and v2
        return result

    def __rand__(self, other: bool) -> TemporalBool:
        return self.__and__(other)

    def __or__(self, other: Union[TemporalBool, bool]) -> TemporalBool:
        if isinstance(other, bool):
            result = TemporalBool()
            for ts, v in self._timeline:
                result[ts] = v or other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalBool()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 or v2
        return result

    def __ror__(self, other: bool) -> TemporalBool:
        return self.__or__(other)

    def __xor__(self, other: Union[TemporalBool, bool]) -> TemporalBool:
        if isinstance(other, bool):
            result = TemporalBool()
            for ts, v in self._timeline:
                result[ts] = v ^ other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalBool()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 ^ v2
        return result

    def __rxor__(self, other: bool) -> TemporalBool:
        return self.__xor__(other)

    def __invert__(self) -> TemporalBool:
        result = TemporalBool()
        for ts, v in self._timeline:
            result[ts] = not v
        return result

    def when_true(self) -> List[Tuple[datetime, datetime]]:
        """Get list of time ranges when value was True."""
        if not self._timeline:
            return []

        ranges = []
        start = None

        for ts, value in self._timeline:
            if value and start is None:
                start = ts
            elif not value and start is not None:
                ranges.append((start, ts))
                start = None

        if start is not None:
            ranges.append((start, now()))

        return ranges

    def when_false(self) -> List[Tuple[datetime, datetime]]:
        """Get list of time ranges when value was False."""
        if not self._timeline:
            return []

        ranges = []
        start = None

        for ts, value in self._timeline:
            if not value and start is None:
                start = ts
            elif value and start is not None:
                ranges.append((start, ts))
                start = None

        if start is not None:
            ranges.append((start, now()))

        return ranges

    def duration_true(self) -> float:
        """Total seconds when value was True."""
        return sum((end - start).total_seconds() for start, end in self.when_true())

    def duration_false(self) -> float:
        """Total seconds when value was False."""
        return sum((end - start).total_seconds() for start, end in self.when_false())

    def copy(self) -> TemporalBool:
        """Create a copy."""
        new = TemporalBool()
        new._timeline = list(self._timeline)
        return new


class TemporalString(Temporal[str]):
    """
    Temporal string type.
    """

    def __init__(
        self,
        initial: Optional[str] = None,
        initial_time: Optional[TimestampType] = None,
    ) -> None:
        super().__init__(initial, initial_time, StepInterpolation())

    def __add__(self, other: Union[TemporalString, str]) -> TemporalString:
        if isinstance(other, str):
            result = TemporalString()
            for ts, v in self._timeline:
                result[ts] = v + other
            return result

        all_times = sorted(set(self.timestamps() + other.timestamps()))
        result = TemporalString()
        for ts in all_times:
            v1 = self.at(ts)
            v2 = other.at(ts)
            if v1 is not None and v2 is not None:
                result[ts] = v1 + v2
        return result

    def __radd__(self, other: str) -> TemporalString:
        result = TemporalString()
        for ts, v in self._timeline:
            result[ts] = other + v
        return result

    def upper(self) -> TemporalString:
        """Return new temporal with uppercase values."""
        result = TemporalString()
        for ts, v in self._timeline:
            result[ts] = v.upper()
        return result

    def lower(self) -> TemporalString:
        """Return new temporal with lowercase values."""
        result = TemporalString()
        for ts, v in self._timeline:
            result[ts] = v.lower()
        return result

    def contains(self, substring: str) -> TemporalBool:
        """Check if substring is in value at each point."""
        result = TemporalBool()
        for ts, v in self._timeline:
            result[ts] = substring in v
        return result

    def length(self) -> TemporalInt:
        """Get length at each point."""
        result = TemporalInt()
        for ts, v in self._timeline:
            result[ts] = len(v)
        return result

    def copy(self) -> TemporalString:
        """Create a copy."""
        new = TemporalString()
        new._timeline = list(self._timeline)
        return new