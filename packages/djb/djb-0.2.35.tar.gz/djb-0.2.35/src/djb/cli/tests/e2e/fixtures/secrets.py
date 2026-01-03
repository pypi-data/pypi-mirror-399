"""Secrets isolation fixtures for E2E tests.

These fixtures provide isolated environments for tools like GPG, age, and SOPS.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from djb.cli.context import CliContext
from djb.cli.utils import CmdRunner
from djb.secrets import SecretsManager

# Constants for test encryption
TEST_PASSPHRASE = "test-passphrase-12345"
TEST_SECRET_VALUE = "super-secret-test-value-abc123"


@pytest.fixture
def gpg_home(project_dir: Path) -> Path:
    """Create an isolated GPG home directory.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    gpg_dir = project_dir / ".gnupg"
    gpg_dir.mkdir(mode=0o700)
    return gpg_dir


@pytest.fixture
def secrets_dir(project_dir: Path) -> Path:
    """Create a secrets directory for testing.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    dir_path = project_dir / "secrets"
    dir_path.mkdir()
    return dir_path


@pytest.fixture
def setup_sops_config(project_dir: Path, secrets_dir: Path) -> Callable[[dict[str, str]], Path]:
    """Factory fixture to create .sops.yaml configuration.

    Example:
        def test_sops(setup_sops_config, alice_key):
            _, alice_public = alice_key
            setup_sops_config({alice_public: "alice@example.com"})
    """
    runner = CliContext(verbose=False).runner

    def _setup(recipients: dict[str, str]) -> Path:
        manager = SecretsManager(runner, project_dir, secrets_dir=secrets_dir)
        return manager.save_config(recipients)

    return _setup
