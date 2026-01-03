"""Interpolation strategies for temporal values."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")
N = TypeVar("N", int, float)


class InterpolationStrategy(ABC, Generic[T]):
    """Abstract base class for interpolation strategies."""

    @abstractmethod
    def interpolate(
        self,
        target: datetime,
        before: Optional[Tuple[datetime, T]],
        after: Optional[Tuple[datetime, T]],
    ) -> Optional[T]:
        """
        Interpolate a value at the target timestamp.

        Args:
            target: The timestamp to interpolate at
            before: The entry before target (timestamp, value) or None
            after: The entry after target (timestamp, value) or None

        Returns:
            The interpolated value, or None if interpolation is not possible
        """
        pass


class StepInterpolation(InterpolationStrategy[T]):
    """
    Step interpolation - returns the most recent value before the target.
    This is the default strategy.
    """

    def interpolate(
        self,
        target: datetime,
        before: Optional[Tuple[datetime, T]],
        after: Optional[Tuple[datetime, T]],
    ) -> Optional[T]:
        if before is not None:
            return before[1]
        return None


class LinearInterpolation(InterpolationStrategy[N]):
    """
    Linear interpolation for numeric types.
    Calculates value based on linear progression between points.
    """

    def interpolate(
        self,
        target: datetime,
        before: Optional[Tuple[datetime, N]],
        after: Optional[Tuple[datetime, N]],
    ) -> Optional[N]:
        if before is None and after is None:
            return None

        if before is None:
            return after[1] if after else None

        if after is None:
            return before[1]

        before_ts, before_val = before
        after_ts, after_val = after

        if before_ts == after_ts:
            return before_val

        total_delta = (after_ts - before_ts).total_seconds()
        target_delta = (target - before_ts).total_seconds()

        if total_delta == 0:
            return before_val

        ratio = target_delta / total_delta
        result = before_val + (after_val - before_val) * ratio

        if isinstance(before_val, int) and isinstance(after_val, int):
            return int(result)
        return result


class NearestInterpolation(InterpolationStrategy[T]):
    """
    Nearest neighbor interpolation.
    Returns the value from the closest timestamp.
    """

    def interpolate(
        self,
        target: datetime,
        before: Optional[Tuple[datetime, T]],
        after: Optional[Tuple[datetime, T]],
    ) -> Optional[T]:
        if before is None and after is None:
            return None

        if before is None:
            return after[1] if after else None

        if after is None:
            return before[1]

        before_delta = (target - before[0]).total_seconds()
        after_delta = (after[0] - target).total_seconds()

        if before_delta <= after_delta:
            return before[1]
        return after[1]