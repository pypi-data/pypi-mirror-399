# Chronotype

**Temporal-native data types for Python.** Every value inherently carries its full history.

[![PyPI version](https://badge.fury.io/py/chronotype.svg)](https://badge.fury.io/py/chronotype)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install chronotype
```

## Quick Start

```python
from datetime import date, datetime
from chronotype import TemporalInt, TemporalFloat, TemporalString

# Create a temporal integer that tracks salary over time
salary = TemporalInt()
salary[date(2020, 1, 1)] = 50000
salary[date(2022, 6, 1)] = 65000
salary[date(2024, 1, 1)] = 80000

# Query at specific points in time
print(salary.at(date(2021, 3, 15)))  # 50000
print(salary.at(date(2023, 1, 1)))   # 65000

# Get the current (latest) value
print(salary.current())  # 80000

# Analyze over time ranges
query = salary.between(date(2020, 1, 1), date(2024, 1, 1))
print(query.average())   # Weighted average by duration
print(query.min())       # 50000
print(query.max())       # 80000

# Interpolation for numeric types
temp = TemporalFloat(interpolate=True)
temp[datetime(2024, 1, 1, 0, 0)] = 20.0
temp[datetime(2024, 1, 1, 12, 0)] = 25.0

print(temp.at(datetime(2024, 1, 1, 6, 0)))  # 22.5 (interpolated)
```

## Features


- **Temporal Primitives**: `TemporalInt`, `TemporalFloat`, `TemporalString`, `TemporalBool`
- **Temporal Containers**: `TemporalList`, `TemporalDict`, `TemporalSet`
- **Generic Wrapper**: `Temporal[T]` for any type
- **Time Queries**: `.at()`, `.between()`, `.current()`, `.first()`
- **Aggregations**: `.average()`, `.min()`, `.max()`, `.sum()`, `.count()`
- **Interpolation**: Linear interpolation for numeric types
- **History**: `.history()`, `.changes()`, `.rollback()`
- **Arithmetic**: Full operator support for numeric temporals
- **Serialization**: JSON and pickle support


## Documentation

### Creating Temporal Values
```python
from chronotype import Temporal, TemporalInt

# With initial value (uses current time)
count = TemporalInt(initial=0)

# Empty, to be populated
score = TemporalInt()

# Generic temporal for custom types
from dataclasses import dataclass

@dataclass
class User:
    name: str
    active: bool

user = Temporal[User]()
user[datetime.now()] = User("Alice", True)
```

### Time Range Queries
```python
query = salary.between(date(2020, 1, 1), date(2023, 12, 31))

# Aggregations (weighted by duration)
query.average()
query.sum()
query.min()
query.max()
query.count()

# Get all entries
query.entries()  # List of (timestamp, value) tuples
query.values()   # List of values only
query.timestamps()  # List of timestamps only
```

### History Operations
```python
# Full history
for timestamp, value in salary.history():
    print(f"{timestamp}: {value}")

# Detect changes
for timestamp, old_val, new_val in salary.changes():
    print(f"{timestamp}: {old_val} -> {new_val}")

# Rollback to previous state
salary.rollback()  # Remove last entry
salary.rollback(to=date(2022, 1, 1))  # Remove all entries after date
```

### Arithmetic Operations
```python
a = TemporalInt(initial=10)
b = TemporalInt(initial=5)

# Operations create new temporals with aligned timestamps
c = a + b  # TemporalInt
c = a - b
c = a * b
c = a / b  # Returns TemporalFloat
c = a // b
c = a % b
c = a ** b

# Comparison creates TemporalBool
is_greater = a > b
```

## License
MIT License - see [LICENSE](LICENSE) file for details.