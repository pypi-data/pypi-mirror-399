"""Tests for query functionality."""

from datetime import timedelta

import pytest

from chronotype import TemporalFloat, TemporalInt
from chronotype.exceptions import EmptyTemporalError


class TestNumericQuery:
    def test_min_max(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 5
        t[time_series[1]] = 10
        t[time_series[2]] = 3

        query = t.between(time_series[0], time_series[2])
        assert query.min() == 3
        assert query.max() == 10

    def test_sum(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 10
        t[time_series[1]] = 20
        t[time_series[2]] = 30

        query = t.between(time_series[0], time_series[2])
        assert query.sum() == 60

    def test_simple_average(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 10
        t[time_series[1]] = 20
        t[time_series[2]] = 30

        query = t.between(time_series[0], time_series[2])
        assert query.simple_average() == 20

    def test_median(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 10
        t[time_series[1]] = 30
        t[time_series[2]] = 20

        query = t.between(time_series[0], time_series[2])
        assert query.median() == 20

    def test_delta(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 100
        t[time_series[1]] = 150

        query = t.between(time_series[0], time_series[1])
        assert query.delta() == 50

    def test_empty_query_raises(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 10

        query = t.between(time_series[5], time_series[8])

        with pytest.raises(EmptyTemporalError):
            query.min()
        with pytest.raises(EmptyTemporalError):
            query.max()
        with pytest.raises(EmptyTemporalError):
            query.average()

    def test_exclude_boundaries(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 1
        t[time_series[1]] = 2
        t[time_series[2]] = 3

        query = t.between(time_series[0], time_series[2], include_start=False, include_end=False)
        assert query.count() == 1
        assert query.values() == [2]

    def test_filter_in_query(self, time_series):
        t = TemporalInt()
        for i, ts in enumerate(time_series):
            t[ts] = i

        query = t.between(time_series[0], time_series[9])
        filtered = query.filter(lambda x: x > 5)
        assert filtered.values() == [6, 7, 8, 9]

    def test_weighted_average_calculation(self, base_time):
        t = TemporalFloat()
        t[base_time] = 10.0
        t[base_time + timedelta(days=1)] = 20.0

        query = t.between(base_time, base_time + timedelta(days=2))
        avg = query.average()
        assert avg == pytest.approx(15.0, rel=0.1)