"""Utility functions for working with tree-sitter AST nodes."""

from typing import Any


def get_node_text(node: Any, source: bytes) -> str:
    """Get the text content of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8")


def find_nodes_by_type(node: Any, type_name: str) -> list[Any]:
    """Find all descendant nodes of a given type."""
    results = []
    if node.type == type_name:
        results.append(node)
    for child in node.children:
        results.extend(find_nodes_by_type(child, type_name))
    return results


def find_nodes_by_types(node: Any, type_names: set[str]) -> list[Any]:
    """Find all descendant nodes matching any of the given types."""
    results = []
    if node.type in type_names:
        results.append(node)
    for child in node.children:
        results.extend(find_nodes_by_types(child, type_names))
    return results


def get_parent_function(node: Any) -> Any | None:
    """Get the parent function/method definition of a node."""
    current = node.parent
    while current:
        if current.type in ("function_definition", "function_declaration", "method_definition"):
            return current
        current = current.parent
    return None
