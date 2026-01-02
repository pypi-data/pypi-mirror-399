"""Tests for utility functions."""

from pathlib import Path

import pytest

from bastion.utils import count_tokens_approx, get_relative_path, truncate_string

pytestmark = pytest.mark.unit


class TestGetRelativePath:
    """Test get_relative_path function."""

    def test_relative_path_from_cwd(self, tmp_path: Path) -> None:
        """Should return relative path from current directory."""
        file_path = tmp_path / "subdir" / "file.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        result = get_relative_path(file_path, tmp_path)
        # Normalize separators for comparison
        assert result.replace("\\", "/") == "subdir/file.py"

    def test_relative_path_default_base(self, tmp_path: Path, monkeypatch) -> None:
        """Should use current directory as default base."""
        monkeypatch.chdir(tmp_path)
        file_path = tmp_path / "test.py"
        file_path.touch()

        result = get_relative_path(file_path)
        assert result == "test.py"

    def test_unrelated_path(self) -> None:
        """Should return absolute path if not relative to base."""
        file_path = Path("/some/absolute/path/file.py")
        base_path = Path("/different/base")

        result = get_relative_path(file_path, base_path)
        # Should return original path when not relative
        assert "file.py" in result


class TestTruncateString:
    """Test truncate_string function."""

    def test_short_string(self) -> None:
        """Should not truncate short strings."""
        result = truncate_string("hello", max_length=80)
        assert result == "hello"

    def test_exact_length(self) -> None:
        """Should not truncate string at exact max length."""
        text = "a" * 80
        result = truncate_string(text, max_length=80)
        assert result == text

    def test_long_string(self) -> None:
        """Should truncate long strings with suffix."""
        text = "a" * 100
        result = truncate_string(text, max_length=80)

        assert len(result) == 80
        assert result.endswith("...")

    def test_custom_suffix(self) -> None:
        """Should use custom suffix."""
        text = "a" * 100
        result = truncate_string(text, max_length=50, suffix="[...]")

        assert len(result) == 50
        assert result.endswith("[...]")


class TestCountTokensApprox:
    """Test count_tokens_approx function."""

    def test_empty_string(self) -> None:
        """Should return 0 for empty string."""
        result = count_tokens_approx("")
        assert result == 0

    def test_short_string(self) -> None:
        """Should estimate tokens for short string."""
        # "hello" is 5 chars, so 5/4 = 1 token
        result = count_tokens_approx("hello")
        assert result == 1

    def test_longer_string(self) -> None:
        """Should estimate tokens for longer string."""
        # 100 chars should be ~25 tokens
        text = "a" * 100
        result = count_tokens_approx(text)
        assert result == 25

    def test_realistic_text(self) -> None:
        """Should give reasonable estimate for realistic text."""
        text = "This is a sample sentence with some words in it."
        result = count_tokens_approx(text)
        # 49 chars / 4 = 12 tokens (rough estimate)
        assert result == 12
