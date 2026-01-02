"""Tests for parser utilities."""

import pytest

from bastion.parsers import (
    ParserRegistry,
    find_nodes_by_type,
    find_nodes_by_types,
    get_node_text,
    get_parent_function,
)

pytestmark = pytest.mark.unit


class TestParserRegistry:
    """Test the ParserRegistry class."""

    def test_get_python_parser(self) -> None:
        """Should return Python parser."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")

        assert parser is not None
        assert parser.language == "python"

    def test_get_javascript_parser(self) -> None:
        """Should return JavaScript parser."""
        registry = ParserRegistry()
        parser = registry.get_parser("javascript")

        assert parser is not None
        assert parser.language == "javascript"

    def test_get_typescript_parser(self) -> None:
        """Should return TypeScript parser."""
        registry = ParserRegistry()
        parser = registry.get_parser("typescript")

        assert parser is not None
        assert parser.language == "typescript"

    def test_get_tsx_parser(self) -> None:
        """Should return TSX parser."""
        registry = ParserRegistry()
        parser = registry.get_parser("tsx")

        assert parser is not None
        assert parser.language == "tsx"

    def test_get_nonexistent_parser(self) -> None:
        """Should return None for unknown language."""
        registry = ParserRegistry()
        parser = registry.get_parser("unknown")

        assert parser is None

    def test_get_parser_for_python_file(self, tmp_path) -> None:
        """Should return Python parser for .py files."""
        from pathlib import Path

        registry = ParserRegistry()
        parser = registry.get_parser_for_file(Path("test.py"))

        assert parser is not None
        assert parser.language == "python"

    def test_get_parser_for_js_file(self, tmp_path) -> None:
        """Should return JavaScript parser for .js files."""
        from pathlib import Path

        registry = ParserRegistry()
        parser = registry.get_parser_for_file(Path("test.js"))

        assert parser is not None
        assert parser.language == "javascript"

    def test_get_parser_for_ts_file(self, tmp_path) -> None:
        """Should return TypeScript parser for .ts files."""
        from pathlib import Path

        registry = ParserRegistry()
        parser = registry.get_parser_for_file(Path("test.ts"))

        assert parser is not None
        assert parser.language == "typescript"

    def test_get_parser_for_unknown_file(self) -> None:
        """Should return None for unknown file type."""
        from pathlib import Path

        registry = ParserRegistry()
        parser = registry.get_parser_for_file(Path("test.txt"))

        assert parser is None


class TestParserUtils:
    """Test parser utility functions."""

    def test_get_node_text(self) -> None:
        """Should extract text from AST node."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        code = "x = 42"
        tree = parser.parse(code)
        source_bytes = code.encode("utf-8")

        # Get the root node text
        text = get_node_text(tree.root_node, source_bytes)
        assert text == "x = 42"

    def test_find_nodes_by_type(self) -> None:
        """Should find all nodes of a given type."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        code = """
x = 1
y = 2
z = 3
"""
        tree = parser.parse(code)

        # Find all assignment nodes
        assignments = find_nodes_by_type(tree.root_node, "assignment")
        assert len(assignments) == 3

    def test_find_nodes_by_types(self) -> None:
        """Should find nodes matching any of the given types."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        code = """
def foo():
    pass

class Bar:
    pass
"""
        tree = parser.parse(code)

        # Find both function and class definitions
        nodes = find_nodes_by_types(
            tree.root_node,
            {"function_definition", "class_definition"}
        )
        assert len(nodes) == 2

    def test_get_parent_function(self) -> None:
        """Should find parent function of a node."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        code = """
def outer():
    x = 1
    return x
"""
        tree = parser.parse(code)

        # Find the assignment node
        assignments = find_nodes_by_type(tree.root_node, "assignment")
        assert len(assignments) == 1

        # Get its parent function
        parent = get_parent_function(assignments[0])
        assert parent is not None
        assert parent.type == "function_definition"

    def test_get_parent_function_no_parent(self) -> None:
        """Should return None if no parent function exists."""
        registry = ParserRegistry()
        parser = registry.get_parser("python")
        assert parser is not None

        code = "x = 1"  # Module-level assignment
        tree = parser.parse(code)

        assignments = find_nodes_by_type(tree.root_node, "assignment")
        assert len(assignments) == 1

        parent = get_parent_function(assignments[0])
        assert parent is None
