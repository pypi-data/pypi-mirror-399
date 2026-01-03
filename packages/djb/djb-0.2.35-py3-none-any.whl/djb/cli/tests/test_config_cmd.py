"""Unit tests for djb config CLI command.

Tests that require real file I/O (config file operations) are in e2e/test_config_cmd.py.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, Mock, patch

import attrs
import pytest

from djb.cli.config_cmd import _format_json_with_provenance
from djb.cli.djb import djb_cli
from djb.config import ConfigSource, DjbConfig, get_field_descriptor
from djb.config.field import ConfigFieldABC


class TestConfigShow:
    """Tests for djb config --show output format."""

    def test_show_outputs_json(self, make_cli_runner, djb_config):
        """--show outputs valid JSON."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--show"])

        assert result.exit_code == 0
        # Should be valid JSON
        config = json.loads(result.output)
        assert isinstance(config, dict)

    def test_show_contains_expected_keys(self, make_cli_runner, djb_config):
        """--show output contains all expected config keys."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Get expected keys from DjbConfig attrs fields.
        # Excludes private fields (starting with _)
        expected_keys = {
            field.name for field in attrs.fields(DjbConfig) if not field.name.startswith("_")
        }
        assert expected_keys == set(config.keys())

    def test_show_excludes_private_attributes(self, make_cli_runner, djb_config):
        """--show output excludes private attributes."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Private attributes should not be in output
        assert "_loaded" not in config
        assert "_provenance" not in config

    def test_show_serializes_enums_as_strings(self, make_cli_runner, djb_config):
        """Mode and platform are serialized as strings, not enum objects."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Should be string values, not enum representations
        assert config["mode"] == "development"
        assert config["platform"] == "heroku"

    def test_show_serializes_path_as_string(self, make_cli_runner, djb_config):
        """project_dir is serialized as a string path."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Should be a string, not a Path object representation
        assert isinstance(config["project_dir"], str)
        assert not config["project_dir"].startswith("PosixPath")

    def test_config_without_args_shows_help(self, make_cli_runner, djb_config):
        """'djb config' without args shows help."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config"])

        assert result.exit_code == 0
        assert "Manage djb configuration" in result.output
        assert "--show" in result.output

    def test_with_provenance_outputs_json_with_comments(self, make_cli_runner, djb_config):
        """--with-provenance adds provenance comments to JSON."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--with-provenance"])

        assert result.exit_code == 0
        # Should contain JSON-like structure with // comments
        assert "{" in result.output
        assert "}" in result.output
        assert "//" in result.output

    def test_with_provenance_shows_all_keys(self, make_cli_runner, djb_config):
        """--with-provenance output contains all config keys."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--with-provenance"])

        assert result.exit_code == 0
        assert '"project_dir"' in result.output
        assert '"project_name"' in result.output
        assert '"mode"' in result.output

    def test_with_provenance_alone_shows_output(self, make_cli_runner, djb_config):
        """--with-provenance alone (without --show) shows output."""
        result = make_cli_runner.invoke(djb_cli, ["-q", "config", "--with-provenance"])

        assert result.exit_code == 0
        # Should output config, not help
        assert '"project_dir"' in result.output


# Tests for config project_name subcommand that require file I/O are in e2e/test_config_cmd.py


class TestFormatJsonWithProvenance:
    """Unit tests for _format_json_with_provenance helper function."""

    def test_formats_config_as_json_with_comments(self):
        """_format_json_with_provenance produces JSON with provenance comments."""
        # Create a mock config object
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "project_dir": "/path/to/project",
            "mode": "development",
        }
        mock_config.get_source.side_effect = lambda key: {
            "project_dir": ConfigSource.CLI,
            "mode": ConfigSource.DEFAULT,
        }.get(key)

        result = _format_json_with_provenance(mock_config)

        # Should have JSON structure with comments
        assert "{" in result
        assert "}" in result
        assert "//" in result
        assert '"project_dir"' in result
        assert '"mode"' in result

    def test_includes_provenance_for_each_key(self):
        """_format_json_with_provenance shows provenance for each config key."""
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "name": "Test User",
            "email": "test@example.com",
        }
        mock_config.get_source.side_effect = lambda key: {
            "name": ConfigSource.LOCAL_CONFIG,
            "email": ConfigSource.ENV,
        }.get(key)

        result = _format_json_with_provenance(mock_config)

        # Should include provenance values
        assert "local_config" in result
        assert "environment" in result

    def test_shows_not_set_for_none_source(self):
        """_format_json_with_provenance shows '(not set)' when source is None."""
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "seed_command": None,
        }
        mock_config.get_source.return_value = None

        result = _format_json_with_provenance(mock_config)

        assert "(not set)" in result

    def test_aligns_provenance_comments(self):
        """_format_json_with_provenance aligns comments across lines."""
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "short": "a",
            "very_long_key_name": "value",
        }
        mock_config.get_source.return_value = ConfigSource.DEFAULT

        result = _format_json_with_provenance(mock_config)

        # Both lines should have "//" at the same column
        lines = [line for line in result.split("\n") if "//" in line]
        comment_positions = [line.index("//") for line in lines]
        assert len(set(comment_positions)) == 1, "Comments should be aligned"


class TestGetFieldDescriptor:
    """Unit tests for get_field_descriptor helper function."""

    def test_returns_config_field_for_valid_field(self):
        """get_field_descriptor returns ConfigFieldABC for valid field."""
        result = get_field_descriptor("project_name")
        assert isinstance(result, ConfigFieldABC)
        assert result.field_name == "project_name"

    def test_raises_for_unknown_field(self):
        """get_field_descriptor raises ValueError for unknown field."""
        with pytest.raises(ValueError) as exc_info:
            get_field_descriptor("nonexistent_field")
        assert "Unknown field" in str(exc_info.value)

    def test_raises_for_non_config_field(self):
        """get_field_descriptor raises ValueError for non-config attrs field."""
        # _loaded and _provenance are internal fields without ConfigFieldABC metadata
        # but they shouldn't be exposed anyway - try an internal field
        # This test verifies the error path even if no such field exists in practice
        # by patching attrs.fields to return an object where fake_field has no metadata
        fake_field = MagicMock()
        fake_field.name = "fake_field"
        fake_field.metadata = {}  # No ATTRSLIB_METADATA_KEY

        # attrs.fields returns a tuple-like object with named attribute access
        # Simulate this with an object that has fake_field as an attribute
        fake_fields = MagicMock()
        fake_fields.fake_field = fake_field

        with (
            patch("djb.config.config.attrs.fields", return_value=fake_fields),
            pytest.raises(ValueError) as exc_info,
        ):
            get_field_descriptor("fake_field")
        assert "not a config field" in str(exc_info.value)
