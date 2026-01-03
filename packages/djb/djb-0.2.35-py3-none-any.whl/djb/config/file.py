"""
Config file operations - Loading and saving TOML config files.

This module provides utilities for reading and writing the .djb/ config files:
- .djb/local.toml: User-specific settings (gitignored)
- .djb/project.toml: Project settings (committed)

Each config file can have mode-based sections:
- Root values are production defaults
- [development] section overrides for development mode
- [staging] section overrides for staging mode
"""

from __future__ import annotations

import tomllib
import warnings
from pathlib import Path
from typing import Any, Literal, overload

import tomli_w

# Type alias for config file types
ConfigFileType = Literal["local", "project", "core"]

# Config type constants
LOCAL: ConfigFileType = "local"
PROJECT: ConfigFileType = "project"
CORE: ConfigFileType = "core"

# Canonical layer order for config resolution (highest to lowest priority)
# cli and env are handled separately; these are the file-based layers
CONFIG_FILE_LAYERS: tuple[ConfigFileType, ...] = (LOCAL, PROJECT, CORE)

# Config file names (internal)
_CONFIG_FILES = {
    LOCAL: "local.toml",
    PROJECT: "project.toml",
    CORE: "core.toml",
}

# Reserved section names for mode-based overrides
# These are excluded from "root" values and handled separately
MODE_SECTIONS: frozenset[str] = frozenset({"development", "staging"})


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dicts, with override taking precedence.

    For nested dicts, recursively merges rather than replacing.
    For non-dict values, override replaces base.

    Args:
        base: Base dict to merge into.
        override: Dict with values that take precedence.

    Returns:
        New merged dict (does not modify inputs).

    Example:
        >>> base = {"hetzner": {"server_type": "cx23", "location": "nbg1"}}
        >>> override = {"hetzner": {"server_type": "cx11"}}
        >>> deep_merge(base, override)
        {"hetzner": {"server_type": "cx11", "location": "nbg1"}}
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = deep_merge(result[key], value)
        else:
            # Override replaces base
            result[key] = value
    return result


def get_config_dir(project_root: Path) -> Path:
    """Get the djb configuration directory (.djb/ in project root).

    Args:
        project_root: Project root path.

    Returns:
        Path to .djb/ directory in the project.
    """
    return project_root / ".djb"


def get_config_path(config_type: ConfigFileType, project_root: Path) -> Path:
    """Get path to a config file by type.

    Args:
        config_type: Config type (LOCAL or PROJECT).
        project_root: Project root path.

    Returns:
        Path to the config file.
    """
    if config_type not in _CONFIG_FILES:
        raise ValueError(f"Unknown config type: {config_type}")
    return get_config_dir(project_root) / _CONFIG_FILES[config_type]


def get_core_config_path() -> Path:
    """Get path to djb's bundled core.toml config.

    The core config is shipped with the djb package and provides default values.

    Returns:
        Path to the core.toml file in the djb package.
    """
    return Path(__file__).parent / "core.toml"


def _load_toml_mapping(path: Path) -> dict[str, Any]:
    """Load a TOML file and return its contents as a dict."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in {path}: {exc}") from exc

    return data


def _split_by_mode(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Split TOML data into root values and mode sections.

    Args:
        data: Raw TOML data dict.

    Returns:
        Tuple of (root_values, mode_sections) where:
        - root_values: All keys not in MODE_SECTIONS
        - mode_sections: Dict mapping mode names to their override dicts
    """
    root = {k: v for k, v in data.items() if k not in MODE_SECTIONS}
    sections = {k: v for k, v in data.items() if k in MODE_SECTIONS and isinstance(v, dict)}
    return root, sections


def load_config_with_sections(
    config_type: ConfigFileType,
    project_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Load a config file, separating root values from mode sections.

    Args:
        config_type: Config type (LOCAL, PROJECT, or CORE).
        project_root: Project root path. Required for LOCAL and PROJECT,
            ignored for CORE (which is bundled with djb).

    Returns:
        Tuple of (root_values, mode_sections) where:
        - root_values: Production defaults (keys not in MODE_SECTIONS)
        - mode_sections: Dict like {"development": {...}, "staging": {...}}
    """
    if config_type == CORE:
        path = get_core_config_path()
    else:
        if project_root is None:
            raise ValueError(f"project_root required for {config_type} config")
        path = get_config_path(config_type, project_root)

    if not path.exists():
        return {}, {}

    data = _load_toml_mapping(path)
    return _split_by_mode(data)


def load_config(
    config_type: ConfigFileType,
    project_root: Path | None = None,
    *,
    known_keys: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Load a configuration file by type (root values only).

    This loads only the root values, ignoring mode sections.
    For mode-aware loading, use load_config_with_sections().

    Args:
        config_type: Config type (LOCAL, PROJECT, or CORE).
        project_root: Project root path. Required for LOCAL and PROJECT,
            ignored for CORE (which is bundled with djb).
        known_keys: If provided, warn about unrecognized config keys (helps catch typos).

    Returns:
        Configuration dict (root values only), or empty dict if file doesn't exist.
    """
    root, _ = load_config_with_sections(config_type, project_root)

    # Warn about unknown keys to help catch typos (skip for CORE)
    if config_type != CORE and known_keys is not None and root:
        unknown_keys = set(root.keys()) - known_keys
        if unknown_keys:
            file_name = _CONFIG_FILES[config_type]
            warnings.warn(
                f"Unknown config keys in .djb/{file_name}: {sorted(unknown_keys)}. "
                f"Known keys: {sorted(known_keys)}",
                stacklevel=2,
            )

    return root


def save_config(config_type: ConfigFileType, data: dict[str, Any], project_root: Path) -> None:
    """Save a configuration file by type.

    Args:
        config_type: Config type (LOCAL or PROJECT).
        data: Configuration dict to save.
        project_root: Project root path.
    """
    path = get_config_path(config_type, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


@overload
def navigate_config_path(
    data: dict[str, Any],
    path: str | list[str] | None,
    *,
    ensure: Literal[True],
) -> dict[str, Any]: ...


@overload
def navigate_config_path(
    data: dict[str, Any],
    path: str | list[str] | None,
    *,
    ensure: Literal[False] = ...,
) -> dict[str, Any] | None: ...


@overload
def navigate_config_path(
    data: Any,
    path: str | list[str] | None,
) -> Any: ...


def navigate_config_path(
    data: Any,
    path: str | list[str] | None,
    *,
    ensure: bool = False,
) -> Any:
    """Navigate to a nested path in a dict or object.

    Works with both dicts (using key access) and objects (using getattr).

    Args:
        data: Root dict or object to navigate from.
        path: Dotted string ("hetzner.eu"), list of parts, or None.
        ensure: If True and data is a dict, create missing dicts.
            Ignored for non-dict objects.

    Returns:
        The nested value at path, or None if not found (when ensure=False).
    """
    if path is None:
        return data

    parts = path.split(".") if isinstance(path, str) else path
    current = data

    for part in parts:
        if isinstance(current, dict):
            # Dict navigation
            if part not in current or not isinstance(current[part], dict):
                if ensure:
                    current[part] = {}
                else:
                    return None
            current = current[part]
        else:
            # Object navigation via getattr
            current = getattr(current, part, None)
            if current is None:
                return None

    return current


def _build_full_path(mode: str | None, section_path: str | None) -> str | None:
    """Build full navigation path from mode and section.

    Args:
        mode: Mode string ("development", "staging", "production", or None).
        section_path: Dotted section path (e.g., "hetzner.eu"), or None.

    Returns:
        Combined path for navigation, or None for root.
    """
    if mode and mode != "production":
        if section_path:
            return f"{mode}.{section_path}"
        return mode
    return section_path


def save_config_value_for_mode(
    config_type: ConfigFileType,
    project_root: Path,
    key: str,
    value: Any,
    mode: str | None = None,
    *,
    section_path: str | None = None,
) -> None:
    """Save a config value to the appropriate section for a mode.

    For flat fields (section_path=None):
        - Production: writes to root
        - Other modes: writes to [mode]

    For nested fields (section_path provided, e.g., "hetzner" or "hetzner.eu"):
        - Production: writes to [section.path] (e.g., [hetzner.eu])
        - Other modes: writes to [mode.section.path] (e.g., [development.hetzner.eu])

    Args:
        config_type: Config type (LOCAL or PROJECT).
        project_root: Project root path.
        key: Configuration key to set.
        value: Value to set.
        mode: Mode string ("development", "staging", "production", or None).
            If None or "production", writes to root/[section_path].
        section_path: For nested fields, the dotted section path (e.g., "hetzner.eu").
    """
    path = get_config_path(config_type, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing file content (preserving all sections)
    if path.exists():
        data = _load_toml_mapping(path)
    else:
        data = {}

    target = navigate_config_path(data, _build_full_path(mode, section_path), ensure=True)
    target[key] = value

    with open(path, "wb") as f:
        tomli_w.dump(data, f)


def _delete_nested_key(data: dict[str, Any], path_parts: list[str], key: str) -> None:
    """Delete a key from a nested dict, cleaning up empty parent dicts.

    Args:
        data: Root dict.
        path_parts: List of keys to navigate to the parent.
        key: Key to delete from the innermost dict.
    """
    if not path_parts:
        data.pop(key, None)
        return

    # Build path to parent dicts for cleanup
    parents: list[tuple[dict[str, Any], str]] = []
    current = data
    for part in path_parts:
        if part not in current or not isinstance(current[part], dict):
            return  # Path doesn't exist
        parents.append((current, part))
        current = current[part]

    # Delete the key
    current.pop(key, None)

    # Clean up empty parent dicts (reverse order)
    for parent, part in reversed(parents):
        if not parent[part]:
            del parent[part]
        else:
            break  # Stop if parent is not empty


def delete_config_value_for_mode(
    config_type: ConfigFileType,
    project_root: Path,
    key: str,
    mode: str | None = None,
    *,
    section_path: str | None = None,
) -> None:
    """Delete a config value from the appropriate section for a mode.

    For flat fields (section_path=None):
        - Production: deletes from root
        - Other modes: deletes from [mode]

    For nested fields (section_path provided, e.g., "hetzner" or "hetzner.eu"):
        - Production: deletes from [section.path] (e.g., [hetzner.eu])
        - Other modes: deletes from [mode.section.path] (e.g., [development.hetzner.eu])

    Args:
        config_type: Config type (LOCAL or PROJECT).
        project_root: Project root path.
        key: Configuration key to delete.
        mode: Mode string ("development", "staging", "production", or None).
            If None or "production", deletes from root/[section_path].
        section_path: For nested fields, the dotted section path (e.g., "hetzner.eu").
    """
    path = get_config_path(config_type, project_root)
    if not path.exists():
        return

    data = _load_toml_mapping(path)

    full_path = _build_full_path(mode, section_path)
    path_parts = full_path.split(".") if full_path else []
    _delete_nested_key(data, path_parts, key)

    with open(path, "wb") as f:
        tomli_w.dump(data, f)


# =============================================================================
# Field provenance lookup
# =============================================================================


def get_field_provenance(
    project_root: Path,
    field_path: str,
    mode: str | None = None,
) -> ConfigFileType | None:
    """Determine which config file contains a field value.

    Checks local -> project -> core order, returns the first file that has the value.
    Supports arbitrary nesting depth in field_path.

    Args:
        project_root: Path to project root.
        field_path: Field path - "field_name" or "section.path.field_name"
        mode: Current mode string (e.g., "development", "staging", "production").

    Returns:
        The ConfigFileType where the value currently resides, or None if not found.
    """
    # Parse field path - all but last part is the section path
    parts = field_path.split(".")
    if len(parts) == 1:
        section_path, field_name = None, parts[0]
    else:
        section_path = ".".join(parts[:-1])
        field_name = parts[-1]

    for config_type in (LOCAL, PROJECT, CORE):
        if config_type == CORE:
            path = get_core_config_path()
        else:
            path = get_config_path(config_type, project_root)

        if not path.exists():
            continue

        data = _load_toml_mapping(path)

        # Check mode-specific first (e.g., [development] or [development.hetzner])
        if mode and mode != "production":
            target = navigate_config_path(data, _build_full_path(mode, section_path))
            if target and field_name in target:
                return config_type

        # Then check root/production (e.g., root or [hetzner])
        target = navigate_config_path(data, section_path)
        if target and field_name in target:
            return config_type

    return None
