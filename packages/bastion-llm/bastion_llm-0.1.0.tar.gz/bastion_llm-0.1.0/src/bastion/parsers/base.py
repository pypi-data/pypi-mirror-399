"""Base parser classes and protocols."""

from typing import Protocol

from tree_sitter import Language, Parser, Tree


class FileParser(Protocol):
    """Protocol for file parsers."""

    def parse(self, content: str) -> Tree:
        """Parse content and return AST."""
        ...

    @property
    def language(self) -> str:
        """Return the language name."""
        ...


class TreeSitterParser:
    """Parser using tree-sitter for AST generation."""

    def __init__(self, language_name: str, language: Language) -> None:
        self._language_name = language_name
        self._parser = Parser(language)

    def parse(self, content: str) -> Tree:
        """Parse content and return tree-sitter AST."""
        return self._parser.parse(bytes(content, "utf-8"))

    @property
    def language(self) -> str:
        """Return the language name for this parser."""
        return self._language_name
