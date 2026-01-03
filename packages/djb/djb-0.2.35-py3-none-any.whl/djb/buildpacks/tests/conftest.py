"""Shared fixtures for buildpacks tests.

Note: make_buildpack_dockerfiles fixture is in e2e/conftest.py
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from djb.testing.fixtures import mock_cmd_runner as mock_cmd_runner  # noqa: F401
from djb.testing.fixtures import project_dir as project_dir  # noqa: F401


@pytest.fixture
def mock_ssh() -> MagicMock:
    """Mock SSHClient for remote buildpack tests."""
    ssh = MagicMock()
    # Default: commands succeed
    ssh.run.return_value = (0, "", "")
    return ssh


@pytest.fixture
def make_pyproject_with_gdal(project_dir: Path) -> Path:
    """Create pyproject.toml with gdal dependency."""
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        """\
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "django>=5.0",
    "gdal==3.10.0",
]
"""
    )
    return pyproject


@pytest.fixture
def make_pyproject_with_gdal_range(project_dir: Path) -> Path:
    """Create pyproject.toml with gdal version range."""
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        """\
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "gdal>=3.9.0,<4.0",
]
"""
    )
    return pyproject


@pytest.fixture
def pyproject_without_gdal(project_dir: Path) -> Path:
    """Create pyproject.toml without gdal dependency."""
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        """\
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "django>=5.0",
]
"""
    )
    return pyproject
