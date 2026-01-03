"""
Config test utilities and base classes.

Autouse Fixtures (conftest.py):
    clean_djb_env - Removes DJB_* environment variables before each test

Provides:
    ConfigTestBase - Base class for test config objects with provenance tracking
    make_test_config - Factory for creating test config instances
"""

from __future__ import annotations

from typing import Any

import attrs

from djb.config.resolution import ConfigSource


@attrs.frozen
class ConfigTestBase:
    """Base class for test configurations with provenance tracking.

    This is a simple @attrs.frozen class that provides the same provenance
    tracking methods as DjbConfig, without the full field resolution machinery.

    Usage:
        @attrs.frozen
        class MyTestConfig(ConfigTestBase):
            name: str = "default"

        config = MyTestConfig(_provenance={"name": ConfigSource.LOCAL_CONFIG})
        assert config.get_source("name") == ConfigSource.LOCAL_CONFIG
    """

    _provenance: dict[str, ConfigSource] = attrs.field(
        factory=dict, repr=False, alias="_provenance"
    )

    def is_explicit(self, field: str) -> bool:
        """Check if a field was explicitly configured."""
        source = self._provenance.get(field)
        return source is not None and source.is_explicit()

    def is_derived(self, field: str) -> bool:
        """Check if a field was derived from secondary sources."""
        source = self._provenance.get(field)
        return source is not None and source.is_derived()

    def is_configured(self, field: str) -> bool:
        """Check if a field has a configured value."""
        return self.get_source(field) is not None

    def get_source(self, field: str) -> ConfigSource | None:
        """Get the source of a field's value."""
        return self._provenance.get(field)


def make_test_config(
    fields: dict[str, Any],
    sources: dict[str, ConfigSource] | None = None,
) -> ConfigTestBase:
    """Factory for creating test config instances with custom fields.

    This is a convenience function for tests that need a quick config with
    specific fields, without defining a full subclass.

    Args:
        fields: Dict mapping field names to their values
        sources: Dict mapping field names to their ConfigSource (for get_source)

    Returns:
        A TestConfigBase instance with the given fields set as attributes

    Usage:
        config = make_test_config(
            fields={"name": "John", "email": "john@example.com"},
            sources={"name": ConfigSource.LOCAL_CONFIG},
        )
        assert config.name == "John"
        assert config.get_source("name") == ConfigSource.LOCAL_CONFIG
    """
    config = ConfigTestBase(_provenance=sources or {})
    for name, value in fields.items():
        object.__setattr__(config, name, value)
    return config


__all__ = [
    "ConfigTestBase",
    "make_test_config",
]
