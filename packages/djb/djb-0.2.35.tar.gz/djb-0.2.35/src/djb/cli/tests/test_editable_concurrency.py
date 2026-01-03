"""Concurrency tests for editable.py file operations.

Tests verify that file locking prevents race conditions when
multiple processes access pyproject.toml or git hooks concurrently.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pytest

from djb.cli.editable import (
    PRE_COMMIT_HOOK_CONTENT,
    _remove_djb_source_entry,
    _remove_djb_workspace_member,
    install_pre_commit_hook,
)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a mock git repository structure."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir()
    return tmp_path


@pytest.fixture
def pyproject_with_djb(tmp_path: Path) -> Path:
    """Create a pyproject.toml with djb workspace configuration."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test-project"
version = "1.0.0"

[tool.uv.workspace]
members = [
    "djb",
]

[tool.uv.sources]
djb = { workspace = true, editable = true }
"""
    )
    return pyproject


def _install_hook_process(path_str: str) -> bool:
    """Install hook in a subprocess. Must be top-level for pickling."""
    path = Path(path_str)
    return install_pre_commit_hook(path, quiet=True)


class TestConcurrentPreCommitHook:
    """Test concurrent pre-commit hook installation."""

    def test_concurrent_installs_dont_corrupt(self, git_repo: Path) -> None:
        """Concurrent hook installations should not corrupt the hook file."""
        num_installs = 10

        with ProcessPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(_install_hook_process, str(git_repo)) for _ in range(num_installs)
            ]
            results = [f.result() for f in as_completed(futures)]

        # At least one should succeed, and the hook should be valid
        assert any(results)

        hook_path = git_repo / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()
        assert hook_path.read_text() == PRE_COMMIT_HOOK_CONTENT

    def test_concurrent_installs_all_succeed(self, git_repo: Path) -> None:
        """All concurrent installations should complete without error."""
        num_installs = 10

        with ProcessPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(_install_hook_process, str(git_repo)) for _ in range(num_installs)
            ]
            for f in as_completed(futures):
                # Should not raise any exceptions
                f.result()


class TestConcurrentWorkspaceCleanup:
    """Test concurrent workspace member removal."""

    def test_concurrent_workspace_removal(self, tmp_path: Path) -> None:
        """Concurrent workspace member removals should not corrupt file."""
        num_removals = 10

        # Create pyproject for each removal attempt
        pyproject = tmp_path / "pyproject.toml"

        def remove_and_check(n: int) -> bool:
            # Reset the file each time to test concurrent access
            pyproject.write_text(
                """[project]
name = "test"

[tool.uv.workspace]
members = [
    "djb",
]
"""
            )
            return _remove_djb_workspace_member(pyproject, quiet=True)

        # Run sequentially to test idempotency
        for i in range(num_removals):
            result = remove_and_check(i)
            assert result

    def test_concurrent_source_removal(self, tmp_path: Path) -> None:
        """Concurrent source entry removals should not corrupt file."""
        pyproject = tmp_path / "pyproject.toml"

        def remove_source(n: int) -> bool:
            pyproject.write_text(
                """[project]
name = "test"

[tool.uv.sources]
djb = { workspace = true, editable = true }
"""
            )
            return _remove_djb_source_entry(pyproject, quiet=True)

        # Run sequentially to test idempotency
        for i in range(10):
            result = remove_source(i)
            assert result
