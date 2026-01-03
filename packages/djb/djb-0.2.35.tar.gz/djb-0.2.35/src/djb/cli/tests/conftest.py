"""
Shared test fixtures for djb CLI **unit tests**.

See __init__.py for the full list of available fixtures and utilities.

Guidelines for Unit Tests vs E2E Tests:
========================================

Unit tests (cli/tests/*.py):
- Use `djb_config` fixture to get a DjbConfig instance (no real directories)
- Use `mock_file_read` and `mock_file_exists` for file operation mocking
- NEVER use `tmp_path` directly - all file I/O should be mocked
- Prefer patching/mocking over creating real project directories

E2E tests (cli/tests/e2e/*.py):
- Use real project directories with `project_dir` fixture
- Use `make_config_file` to create .djb/local.toml and .djb/project.toml
- Use `pyproject_dir_with_git` for a complete project setup
- E2E fixtures are defined in cli/tests/e2e/fixtures/

Unit Test Fixtures:
    make_cli_runner - Click CliRunner for invoking CLI commands
    mock_cmd_runner - Mock for CmdRunner methods (provides .run)
    djb_config - DjbConfig instance with fake project_dir (no real directories)
    make_djb_config - Factory function for creating DjbConfig with custom overrides
    mock_project_with_git_repo - Mock a git repo structure (no real directories)
    mock_file_read - Factory for mocking Path.read_text() with specific content
    mock_file_exists - Factory for controlling Path.exists() results
    mock_cwd - Factory for mocking Path.cwd() to return a fake path
    mock_load_pyproject - Factory for mocking load_pyproject() calls

Shared Fixtures (from djb.testing):
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob
    pty_stdin - Creates a PTY and replaces stdin for interactive input testing

Auto-enabled fixtures (applied to all tests automatically):
    configure_logging - Initializes djb CLI logging system (session-scoped)
    clear_config_cache - Clears the config cache before each test
    disable_gpg_protection - Disables GPG protection to avoid pinentry prompts

Constants:
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
"""

from __future__ import annotations

import tomllib
from collections.abc import Callable, Generator
from contextlib import contextmanager, nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from djb import get_logger
from djb.config import DjbConfig
from djb.testing import (
    DEFAULT_CLOUDFLARE_CONFIG,
    DEFAULT_HEROKU_CONFIG,
    DEFAULT_HETZNER_CONFIG,
    DEFAULT_K8S_CONFIG,
    DJB_PYPROJECT_CONTENT,
    EDITABLE_PYPROJECT_TEMPLATE,
    FAKE_PROJECT_DIR,
    alice_key,
    bob_key,
    clear_config_cache,
    configure_logging,
    make_age_key,
    make_cli_ctx,
    make_cmd_runner,
    make_djb_config,
    make_editable_pyproject,
    mock_cli_ctx,
    mock_cmd_runner,
    pty_stdin,
)
from djb.types import Mode, Platform

# Re-export shared fixtures so they're available to tests in this package
__all__ = [
    # Fixtures from djb.testing.fixtures
    "clear_config_cache",
    "configure_logging",
    "pty_stdin",
    "make_age_key",
    "make_cli_ctx",
    "mock_cli_ctx",
    "make_cmd_runner",
    "mock_cmd_runner",
    "alice_key",
    "bob_key",
    "make_djb_config",
    # Constants from djb.testing.fixtures
    "FAKE_PROJECT_DIR",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_editable_pyproject",
    # Local fixtures
    "make_cli_runner",
    "mock_project_with_git_repo",
]

logger = get_logger(__name__)


# =============================================================================
# CLI Testing Fixtures
# =============================================================================


@pytest.fixture
def make_cli_runner() -> CliRunner:
    """Click CLI test runner.

    Returns a CliRunner instance for invoking Click commands
    in tests. The CliRunner captures stdout/stderr and provides
    access to exit codes and output.

    Example:
        def test_my_command(make_cli_runner):
            result = make_cli_runner.invoke(djb_cli, ["health"])
            assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture(autouse=True)
def disable_gpg_protection():
    """Disable GPG protection to avoid pinentry prompts in tests.

    GPG requires an interactive pinentry for decryption, which fails in
    automated test environments. By marking GPG as unavailable, we skip
    the GPG-protection code path entirely.
    """
    logger.debug("Disabling GPG protection for testing (avoiding pinentry prompts)")
    with (
        patch("djb.secrets.init.check_gpg_installed", return_value=False),
        patch("djb.secrets.protected.check_gpg_installed", return_value=False),
    ):
        yield


# =============================================================================
# Unit Test Fixtures (no io)
# =============================================================================


@pytest.fixture
def djb_config() -> Generator[DjbConfig, None, None]:
    """Create a DjbConfig for unit tests - no real directories created.

    Returns a DjbConfig instance with a fake project_dir. The fixture
    automatically patches djb_get_config to return this config, so
    ctx.obj.config in CLI commands will also use it.

    For tests needing config with specific overrides (like seed_command),
    use the make_djb_config factory fixture instead.

    Example:
        def test_something(djb_config):
            assert djb_config.project_name == "test-project"
    """
    config = DjbConfig(
        project_dir=FAKE_PROJECT_DIR,
        project_name="test-project",
        mode=Mode.DEVELOPMENT,
        platform=Platform.HEROKU,
        name="Test User",
        email="test@example.com",
        seed_command=None,
        log_level="info",
        encrypt_development_secrets=True,
        encrypt_staging_secrets=True,
        encrypt_production_secrets=True,
        hetzner=DEFAULT_HETZNER_CONFIG,
        heroku=DEFAULT_HEROKU_CONFIG,
        k8s=DEFAULT_K8S_CONFIG,
        cloudflare=DEFAULT_CLOUDFLARE_CONFIG,
    )

    with patch("djb.cli.djb.djb_get_config", return_value=config):
        yield config


@pytest.fixture
def mock_project_with_git_repo(monkeypatch):
    """Mock a git repository structure with required config.

    Uses FAKE_PROJECT_DIR and mocks file checks instead of creating real
    directories. Sets DJB_* environment variables to avoid config file I/O.
    Mocks Path.exists to return True for .git directory.

    This is the unit test sibling of make_project_with_git_repo (for E2E tests).

    Example:
        def test_something(mock_project_with_git_repo):
            # FAKE_PROJECT_DIR is returned and .git appears to exist
            assert mock_project_with_git_repo == FAKE_PROJECT_DIR
    """
    # Mock config via environment variables instead of creating files
    monkeypatch.setenv("DJB_NAME", "Test User")
    monkeypatch.setenv("DJB_EMAIL", "test@example.com")
    # Also mock Path.cwd to return FAKE_PROJECT_DIR
    monkeypatch.setattr(Path, "cwd", lambda: FAKE_PROJECT_DIR)

    # Mock .git to exist
    original_exists = Path.exists
    original_is_dir = Path.is_dir

    def mock_exists(self):
        if ".git" in str(self):
            return True
        return original_exists(self)

    def mock_is_dir(self):
        if ".git" in str(self):
            return True
        return original_is_dir(self)

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(Path, "is_dir", mock_is_dir)

    return FAKE_PROJECT_DIR


# =============================================================================
# File Mocking Fixtures
# =============================================================================


@pytest.fixture
def mock_file_read() -> Callable[[dict[str, str]], Any]:
    """Factory for mocking Path.read_text() with specific content.

    Returns a context manager that patches Path.read_text to return
    content based on filename matching.

    Example:
        def test_parse_pyproject(mock_file_read):
            with mock_file_read({"pyproject.toml": '[project]\\nname = "test"\\n'}):
                content = (Path("/any") / "pyproject.toml").read_text()
                assert "test" in content
    """

    @contextmanager
    def _mock_read(content_map: dict[str, str]) -> Generator[None, None, None]:
        original_read_text = Path.read_text

        def patched_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
            for pattern, content in content_map.items():
                if self.name == pattern or str(self).endswith(pattern):
                    return content
            # Fall back to original for unmocked files (will raise if doesn't exist)
            return original_read_text(self, *args, **kwargs)

        with patch.object(Path, "read_text", patched_read_text):
            yield

    return _mock_read


@pytest.fixture
def mock_file_exists() -> Callable[[dict[str, bool]], Any]:
    """Factory for controlling Path.exists() and Path.is_dir() results.

    Returns a context manager that patches Path.exists and Path.is_dir
    to return values based on filename matching.

    Example:
        def test_frontend_exists(mock_file_exists):
            with mock_file_exists({"frontend": True, "pyproject.toml": True}):
                assert (Path("/project") / "frontend").exists()
    """

    @contextmanager
    def _mock_exists(file_map: dict[str, bool]) -> Generator[None, None, None]:
        def patched_exists(self: Path) -> bool:
            for pattern, exists in file_map.items():
                if self.name == pattern or str(self).endswith(pattern):
                    return exists
            return False  # Default: file doesn't exist

        def patched_is_dir(self: Path) -> bool:
            for pattern, is_dir in file_map.items():
                if self.name == pattern or str(self).endswith(pattern):
                    return is_dir
            return False

        with (
            patch.object(Path, "exists", patched_exists),
            patch.object(Path, "is_dir", patched_is_dir),
        ):
            yield

    return _mock_exists


@pytest.fixture
def mock_cwd() -> Callable[[Path], Any]:
    """Factory for mocking Path.cwd() to return a fake path.

    Replaces monkeypatch.chdir(tmp_path) pattern used in unit tests.

    Example:
        def test_cwd_detection(mock_cwd):
            with mock_cwd(Path("/fake/project")):
                result = Path.cwd()
                assert result == Path("/fake/project")
    """

    @contextmanager
    def _mock_cwd(fake_cwd: Path) -> Generator[None, None, None]:
        with patch("pathlib.Path.cwd", return_value=fake_cwd):
            yield

    return _mock_cwd


@pytest.fixture
def mock_load_pyproject() -> Callable[[dict[str, Any] | None], Any]:
    """Factory for mocking load_pyproject() to return specific content.

    Returns a context manager that patches load_pyproject in all modules
    that import it. This affects all functions that use load_pyproject
    including find_dependency, _get_djb_source_config, is_djb_package_dir, etc.

    Example:
        def test_something(mock_load_pyproject):
            parsed = {"project": {"name": "test", "dependencies": ["djb>=0.2.6"]}}
            with mock_load_pyproject(parsed):
                result = get_djb_version_specifier(Path("/fake"))
    """

    @contextmanager
    def _mock_load(
        content: dict[str, Any] | None = None,
        *,
        raise_error: bool = False,
    ) -> Generator[None, None, None]:
        def fake_load(_path: Path) -> dict[str, Any] | None:
            if raise_error:
                raise tomllib.TOMLDecodeError("Invalid TOML", "", 0)
            return content

        # Patch in all modules that import load_pyproject
        # Python's import creates a reference in each importing module's namespace
        with (
            patch("djb.cli.utils.pyproject.load_pyproject", side_effect=fake_load),
            patch("djb.cli.editable.load_pyproject", side_effect=fake_load),
        ):
            yield

    return _mock_load


@pytest.fixture
def mock_locking():
    """Mock file locking functions to avoid real I/O in unit tests.

    Patches get_lock_for_path to return a no-op context manager
    and atomic_write to track writes in a dictionary.

    This fixture should be used instead of tmp_path for tests
    that call functions using the locking module.

    Example:
        def test_removes_workspace(mock_locking, mock_file_read):
            input_content = '[project]\\nname = "test"'
            with mock_file_read({"pyproject.toml": input_content}):
                _remove_djb_workspace_member(FAKE_PROJECT_DIR / "pyproject.toml")
            assert FAKE_PROJECT_DIR / "pyproject.toml" in mock_locking

    Yields:
        dict[Path, str]: Dictionary mapping paths to written content
    """
    written_files: dict[Path, str] = {}

    def fake_atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
        written_files[path] = content

    with (
        patch("djb.cli.editable.file_lock", return_value=nullcontext()),
        patch("djb.cli.editable.atomic_write", side_effect=fake_atomic_write),
    ):
        yield written_files


@pytest.fixture
def mock_hook_io():
    """Mock I/O for pre-commit hook installation tests.

    Provides a mock filesystem for testing install_pre_commit_hook
    without real file I/O.

    The fixture returns a SimpleNamespace with:
        - files: dict[Path, str] - Map of path to file contents
        - dirs: set[Path] - Set of directories that "exist"
        - written_files: dict[Path, str] - Files written via atomic_write
        - chmod_calls: list[tuple[Path, int]] - chmod calls made

    Example:
        def test_installs_hook(mock_hook_io):
            mock_hook_io.dirs.add(FAKE_PROJECT_DIR / ".git")
            mock_hook_io.dirs.add(FAKE_PROJECT_DIR / ".git" / "hooks")

            install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

            hook = FAKE_PROJECT_DIR / ".git" / "hooks" / "pre-commit"
            assert hook in mock_hook_io.written_files
    """
    state = SimpleNamespace(
        files={},  # type: dict[Path, str]
        dirs=set(),  # type: set[Path]
        written_files={},  # type: dict[Path, str]
        chmod_calls=[],  # type: list[tuple[Path, int]]
    )

    def mock_is_dir(self: Path) -> bool:
        return self in state.dirs

    def mock_exists(self: Path) -> bool:
        return self in state.files or self in state.dirs

    def mock_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        if self in state.files:
            return state.files[self]
        raise FileNotFoundError(self)

    def mock_mkdir(self: Path, *args: Any, **kwargs: Any) -> None:
        state.dirs.add(self)

    def mock_chmod(self: Path, mode: int) -> None:
        state.chmod_calls.append((self, mode))

    def fake_atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
        state.written_files[path] = content
        state.files[path] = content  # Also update files for subsequent reads

    with (
        patch.object(Path, "is_dir", mock_is_dir),
        patch.object(Path, "exists", mock_exists),
        patch.object(Path, "read_text", mock_read_text),
        patch.object(Path, "mkdir", mock_mkdir),
        patch.object(Path, "chmod", mock_chmod),
        patch("djb.cli.editable.file_lock", return_value=nullcontext()),
        patch("djb.cli.editable.atomic_write", side_effect=fake_atomic_write),
    ):
        yield state


# DJB_PYPROJECT_CONTENT, EDITABLE_PYPROJECT_TEMPLATE, and make_editable_pyproject
# are imported from djb.testing.fixtures and re-exported via __all__
