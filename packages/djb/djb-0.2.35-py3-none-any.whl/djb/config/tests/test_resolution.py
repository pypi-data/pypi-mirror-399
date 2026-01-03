"""Tests for djb.config.resolution module; ProvenanceChainMap and ResolutionContext."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from djb.config.resolution import (
    ConfigSource,
    ProvenanceChainMap,
    ResolutionContext,
)


class TestProvenanceChainMapGet:
    """Tests for ProvenanceChainMap.get() method."""

    def test_get_from_cli_layer(self):
        """get() returns value from CLI layer with correct source."""
        chain = ProvenanceChainMap(
            cli={"project_name": "cli-value"},
            file_layers={
                "local": {"project_name": "local-value"},
                "project": {"project_name": "project-value"},
            },
        )

        value, source = chain.get("project_name", "DJB_PROJECT_NAME")
        assert value == "cli-value"
        assert source == ConfigSource.CLI

    def test_get_from_env_layer(self):
        """get() returns value from env layer with correct source."""
        chain = ProvenanceChainMap(
            cli={},
            env={"DJB_PROJECT_NAME": "env-value"},
            file_layers={
                "local": {"project_name": "local-value"},
                "project": {"project_name": "project-value"},
            },
        )

        value, source = chain.get("project_name", "DJB_PROJECT_NAME")
        assert value == "env-value"
        assert source == ConfigSource.ENV

    def test_get_from_local_layer(self):
        """get() returns value from local layer with correct source."""
        chain = ProvenanceChainMap(
            cli={},
            env={},
            file_layers={
                "local": {"name": "local-value"},
                "project": {"name": "project-value"},
            },
        )

        value, source = chain.get("name", "DJB_NAME")
        assert value == "local-value"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_from_project_layer(self):
        """get() returns value from project layer with correct source."""
        chain = ProvenanceChainMap(
            cli={},
            env={},
            file_layers={"project": {"seed_command": "project-value"}},
        )

        value, source = chain.get("seed_command", "DJB_SEED_COMMAND")
        assert value == "project-value"
        assert source == ConfigSource.PROJECT_CONFIG

    def test_get_not_found(self):
        """get() returns (None, None) when key not found."""
        chain = ProvenanceChainMap(cli={}, env={})

        value, source = chain.get("missing_key", "DJB_MISSING")
        assert value is None
        assert source is None

    def test_get_respects_priority_order(self):
        """get() respects cli > env > local > project priority."""
        chain = ProvenanceChainMap(
            cli={"key": "cli"},
            env={"DJB_KEY": "env"},
            file_layers={
                "local": {"key": "local"},
                "project": {"key": "project"},
            },
        )

        # CLI wins
        value, source = chain.get("key", "DJB_KEY")
        assert value == "cli"
        assert source == ConfigSource.CLI

    def test_get_falls_back_to_env_when_cli_empty(self):
        """env is used when CLI has empty string."""
        chain = ProvenanceChainMap(
            cli={"key": ""},
            env={"DJB_KEY": "env"},
            file_layers={
                "local": {"key": "local"},
                "project": {"key": "project"},
            },
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value == "env"
        assert source == ConfigSource.ENV

    def test_get_falls_back_to_local_when_cli_and_env_empty(self):
        """local config is used when CLI and ENV have empty strings."""
        chain = ProvenanceChainMap(
            cli={"key": ""},
            env={"DJB_KEY": ""},
            file_layers={
                "local": {"key": "local"},
                "project": {"key": "project"},
            },
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value == "local"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_falls_back_to_project_when_others_empty(self):
        """project config is used when CLI, ENV, and LOCAL all have empty strings."""
        chain = ProvenanceChainMap(
            cli={"key": ""},
            env={"DJB_KEY": ""},
            file_layers={
                "local": {"key": ""},
                "project": {"key": "project"},
            },
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value == "project"
        assert source == ConfigSource.PROJECT_CONFIG

    def test_get_skips_empty_string_in_env(self):
        """get() treats empty string as not set (especially for env vars)."""
        chain = ProvenanceChainMap(
            cli={},
            env={"DJB_NAME": ""},
            file_layers={"local": {"name": "local-value"}},
        )

        value, source = chain.get("name", "DJB_NAME")
        assert value == "local-value"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_skips_empty_string_in_config(self):
        """get() treats empty string as not set in config layers too."""
        chain = ProvenanceChainMap(
            cli={"name": ""},
            env={},
            file_layers={"local": {"name": "local-value"}},
        )

        value, source = chain.get("name", "DJB_NAME")
        assert value == "local-value"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_skips_empty_string_in_local(self):
        """get() treats empty string as not set in local layer."""
        chain = ProvenanceChainMap(
            cli={},
            env={},
            file_layers={
                "local": {"name": ""},
                "project": {"name": "project-value"},
            },
        )
        value, source = chain.get("name", "DJB_NAME")
        assert value == "project-value"
        assert source == ConfigSource.PROJECT_CONFIG

    def test_get_skips_empty_string_in_project(self):
        """get() treats empty string as not set in project layer (returns None)."""
        chain = ProvenanceChainMap(
            cli={},
            env={},
            file_layers={"project": {"name": ""}},
        )
        value, source = chain.get("name", "DJB_NAME")
        assert value is None
        assert source is None

    def test_get_all_layers_empty_string_returns_none(self):
        """get() returns None when all layers have empty strings."""
        chain = ProvenanceChainMap(
            cli={"key": ""},
            env={"DJB_KEY": ""},
            file_layers={
                "local": {"key": ""},
                "project": {"key": ""},
            },
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value is None
        assert source is None

    def test_get_with_no_env_key_skips_env(self):
        """get() skips env layer when env_key is None."""
        chain = ProvenanceChainMap(
            cli={},
            env={"DJB_PROJECT_DIR": "env-value"},
        )

        # Passing None for env_key should skip env layer
        value, source = chain.get("project_dir", None)
        assert value is None
        assert source is None

    def test_get_uses_different_keys_per_layer(self):
        """get() uses config_file_key for cli/local/project and env_key for env."""
        chain = ProvenanceChainMap(
            cli={},
            env={"DJB_EMAIL": "env@example.com"},
        )

        # env layer should be accessed with env_key, not config_file_key
        value, source = chain.get("email", "DJB_EMAIL")
        assert value == "env@example.com"
        assert source == ConfigSource.ENV

        # If we don't provide env_key, env layer should be skipped
        chain2 = ProvenanceChainMap(
            cli={},
            env={"email": "env@example.com"},  # Won't match without env_key
        )
        value2, source2 = chain2.get("email", None)
        assert value2 is None
        assert source2 is None

    def test_get_env_key_different_from_config_file_key(self):
        """env layer uses env_key while others use config_file_key."""
        chain = ProvenanceChainMap(
            cli={"email": "cli@example.com"},
            env={"DJB_USER_EMAIL": "env@example.com"},  # Different key format
            file_layers={
                "local": {"email": "local@example.com"},
                "project": {"email": "project@example.com"},
            },
        )
        # env_key is different from config_file_key
        value, source = chain.get("email", "DJB_USER_EMAIL")
        assert value == "cli@example.com"  # CLI wins using config_file_key
        assert source == ConfigSource.CLI

    def test_get_env_key_none_with_env_value_present(self):
        """env layer is skipped when env_key is None, even with matching key."""
        chain = ProvenanceChainMap(
            cli={},
            env={"project_name": "env-value"},  # Uses config_file_key format
            file_layers={"local": {"project_name": "local-value"}},
        )
        # With env_key=None, env layer should be skipped
        value, source = chain.get("project_name", None)
        assert value == "local-value"  # Falls through to local
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_env_key_empty_string_skips_env(self):
        """Empty string env_key behaves like None (skips env layer)."""
        chain = ProvenanceChainMap(
            cli={},
            env={"": "env-value", "DJB_KEY": "real-env"},
            file_layers={"local": {"key": "local-value"}},
        )
        # Empty string env_key should skip env layer (key check fails)
        value, source = chain.get("key", "")
        assert value == "local-value"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_key_missing_from_layer_falls_through(self):
        """Missing key (not empty string) falls through to next layer."""
        chain = ProvenanceChainMap(
            cli={},  # key doesn't exist
            env={},  # key doesn't exist
            file_layers={
                "local": {"key": "local-value"},
                "project": {"key": "project-value"},
            },
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value == "local-value"
        assert source == ConfigSource.LOCAL_CONFIG

    def test_get_mixed_missing_and_empty_string(self):
        """Mix of missing keys and empty strings falls through correctly."""
        chain = ProvenanceChainMap(
            cli={},  # key missing
            env={"DJB_KEY": ""},  # key empty
            file_layers={"project": {"key": "project-value"}},  # local missing
        )
        value, source = chain.get("key", "DJB_KEY")
        assert value == "project-value"
        assert source == ConfigSource.PROJECT_CONFIG


class TestProvenanceChainMapContains:
    """Tests for ProvenanceChainMap.__contains__() method."""

    def test_contains_in_cli(self):
        """__contains__ finds key in CLI layer."""
        chain = ProvenanceChainMap(cli={"key": "value"})
        assert "key" in chain

    def test_contains_in_env(self):
        """__contains__ finds key in env layer (uses config_file_key)."""
        # Note: __contains__ uses config_file_key for all layers
        chain = ProvenanceChainMap(env={"key": "value"})
        assert "key" in chain

    def test_contains_in_local(self):
        """__contains__ finds key in local layer."""
        chain = ProvenanceChainMap(file_layers={"local": {"key": "value"}})
        assert "key" in chain

    def test_contains_in_project(self):
        """__contains__ finds key in project layer."""
        chain = ProvenanceChainMap(file_layers={"project": {"key": "value"}})
        assert "key" in chain

    def test_not_contains(self):
        """__contains__ returns False for missing key."""
        chain = ProvenanceChainMap(cli={}, env={})
        assert "missing" not in chain


class TestProvenanceChainMapDefaults:
    """Tests for ProvenanceChainMap default behavior."""

    def test_default_env_is_os_environ(self):
        """Default env layer uses os.environ."""
        # Create a chain without specifying env
        chain = ProvenanceChainMap()

        # Access internal layers to verify os.environ is used
        assert chain._layers["env"] is os.environ

    def test_default_layers_are_empty_dicts(self):
        """Default cli/local/project layers are empty dicts."""
        chain = ProvenanceChainMap()

        assert chain._layers["cli"] == {}
        assert chain._layers["local"] == {}
        assert chain._layers["project"] == {}


class TestResolutionContext:
    """Tests for ResolutionContext dataclass."""

    def test_creation(self, tmp_path: Path):
        """ResolutionContext can be created."""
        chain = ProvenanceChainMap()
        ctx = ResolutionContext(
            project_root=tmp_path,
            project_root_source=ConfigSource.PYPROJECT,
            configs=chain,
        )

        assert ctx.project_root == tmp_path
        assert ctx.project_root_source == ConfigSource.PYPROJECT
        assert ctx.configs is chain

    def test_is_frozen(self, tmp_path: Path):
        """ResolutionContext is immutable (frozen)."""
        ctx = ResolutionContext(
            project_root=tmp_path,
            project_root_source=ConfigSource.PYPROJECT,
        )

        with pytest.raises(AttributeError):
            ctx.project_root = tmp_path / "other"  # type: ignore[misc]

    def test_default_configs(self, tmp_path: Path):
        """ResolutionContext has default empty ProvenanceChainMap."""
        ctx = ResolutionContext(
            project_root=tmp_path,
            project_root_source=ConfigSource.CWD_PATH,
        )

        assert isinstance(ctx.configs, ProvenanceChainMap)
        value, source = ctx.configs.get("any_key", "DJB_ANY")
        assert value is None
        assert source is None


class TestConfigSourceEnum:
    """Additional tests for ConfigSource enum beyond test_config.py coverage."""

    def test_config_file_type_for_local(self):
        """config_file_type property returns 'local' for LOCAL_CONFIG."""
        assert ConfigSource.LOCAL_CONFIG.config_file_type == "local"

    def test_config_file_type_for_project(self):
        """config_file_type property returns 'project' for PROJECT_CONFIG."""
        assert ConfigSource.PROJECT_CONFIG.config_file_type == "project"

    def test_config_file_type_for_non_config_sources(self):
        """config_file_type returns None for non-config sources."""
        assert ConfigSource.CLI.config_file_type is None
        assert ConfigSource.ENV.config_file_type is None
        assert ConfigSource.PYPROJECT.config_file_type is None
        assert ConfigSource.GIT.config_file_type is None
        assert ConfigSource.CWD_PATH.config_file_type is None
        assert ConfigSource.CWD_NAME.config_file_type is None
        assert ConfigSource.DEFAULT.config_file_type is None
        assert ConfigSource.DERIVED.config_file_type is None
        assert ConfigSource.PROMPTED.config_file_type is None

    def test_cwd_path_and_cwd_name_are_derived(self):
        """CWD_PATH and CWD_NAME are classified as derived."""
        assert ConfigSource.CWD_PATH.is_derived() is True
        assert ConfigSource.CWD_NAME.is_derived() is True
        assert ConfigSource.CWD_PATH.is_explicit() is False
        assert ConfigSource.CWD_NAME.is_explicit() is False

    def test_default_is_derived(self):
        """DEFAULT is classified as derived."""
        assert ConfigSource.DEFAULT.is_derived() is True
        assert ConfigSource.DEFAULT.is_explicit() is False
