"""
Shared test fixtures for djb tests.

This module provides reusable pytest fixtures that can be imported by both
CLI unit tests and E2E tests to avoid duplication.

Fixtures:
    configure_logging - Initializes djb CLI logging system (session-scoped, autouse)
    clear_config_cache - Clears djb config cache before each test (autouse)
    pty_stdin - Creates a PTY and temporarily replaces stdin for interactive input testing
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob
    make_djb_config - Factory for creating DjbConfig with custom overrides
    require_docker - Skip test if Docker is not available (E2E)

Functions:
    is_docker_available() - Check if Docker daemon is running

Constants:
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
    DEFAULT_HETZNER_CONFIG - Default HetznerConfig for unit tests
    DEFAULT_HEROKU_CONFIG - Default HerokuConfig for unit tests
    DEFAULT_K8S_CONFIG - Default K8sConfig for unit tests
    DEFAULT_CLOUDFLARE_CONFIG - Default CloudflareConfig for unit tests
    DJB_PYPROJECT_CONTENT - Common pyproject.toml content for testing djb package
    EDITABLE_PYPROJECT_TEMPLATE - Template for editable pyproject.toml
    make_editable_pyproject() - Function to generate editable pyproject.toml content

Usage:
    Import the fixtures you need in your conftest.py:

        from djb.testing.fixtures import configure_logging, pty_stdin

    Or import all fixtures:

        from djb.testing.fixtures import *
"""

from __future__ import annotations

import os
import pty
import subprocess
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

if TYPE_CHECKING:
    from djb.core import CmdRunner

from djb.config import (
    CloudflareConfig,
    DjbConfig,
    HerokuConfig,
    HetznerConfig,
    HetznerImage,
    HetznerLocation,
    HetznerServerType,
    K8sBackendConfig,
    K8sConfig,
    _clear_config_cache,
)
from djb.cli.context import CliContext
from djb.core import CmdRunner, RunResult, setup_logging
from djb.secrets import generate_age_key
from djb.types import Mode, Platform


# =============================================================================
# Shared Testing Fixtures
# =============================================================================


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Empty project directory for testing.

    Returns tmp_path directly. djb should work in the simplest case.
    This is the base fixture that other project fixtures build on.

    Example:
        def test_something(project_dir):
            (project_dir / "pyproject.toml").write_text('[project]\\nname = "test"')
    """
    return tmp_path


@pytest.fixture
def make_cli_ctx() -> CliContext:
    """Create a real CliContext for E2E tests.

    This is the base context fixture. The context has a real runner (via
    cached_property) that executes real commands.

    Use this for integration/E2E tests that need actual command execution.

    Example:
        def test_something(make_cli_ctx):
            result = make_cli_ctx.runner.run(["echo", "hello"])
            assert result.returncode == 0
    """
    return CliContext()


@pytest.fixture
def mock_cli_ctx(make_cli_ctx: CliContext):
    """Create a CliContext with mocked runner for unit tests.

    The runner's methods (run, check) are mocked.
    Use this for unit tests that should not execute real commands.

    Access the runner via `cli_ctx.runner`, and configure mocks on the runner:
        - `cli_ctx.runner.run` - Mock object for run method
        - `cli_ctx.runner.check` - Mock object for check method

    Example:
        def test_something(mock_cli_ctx):
            mock_cli_ctx.runner.run.return_value = Mock(returncode=0, stdout="output", stderr="")
            result = some_function(mock_cli_ctx)
            assert mock_cli_ctx.runner.run.call_count >= 1
    """
    with (
        patch.object(CmdRunner, "run") as mock_run,
        patch.object(CmdRunner, "check") as mock_check,
    ):
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_check.return_value = True
        yield make_cli_ctx


@pytest.fixture
def make_cmd_runner(make_cli_ctx: CliContext) -> CmdRunner:
    """Create a CmdRunner for E2E tests that need real command execution.

    Use mock_cmd_runner in unit-tests that don't need real command execution.
    Prefer using make_cli_ctx.runner directly.

    Example:
        def test_something(make_cmd_runner):
            result = make_cmd_runner.run(["echo", "hello"])
            assert result.returncode == 0
    """
    return make_cli_ctx.runner


@pytest.fixture
def mock_cmd_runner(make_cli_ctx: CliContext):  # noqa: ARG001
    """Mock CmdRunner.run for testing CLI modules.

    Returns a namespace with .run and .check Mock objects.

    Modes:
        Full mock (default): All commands return mock results.
        Selective mock: Call mock_cmd_runner.run.only_mock(patterns) to only
            mock matching commands; non-matching commands execute for real.

    Attributes:
        run: Mock object for configuring return values and asserting calls.
        check: Mock object for the check method.

    The mock replicates real run() behavior: raises fail_msg if returncode != 0
    and fail_msg is an Exception.

    Examples::

        # Check that a command was called
        def test_calls_uv(mock_cmd_runner):
            do_something(mock_cmd_runner)
            assert mock_cmd_runner.run.call_count == 1
            assert mock_cmd_runner.run.call_args.args[0] == ["uv", "sync"]

        # Configure a failure response
        def test_handles_failure(mock_cmd_runner):
            mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="error")
            result = do_something(mock_cmd_runner)
            assert result.exit_code == 1

        # Sequential return values
        def test_retry_logic(mock_cmd_runner):
            mock_cmd_runner.run.side_effect_values.extend([
                Mock(returncode=1, stderr="fail"),  # First call fails
                Mock(returncode=0, stdout="ok"),    # Retry succeeds
            ])
            assert do_something_with_retry(mock_cmd_runner) == "ok"

        # Custom side_effect function
        def test_dynamic_response(mock_cmd_runner):
            def side_effect(cmd, *args, **kwargs):
                if "heroku" in cmd[0]:
                    return Mock(returncode=0, stdout="heroku ok")
                return Mock(returncode=1, stderr="unknown")
            mock_cmd_runner.run.side_effect = side_effect

        # Selective mocking: mock heroku, run git for real
        def test_e2e_with_selective_mock(mock_cmd_runner, make_cli_runner):
            mock_cmd_runner.run.only_mock(["heroku"])
            result = make_cli_runner.invoke(cli, ["deploy"])
            assert result.exit_code == 0
    """
    # Store original for selective mode fallthrough
    original_run = CmdRunner.run

    # List for sequential return values
    side_effect_values: list[RunResult] = []

    # State for selective mode (closure variables)
    selective_patterns: list[str] | None = None
    selective_result: RunResult | None = None

    # Mock for tracking calls
    mock_run = Mock()
    mock_run.return_value = RunResult(0, "", "")
    mock_run.side_effect_values = side_effect_values

    def run_side_effect(_cmd: list[str], *_args, **kwargs) -> RunResult:
        """Side effect for direct calls to mock_cmd_runner.run(...)."""
        # Get result from sequential values or return_value
        if side_effect_values:
            result = side_effect_values.pop(0)
        else:
            result = mock_run.return_value

        # Handle fail_msg (replicate CmdRunner behavior)
        if result.returncode != 0:
            fail_msg = kwargs.get("fail_msg")
            if isinstance(fail_msg, Exception):
                raise fail_msg
        return result

    mock_run.side_effect = run_side_effect

    def only_mock(patterns: list[str], default_result: RunResult | None = None) -> None:
        """Enable selective mocking - only mock commands matching patterns."""
        nonlocal selective_patterns, selective_result
        selective_patterns = patterns
        selective_result = default_result or RunResult(0, "", "")

    # Attach only_mock method to the mock
    mock_run.only_mock = only_mock

    def patched_run(runner_self: CmdRunner, cmd: list[str], *args, **kwargs) -> RunResult:
        """Patched CmdRunner.run that delegates to mock or original."""
        nonlocal selective_patterns, selective_result
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

        # Selective mode: check if command matches any pattern (prefix match)
        if selective_patterns is not None and selective_result is not None:
            for pattern in selective_patterns:
                if cmd_str.startswith(pattern):
                    # Match - record call and return mock result
                    mock_run(cmd, *args, **kwargs)
                    return selective_result
            # No match - call original (real execution)
            return original_run(runner_self, cmd, *args, **kwargs)

        # Full mock mode: call mock (which triggers run_side_effect)
        return mock_run(cmd, *args, **kwargs)

    mock_check = Mock()
    mock_check.return_value = True

    with (
        patch.object(CmdRunner, "run", patched_run),
        patch.object(CmdRunner, "check", mock_check),
    ):
        yield types.SimpleNamespace(run=mock_run, check=mock_check)


@pytest.fixture
def make_cli_runner() -> CliRunner:
    """Click CLI test runner.

    Returns a CliRunner instance for invoking Click commands
    in tests. The CliRunner captures stdout/stderr and provides
    access to exit codes and output.

    Example:
        def test_health_help(make_cli_runner):
            result = make_cli_runner.invoke(djb_cli, ["health", "--help"])
            assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for all CLI tests (session-scoped).

    This fixture runs once per test session to initialize the djb CLI
    logging system. Session scope is safe since logging is inherently
    global and idempotent.
    """
    setup_logging()


@pytest.fixture(autouse=True)
def clear_config_cache() -> None:
    """Clear the config cache before each test for isolation.

    This fixture runs before each test to ensure config state doesn't
    leak between tests. The config module caches the configuration
    after first load, so this must be cleared for tests that modify
    config or environment variables.
    """
    _clear_config_cache()


# =============================================================================
# Age Key Fixtures
# =============================================================================


class AgePathAndPublicKey(NamedTuple):
    """Path to an age key file and its public key.

    Note: This is distinct from djb.secrets.AgeKeyPair which contains
    the actual public_key and private_key strings (key content).
    """

    key_path: Path
    public_key: str


@pytest.fixture
def pty_stdin():
    """Fixture that creates a PTY and temporarily replaces stdin.

    This fixture properly saves and restores stdin state between tests,
    avoiding pollution that can occur with manual save/restore.

    Yields the master fd which can be written to simulate user input.

    Example:
        def test_interactive_input(pty_stdin):
            os.write(pty_stdin, b"yes\\n")
            # ... code that reads from stdin
    """
    # Create PTY pair
    master_fd, slave_fd = pty.openpty()

    # Save original stdin state
    original_stdin_fd = os.dup(0)

    # Replace stdin with slave end of PTY
    os.dup2(slave_fd, 0)
    os.close(slave_fd)  # Close original fd since we dup2ed it
    sys.stdin = os.fdopen(0, "r", closefd=False)

    yield master_fd

    # Restore original stdin
    # First, close the current sys.stdin without closing fd 0
    sys.stdin.close()
    # Restore fd 0 to original
    os.dup2(original_stdin_fd, 0)
    os.close(original_stdin_fd)
    # Recreate sys.stdin from restored fd 0
    sys.stdin = os.fdopen(0, "r", closefd=False)
    # Close master end
    os.close(master_fd)


@pytest.fixture
def make_age_key(tmp_path: Path) -> Callable[[str], AgePathAndPublicKey]:
    """Factory fixture to create age key pairs.

    Creates age keys in a structured directory under tmp_path/.age/{name}/keys.txt.
    Each call with a different name creates a separate key pair.

    Returns a factory function that takes a name and returns an AgePathAndPublicKey.

    Pytest:
        Uses pytest's `tmp_path` fixture internally, so keys are created in the
        same temporary directory available to the test function.

    Example:
        def test_with_keys(tmp_path, make_age_key):
            # make_age_key uses the same tmp_path as the test
            alice_key_path, alice_public_key = make_age_key("alice")
            bob_key_path, bob_public_key = make_age_key("bob")
    """
    runner = CmdRunner()  # Non-verbose runner for key generation

    def _make_key(name: str) -> AgePathAndPublicKey:
        key_dir = tmp_path / ".age" / name
        key_dir.mkdir(parents=True, exist_ok=True)
        key_path = key_dir / "keys.txt"
        public_key, _ = generate_age_key(runner, key_path)
        return AgePathAndPublicKey(key_path, public_key)

    return _make_key


@pytest.fixture
def alice_key(make_age_key: Callable[[str], AgePathAndPublicKey]) -> AgePathAndPublicKey:
    """Create Alice's age key pair.

    Returns an AgePathAndPublicKey for Alice.
    Useful for tests that need a pre-made key without calling make_age_key directly.

    Pytest:
        Depends on `make_age_key` fixture, which in turn uses `tmp_path`.

    Example:
        def test_encryption(alice_key):
            key_path, public_key = alice_key
            # ... use key for encryption
    """
    return make_age_key("alice")


@pytest.fixture
def bob_key(make_age_key: Callable[[str], AgePathAndPublicKey]) -> AgePathAndPublicKey:
    """Create Bob's age key pair.

    Returns an AgePathAndPublicKey for Bob.
    Useful for tests that need two different keys (e.g., testing key rotation).

    Pytest:
        Depends on `make_age_key` fixture, which in turn uses `tmp_path`.

    Example:
        def test_rotation(alice_key, bob_key):
            alice_path, alice_public = alice_key
            bob_path, bob_public = bob_key
            # ... test key rotation
    """
    return make_age_key("bob")


# =============================================================================
# Docker Fixtures (E2E)
# =============================================================================


def is_docker_available() -> bool:
    """Check if Docker is available and daemon is running.

    Returns:
        True if Docker daemon is accessible, False otherwise.

    Example:
        if is_docker_available():
            # Run Docker-dependent code
            ...
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture
def require_docker() -> None:
    """Skip test if Docker is not available.

    Use this fixture in E2E tests that require Docker to be running.

    Example:
        def test_build_image(require_docker, make_cmd_runner):
            # This test will be skipped if Docker is not available
            ...
    """
    if not is_docker_available():
        pytest.skip("Docker not available (install Docker or start Docker daemon)")


# =============================================================================
# Test Constants
# =============================================================================

# Default fake project directory for unit tests
FAKE_PROJECT_DIR = Path("/fake/test-project")

# Default HetznerConfig for unit tests (matches resolution defaults)
DEFAULT_HETZNER_CONFIG = HetznerConfig(
    default_server_type=HetznerServerType.CX23.value,
    default_location=HetznerLocation.NBG1.value,
    default_image=HetznerImage.UBUNTU_24_04.value,
    server_name=None,
    server_ip=None,
    ssh_key_name=None,
)

# Default HerokuConfig for unit tests
DEFAULT_HEROKU_CONFIG = HerokuConfig(domain_names={})

# Default K8sConfig for unit tests
DEFAULT_K8S_BACKEND_CONFIG = K8sBackendConfig(
    managed_dockerfile=True,
    remote_build=True,
    buildpacks=["python:3.14-slim"],
    buildpack_registry="localhost:32000",
)
DEFAULT_K8S_CONFIG = K8sConfig(domain_names={}, backend=DEFAULT_K8S_BACKEND_CONFIG, db_name="")

# Default CloudflareConfig for unit tests
DEFAULT_CLOUDFLARE_CONFIG = CloudflareConfig(
    auto_dns=True,
    ttl=60,
    proxied=False,
)

# Common pyproject.toml content for testing djb package
DJB_PYPROJECT_CONTENT = '[project]\nname = "djb"\nversion = "0.1.0"\n'

# Template for editable pyproject.toml (host project with djb in editable mode)
EDITABLE_PYPROJECT_TEMPLATE = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = ["{path}"]

[tool.uv.sources]
djb = {{ workspace = true, editable = true }}
"""


def make_editable_pyproject(djb_path: str = "djb") -> str:
    """Generate editable pyproject.toml content with given djb path."""
    return EDITABLE_PYPROJECT_TEMPLATE.format(path=djb_path)


# =============================================================================
# DjbConfig Fixture
# =============================================================================


@pytest.fixture
def make_djb_config() -> Callable[..., DjbConfig]:
    """Factory fixture for creating DjbConfig with custom overrides.

    Returns a factory function that creates configs with specific values.
    No real directories are created - all values are mocked.

    Example:
        def test_with_custom_project(make_djb_config):
            config = make_djb_config(project_name="my-app", mode=Mode.PRODUCTION)
            assert config.project_name == "my-app"

        def test_with_seed_command(make_djb_config):
            config = make_djb_config(seed_command="myapp.cli:seed")
            assert config.seed_command == "myapp.cli:seed"
    """

    def _make_config(
        project_dir: Path = FAKE_PROJECT_DIR,
        project_name: str = "test-project",
        mode: Mode = Mode.DEVELOPMENT,
        platform: Platform = Platform.HEROKU,
        name: str | None = "Test User",
        email: str | None = "test@example.com",
        seed_command: str | None = None,
        log_level: str = "info",
        encrypt_development_secrets: bool = True,
        encrypt_staging_secrets: bool = True,
        encrypt_production_secrets: bool = True,
        hetzner: HetznerConfig | None = None,
        heroku: HerokuConfig | None = None,
        k8s: K8sConfig | None = None,
        cloudflare: CloudflareConfig | None = None,
    ) -> DjbConfig:
        return DjbConfig(
            project_dir=project_dir,
            project_name=project_name,
            mode=mode,
            platform=platform,
            name=name,
            email=email,
            seed_command=seed_command,
            log_level=log_level,
            encrypt_development_secrets=encrypt_development_secrets,
            encrypt_staging_secrets=encrypt_staging_secrets,
            encrypt_production_secrets=encrypt_production_secrets,
            hetzner=hetzner if hetzner is not None else DEFAULT_HETZNER_CONFIG,
            heroku=heroku if heroku is not None else DEFAULT_HEROKU_CONFIG,
            k8s=k8s if k8s is not None else DEFAULT_K8S_CONFIG,
            cloudflare=cloudflare if cloudflare is not None else DEFAULT_CLOUDFLARE_CONFIG,
        )

    return _make_config


__all__ = [
    # Project directory fixtures
    "project_dir",
    # CLI testing fixtures
    "configure_logging",
    "clear_config_cache",
    "make_cli_ctx",
    "mock_cli_ctx",
    "make_cmd_runner",
    "mock_cmd_runner",
    "make_cli_runner",
    # PTY fixtures
    "pty_stdin",
    # Age key fixtures
    "AgePathAndPublicKey",
    "make_age_key",
    "alice_key",
    "bob_key",
    # Docker fixtures (E2E)
    "is_docker_available",
    "require_docker",
    # Config fixtures
    "make_djb_config",
    # Test constants
    "FAKE_PROJECT_DIR",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_editable_pyproject",
]
