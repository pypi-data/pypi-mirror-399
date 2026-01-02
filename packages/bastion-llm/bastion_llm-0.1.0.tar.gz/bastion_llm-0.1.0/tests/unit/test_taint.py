"""Tests for taint analysis module."""

import pytest

from bastion.taint import TaintFlow, TaintSink, TaintSource, TaintTracker

pytestmark = pytest.mark.unit


class TestTaintSource:
    """Test TaintSource dataclass."""

    def test_create_source(self) -> None:
        """Should create a taint source."""
        source = TaintSource(
            name="user_input",
            node=None,
            line=10,
            source_type="parameter",
        )

        assert source.name == "user_input"
        assert source.line == 10
        assert source.source_type == "parameter"


class TestTaintSink:
    """Test TaintSink dataclass."""

    def test_create_sink(self) -> None:
        """Should create a taint sink."""
        sink = TaintSink(
            name="llm.invoke",
            node=None,
            line=25,
            sink_type="llm_call",
        )

        assert sink.name == "llm.invoke"
        assert sink.line == 25
        assert sink.sink_type == "llm_call"


class TestTaintFlow:
    """Test TaintFlow dataclass."""

    def test_create_flow(self) -> None:
        """Should create a taint flow."""
        source = TaintSource("input", None, 5, "parameter")
        sink = TaintSink("output", None, 10, "llm_call")

        flow = TaintFlow(
            source=source,
            sink=sink,
            path=["input", "processed", "output"],
        )

        assert flow.source == source
        assert flow.sink == sink
        assert len(flow.path) == 3

    def test_flow_default_path(self) -> None:
        """Should have empty path by default."""
        source = TaintSource("input", None, 5, "parameter")
        sink = TaintSink("output", None, 10, "llm_call")

        flow = TaintFlow(source=source, sink=sink)

        assert flow.path == []


class TestTaintTracker:
    """Test TaintTracker class."""

    def test_mark_tainted(self) -> None:
        """Should mark a variable as tainted."""
        tracker = TaintTracker()
        source = TaintSource("user_input", None, 5, "parameter")

        tracker.mark_tainted("input_var", source)

        assert tracker.is_tainted("input_var")

    def test_is_not_tainted(self) -> None:
        """Should return False for non-tainted variable."""
        tracker = TaintTracker()

        assert not tracker.is_tainted("clean_var")

    def test_get_source(self) -> None:
        """Should return source of tainted variable."""
        tracker = TaintTracker()
        source = TaintSource("user_input", None, 5, "request")

        tracker.mark_tainted("data", source)
        retrieved = tracker.get_source("data")

        assert retrieved is not None
        assert retrieved.name == "user_input"
        assert retrieved.source_type == "request"

    def test_get_source_not_found(self) -> None:
        """Should return None for non-tainted variable."""
        tracker = TaintTracker()

        result = tracker.get_source("nonexistent")

        assert result is None

    def test_propagate_taint(self) -> None:
        """Should propagate taint from one variable to another."""
        tracker = TaintTracker()
        source = TaintSource("input", None, 1, "parameter")

        tracker.mark_tainted("original", source)
        tracker.propagate("original", "derived")

        assert tracker.is_tainted("derived")
        assert tracker.get_source("derived") == source

    def test_propagate_non_tainted(self) -> None:
        """Should not propagate from non-tainted variable."""
        tracker = TaintTracker()

        tracker.propagate("clean", "derived")

        assert not tracker.is_tainted("derived")

    def test_clear_taint(self) -> None:
        """Should clear all taint tracking."""
        tracker = TaintTracker()
        source = TaintSource("input", None, 1, "parameter")

        tracker.mark_tainted("var1", source)
        tracker.mark_tainted("var2", source)
        tracker.clear()

        assert not tracker.is_tainted("var1")
        assert not tracker.is_tainted("var2")
