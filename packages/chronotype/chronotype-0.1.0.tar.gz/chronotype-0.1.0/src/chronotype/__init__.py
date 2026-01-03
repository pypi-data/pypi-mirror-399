"""
Chronotype - Temporal-native data types for Python.

Every value inherently carries its full history.
"""

from chronotype.base import Temporal
from chronotype.containers import TemporalDict, TemporalList
from chronotype.exceptions import (
    ChronotypeError,
    EmptyTemporalError,
    InterpolationError,
    InvalidTimestampError,
)
from chronotype.interpolation import InterpolationStrategy, LinearInterpolation, StepInterpolation
from chronotype.numeric import TemporalBool, TemporalFloat, TemporalInt
from chronotype.query import TemporalQuery

__version__ = "0.1.0"

__all__ = [
    # Core
    "Temporal",
    # Numeric types
    "TemporalInt",
    "TemporalFloat",
    "TemporalBool",
    # Containers
    "TemporalList",
    "TemporalDict",
    # Query
    "TemporalQuery",
    # Interpolation
    "InterpolationStrategy",
    "LinearInterpolation",
    "StepInterpolation",
    # Exceptions
    "ChronotypeError",
    "EmptyTemporalError",
    "InvalidTimestampError",
    "InterpolationError",
]