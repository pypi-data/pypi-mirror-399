"""
djb.cli.tests - Test utilities for djb CLI unit tests.

Unit tests use mocking instead of real file I/O. For E2E tests with real
directories, see djb.cli.tests.e2e.

Unit Test Fixtures (auto-discovered by pytest from conftest.py):
    make_cli_runner - Click CliRunner for invoking CLI commands
    mock_cmd_runner - Mock for CmdRunner (provides .run)
    djb_config - DjbConfig instance with fake project_dir (no real directories)
    make_djb_config - Factory for creating DjbConfig with custom overrides
    mock_file_read - Factory for mocking Path.read_text() with specific content
    mock_file_exists - Factory for controlling Path.exists() results
    mock_cwd - Factory for mocking Path.cwd() to return a fake path
    mock_load_pyproject - Factory for mocking load_pyproject() calls
    mock_locking - Mock file locking functions to avoid real I/O
    mock_hook_io - Mock I/O for pre-commit hook installation tests

Shared Fixtures (from djb.testing):
    pty_stdin - Creates a PTY and replaces stdin for interactive input testing
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob

Auto-enabled fixtures (applied to all tests automatically):
    configure_logging - Initializes djb CLI logging system (session-scoped)
    clear_config_cache - Clears the config cache before each test
    disable_gpg_protection - Disables GPG protection to avoid pinentry prompts

Helper functions:
    make_editable_pyproject - Generate editable pyproject.toml content

Constants:
    DJB_PYPROJECT_CONTENT - Common pyproject.toml content for testing
    EDITABLE_PYPROJECT_TEMPLATE - Template for editable pyproject.toml
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
    DEFAULT_HETZNER_CONFIG - Default HetznerConfig for unit tests
    DEFAULT_HEROKU_CONFIG - Default HerokuConfig for unit tests
    DEFAULT_K8S_CONFIG - Default K8sConfig for unit tests
    DEFAULT_CLOUDFLARE_CONFIG - Default CloudflareConfig for unit tests
"""

from __future__ import annotations

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
    make_djb_config,
    make_editable_pyproject,
    pty_stdin,
)

from .conftest import (
    make_cli_runner,
    disable_gpg_protection,
    djb_config,
    mock_cmd_runner,
    mock_cwd,
    mock_file_exists,
    mock_file_read,
    mock_hook_io,
    mock_load_pyproject,
    mock_locking,
)

__all__ = [
    # Constants
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "FAKE_PROJECT_DIR",
    # Helper functions
    "make_editable_pyproject",
    # Shared fixtures (from djb.testing)
    "alice_key",
    "bob_key",
    "clear_config_cache",
    "configure_logging",
    "make_age_key",
    "pty_stdin",
    # Unit test fixtures
    "make_cli_runner",
    "disable_gpg_protection",
    "djb_config",
    "make_djb_config",
    "mock_cmd_runner",
    "mock_cwd",
    "mock_file_exists",
    "mock_file_read",
    "mock_hook_io",
    "mock_load_pyproject",
    "mock_locking",
]
