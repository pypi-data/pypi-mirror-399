"""Helper utility functions for Bastion."""

from pathlib import Path


def get_relative_path(file_path: Path, base_path: Path | None = None) -> str:
    """Get relative path from base or current directory."""
    if base_path is None:
        base_path = Path.cwd()

    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)


def truncate_string(s: str, max_length: int = 80, suffix: str = "...") -> str:
    """Truncate a string to max_length, adding suffix if truncated."""
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def count_tokens_approx(text: str) -> int:
    """Approximate token count (rough estimate: 4 chars per token)."""
    return len(text) // 4
