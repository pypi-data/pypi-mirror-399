"""Tests for numeric temporal types."""

from datetime import datetime, timedelta

import pytest

from chronotype import TemporalBool, TemporalFloat, TemporalInt
from chronotype.exceptions import EmptyTemporalError


class TestTemporalInt:
    def test_basic_operations(self, base_time):
        t = TemporalInt(initial=10, initial_time=base_time)
        assert t.current() == 10

    def test_addition(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        t[base_time + timedelta(days=1)] = 20

        result = t + 5
        assert result.at(base_time) == 15
        assert result.at(base_time + timedelta(days=1)) == 25

    def test_addition_temporal(self, base_time):
        t1 = TemporalInt()
        t1[base_time] = 10

        t2 = TemporalInt()
        t2[base_time] = 5

        result = t1 + t2
        assert result.at(base_time) == 15

    def test_subtraction(self, base_time):
        t = TemporalInt()
        t[base_time] = 20
        result = t - 5
        assert result.at(base_time) == 15

    def test_multiplication(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        result = t * 3
        assert result.at(base_time) == 30

    def test_division_returns_float(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        result = t / 4
        assert isinstance(result, TemporalFloat)
        assert result.at(base_time) == 2.5

    def test_floor_division(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        result = t // 3
        assert result.at(base_time) == 3

    def test_modulo(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        result = t % 3
        assert result.at(base_time) == 1

    def test_power(self, base_time):
        t = TemporalInt()
        t[base_time] = 2
        result = t**3
        assert result.at(base_time) == 8

    def test_negation(self, base_time):
        t = TemporalInt()
        t[base_time] = 10
        result = -t
        assert result.at(base_time) == -10

    def test_abs(self, base_time):
        t = TemporalInt()
        t[base_time] = -10
        result = abs(t)
        assert result.at(base_time) == 10

    def test_comparison(self, base_time):
        t = TemporalInt()
        t[base_time] = 10

        result = t > 5
        assert isinstance(result, TemporalBool)
        assert result.at(base_time) is True

        result = t < 5
        assert result.at(base_time) is False

    def test_numeric_query_aggregations(self, time_series):
        t = TemporalInt()
        t[time_series[0]] = 10
        t[time_series[1]] = 20
        t[time_series[2]] = 30

        query = t.between(time_series[0], time_series[2])
        assert query.min() == 10
        assert query.max() == 30
        assert query.sum() == 60
        assert query.simple_average() == 20


class TestTemporalFloat:
    def test_interpolation_disabled(self, base_time):
        t = TemporalFloat(interpolate=False)
        t[base_time] = 10.0
        t[base_time + timedelta(hours=2)] = 20.0

        mid = base_time + timedelta(hours=1)
        assert t.at(mid) == 10.0

    def test_interpolation_enabled(self, base_time):
        t = TemporalFloat(interpolate=True)
        t[base_time] = 10.0
        t[base_time + timedelta(hours=2)] = 20.0

        mid = base_time + timedelta(hours=1)
        assert t.at(mid) == 15.0

    def test_weighted_average(self, base_time):
        t = TemporalFloat()
        t[base_time] = 10.0
        t[base_time + timedelta(days=1)] = 30.0

        query = t.between(base_time, base_time + timedelta(days=2))
        avg = query.average()
        assert avg == pytest.approx(20.0, rel=0.01)

    def test_rate_of_change(self, base_time):
        t = TemporalFloat()
        t[base_time] = 0.0
        t[base_time + timedelta(seconds=10)] = 100.0

        query = t.between(base_time, base_time + timedelta(seconds=10))
        assert query.rate_of_change() == pytest.approx(10.0)

    def test_statistics(self, time_series):
        t = TemporalFloat()
        t[time_series[0]] = 10.0
        t[time_series[1]] = 20.0
        t[time_series[2]] = 30.0

        query = t.between(time_series[0], time_series[2])
        assert query.median() == 20.0
        assert query.variance() == pytest.approx(66.666, rel=0.01)


class TestTemporalBool:
    def test_logical_and(self, base_time):
        t = TemporalBool()
        t[base_time] = True

        result = t & True
        assert result.at(base_time) is True

        result = t & False
        assert result.at(base_time) is False

    def test_logical_or(self, base_time):
        t = TemporalBool()
        t[base_time] = False

        result = t | True
        assert result.at(base_time) is True

        result = t | False
        assert result.at(base_time) is False

    def test_logical_xor(self, base_time):
        t = TemporalBool()
        t[base_time] = True

        result = t ^ True
        assert result.at(base_time) is False

        result = t ^ False
        assert result.at(base_time) is True

    def test_invert(self, base_time):
        t = TemporalBool()
        t[base_time] = True
        result = ~t
        assert result.at(base_time) is False

    def test_when_true(self, base_time):
        t = TemporalBool()
        t[base_time] = True
        t[base_time + timedelta(hours=2)] = False
        t[base_time + timedelta(hours=4)] = True

        ranges = t.when_true()
        assert len(ranges) >= 1

    def test_duration_true(self, base_time):
        t = TemporalBool()
        t[base_time] = True
        t[base_time + timedelta(hours=2)] = False

        duration = t.duration_true()
        assert duration >= 7200