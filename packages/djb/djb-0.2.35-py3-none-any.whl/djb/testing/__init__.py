"""
djb.testing - Reusable testing utilities for djb-based projects.

Usage in your conftest.py:
    from djb.testing import (
        pytest_addoption,
        pytest_configure,
        pytest_collection_modifyitems,
        alice_key,
        bob_key,
    )

    # Re-export pytest hooks (required for pytest to find them)
    __all__ = ["pytest_addoption", "pytest_configure", "pytest_collection_modifyitems"]

    # Use fixtures in tests
    def test_encryption(alice_key, bob_key):
        assert alice_key.public != bob_key.public

Pytest Secrets Plugin:
    Register in pytest.ini to automatically set up test secrets:
        [pytest]
        addopts = -p djb.testing.pytest_secrets
        DJANGO_SETTINGS_MODULE = myproject.settings

    Or use the functions directly for custom setup:
        from djb.testing import setup_test_secrets, cleanup_test_secrets

Exports:
    test_typecheck - Importable test function for running pyright
    has_pytest_cov - Check if pytest-cov is available
    has_pytest_xdist - Check if pytest-xdist is available
    pytest_addoption - Add --no-e2e and --only-e2e options
    pytest_configure - Register e2e marker
    pytest_collection_modifyitems - Skip e2e tests if --no-e2e is provided
    setup_test_secrets - Create isolated test secrets (for custom plugins)
    cleanup_test_secrets - Clean up test secrets directory
    TestSecretsPaths - NamedTuple returned by setup_test_secrets

Shared Fixtures (import in your conftest.py):
    configure_logging - Initializes djb CLI logging system (session-scoped, autouse)
    clear_config_cache - Clears djb config cache before each test (autouse)
    AgePathAndPublicKey - NamedTuple with key file path and public key
    pty_stdin - Creates a PTY and temporarily replaces stdin
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob
"""

from __future__ import annotations

from djb.testing.fixtures import (
    DEFAULT_CLOUDFLARE_CONFIG,
    DEFAULT_HEROKU_CONFIG,
    DEFAULT_HETZNER_CONFIG,
    DEFAULT_K8S_CONFIG,
    DJB_PYPROJECT_CONTENT,
    EDITABLE_PYPROJECT_TEMPLATE,
    FAKE_PROJECT_DIR,
    AgePathAndPublicKey,
    alice_key,
    bob_key,
    clear_config_cache,
    configure_logging,
    is_docker_available,
    make_age_key,
    make_cli_ctx,
    make_cli_runner,
    make_cmd_runner,
    make_djb_config,
    mock_cli_ctx,
    mock_cmd_runner,
    make_editable_pyproject,
    pty_stdin,
    require_docker,
)
from djb.testing.pytest_e2e import (
    pytest_addoption,
    pytest_collection_modifyitems,
    pytest_configure,
)
from djb.testing.pytest_secrets import (
    TestSecretsPaths,
    cleanup_test_secrets,
    setup_test_secrets,
)
from djb.testing.typecheck import test_typecheck
from djb.testing.pytest_cov import has_pytest_cov
from djb.testing.pytest_xdist import has_pytest_xdist

__all__ = [
    # Type checking
    "test_typecheck",
    # Pytest plugin detection
    "has_pytest_cov",
    "has_pytest_xdist",
    # Pytest E2E hooks
    "pytest_addoption",
    "pytest_collection_modifyitems",
    "pytest_configure",
    # Test secrets setup
    "TestSecretsPaths",
    "cleanup_test_secrets",
    "setup_test_secrets",
    # Shared fixtures
    "AgePathAndPublicKey",
    "clear_config_cache",
    "configure_logging",
    "pty_stdin",
    "make_age_key",
    "make_cli_ctx",
    "mock_cli_ctx",
    "make_cli_runner",
    "make_cmd_runner",
    "mock_cmd_runner",
    "alice_key",
    "bob_key",
    "make_djb_config",
    # Docker fixtures (E2E)
    "is_docker_available",
    "require_docker",
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
