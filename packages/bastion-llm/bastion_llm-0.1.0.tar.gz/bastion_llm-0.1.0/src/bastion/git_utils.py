"""Git utilities for incremental scanning."""

import subprocess
from pathlib import Path


class GitError(Exception):
    """Exception raised for git-related errors."""


def is_git_repo(path: Path | None = None) -> bool:
    """Check if the path is inside a git repository."""
    if path is None:
        path = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_repo_root(path: Path | None = None) -> Path | None:
    """Get the root directory of the git repository."""
    if path is None:
        path = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_changed_files(
    base: str = "HEAD",
    path: Path | None = None,
    staged_only: bool = False,
    include_untracked: bool = True,
) -> list[Path]:
    """Get list of files changed since base commit.

    Args:
        base: The base commit/branch to compare against (default: HEAD)
        path: Working directory (default: current directory)
        staged_only: Only return staged files
        include_untracked: Include untracked files

    Returns:
        List of changed file paths (absolute)
    """
    if path is None:
        path = Path.cwd()

    changed_files: set[Path] = set()
    repo_root = get_repo_root(path)

    if not repo_root:
        raise GitError("Not a git repository")

    try:
        if staged_only:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            # Get modified files (staged and unstaged)
            result = subprocess.run(
                ["git", "diff", base, "--name-only", "--diff-filter=ACMR"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

        for line in result.stdout.strip().split("\n"):
            if line:
                file_path = repo_root / line
                if file_path.exists():
                    changed_files.add(file_path.resolve())

        # Also get unstaged changes
        if not staged_only:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    file_path = repo_root / line
                    if file_path.exists():
                        changed_files.add(file_path.resolve())

        # Get untracked files
        if include_untracked:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    file_path = repo_root / line
                    if file_path.exists():
                        changed_files.add(file_path.resolve())

    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e.stderr}") from e

    return sorted(changed_files)


def get_staged_files(path: Path | None = None) -> list[Path]:
    """Get list of staged files (for pre-commit hooks)."""
    return get_changed_files(path=path, staged_only=True, include_untracked=False)


def get_current_branch(path: Path | None = None) -> str | None:
    """Get the current git branch name."""
    if path is None:
        path = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_merge_base(
    branch1: str,
    branch2: str = "HEAD",
    path: Path | None = None,
) -> str | None:
    """Get the merge base between two branches."""
    if path is None:
        path = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "merge-base", branch1, branch2],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


__all__ = [
    "GitError",
    "is_git_repo",
    "get_repo_root",
    "get_changed_files",
    "get_staged_files",
    "get_current_branch",
    "get_merge_base",
]
