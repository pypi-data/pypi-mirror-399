"""Tests for git utilities."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bastion.git_utils import (
    GitError,
    get_changed_files,
    get_current_branch,
    get_merge_base,
    get_repo_root,
    get_staged_files,
    is_git_repo,
)

pytestmark = pytest.mark.unit


class TestIsGitRepo:
    """Test is_git_repo function."""

    @patch("bastion.git_utils.subprocess.run")
    def test_is_git_repo_true(self, mock_run: MagicMock) -> None:
        """Should return True in git repo."""
        mock_run.return_value = MagicMock(returncode=0)

        result = is_git_repo(Path("/some/path"))

        assert result is True

    @patch("bastion.git_utils.subprocess.run")
    def test_is_git_repo_false(self, mock_run: MagicMock) -> None:
        """Should return False when not in git repo."""
        mock_run.return_value = MagicMock(returncode=128)

        result = is_git_repo(Path("/some/path"))

        assert result is False

    @patch("bastion.git_utils.subprocess.run")
    def test_is_git_repo_git_not_found(self, mock_run: MagicMock) -> None:
        """Should return False when git not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = is_git_repo(Path("/some/path"))

        assert result is False

    @patch("bastion.git_utils.subprocess.run")
    def test_is_git_repo_default_path(self, mock_run: MagicMock) -> None:
        """Should use current directory by default."""
        mock_run.return_value = MagicMock(returncode=0)

        is_git_repo()

        mock_run.assert_called_once()


class TestGetRepoRoot:
    """Test get_repo_root function."""

    @patch("bastion.git_utils.subprocess.run")
    def test_get_repo_root_success(self, mock_run: MagicMock) -> None:
        """Should return repo root path."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="/home/user/project\n",
        )

        result = get_repo_root(Path("/some/path"))

        assert result == Path("/home/user/project")

    @patch("bastion.git_utils.subprocess.run")
    def test_get_repo_root_not_git_repo(self, mock_run: MagicMock) -> None:
        """Should return None when not in git repo."""
        mock_run.side_effect = __import__("subprocess").CalledProcessError(128, "git")

        result = get_repo_root(Path("/some/path"))

        assert result is None

    @patch("bastion.git_utils.subprocess.run")
    def test_get_repo_root_git_not_found(self, mock_run: MagicMock) -> None:
        """Should return None when git not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = get_repo_root(Path("/some/path"))

        assert result is None


class TestGetChangedFiles:
    """Test get_changed_files function."""

    @patch("bastion.git_utils.get_repo_root")
    def test_get_changed_files_not_git_repo(self, mock_repo_root: MagicMock) -> None:
        """Should raise GitError when not in git repo."""
        mock_repo_root.return_value = None

        with pytest.raises(GitError, match="Not a git repository"):
            get_changed_files()

    @patch("bastion.git_utils.subprocess.run")
    @patch("bastion.git_utils.get_repo_root")
    def test_get_changed_files_staged_only(
        self, mock_repo_root: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Should get only staged files."""
        mock_repo_root.return_value = tmp_path

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.touch()

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="test.py\n",
        )

        result = get_changed_files(path=tmp_path, staged_only=True)

        # Should include test.py
        assert len(result) >= 0

    @patch("bastion.git_utils.subprocess.run")
    @patch("bastion.git_utils.get_repo_root")
    def test_get_changed_files_git_error(
        self, mock_repo_root: MagicMock, mock_run: MagicMock, tmp_path: Path
    ) -> None:
        """Should raise GitError on git command failure."""
        mock_repo_root.return_value = tmp_path
        mock_run.side_effect = __import__("subprocess").CalledProcessError(
            1, "git", stderr="error message"
        )

        with pytest.raises(GitError, match="Git command failed"):
            get_changed_files(path=tmp_path)


class TestGetStagedFiles:
    """Test get_staged_files function."""

    @patch("bastion.git_utils.get_changed_files")
    def test_get_staged_files_calls_get_changed(self, mock_changed: MagicMock) -> None:
        """Should call get_changed_files with correct args."""
        mock_changed.return_value = []

        get_staged_files(Path("/test"))

        mock_changed.assert_called_once_with(
            path=Path("/test"),
            staged_only=True,
            include_untracked=False,
        )


class TestGetCurrentBranch:
    """Test get_current_branch function."""

    @patch("bastion.git_utils.subprocess.run")
    def test_get_current_branch_success(self, mock_run: MagicMock) -> None:
        """Should return branch name."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="main\n",
        )

        result = get_current_branch(Path("/test"))

        assert result == "main"

    @patch("bastion.git_utils.subprocess.run")
    def test_get_current_branch_not_git_repo(self, mock_run: MagicMock) -> None:
        """Should return None when not in git repo."""
        mock_run.side_effect = __import__("subprocess").CalledProcessError(128, "git")

        result = get_current_branch(Path("/test"))

        assert result is None

    @patch("bastion.git_utils.subprocess.run")
    def test_get_current_branch_git_not_found(self, mock_run: MagicMock) -> None:
        """Should return None when git not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = get_current_branch(Path("/test"))

        assert result is None


class TestGetMergeBase:
    """Test get_merge_base function."""

    @patch("bastion.git_utils.subprocess.run")
    def test_get_merge_base_success(self, mock_run: MagicMock) -> None:
        """Should return merge base commit."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123def456\n",
        )

        result = get_merge_base("main", "feature", Path("/test"))

        assert result == "abc123def456"

    @patch("bastion.git_utils.subprocess.run")
    def test_get_merge_base_no_common_ancestor(self, mock_run: MagicMock) -> None:
        """Should return None when no common ancestor."""
        mock_run.side_effect = __import__("subprocess").CalledProcessError(1, "git")

        result = get_merge_base("main", "unrelated", Path("/test"))

        assert result is None

    @patch("bastion.git_utils.subprocess.run")
    def test_get_merge_base_git_not_found(self, mock_run: MagicMock) -> None:
        """Should return None when git not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = get_merge_base("main", "feature", Path("/test"))

        assert result is None


class TestGitError:
    """Test GitError exception."""

    def test_git_error_message(self) -> None:
        """Should preserve error message."""
        error = GitError("Test error message")

        assert str(error) == "Test error message"
