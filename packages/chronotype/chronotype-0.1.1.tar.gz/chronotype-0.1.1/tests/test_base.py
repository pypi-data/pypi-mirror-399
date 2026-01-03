"""Tests for base Temporal class."""

from datetime import date, datetime, timedelta

import pytest

from chronotype import Temporal
from chronotype.exceptions import EmptyTemporalError, InvalidTimestampError


class TestTemporalBasics:
    def test_create_empty(self):
        t = Temporal[int]()
        assert len(t) == 0
        assert not t

    def test_create_with_initial(self):
        t = Temporal[int](initial=42)
        assert len(t) == 1
        assert t.current() == 42

    def test_set_and_get(self, base_time):
        t = Temporal[str]()
        t[base_time] = "hello"
        assert t.at(base_time) == "hello"

    def test_multiple_values(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series):
            t[ts] = i * 10

        assert t.at(time_series[0]) == 0
        assert t.at(time_series[5]) == 50
        assert t.at(time_series[9]) == 90

    def test_query_between_times(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series):
            t[ts] = i

        halfway = time_series[3] + timedelta(hours=12)
        assert t.at(halfway) == 3

    def test_first_and_current(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 100
        t[time_series[5]] = 200

        assert t.first() == 100
        assert t.current() == 200

    def test_empty_raises(self):
        t = Temporal[int]()
        with pytest.raises(EmptyTemporalError):
            t.current()
        with pytest.raises(EmptyTemporalError):
            t.first()

    def test_history(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 1
        t[time_series[1]] = 2
        t[time_series[2]] = 3

        history = t.history()
        assert len(history) == 3
        assert history[0] == (time_series[0], 1)
        assert history[2] == (time_series[2], 3)

    def test_changes(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 10
        t[time_series[1]] = 20
        t[time_series[2]] = 30

        changes = t.changes()
        assert len(changes) == 3
        assert changes[0] == (time_series[0], None, 10)
        assert changes[1] == (time_series[1], 10, 20)
        assert changes[2] == (time_series[2], 20, 30)

    def test_rollback_steps(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 1
        t[time_series[1]] = 2
        t[time_series[2]] = 3

        t.rollback(steps=1)
        assert t.current() == 2
        assert len(t) == 2

    def test_rollback_to_time(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 1
        t[time_series[1]] = 2
        t[time_series[2]] = 3

        t.rollback(to=time_series[1])
        assert t.current() == 2
        assert len(t) == 2

    def test_between_query(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series):
            t[ts] = i

        query = t.between(time_series[2], time_series[5])
        assert query.count() == 4
        assert query.values() == [2, 3, 4, 5]

    def test_date_support(self):
        t = Temporal[int]()
        t[date(2024, 1, 1)] = 100
        t[date(2024, 6, 1)] = 200

        assert t.at(date(2024, 3, 1)) == 100
        assert t.at(date(2024, 8, 1)) == 200

    def test_contains(self, base_time):
        t = Temporal[int]()
        t[base_time] = 42
        assert base_time in t
        assert (base_time + timedelta(days=1)) not in t

    def test_iteration(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 1
        t[time_series[1]] = 2

        entries = list(t)
        assert len(entries) == 2
        assert entries[0] == (time_series[0], 1)

    def test_copy(self, base_time):
        t = Temporal[int](initial=42, initial_time=base_time)
        t2 = t.copy()

        t2[base_time + timedelta(days=1)] = 100

        assert t.current() == 42
        assert t2.current() == 100

    def test_merge(self, time_series):
        t1 = Temporal[int]()
        t1[time_series[0]] = 1
        t1[time_series[2]] = 3

        t2 = Temporal[int]()
        t2[time_series[1]] = 2
        t2[time_series[2]] = 30

        merged = t1.merge(t2, prefer_self=True)
        assert merged.at(time_series[0]) == 1
        assert merged.at(time_series[1]) == 2
        assert merged.at(time_series[2]) == 3

    def test_serialization_json(self, base_time):
        t = Temporal[int]()
        t[base_time] = 42
        t[base_time + timedelta(days=1)] = 100

        json_str = t.to_json()
        t2 = Temporal[int].from_json(json_str)

        assert t2.at(base_time) == 42
        assert len(t2) == 2

    def test_repr(self, base_time):
        t = Temporal[int](initial=42, initial_time=base_time)
        assert "Temporal" in repr(t)
        assert "42" in repr(t)

    def test_equality(self, base_time):
        t1 = Temporal[int]()
        t1[base_time] = 42

        t2 = Temporal[int]()
        t2[base_time] = 42

        assert t1 == t2

    def test_slice(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series):
            t[ts] = i

        sliced = t.slice(time_series[2], time_series[5])
        assert len(sliced) == 4
        assert sliced.first() == 2


class TestTemporalQuery:
    def test_query_empty(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 1

        query = t.between(time_series[5], time_series[8])
        assert query.is_empty()
        assert query.count() == 0

    def test_query_filter(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series):
            t[ts] = i

        query = t.between(time_series[0], time_series[9])
        filtered = query.filter(lambda x: x % 2 == 0)
        assert filtered.values() == [0, 2, 4, 6, 8]

    def test_query_map(self, time_series):
        t = Temporal[int]()
        for i, ts in enumerate(time_series[:3]):
            t[ts] = i

        query = t.between(time_series[0], time_series[2])
        mapped = query.map(lambda x: x * 10)
        assert mapped.values() == [0, 10, 20]

    def test_query_first_last(self, time_series):
        t = Temporal[int]()
        t[time_series[0]] = 10
        t[time_series[5]] = 50

        query = t.between(time_series[0], time_series[9])
        assert query.first_value() == 10
        assert query.last_value() == 50