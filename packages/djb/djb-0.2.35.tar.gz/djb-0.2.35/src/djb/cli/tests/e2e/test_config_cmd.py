"""E2E tests for djb config CLI command.

These tests require real file I/O for testing config file operations.
Unit tests for output format are in ../test_config_cmd.py.
"""

from __future__ import annotations

import pytest

from djb.config.config import _clear_config_cache
from djb.cli.djb import djb_cli


pytestmark = pytest.mark.e2e_marker


class TestConfigShow:
    """E2E tests for djb config --show with real project directories."""

    def test_with_provenance_shows_environment_source(
        self, make_cli_runner, project_dir, monkeypatch
    ):
        """--with-provenance shows environment as source for env vars."""
        # Set an env var directly to test environment source detection
        monkeypatch.setenv("DJB_PROJECT_NAME", "env-project")
        _clear_config_cache()  # Clear cache so next CLI call picks up env var

        result = make_cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "--with-provenance"]
        )

        assert result.exit_code == 0
        assert "environment" in result.output


class TestConfigProjectName:
    """E2E tests for djb config project_name subcommand."""

    def test_show_current_value_from_pyproject(self, make_cli_runner, pyproject_dir_with_git):
        """Showing current project_name (falls back to pyproject.toml)."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(pyproject_dir_with_git), "-q", "config", "project_name"],
        )

        assert result.exit_code == 0
        # Should show the project name from pyproject.toml
        assert "project_name:" in result.output

    def test_set_valid_project_name(self, make_cli_runner, project_dir):
        """Setting a valid project name."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "my-app"],
        )

        assert result.exit_code == 0
        assert "project_name set to: my-app" in result.output

    def test_set_invalid_project_name_uppercase(self, make_cli_runner, project_dir):
        """Uppercase project names are rejected."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "MyApp"],
        )

        assert result.exit_code != 0
        assert "DNS label" in result.output

    def test_set_invalid_project_name_starts_with_hyphen(self, make_cli_runner, project_dir):
        """Project names starting with hyphen are rejected."""
        # Use -- to separate options from arguments (otherwise -myapp is parsed as -m option)
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--", "-myapp"],
        )

        assert result.exit_code != 0
        assert "DNS label" in result.output

    def test_delete_project_name(self, make_cli_runner, project_dir):
        """Deleting the project_name setting."""
        # Clear pyproject.toml name so we can test config file operations
        (project_dir / "pyproject.toml").write_text("[project]\n")

        # First set a value (writes to djb.yaml config file)
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "my-app"],
        )
        assert result.exit_code == 0

        # Clear cache so next CLI call picks up the config file change
        _clear_config_cache()

        # Then delete it
        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        assert result.exit_code == 0
        assert "project_name removed" in result.output

    def test_delete_from_mode_section_even_when_value_from_environment(
        self, make_cli_runner, project_dir, monkeypatch
    ):
        """Delete removes from mode section even if value comes from environment."""
        # Set env var - this will still be the effective value after delete
        monkeypatch.setenv("DJB_PROJECT_NAME", "env-project")
        _clear_config_cache()

        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        # Delete succeeds (removes from mode section, even if nothing was there)
        assert result.exit_code == 0
        assert "project_name removed" in result.output

    def test_delete_from_mode_section_even_when_value_from_directory_name(
        self, make_cli_runner, project_dir
    ):
        """Delete removes from mode section even if value derived from directory name."""
        # Clear pyproject.toml so it falls back to directory name
        (project_dir / "pyproject.toml").write_text("[project]\n")
        _clear_config_cache()

        result = make_cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        # Delete succeeds (removes from mode section, even if nothing was there)
        assert result.exit_code == 0
        assert "project_name removed" in result.output


class TestConfigModeSpecificWriting:
    """E2E tests for writing config values to mode-specific sections."""

    def test_set_with_mode_development_writes_to_development_section(
        self, make_cli_runner, project_dir
    ):
        """Setting a value with --mode development writes to [development] section."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:dev_seed in project.toml in [development]"
            in result.output
        )

        # Verify the file contains the [development] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content
        assert 'seed_command = "myapp.cli:dev_seed"' in content

    def test_set_with_mode_staging_writes_to_staging_section(self, make_cli_runner, project_dir):
        """Setting a value with --mode staging writes to [staging] section."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "staging",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:staging_seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:staging_seed in project.toml in [staging]"
            in result.output
        )

        # Verify the file contains the [staging] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[staging]" in content
        assert 'seed_command = "myapp.cli:staging_seed"' in content

    def test_set_with_mode_production_writes_to_root(self, make_cli_runner, project_dir):
        """Setting a value with --mode production writes to root section."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "production",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )

        assert result.exit_code == 0
        # Production writes to root, no section indicator in output
        assert "seed_command set to: myapp.cli:seed" in result.output
        assert "[production]" not in result.output

        # Verify seed_command is at root level, not in a section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        # Hostname should appear at root (before any section headers)
        lines = content.split("\n")
        seed_command_line = next((i for i, line in enumerate(lines) if "seed_command" in line), -1)
        section_line = next((i for i, line in enumerate(lines) if line.startswith("[")), len(lines))
        assert (
            seed_command_line < section_line
        ), "seed_command should be in root section (before any [section])"

    def test_set_without_mode_uses_default_development_mode(self, make_cli_runner, project_dir):
        """Setting a value without --mode uses the default mode (development)."""
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:seed in project.toml in [development]" in result.output
        )

        # Verify the file contains the [development] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content

    def test_delete_with_mode_removes_from_mode_section(self, make_cli_runner, project_dir):
        """Deleting with --mode removes value from that mode's section."""
        # First set a value in development section
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )
        assert result.exit_code == 0

        _clear_config_cache()

        # Now delete it from development section
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "--delete",
            ],
        )

        assert result.exit_code == 0
        assert "seed_command removed from project.toml in [development]" in result.output

        # Verify seed_command is gone from the file
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "seed_command" not in content

    def test_mode_sections_are_preserved_when_adding_new_values(self, make_cli_runner, project_dir):
        """Adding values to different mode sections preserves existing sections."""
        # Set development seed_command
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )
        assert result.exit_code == 0

        _clear_config_cache()

        # Set staging seed_command
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "staging",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:staging_seed",
            ],
        )
        assert result.exit_code == 0

        _clear_config_cache()

        # Set production (root) seed_command
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "production",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )
        assert result.exit_code == 0

        # Verify all three are in the file
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content
        assert "[staging]" in content
        assert content.count("seed_command") == 3  # One for each mode
