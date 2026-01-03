"""
Shared test fixtures for djb config tests.

See __init__.py for the full list of available fixtures and utilities.

Auto-enabled fixtures (applied to all tests automatically):
    clean_djb_env - Ensures a clean environment by removing DJB_* env vars

Factory fixtures:
    make_config_file - Factory for creating config files in .djb directory
    mock_cmd_runner - Mock for CmdRunner methods (provides .run)
"""

from __future__ import annotations

import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Literal

import pytest
import tomli_w

from djb.config.config import _clear_config_cache
from djb.testing.fixtures import (  # noqa: F401 - exported fixtures
    make_cli_ctx,
    mock_cli_ctx,
    mock_cmd_runner,
)

# Environment variables that may be set by CLI test fixtures
_DJB_ENV_VARS = [
    "DJB_PROJECT_DIR",
    "DJB_PROJECT_NAME",
    "DJB_NAME",
    "DJB_EMAIL",
    "DJB_MODE",
    "DJB_PLATFORM",
    "DJB_HOSTNAME",
]


@pytest.fixture(autouse=True)
def clean_djb_env() -> Generator[None, None, None]:
    """Ensure a clean environment for config tests.

    This fixture:
    - Clears the config cache before each test
    - Removes all DJB_* environment variables before each test
    - Restores the original env state afterward
    """
    _clear_config_cache()
    old_env = {k: os.environ.get(k) for k in _DJB_ENV_VARS}
    for k in _DJB_ENV_VARS:
        os.environ.pop(k, None)
    try:
        yield
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture
def make_config_file(tmp_path: Path) -> Callable[..., Path]:
    """Factory for creating config files in .djb directory.

    Returns a factory function that creates config files with the given content.

    Pytest:
        Uses pytest's `tmp_path` fixture internally, so files are created in the
        same temporary directory available to the test function.

    Args:
        content: Dict or TOML string content to write to the config file
        config_type: Either "local" or "project" (default: "local")

    Returns:
        Path to the created config file

    Usage:
        def test_something(tmp_path, make_config_file):
            # Pass a dict (recommended):
            config_path = make_config_file({"name": "John", "email": "john@example.com"})
            # Creates {tmp_path}/.djb/local.toml

            # For project config:
            config_path = make_config_file({"seed_command": "myapp.cli:seed"}, config_type="project")
            # Creates {tmp_path}/.djb/project.toml

            # You can also pass a TOML string:
            config_path = make_config_file('name = "John"')
    """
    config_dir = tmp_path / ".djb"

    def _create(
        content: str | dict,
        config_type: Literal["local", "project"] = "local",
    ) -> Path:
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / f"{config_type}.toml"

        if isinstance(content, dict):
            with open(config_file, "wb") as f:
                tomli_w.dump(content, f)
        else:
            config_file.write_text(content)

        return config_file

    return _create
