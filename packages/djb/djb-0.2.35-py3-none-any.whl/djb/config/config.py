"""
DjbConfig: configuration class with djb_get_config() factory function.

This module provides:
- DjbConfig: Immutable configuration dataclass with field definitions and persistence
- djb_get_config(): Factory function that creates DjbConfig instances with caching

Configuration is loaded with the following priority (highest to lowest):
1. Explicit kwargs passed to djb_get_config()
2. Environment variables (DJB_ prefix)
3. Local config (.djb/local.toml) - user-specific, gitignored
4. Project config (.djb/project.toml) - shared, committed
5. Core config (djb/config/core.toml) - djb defaults
6. Field default values

Each config file can have mode-based sections ([development], [staging]).
For non-production modes, the mode section is merged onto root values within each file.
File priority takes precedence over section priority.

The config_class option allows host projects to extend DjbConfig with custom fields.

Usage:
    # CLI: get config with overrides, attach to context
    cfg = djb_get_config(project_dir=project_dir, mode=Mode.PRODUCTION)
    ctx.obj.config = cfg

    # Tests: bypass cache for isolation
    cfg = djb_get_config(project_dir=tmp_path, _bypass_cache=True)

    # Django settings.py: get cached config
    djb_config = djb_get_config()
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any

import attrs

from djb.config.resolution import (
    ProvenanceChainMap,
    ResolutionContext,
)
from djb.config.fields import (
    DEFAULT_LOG_LEVEL,
    BoolField,
    EmailField,
    EnumField,
    LogLevelField,
    NameField,
    ProjectDirField,
    ProjectNameField,
    SeedCommandField,
    find_project_root,
)
from djb.config.fields.cloudflare import CloudflareConfig
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.heroku import HerokuConfig
from djb.config.fields.hetzner import HetznerConfig
from djb.config.fields.k8s import K8sConfig
from djb.config.fields.nested import NestedConfigField
from djb.config.field import ClassField, ConfigValidationError
from djb.config.file import (
    CONFIG_FILE_LAYERS,
    CORE,
    LOCAL,
    PROJECT,
    ConfigFileType,
    deep_merge,
    get_field_provenance,
    load_config,
    load_config_with_sections,
    save_config,
)
from djb.config.constants import ATTRSLIB_METADATA_KEY
from djb.config.resolution import ConfigSource
from djb.types import Mode, Platform


# =============================================================================
# DjbConfig class
# =============================================================================


@attrs.frozen
class DjbConfig:
    """Immutable configuration for djb CLI.

    Created via djb_get_config() which resolves values from multiple sources.

    Field resolution priority (handled by djb_get_config):
    1. Explicit kwargs passed to djb_get_config()
    2. Environment variables (DJB_ prefix)
    3. Local config (.djb/local.toml)
    4. Project config (.djb/project.toml)
    5. Defaults (e.g. pyproject.toml for project_name)

    Provenance tracking records where each value came from, enabling:
    - Consistent save behavior (preserve original source file)
    - Init workflow (skip already-configured fields)
    - Debugging (show source in `djb config show --provenance`)
    """

    # === Mandatory fields ===
    project_dir: Path = ProjectDirField()()
    project_name: str = ProjectNameField(config_file="project")()

    # === Optional fields ===
    mode: Mode = EnumField(Mode, config_file="local", default=Mode.DEVELOPMENT)()
    platform: Platform = EnumField(Platform, config_file="project", default=Platform.HEROKU)()
    name: str | None = NameField(config_file="local", default=None)()
    email: str | None = EmailField(config_file="local", default=None)()
    seed_command: str | None = SeedCommandField(config_file="project", default=None)()
    log_level: str = LogLevelField(config_file="project", default=DEFAULT_LOG_LEVEL)()

    # === Secrets encryption settings ===
    encrypt_development_secrets: bool = BoolField(config_file="project", default=True)()
    encrypt_staging_secrets: bool = BoolField(config_file="project", default=True)()
    encrypt_production_secrets: bool = BoolField(config_file="project", default=True)()

    # === Hetzner Cloud settings ===
    # Nested config for Hetzner Cloud (reads from [hetzner] section)
    # Contains both defaults (from core.toml) and instance state (from project.toml)
    # Section name derived from field name "hetzner" -> [hetzner]
    hetzner: HetznerConfig = NestedConfigField(HetznerConfig)()

    # === Heroku deployment settings ===
    # Nested config for Heroku deployment (reads from [heroku] section)
    heroku: HerokuConfig = NestedConfigField(HerokuConfig)()

    # === Kubernetes deployment settings ===
    # Nested config for K8s deployment (reads from [k8s] section)
    k8s: K8sConfig = NestedConfigField(K8sConfig)()

    # === Cloudflare DNS settings ===
    # Nested config for Cloudflare DNS management (reads from [cloudflare] section)
    cloudflare: CloudflareConfig = NestedConfigField(CloudflareConfig)()

    # === Internal fields ===
    _provenance: dict[str, ConfigSource] = attrs.field(
        factory=dict, repr=False, alias="_provenance"
    )

    @property
    def domain_names(self) -> dict[str, DomainNameConfig]:
        """Get domain names map for the active deployment platform.

        This is the primary interface for application code that needs domain names
        without caring about the deployment platform. Returns heroku.domain_names or
        k8s.domain_names based on the current platform setting.

        Example:
            config = djb_get_config()
            for domain, domain_config in config.domain_names.items():
                print(f"Serving on {domain} (manager: {domain_config.manager})")
        """
        if self.platform == Platform.HEROKU:
            return self.heroku.domain_names
        else:  # K8S
            return self.k8s.domain_names

    @property
    def domain_names_list(self) -> list[str]:
        """Get list of domain names for the active deployment platform.

        Convenience property that returns just the domain name strings.

        Example:
            config = djb_get_config()
            for domain in config.domain_names_list:
                print(f"Serving on {domain}")
        """
        return list(self.domain_names.keys())

    @property
    def db_name(self) -> str:
        """Get database name for PostgreSQL.

        Returns k8s.db_name if configured, otherwise derives from project_name
        by replacing hyphens with underscores (PostgreSQL identifier requirement).

        Example:
            config = djb_get_config()
            # For project_name="my-app", returns "my_app"
            # Or returns k8s.db_name if explicitly configured
            print(f"Database: {config.db_name}")
        """
        if self.k8s.db_name:
            return self.k8s.db_name
        return self.project_name.replace("-", "_")

    def to_dict(self) -> dict[str, Any]:
        """Convert config to a JSON-serializable dictionary.

        Returns:
            Dictionary with all config values. Path objects are converted
            to strings, Enum values to their string values, and private
            attributes are excluded.
        """
        config_dict = attrs.asdict(self)
        # Convert Path to string
        config_dict["project_dir"] = str(config_dict["project_dir"])
        # Convert Enum values to strings
        config_dict["mode"] = config_dict["mode"].value
        config_dict["platform"] = config_dict["platform"].value
        # Remove private attributes
        config_dict.pop("_provenance", None)
        return config_dict

    def to_json(self, indent: int = 2) -> str:
        """Convert config to a JSON string.

        Args:
            indent: Number of spaces for indentation. Default is 2.

        Returns:
            JSON string representation of the config.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, project_root: Path | None = None) -> None:
        """Save config using provenance (or config_file default) for storage location.

        Only saves config files that have changes.

        Args:
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        local_config = load_config(LOCAL, project_root)
        project_config = load_config(PROJECT, project_root)
        local_changed = False
        project_changed = False

        for field in attrs.fields(type(self)):  # Use type(self) for subclass support
            config_field = field.metadata.get(ATTRSLIB_METADATA_KEY)
            if config_field is None:
                continue

            # Skip fields without a config_file (e.g., project_dir is derived)
            if config_field.config_file is None:
                continue

            field_name = field.name
            config_field.field_name = field_name
            default_file = config_field.config_file
            file_key = config_field.config_file_key  # Defaults to field_name
            value = getattr(self, field_name)
            if value is None:
                continue

            # Convert enums to strings for storage
            if isinstance(value, Enum):
                value = str(value)

            # Determine storage: provenance takes precedence over default
            source = self._provenance.get(field_name)
            target_file = (source.config_file_type if source else None) or default_file

            if target_file == LOCAL:
                local_config[file_key] = value
                local_changed = True
            elif target_file == PROJECT:
                project_config[file_key] = value
                project_changed = True

        if local_changed:
            save_config(LOCAL, local_config, project_root)
        if project_changed:
            save_config(PROJECT, project_config, project_root)

    def save_field(self, field_name: str, project_root: Path | None = None) -> None:
        """Save a single field to its configured storage location.

        Used when --mode or --platform is explicitly passed to persist it.
        The storage location (local.toml or project.toml) is determined by
        the field's config_file metadata.

        Args:
            field_name: Name of the field to save (e.g., "mode", "platform").
            project_root: Project root path. Defaults to self.project_dir.
        """
        if project_root is None:
            project_root = self.project_dir

        # Get field metadata to determine storage location
        field_meta = get_field_descriptor(field_name)
        target_file = field_meta.config_file  # "local" or "project"

        existing = load_config(target_file, project_root)
        value = getattr(self, field_name)
        existing[field_name] = str(value) if isinstance(value, Enum) else value
        save_config(target_file, existing, project_root)

    def is_explicit(self, field: str) -> bool:
        """Check if a field was explicitly configured.

        Args:
            field: Field name to check.

        Returns:
            True if the field value came from an explicit source
            (CLI, env var, or config file).
        """
        source = self._provenance.get(field)
        return source is not None and source.is_explicit()

    def is_derived(self, field: str) -> bool:
        """Check if a field was derived from secondary sources.

        Args:
            field: Field name to check.

        Returns:
            True if the field value was derived (from pyproject.toml,
            git config, or directory name).
        """
        source = self._provenance.get(field)
        return source is not None and source.is_derived()

    def is_configured(self, field: str) -> bool:
        """Check if a field has a configured value.

        Args:
            field: Field name to check.

        Returns:
            True if the field has a source in provenance tracking.
        """
        return self.get_source(field) is not None

    def get_source(self, field: str) -> ConfigSource | None:
        """Get the source of a field's value.

        Args:
            field: Field name to check.

        Returns:
            The ConfigSource for the field, or None if not tracked.
        """
        return self._provenance.get(field)


# =============================================================================
# Module-level cache
# =============================================================================

_cached_config: DjbConfig | None = None


def _clear_config_cache() -> None:
    """Clear the cached config. For test fixtures only.

    This is a private function (underscore prefix) used by pytest fixtures
    to reset state between tests. It should not be used in application code.
    """
    global _cached_config
    _cached_config = None


# =============================================================================
# Field utilities
# =============================================================================


def _get_attrs_field(cls: type, field_name: str) -> attrs.Attribute[Any] | None:
    """Get an attrs field by name.

    Args:
        cls: The attrs class to get the field from.
        field_name: Name of the field to get.

    Returns:
        The attrs.Attribute if found, None otherwise.
    """
    return getattr(attrs.fields(cls), field_name, None)


def get_field_descriptor(
    field_path: str,
    config_class: type[DjbConfig] | None = None,
) -> Any:
    """Get the field descriptor for a DjbConfig field.

    Supports flat fields and nested field paths of arbitrary depth:
    - "project_name" - flat field
    - "hetzner.default_server_type" - one level nesting
    - "hetzner.eu.server_type" - two levels nesting

    Args:
        field_path: Field path - "field_name" or "section.path.field_name"
        config_class: Config class to inspect (default: DjbConfig)

    Returns:
        The ConfigFieldABC instance for the field.

    Raises:
        ValueError: If the field doesn't exist or has no metadata.
    """
    cls = config_class or DjbConfig

    # Parse field path into parts
    parts = field_path.split(".")

    # Navigate through nested classes for all but the last part
    current_class = cls
    section_parts: list[str] = []

    for part in parts[:-1]:
        section_parts.append(part)
        section_field = _get_attrs_field(current_class, part)
        if section_field is None:
            raise ValueError(f"Unknown section: {'.'.join(section_parts)}")

        section_meta = section_field.metadata.get(ATTRSLIB_METADATA_KEY)
        if section_meta is None or not hasattr(section_meta, "nested_class"):
            raise ValueError(f"{'.'.join(section_parts)} is not a nested config section")

        current_class = section_meta.nested_class

    # The last part is the field name
    field_name = parts[-1]
    target_field = _get_attrs_field(current_class, field_name)
    if target_field is None:
        raise ValueError(f"Unknown field: {field_path}")

    config_field = target_field.metadata.get(ATTRSLIB_METADATA_KEY)
    if config_field is None:
        raise ValueError(f"{field_path} is not a config field")

    # Set context on the descriptor
    config_field.field_name = field_name
    if section_parts:
        config_field.section_path = ".".join(section_parts)

    return config_field


# =============================================================================
# Write target resolution
# =============================================================================


class WriteTargetError(Exception):
    """Raised when write target cannot be determined automatically."""

    def __init__(self, field_path: str, message: str):
        self.field_path = field_path
        super().__init__(message)


def resolve_write_target(
    project_root: Path,
    field_path: str,
    mode: str | None = None,
) -> ConfigFileType:
    """Determine which file to write to based on provenance.

    Logic:
    1. If value exists in LOCAL or PROJECT, write back to that file.
    2. If field's config_file is CORE and value only exists in CORE (or nowhere),
       raise WriteTargetError - caller must specify target explicitly.
    3. Otherwise, write to the field's config_file.

    Args:
        project_root: Path to project root.
        field_path: Field path - either "field_name" or "section.field_name"
        mode: Current mode string.

    Returns:
        The ConfigFileType to write to.

    Raises:
        WriteTargetError: If field is from core.toml and no override exists.
    """
    field_meta = get_field_descriptor(field_path)
    field_config_file = field_meta.config_file or PROJECT
    provenance = get_field_provenance(project_root, field_path, mode)

    # If value already exists in project or local, write back there
    if provenance in (PROJECT, LOCAL):
        return provenance

    # If field is defined in core and only exists there (or nowhere),
    # require explicit target
    if field_config_file == CORE:
        raise WriteTargetError(
            field_path,
            f"{field_path} is defined in core.toml. Use --project or --local to override.",
        )

    # Otherwise, write to the field's default config file
    return field_config_file


def _get_known_keys(
    config_file: str, config_class: type[DjbConfig] | None = None
) -> frozenset[str]:
    """Get known config keys for a file type.

    Args:
        config_file: Either "local" or "project".
        config_class: Config class to inspect (default: DjbConfig)

    Returns:
        Frozenset of known key names for that config file.
    """
    cls = config_class or DjbConfig
    keys: set[str] = set()
    for field in attrs.fields(cls):
        config_field = field.metadata.get(ATTRSLIB_METADATA_KEY)
        if config_field is None:
            continue
        config_field.field_name = field.name
        # Local config can contain any key (local or project) since it can override
        # project settings. Project config only contains project-level keys.
        if config_file == "local" or config_field.config_file == config_file:
            keys.add(config_field.config_file_key)
    return frozenset(keys)


# =============================================================================
# Config class resolution (bootstrap)
# =============================================================================

# Module-level field definition for config_class
# Uses ClassField for validation - resolved via same machinery as all other fields
CONFIG_CLASS_FIELD = ClassField(
    config_file="project",
    default="djb.DjbConfig",
)
CONFIG_CLASS_FIELD.field_name = "config_class"  # Set for env_key derivation

# Module-level field definition for mode (bootstrap resolution)
# Resolved BEFORE mode-aware layer loading to avoid circular dependency
MODE_FIELD = EnumField(Mode, config_file="local", default=Mode.DEVELOPMENT)
MODE_FIELD.field_name = "mode"  # Set for env_key derivation


def resolve_mode(ctx: ResolutionContext) -> tuple[Mode, ConfigSource | None]:
    """Resolve the deployment mode.

    Uses standard field resolution - same as all other fields.
    Called during bootstrap phase with root-only layers.

    Args:
        ctx: Resolution context with root-only config layers.

    Returns:
        Tuple of (mode, source).
    """
    return MODE_FIELD.resolve(ctx)


def load_config_layers_root_only(project_root: Path) -> dict[str, dict[str, Any]]:
    """Load all config file layers as raw dicts (root values only, no mode sections).

    Used for bootstrap phase to resolve mode before mode-aware loading.

    Args:
        project_root: Project root path.

    Returns:
        Dict mapping layer names to config dicts with only root values.
    """
    layers: dict[str, dict[str, Any]] = {}
    for layer_type in CONFIG_FILE_LAYERS:
        if layer_type == CORE:
            root, _ = load_config_with_sections(layer_type)
        else:
            root, _ = load_config_with_sections(layer_type, project_root)
        layers[layer_type] = root
    return layers


def load_config_layers(
    project_root: Path,
    mode: Mode = Mode.PRODUCTION,
) -> dict[str, dict[str, Any]]:
    """Load all config file layers with mode-aware section merging.

    For production mode:
        Returns root values from each file.

    For development/staging mode:
        Returns root values merged with mode-specific section values.
        Mode sections override root values within each file.
        File priority (local > project > core) takes precedence over
        section priority (mode > root).

    Args:
        project_root: Project root path.
        mode: Deployment mode for section selection.

    Returns:
        Dict mapping layer names to merged config dicts, e.g.:
        {"local": {...}, "project": {...}, "core": {...}}
    """
    layers: dict[str, dict[str, Any]] = {}
    for layer_type in CONFIG_FILE_LAYERS:
        if layer_type == CORE:
            root, sections = load_config_with_sections(layer_type)
        else:
            root, sections = load_config_with_sections(layer_type, project_root)

        # For non-production modes, deep merge mode-specific section onto root
        # Deep merge ensures nested sections (e.g., [development.hetzner])
        # properly merge with root sections (e.g., [hetzner])
        if mode != Mode.PRODUCTION:
            mode_section = sections.get(mode.value, {})
            layers[layer_type] = deep_merge(root, mode_section)
        else:
            layers[layer_type] = root

    return layers


def create_resolution_context(
    project_root: Path,
    project_root_source: ConfigSource,
    overrides: dict[str, Any],
    env: Mapping[str, str] | None,
    layers: dict[str, dict[str, Any]],
) -> ResolutionContext:
    """Create ResolutionContext from loaded layers.

    Reused by both bootstrap (config_class) and full resolution.

    Args:
        project_root: Resolved project root directory.
        project_root_source: How project_root was determined.
        overrides: CLI/explicit overrides.
        env: Environment variables mapping (None uses os.environ).
        layers: Loaded config file layers from load_config_layers().

    Returns:
        ResolutionContext ready for field resolution.
    """
    configs = ProvenanceChainMap(
        cli=overrides,
        env=env,
        file_layers=layers,
    )
    return ResolutionContext(
        project_root=project_root,
        project_root_source=project_root_source,
        configs=configs,
    )


def resolve_config_class(ctx: ResolutionContext) -> tuple[type[DjbConfig], ConfigSource | None]:
    """Resolve and import the config class.

    Uses standard field resolution - same as all other fields.

    Args:
        ctx: Resolution context with all config layers.

    Returns:
        Tuple of (config_class, source).

    Raises:
        ConfigValidationError: If config_class is invalid or not a DjbConfig subclass.
    """
    class_path, source = CONFIG_CLASS_FIELD.resolve(ctx)
    config_class = CONFIG_CLASS_FIELD.import_class(class_path)

    # Validate it's a DjbConfig subclass (can't do in ClassField due to circular import)
    if not issubclass(config_class, DjbConfig):
        raise ConfigValidationError(
            f"config_class must be a DjbConfig subclass, got: {config_class}"
        )

    return config_class, source


# =============================================================================
# Config resolution
# =============================================================================


def _resolve_config(
    config_class: type[DjbConfig],
    ctx: ResolutionContext,
) -> DjbConfig:
    """Resolve all fields and create a config instance.

    Args:
        config_class: The DjbConfig class (or subclass) to instantiate.
        ctx: Pre-built resolution context with all layers.

    Returns:
        A fully resolved config instance.
    """
    resolved_values: dict[str, Any] = {}
    provenance: dict[str, ConfigSource] = {}

    for field in attrs.fields(config_class):
        config_field = field.metadata.get(ATTRSLIB_METADATA_KEY)
        if config_field is None:
            continue

        # Set field_name so env_key/file_key can auto-derive
        config_field.field_name = field.name

        # All resolution logic is inside the ConfigField class
        value, source = config_field.resolve(ctx)

        # Validate the resolved value
        config_field.validate(value)

        resolved_values[field.name] = value
        if source:
            provenance[field.name] = source

    return config_class(**resolved_values, _provenance=provenance)


# =============================================================================
# Public API
# =============================================================================


def _create_config(
    overrides: dict[str, Any],
    env: Mapping[str, str] | None,
) -> DjbConfig:
    """Create a fresh config instance using two-phase resolution.

    This is the internal implementation that:
    1. Finds project root
    2. Bootstrap phase: load root-only layers and resolve mode
    3. Full phase: load mode-aware layers
    4. Resolves config_class to determine which class to use
    5. Resolves all fields and creates the config instance

    Args:
        overrides: CLI/explicit overrides.
        env: Environment variables mapping.

    Returns:
        A fully resolved config instance.
    """
    # 1. Find project root (existing bootstrap)
    cli_project_dir = Path(overrides["project_dir"]) if "project_dir" in overrides else None
    resolved_root, root_source = find_project_root(
        project_root=cli_project_dir,
        fallback_to_cwd=True,
    )

    # 2. Bootstrap phase: load root-only layers to resolve mode
    bootstrap_layers = load_config_layers_root_only(resolved_root)
    bootstrap_ctx = create_resolution_context(
        project_root=resolved_root,
        project_root_source=root_source,
        overrides=overrides,
        env=env,
        layers=bootstrap_layers,
    )

    # 3. Resolve mode using bootstrap context
    mode, _ = resolve_mode(bootstrap_ctx)

    # 4. Full phase: load layers with mode-aware section merging
    layers = load_config_layers(resolved_root, mode)
    ctx = create_resolution_context(
        project_root=resolved_root,
        project_root_source=root_source,
        overrides=overrides,
        env=env,
        layers=layers,
    )

    # 5. Resolve config_class using SAME resolve() machinery
    config_cls, _ = resolve_config_class(ctx)

    # 6. Resolve all other fields using SAME ctx
    return _resolve_config(config_cls, ctx)


def djb_get_config(
    *,
    project_dir: Path | str | None = None,
    mode: Mode | str | None = None,
    platform: Platform | str | None = None,
    name: str | None = None,
    email: str | None = None,
    log_level: str | None = None,
    config_class: str | None = None,
    env: Mapping[str, str] | None = None,
    _bypass_cache: bool = False,
) -> DjbConfig:
    """Get the djb configuration, resolving from multiple sources.

    Resolution order (highest to lowest priority):
    1. Explicit kwargs passed to this function
    2. Environment variables (DJB_*)
    3. Local config (.djb/local.yaml)
    4. Project config (.djb/project.yaml)
    5. Core config (djb/config/core.yaml) - djb defaults
    6. Field default values

    The config_class option allows host projects to extend DjbConfig:
    - Create a subclass of DjbConfig with custom fields
    - Set config_class in project.yaml or pass via CLI/env
    - djb will use your subclass for all config operations

    Caching behavior:
    - First call with overrides creates and caches the config
    - Subsequent calls with no overrides return the cached config
    - Calling with overrides after config is cached raises RuntimeError
    - Pass _bypass_cache=True to get a fresh instance without caching

    Args:
        project_dir: Project root directory (default: auto-detect).
        mode: Deployment mode (development, staging, production).
        platform: Deployment platform (heroku, k8s).
        name: User name for commits/deployments.
        email: User email for commits/deployments.
        log_level: Logging verbosity level.
        config_class: Config class to use (default: from config or DjbConfig).
            Format: "module.path.ClassName"
        env: Environment variables mapping. If None, uses os.environ.
            Pass an empty dict {} for test isolation.
        _bypass_cache: If True, skip cache and create a fresh instance.
            Use this in tests for isolation.

    Returns:
        A DjbConfig instance (or subclass) with all fields resolved.

    Raises:
        RuntimeError: If called with overrides after config is already cached.

    Example:
        # CLI usage (first call, populates cache)
        config = djb_get_config(project_dir=Path("/my/project"), mode=Mode.PRODUCTION)

        # Django settings.py (uses cached instance from CLI)
        from djb import djb_get_config
        djb_config = djb_get_config()

        # Test usage (use Pytest djb_config fixture)
        test_foo(djb_config: DjbConfig)
    """
    global _cached_config

    # Build overrides dict, converting types as needed
    overrides: dict[str, Any] = {}

    if project_dir is not None:
        overrides["project_dir"] = (
            str(project_dir) if isinstance(project_dir, Path) else project_dir
        )

    if mode is not None:
        overrides["mode"] = Mode(mode.lower()) if isinstance(mode, str) else mode

    if platform is not None:
        overrides["platform"] = (
            Platform(platform.lower()) if isinstance(platform, str) else platform
        )

    if name is not None:
        overrides["name"] = name

    if email is not None:
        overrides["email"] = email

    if log_level is not None:
        overrides["log_level"] = log_level.lower() if isinstance(log_level, str) else log_level

    if config_class is not None:
        overrides["config_class"] = config_class

    has_overrides = bool(overrides) or env is not None

    # If bypassing cache, just resolve and return without caching
    if _bypass_cache:
        return _create_config(overrides, env=env)

    # If cache exists and we have overrides, someone is trying to use different config
    if _cached_config is not None and has_overrides:
        raise RuntimeError(
            "djb_get_config() called with overrides but config was already created "
            "(possibly with different values). Use _bypass_cache=True for test isolation."
        )

    # Return cached config if available
    if _cached_config is not None:
        return _cached_config

    # Create and cache new config
    cfg = _create_config(overrides, env=env)
    _cached_config = cfg
    return cfg
