"""Tests for temporal container types."""

from datetime import timedelta

import pytest

from chronotype import TemporalDict, TemporalList
from chronotype.exceptions import EmptyTemporalError


class TestTemporalList:
    def test_create_with_initial(self, base_time):
        t = TemporalList(initial=[1, 2, 3], initial_time=base_time)
        assert t.current() == [1, 2, 3]

    def test_append(self, base_time):
        t = TemporalList(initial=[1], initial_time=base_time)
        t.append(2, base_time + timedelta(days=1))

        assert t.at(base_time) == [1]
        assert t.at(base_time + timedelta(days=1)) == [1, 2]

    def test_extend(self, base_time):
        t = TemporalList(initial=[1], initial_time=base_time)
        t.extend([2, 3], base_time + timedelta(days=1))

        assert t.current() == [1, 2, 3]

    def test_insert(self, base_time):
        t = TemporalList(initial=[1, 3], initial_time=base_time)
        t.insert(1, 2, base_time + timedelta(days=1))

        assert t.current() == [1, 2, 3]

    def test_remove(self, base_time):
        t = TemporalList(initial=[1, 2, 3], initial_time=base_time)
        t.remove(2, base_time + timedelta(days=1))

        assert t.at(base_time) == [1, 2, 3]
        assert t.current() == [1, 3]

    def test_pop(self, base_time):
        t = TemporalList(initial=[1, 2, 3], initial_time=base_time)
        value = t.pop(timestamp=base_time + timedelta(days=1))

        assert value == 3
        assert t.current() == [1, 2]

    def test_history_preserves_copies(self, base_time):
        t = TemporalList(initial=[1], initial_time=base_time)
        t.append(2, base_time + timedelta(days=1))

        history = t.history()
        assert history[0][1] == [1]
        assert history[1][1] == [1, 2]

    def test_contains_at(self, base_time):
        t = TemporalList(initial=[1, 2, 3], initial_time=base_time)
        assert t.contains_at(base_time, 2) is True
        assert t.contains_at(base_time, 5) is False

    def test_get_item_at(self, base_time):
        t = TemporalList(initial=[10, 20, 30], initial_time=base_time)
        assert t.get_item_at(base_time, 1) == 20
        assert t.get_item_at(base_time, -1) == 30

    def test_len_at(self, base_time):
        t = TemporalList(initial=[1, 2, 3], initial_time=base_time)
        t.append(4, base_time + timedelta(days=1))

        assert t.len_at(base_time) == 3
        assert t.len_at(base_time + timedelta(days=1)) == 4


class TestTemporalDict:
    def test_create_with_initial(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        assert t.current() == {"a": 1}

    def test_set_item(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        t.set_item("b", 2, base_time + timedelta(days=1))

        assert t.at(base_time) == {"a": 1}
        assert t.current() == {"a": 1, "b": 2}

    def test_delete_item(self, base_time):
        t = TemporalDict(initial={"a": 1, "b": 2}, initial_time=base_time)
        t.delete_item("a", base_time + timedelta(days=1))

        assert t.at(base_time) == {"a": 1, "b": 2}
        assert t.current() == {"b": 2}

    def test_update_dict(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        t.update_dict({"b": 2, "c": 3}, base_time + timedelta(days=1))

        assert t.current() == {"a": 1, "b": 2, "c": 3}

    def test_pop_item(self, base_time):
        t = TemporalDict(initial={"a": 1, "b": 2}, initial_time=base_time)
        value = t.pop_item("a", base_time + timedelta(days=1))

        assert value == 1
        assert t.current() == {"b": 2}

    def test_get_item_at(self, base_time):
        t = TemporalDict(initial={"a": 1, "b": 2}, initial_time=base_time)
        assert t.get_item_at(base_time, "a") == 1
        assert t.get_item_at(base_time, "c") is None

    def test_contains_key_at(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        assert t.contains_key_at(base_time, "a") is True
        assert t.contains_key_at(base_time, "b") is False

    def test_keys_values_items_at(self, base_time):
        t = TemporalDict(initial={"a": 1, "b": 2}, initial_time=base_time)

        keys = t.keys_at(base_time)
        values = t.values_at(base_time)
        items = t.items_at(base_time)
        
        assert keys is not None and set(keys) == {"a", "b"}
        assert values is not None and set(values) == {1, 2}
        assert items is not None and set(items) == {("a", 1), ("b", 2)}

    def test_key_history(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        t.set_item("a", 2, base_time + timedelta(days=1))
        t.set_item("a", 3, base_time + timedelta(days=2))

        history = t.key_history("a")
        assert len(history) == 3
        assert history[0][1] == 1
        assert history[1][1] == 2
        assert history[2][1] == 3

    def test_history_preserves_copies(self, base_time):
        t = TemporalDict(initial={"a": 1}, initial_time=base_time)
        t.set_item("b", 2, base_time + timedelta(days=1))

        history = t.history()
        assert history[0][1] == {"a": 1}
        assert history[1][1] == {"a": 1, "b": 2}