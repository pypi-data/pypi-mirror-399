"""Unit tests for config file operations.

Tests for save_config_value_for_mode and delete_config_value_for_mode functions.
"""

from __future__ import annotations

import tomllib

import pytest

from djb.config import (
    LOCAL,
    PROJECT,
    WriteTargetError,
    delete_config_value_for_mode,
    get_field_provenance,
    resolve_write_target,
    save_config_value_for_mode,
)
from djb.config.file import deep_merge


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_merges_flat_dicts(self):
        """Flat dicts are merged with override taking precedence."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_does_not_mutate_inputs(self):
        """Neither input dict is mutated."""
        base = {"a": 1}
        override = {"b": 2}
        deep_merge(base, override)
        assert base == {"a": 1}
        assert override == {"b": 2}

    def test_merges_nested_dicts(self):
        """Nested dicts are recursively merged."""
        base = {"hetzner": {"server_type": "cx22", "location": "nbg1"}}
        override = {"hetzner": {"server_type": "cx32"}}
        result = deep_merge(base, override)
        assert result == {"hetzner": {"server_type": "cx32", "location": "nbg1"}}

    def test_partial_nested_override(self):
        """Partial override preserves unspecified nested fields."""
        base = {
            "hetzner": {
                "server_type": "cx22",
                "location": "nbg1",
                "image": "ubuntu-24.04",
            }
        }
        override = {"hetzner": {"server_type": "cx11"}}
        result = deep_merge(base, override)
        assert result == {
            "hetzner": {
                "server_type": "cx11",
                "location": "nbg1",
                "image": "ubuntu-24.04",
            }
        }

    def test_full_nested_override(self):
        """Full override replaces all nested fields."""
        base = {"hetzner": {"server_type": "cx22", "location": "nbg1"}}
        override = {"hetzner": {"server_type": "cx32", "location": "fsn1", "image": "debian-12"}}
        result = deep_merge(base, override)
        assert result == {
            "hetzner": {"server_type": "cx32", "location": "fsn1", "image": "debian-12"}
        }

    def test_override_replaces_non_dict_with_dict(self):
        """A dict in override replaces a non-dict in base."""
        base = {"key": "value"}
        override = {"key": {"nested": "value"}}
        result = deep_merge(base, override)
        assert result == {"key": {"nested": "value"}}

    def test_override_replaces_dict_with_non_dict(self):
        """A non-dict in override replaces a dict in base."""
        base = {"key": {"nested": "value"}}
        override = {"key": "value"}
        result = deep_merge(base, override)
        assert result == {"key": "value"}

    def test_deeply_nested_merge(self):
        """Merge works for arbitrarily deep nesting."""
        base = {"a": {"b": {"c": {"d": 1}}}}
        override = {"a": {"b": {"c": {"e": 2}}}}
        result = deep_merge(base, override)
        assert result == {"a": {"b": {"c": {"d": 1, "e": 2}}}}


class TestSaveConfigValueForMode:
    """Tests for save_config_value_for_mode function."""

    def test_writes_to_root_when_mode_is_none(self, tmp_path):
        """When mode is None, value is written to root section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode=None
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert data["seed_command"] == "myapp.cli:seed"
        assert "development" not in data
        assert "staging" not in data

    def test_writes_to_root_when_mode_is_production(self, tmp_path):
        """When mode is 'production', value is written to root section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode="production"
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert data["seed_command"] == "myapp.cli:seed"
        assert "development" not in data
        assert "staging" not in data

    def test_writes_to_development_section(self, tmp_path):
        """When mode is 'development', value is written to [development] section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "seed_command" not in data  # Not at root
        assert data["development"]["seed_command"] == "myapp.cli:dev_seed"

    def test_writes_to_staging_section(self, tmp_path):
        """When mode is 'staging', value is written to [staging] section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:staging_seed", mode="staging"
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "seed_command" not in data  # Not at root
        assert data["staging"]["seed_command"] == "myapp.cli:staging_seed"

    def test_preserves_existing_root_values(self, tmp_path):
        """Adding a mode section preserves existing root values."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # First write a root value
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode="production"
        )

        # Then add a development override
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert data["seed_command"] == "myapp.cli:seed"
        assert data["development"]["seed_command"] == "myapp.cli:dev_seed"

    def test_preserves_existing_mode_sections(self, tmp_path):
        """Adding values to one mode section preserves other mode sections."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # Write to development
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )

        # Write to staging
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:staging_seed", mode="staging"
        )

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert data["development"]["seed_command"] == "myapp.cli:dev_seed"
        assert data["staging"]["seed_command"] == "myapp.cli:staging_seed"

    def test_creates_djb_directory_if_not_exists(self, tmp_path):
        """The .djb directory is created if it doesn't exist."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        # Note: .djb directory is NOT created

        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode=None
        )

        config_file = project_dir / ".djb" / "project.toml"
        assert config_file.exists()


class TestDeleteConfigValueForMode:
    """Tests for delete_config_value_for_mode function."""

    def test_deletes_from_root_when_mode_is_none(self, tmp_path):
        """When mode is None, value is deleted from root section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # First set a value
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode=None
        )

        # Then delete it
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode=None)

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "seed_command" not in data

    def test_deletes_from_root_when_mode_is_production(self, tmp_path):
        """When mode is 'production', value is deleted from root section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # First set a value
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode="production"
        )

        # Then delete it
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode="production")

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "seed_command" not in data

    def test_deletes_from_development_section(self, tmp_path):
        """When mode is 'development', value is deleted from [development] section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # First set a value
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )

        # Then delete it
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode="development")

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        # Section should be cleaned up since it's empty
        assert "development" not in data

    def test_preserves_other_values_in_section(self, tmp_path):
        """Deleting one value preserves other values in the same section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # Set two values in development
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )
        save_config_value_for_mode(PROJECT, project_dir, "log_level", "debug", mode="development")

        # Delete only seed_command
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode="development")

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "seed_command" not in data["development"]
        assert data["development"]["log_level"] == "debug"

    def test_preserves_other_sections(self, tmp_path):
        """Deleting from one section preserves other sections."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # Set values in both sections
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:dev_seed", mode="development"
        )
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:staging_seed", mode="staging"
        )

        # Delete only from development
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode="development")

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert "development" not in data  # Cleaned up
        assert data["staging"]["seed_command"] == "myapp.cli:staging_seed"

    def test_noop_when_file_does_not_exist(self, tmp_path):
        """Deleting from a non-existent file is a no-op."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # Should not raise
        delete_config_value_for_mode(PROJECT, project_dir, "seed_command", mode="development")

        config_file = project_dir / ".djb" / "project.toml"
        assert not config_file.exists()

    def test_noop_when_key_does_not_exist(self, tmp_path):
        """Deleting a non-existent key is a no-op."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # Set one value
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode="production"
        )

        # Try to delete a different key
        delete_config_value_for_mode(PROJECT, project_dir, "nonexistent", mode="production")

        config_file = project_dir / ".djb" / "project.toml"
        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        assert data["seed_command"] == "myapp.cli:seed"


class TestGetFieldProvenance:
    """Tests for get_field_provenance function."""

    def test_finds_flat_field_in_project(self, tmp_path):
        """get_field_provenance finds flat field in project.toml."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode=None
        )

        result = get_field_provenance(project_dir, "seed_command")
        assert result == PROJECT

    def test_finds_flat_field_in_local(self, tmp_path):
        """get_field_provenance finds flat field in local.toml."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(LOCAL, project_dir, "name", "John", mode=None)

        result = get_field_provenance(project_dir, "name")
        assert result == LOCAL

    def test_returns_none_if_not_found(self, tmp_path):
        """get_field_provenance returns None when field is not found."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        result = get_field_provenance(project_dir, "nonexistent")
        assert result is None

    def test_priority_local_over_project(self, tmp_path):
        """get_field_provenance returns LOCAL when field exists in both files."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:project_seed", mode=None
        )
        save_config_value_for_mode(
            LOCAL, project_dir, "seed_command", "myapp.cli:local_seed", mode=None
        )

        result = get_field_provenance(project_dir, "seed_command")
        assert result == LOCAL

    def test_finds_nested_field_in_section(self, tmp_path):
        """get_field_provenance finds nested field in [section]."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT, project_dir, "default_server_type", "cx32", mode=None, section_path="hetzner"
        )

        result = get_field_provenance(project_dir, "hetzner.default_server_type")
        assert result == PROJECT

    def test_finds_nested_field_in_mode_section(self, tmp_path):
        """get_field_provenance finds nested field in [mode.section]."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT,
            project_dir,
            "default_server_type",
            "cx32",
            mode="development",
            section_path="hetzner",
        )

        result = get_field_provenance(
            project_dir, "hetzner.default_server_type", mode="development"
        )
        assert result == PROJECT

    def test_finds_flat_field_in_mode_section(self, tmp_path):
        """get_field_provenance finds flat field in [mode] section."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(LOCAL, project_dir, "log_level", "debug", mode="development")

        result = get_field_provenance(project_dir, "log_level", mode="development")
        assert result == LOCAL


class TestResolveWriteTarget:
    """Tests for resolve_write_target function."""

    def test_returns_provenance_if_exists_in_project(self, tmp_path):
        """resolve_write_target returns PROJECT when value exists in project.toml."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT, project_dir, "seed_command", "myapp.cli:seed", mode=None
        )

        result = resolve_write_target(project_dir, "seed_command")
        assert result == PROJECT

    def test_returns_provenance_if_exists_in_local(self, tmp_path):
        """resolve_write_target returns LOCAL when value exists in local.toml."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(LOCAL, project_dir, "seed_command", "myapp.cli:seed", mode=None)

        result = resolve_write_target(project_dir, "seed_command")
        assert result == LOCAL

    def test_returns_field_config_file_for_new_field(self, tmp_path):
        """resolve_write_target returns field's config_file when not yet set."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # seed_command is defined in project by default
        result = resolve_write_target(project_dir, "seed_command")
        assert result == PROJECT

    def test_returns_field_config_file_for_local_field(self, tmp_path):
        """resolve_write_target returns LOCAL for fields defined in local.toml."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # name is defined in local by default
        result = resolve_write_target(project_dir, "name")
        assert result == LOCAL

    def test_raises_for_core_field_without_override(self, tmp_path):
        """resolve_write_target raises WriteTargetError for core.toml fields."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".djb").mkdir()

        # hetzner.default_server_type is defined in core.toml
        with pytest.raises(WriteTargetError) as exc_info:
            resolve_write_target(project_dir, "hetzner.default_server_type")

        assert "hetzner.default_server_type" in str(exc_info.value)
        assert "core.toml" in str(exc_info.value)

    def test_returns_provenance_for_core_field_with_override(self, tmp_path):
        """resolve_write_target returns provenance file when core field is overridden."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        save_config_value_for_mode(
            PROJECT, project_dir, "default_server_type", "cx32", mode=None, section_path="hetzner"
        )

        result = resolve_write_target(project_dir, "hetzner.default_server_type")
        assert result == PROJECT


class TestWriteTargetError:
    """Tests for WriteTargetError exception."""

    def test_stores_field_path(self):
        """WriteTargetError stores field_path for CLI error handling."""
        error = WriteTargetError("hetzner.default_server_type", "test message")
        assert error.field_path == "hetzner.default_server_type"
        assert "test message" in str(error)
