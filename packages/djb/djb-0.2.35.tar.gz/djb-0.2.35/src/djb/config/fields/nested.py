"""
NestedConfigField - Field for nested config dataclasses.

Reads from a TOML section matching the field name (e.g., [hetzner]).
Mode overrides come from [mode.section] (e.g., [development.hetzner]).
Supports arbitrary nesting depth (e.g., [hetzner.eu] for hetzner.eu.server_type).
"""

from __future__ import annotations

from typing import Any

import attrs

from djb.config.constants import ATTRSLIB_METADATA_KEY
from djb.config.field import ConfigFieldABC
from djb.config.file import navigate_config_path
from djb.config.resolution import ConfigSource, ResolutionContext


class NestedConfigField(ConfigFieldABC):
    """Field for nested config dataclasses.

    Section path is derived from field_name, combined with parent section path
    for deeply nested configs. e.g., field name "hetzner" reads from [hetzner]
    TOML section, and field "eu" nested under "hetzner" reads from [hetzner.eu].

    The nested class must be an attrs frozen dataclass with fields
    that use ConfigFieldABC subclasses (e.g., EnumField, StringField).

    Usage in DjbConfig:
        hetzner: HetznerConfig = NestedConfigField(HetznerConfig)()

    For deeply nested configs:
        # In HetznerConfig:
        eu: HetznerRegionConfig = NestedConfigField(HetznerRegionConfig)()
        # Reads from [hetzner.eu] section
    """

    # Parent section path for deeply nested configs (set during resolution)
    _parent_section_path: str | None = None

    def __init__(self, nested_class: type, **kwargs: Any):
        """Initialize a nested config field.

        Args:
            nested_class: An attrs frozen dataclass with ConfigField fields.
            **kwargs: Passed to ConfigFieldABC.__init__().
        """
        super().__init__(**kwargs)
        self.nested_class = nested_class
        self._parent_section_path = None

    def get_section_path(self) -> str:
        """Get full section path including parent sections.

        For top-level nested fields like "hetzner", returns "hetzner".
        For deeply nested fields like "eu" under "hetzner", returns "hetzner.eu".

        Raises:
            RuntimeError: If accessed before field_name is set.
        """
        if self.field_name is None:
            raise RuntimeError(
                "section_path accessed before field_name was set. "
                "Ensure field_name is assigned before accessing section_path."
            )
        if self._parent_section_path:
            return f"{self._parent_section_path}.{self.field_name}"
        return self.field_name

    def resolve(self, ctx: ResolutionContext) -> tuple[Any, ConfigSource | None]:
        """Resolve nested config from TOML section.

        Reads from [section_path] in each config layer, with mode sections
        (e.g., [development.hetzner]) merged on top. Supports arbitrary nesting
        depth by passing parent section path to nested NestedConfigFields.

        Args:
            ctx: Resolution context with project_root and config layers.

        Returns:
            Tuple of (nested_instance, source). Source is DERIVED if any
            value came from config (since nested configs aggregate from
            multiple sources), otherwise DEFAULT.
        """
        # Get section data from config layers
        section_data = self._get_section_data(ctx)

        # Resolve each field in the nested class
        resolved_values: dict[str, Any] = {}
        any_from_config = False

        for field in attrs.fields(self.nested_class):
            field: attrs.Attribute[object] = field
            maybe_config_field = field.metadata.get(ATTRSLIB_METADATA_KEY)
            if maybe_config_field is None:
                continue
            config_field: ConfigFieldABC = maybe_config_field

            # Set field_name for key derivation
            config_field.field_name = field.name

            # Handle nested NestedConfigField (for deep nesting)
            if isinstance(config_field, NestedConfigField):
                # Pass our section_path as the parent for the nested field
                config_field._parent_section_path = self.get_section_path()
                # Recursively resolve the nested config
                value, nested_source = config_field.resolve(ctx)
                # If nested config got any value from config (not just defaults)
                if nested_source is not None and nested_source != ConfigSource.DEFAULT:
                    any_from_config = True
                resolved_values[field.name] = value
                continue

            # Look up value in section data for regular fields
            key = config_field.config_file_key
            raw_value = section_data.get(key)

            if raw_value is not None:
                # Normalize and use value from config
                value = config_field.normalize(raw_value)
                any_from_config = True
            else:
                # Use default
                value = config_field.get_default()

            resolved_values[field.name] = value

        # Create nested instance
        nested_instance = self.nested_class(**resolved_values)

        # Source is DERIVED if any value came from config (nested configs aggregate
        # values from multiple sources, so we can't claim a single specific source),
        # else DEFAULT
        source = ConfigSource.DERIVED if any_from_config else ConfigSource.DEFAULT
        return (nested_instance, source)

    def _get_section_data(self, ctx: ResolutionContext) -> dict[str, Any]:
        """Get merged section data from all config layers.

        Navigates nested TOML tables for dotted section paths.
        For section_path "hetzner.eu", navigates to data["hetzner"]["eu"].
        Layer priority: cli > env > local > project > core

        Environment variables use the format DJB_<PATH>_<FIELD> with underscores,
        e.g., DJB_HETZNER_EU_SERVER_TYPE for config.hetzner.eu.server_type.

        Args:
            ctx: Resolution context with config layers.

        Returns:
            Merged section data dict.
        """
        section_path = self.get_section_path()
        merged: dict[str, Any] = {}

        # Iterate in priority order (lowest first, highest overwrites)
        # The configs in ctx already have mode sections merged per-layer
        # We just need to navigate to the section in each layer
        for layer_name in ["core", "project", "local"]:
            layer = ctx.configs._layers.get(layer_name, {})
            if not isinstance(layer, dict):
                continue

            section_data = navigate_config_path(layer, section_path) or {}
            if section_data:
                merged.update(section_data)

        # Environment variables: look for DJB_<PATH>_<FIELD> pattern
        # e.g., DJB_HETZNER_EU_SERVER_TYPE for config.hetzner.eu.server_type
        # The section path parts are joined with underscores
        env_layer = ctx.configs._layers.get("env", {})
        env_prefix = f"DJB_{section_path.upper().replace('.', '_')}_"
        for env_key, value in env_layer.items():
            if env_key.startswith(env_prefix) and value != "":
                # Extract field name: DJB_HETZNER_EU_SERVER_TYPE -> server_type
                field_name = env_key[len(env_prefix) :].lower()
                merged[field_name] = value

        # CLI overrides (if any, would be in ctx.configs._layers["cli"])
        cli_layer = ctx.configs._layers.get("cli", {})
        if isinstance(cli_layer, dict):
            cli_section = navigate_config_path(cli_layer, section_path) or {}
            if cli_section:
                merged.update(cli_section)

        return merged
