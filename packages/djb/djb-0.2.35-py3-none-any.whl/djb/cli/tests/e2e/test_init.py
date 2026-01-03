"""End-to-end tests for djb init CLI command.

These tests exercise the init command while mocking external installers
(Homebrew, uv, bun) to avoid side effects.

Commands tested:
- djb init
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.cli.djb import djb_cli
from djb.cli.init.project import (
    add_djb_to_installed_apps,
    find_settings_file,
    update_gitignore_for_project_config,
)
from djb.cli.utils import CmdRunner
from djb.config.config import _clear_config_cache
from djb.config.acquisition import GitConfigSource


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(django_project: Path) -> Path:
    """Use django_project for all tests in this module."""
    return django_project


class TestInitHelperFunctions:
    """E2E tests for init helper functions."""

    def test_find_settings_file(self, project_dir: Path):
        """Finding Django settings.py."""
        settings_path = find_settings_file(project_dir)
        assert settings_path is not None
        assert settings_path.name == "settings.py"
        assert settings_path.parent.name == "myproject"

    def test_find_settings_file_not_found(self, project_dir: Path):
        """When no settings.py exists."""
        empty_dir = project_dir / "empty"
        empty_dir.mkdir()
        settings_path = find_settings_file(empty_dir)
        assert settings_path is None

    def test_add_djb_to_installed_apps(self, project_dir: Path):
        """Adding djb to INSTALLED_APPS."""
        result = add_djb_to_installed_apps(project_dir)
        assert result is True

        # Verify djb is in the settings
        settings = project_dir / "myproject" / "settings.py"
        content = settings.read_text()
        assert '"djb"' in content or "'djb'" in content

    def test_add_djb_to_installed_apps_already_present(self, project_dir: Path):
        """Adding djb is idempotent."""
        # Add djb first time
        result1 = add_djb_to_installed_apps(project_dir)
        assert result1 is True

        # Second time should return False (already present)
        result2 = add_djb_to_installed_apps(project_dir)
        assert result2 is False

    def test_update_gitignore_for_project_config(self, project_dir: Path):
        """Adding .djb/local.toml to .gitignore."""
        result = update_gitignore_for_project_config(project_dir)
        assert result is True

        gitignore = project_dir / ".gitignore"
        content = gitignore.read_text()
        assert ".djb/local.toml" in content
        assert content.count(".djb/local.toml") == 1

    def test_git_config_source_reads_values(self, project_dir: Path):
        """Reading git config values from global config."""
        # GitConfigSource reads global config, so it returns the user's actual values
        # We just verify it can read some value (not specifically what we set in the test repo)
        email = GitConfigSource("user.email").get()
        name = GitConfigSource("user.name").get()

        # Should get non-empty values from global git config
        assert email is not None and len(email) > 0
        assert name is not None and len(name) > 0


class TestInit:
    """E2E tests for djb init command."""

    def test_init_skips_all(
        self,
        make_cli_runner,
        project_dir,
    ):
        """Init with all skip flags."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-frontend",
                "--skip-db",
                "--skip-secrets",
                "--skip-hooks",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should show success message
        assert "initialization complete" in result.output.lower()

    def test_init_adds_djb_to_installed_apps(
        self,
        make_cli_runner,
        project_dir,
    ):
        """Init adds djb to INSTALLED_APPS."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-frontend",
                "--skip-db",
                "--skip-secrets",
                "--skip-hooks",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify djb was added to INSTALLED_APPS
        settings = project_dir / "myproject" / "settings.py"
        content = settings.read_text()
        assert '"djb"' in content

    def test_init_updates_gitignore(
        self,
        make_cli_runner,
        project_dir,
    ):
        """Init updates .gitignore."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "init",
                "--skip-brew",
                "--skip-python",
                "--skip-frontend",
                "--skip-db",
                "--skip-secrets",
                "--skip-hooks",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify .gitignore was updated
        gitignore = project_dir / ".gitignore"
        content = gitignore.read_text()
        assert ".djb/local.toml" in content

    def test_init_fails_without_pyproject(
        self,
        make_cli_runner,
        project_dir: Path,
    ):
        """Init fails when pyproject.toml is missing."""
        empty_dir = project_dir / "empty"
        empty_dir.mkdir()

        env = {
            "DJB_PROJECT_DIR": str(empty_dir),
            "DJB_NAME": "Test User",
            "DJB_EMAIL": "test@example.com",
        }

        with patch.dict(os.environ, env):
            result = make_cli_runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-db",
                    "--skip-secrets",
                    "--skip-hooks",
                ],
            )

        # Should fail with helpful error
        assert result.exit_code != 0
        assert "pyproject.toml" in result.output.lower()

    def test_init_with_mocked_brew(
        self,
        make_cli_runner,
        project_dir,
    ):
        """Init with mocked Homebrew commands."""

        # Mock check to pretend brew packages are installed
        def mock_check(cmd, *args, **kwargs):
            cmd_str = " ".join(cmd)
            if "brew" in cmd_str:
                return True  # All brew packages "installed"
            if "which" in cmd_str:
                return True  # All tools "available"
            return True

        with patch.object(CmdRunner, "check", side_effect=mock_check):
            result = make_cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "init",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-db",
                    "--skip-secrets",
                    "--skip-hooks",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should show that packages are already installed
        assert "already installed" in result.output.lower()

    def test_init_is_idempotent(
        self,
        make_cli_runner,
        project_dir,
    ):
        """Running 'djb init' twice is idempotent: INSTALLED_APPS contains djb only once."""
        skip_flags = [
            "--skip-brew",
            "--skip-python",
            "--skip-frontend",
            "--skip-db",
            "--skip-secrets",
            "--skip-hooks",
        ]

        # First run
        result1 = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "init", *skip_flags],
        )
        assert result1.exit_code == 0, f"First run failed: {result1.output}"

        # Reset config between CLI invocations so configure() can be called again
        _clear_config_cache()

        # Second run
        result2 = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "init", *skip_flags],
        )
        assert result2.exit_code == 0, f"Second run failed: {result2.output}"

        # Verify djb is still in INSTALLED_APPS (only once)
        settings = project_dir / "myproject" / "settings.py"
        content = settings.read_text()
        # Should have "djb" only once
        assert content.count('"djb"') == 1 or content.count("'djb'") == 1

    def test_init_creates_config_files_in_fresh_project(
        self,
        make_cli_runner,
        project_dir: Path,
    ):
        """Init creates .djb/local.toml and .djb/project.toml in fresh project.

        When running djb init in a project that has never had djb initialized,
        it should create both config files with appropriate values.

        Note: We only set DJB_PROJECT_DIR to point to the test project.
        Name/email will be acquired from git config (set up in the fixture),
        which is a "derived" source, so they get saved to local.toml.
        """
        # Ensure no .djb directory exists yet
        djb_dir = project_dir / ".djb"
        assert not djb_dir.exists(), "Test requires fresh project without .djb directory"

        # Only set project dir - let name/email come from git config (derived source)
        env = {
            "DJB_PROJECT_DIR": str(project_dir),
        }

        with patch.dict(os.environ, env):
            result = make_cli_runner.invoke(
                djb_cli,
                [
                    "init",
                    "--skip-brew",
                    "--skip-python",
                    "--skip-frontend",
                    "--skip-db",
                    "--skip-secrets",
                    "--skip-hooks",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify .djb directory was created
        assert djb_dir.exists(), ".djb directory should be created"

        # Verify local.toml was created with user settings (from git config)
        local_toml = djb_dir / "local.toml"
        assert local_toml.exists(), ".djb/local.toml should be created"
        local_content = local_toml.read_text()
        assert "name = " in local_content or "email = " in local_content

        # Verify project.toml was created with project settings
        project_toml = djb_dir / "project.toml"
        assert project_toml.exists(), ".djb/project.toml should be created"
        project_content = project_toml.read_text()
        assert "project_name = " in project_content
