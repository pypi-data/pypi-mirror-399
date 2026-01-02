"""Parser registry for managing language parsers."""

from pathlib import Path

import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_typescript
from tree_sitter import Language

from .base import TreeSitterParser


class ParserRegistry:
    """Registry for language parsers."""

    def __init__(self) -> None:
        self._parsers: dict[str, TreeSitterParser] = {}
        self._extension_map: dict[str, str] = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
        }
        self._initialize_parsers()

    def _initialize_parsers(self) -> None:
        """Initialize built-in parsers."""
        # Python parser
        py_language = Language(tree_sitter_python.language())
        self._parsers["python"] = TreeSitterParser("python", py_language)

        # JavaScript parser
        js_language = Language(tree_sitter_javascript.language())
        self._parsers["javascript"] = TreeSitterParser("javascript", js_language)

        # TypeScript parser (proper tree-sitter-typescript)
        ts_language = Language(tree_sitter_typescript.language_typescript())
        self._parsers["typescript"] = TreeSitterParser("typescript", ts_language)

        # TSX parser (TypeScript with JSX)
        tsx_language = Language(tree_sitter_typescript.language_tsx())
        self._parsers["tsx"] = TreeSitterParser("tsx", tsx_language)

    def get_parser(self, language: str) -> TreeSitterParser | None:
        """Get parser for a language."""
        return self._parsers.get(language)

    def get_parser_for_file(self, file_path: Path) -> TreeSitterParser | None:
        """Get parser for a file based on extension."""
        ext = file_path.suffix.lower()
        language = self._extension_map.get(ext)
        if language:
            return self.get_parser(language)
        return None

    def register_parser(self, language: str, parser: TreeSitterParser) -> None:
        """Register a parser for a language."""
        self._parsers[language] = parser

    def register_extension(self, extension: str, language: str) -> None:
        """Map a file extension to a language."""
        self._extension_map[extension] = language
