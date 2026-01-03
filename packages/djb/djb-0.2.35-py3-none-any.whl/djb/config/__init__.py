"""
djb.config - Unified configuration system for djb CLI.

Quick start:
    from djb import djb_get_config

    config = djb_get_config()
    print(f"Mode: {config.mode}")        # development, staging, production
    print(f"Platform: {config.platform}")  # heroku
    print(f"Project: {config.project_name}")

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

Two config files are used:
- .djb/local.toml: User-specific settings (name, email, mode) - NOT committed
- .djb/project.toml: Project settings (project_name, platform) - committed

Local config can override any project setting for user experimentation.

## Public API

### Main API
- djb_get_config: Factory function to get config (cached per-process)
- DjbConfig: Immutable configuration dataclass
- ConfigSource: Enum tracking where a config value came from

### Config File Operations
- get_config_dir: Get path to .djb/ directory
- get_config_path: Get path to a specific config file
- load_config: Load a config file by type
- save_config: Save a config file by type
- save_config_value_for_mode: Save a value to mode-specific section
- delete_config_value_for_mode: Delete a value from mode-specific section
- get_field_provenance: Find which config file contains a field value
- resolve_write_target: Determine which file to write a field value to
- WriteTargetError: Exception when write target cannot be auto-determined
- LOCAL, PROJECT, CORE: Config type constants
- CONFIG_FILE_LAYERS: Canonical layer order for resolution

### Config Class Extension
- load_config_layers: Load all config layers as dicts (mode-aware)
- load_config_layers_root_only: Load config layers (root values only, for bootstrap)
- create_resolution_context: Create context for field resolution
- resolve_config_class: Resolve and import the config class
- resolve_mode: Resolve the deployment mode
- CONFIG_CLASS_FIELD: Field definition for config_class option
- MODE_FIELD: Field definition for mode option

### Field System (for extending DjbConfig)
- ConfigFieldABC: Abstract base class for config fields
- StringField, EnumField, ClassField: Common field types
- ProjectDirField, ProjectNameField, EmailField, SeedCommandField: Specialized fields
- ProvenanceChainMap: Layered config resolution with provenance tracking
- ResolutionContext: Context passed to field resolution
- ATTRSLIB_METADATA_KEY: Metadata key for storing ConfigField in attrs metadata

### Project Detection
- find_project_root: Find the project root directory
- find_pyproject_root: Find the nearest pyproject.toml

### Validation & Normalization
- ConfigValidationError: Exception for validation failures
- ConfigFileType: Type alias for config file types
- normalize_project_name: Normalize a string to DNS-safe label
- get_project_name_from_pyproject: Extract project name from pyproject.toml
- DEFAULT_PROJECT_NAME: Default project name when resolution fails
- DNS_LABEL_PATTERN: Pattern for validating DNS labels
"""

from djb.config.acquisition import (
    AcquisitionContext,
    AcquisitionResult,
    ExternalSource,
    GitConfigSource,
    acquire_all_fields,
)
from djb.config.field import (
    ClassField,
    ConfigFieldABC,
    ConfigValidationError,
    StringField,
)
from djb.config.fields import (
    CloudflareConfig,
    EnumField,
    HerokuConfig,
    HetznerConfig,
    K8sBackendConfig,
    K8sConfig,
)
from djb.config.constants import HetznerImage, HetznerLocation, HetznerServerType
from djb.config.resolution import (
    ConfigSource,
    ProvenanceChainMap,
    ResolutionContext,
)
from djb.config.config import (
    CONFIG_CLASS_FIELD,
    MODE_FIELD,
    DjbConfig,
    WriteTargetError,
    _clear_config_cache,
    create_resolution_context,
    djb_get_config,
    get_field_descriptor,
    load_config_layers,
    load_config_layers_root_only,
    resolve_config_class,
    resolve_mode,
    resolve_write_target,
)
from djb.config.fields import (
    DEFAULT_PROJECT_NAME,
    DNS_LABEL_PATTERN,
    EmailField,
    ProjectDirField,
    ProjectNameField,
    SeedCommandField,
    get_project_name_from_pyproject,
    normalize_project_name,
)
from djb.config.file import (
    CONFIG_FILE_LAYERS,
    CORE,
    LOCAL,
    PROJECT,
    ConfigFileType,
    delete_config_value_for_mode,
    get_config_dir,
    get_config_path,
    get_field_provenance,
    load_config,
    navigate_config_path,
    save_config,
    save_config_value_for_mode,
)
from djb.config.fields import find_project_root, find_pyproject_root
from djb.config.constants import ATTRSLIB_METADATA_KEY

__all__ = [
    # Main API
    "djb_get_config",
    "DjbConfig",
    "ConfigSource",
    # Test utilities
    "_clear_config_cache",
    # Nested config types
    "CloudflareConfig",
    "HerokuConfig",
    "HetznerConfig",
    "K8sBackendConfig",
    "K8sConfig",
    # Hetzner enums
    "HetznerImage",
    "HetznerLocation",
    "HetznerServerType",
    # Config file operations
    "get_config_dir",
    "get_config_path",
    "load_config",
    "save_config",
    "save_config_value_for_mode",
    "delete_config_value_for_mode",
    "get_field_provenance",
    "resolve_write_target",
    "WriteTargetError",
    "LOCAL",
    "PROJECT",
    "CORE",
    "CONFIG_FILE_LAYERS",
    "navigate_config_path",
    # Config class extension
    "load_config_layers",
    "load_config_layers_root_only",
    "create_resolution_context",
    "resolve_config_class",
    "resolve_mode",
    "CONFIG_CLASS_FIELD",
    "MODE_FIELD",
    # Field system
    "ConfigFieldABC",
    "StringField",
    "EnumField",
    "ClassField",
    "ProjectDirField",
    "ProjectNameField",
    "EmailField",
    "SeedCommandField",
    "ProvenanceChainMap",
    "ResolutionContext",
    "ATTRSLIB_METADATA_KEY",
    "get_field_descriptor",
    # Interactive acquisition (for field.acquire())
    "AcquisitionContext",
    "AcquisitionResult",
    "ExternalSource",
    "GitConfigSource",
    "acquire_all_fields",
    # Project detection
    "find_project_root",
    "find_pyproject_root",
    # Validation & normalization
    "ConfigValidationError",
    "ConfigFileType",
    "normalize_project_name",
    "get_project_name_from_pyproject",
    "DEFAULT_PROJECT_NAME",
    "DNS_LABEL_PATTERN",
]
