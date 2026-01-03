"""
djb config CLI - Manage djb configuration.

Provides a discoverable, documented interface for viewing and modifying
djb settings. Each config option is a subcommand with its own documentation.
"""

from __future__ import annotations

import json
from typing import Any

import click

from djb.cli.context import CliConfigContext, CliContext, djb_pass_context
from djb.config import (
    ConfigFileType,
    ConfigValidationError,
    DjbConfig,
    WriteTargetError,
    delete_config_value_for_mode,
    get_field_descriptor,
    navigate_config_path,
    resolve_write_target,
    save_config_value_for_mode,
)
from djb.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Provenance helpers
# =============================================================================


def _resolve_write_target_cli(
    project_root: Any,
    field_path: str,
    mode: str,
) -> ConfigFileType:
    """Resolve write target, converting WriteTargetError to ClickException.

    Thin wrapper around config module's resolve_write_target that converts
    the WriteTargetError exception to a CLI-friendly ClickException.

    Args:
        project_root: Path to project root.
        field_path: Field path - either "field_name" or "section.field_name"
        mode: Current mode string.

    Returns:
        The ConfigFileType to write to.

    Raises:
        click.ClickException: If field is from core.toml and no override exists.
    """
    try:
        return resolve_write_target(project_root, field_path, mode)
    except WriteTargetError as e:
        raise click.ClickException(f"{e}\nExample: djb config --project {e.field_path} <value>")


def _format_json_with_provenance(config: DjbConfig) -> str:
    """Format config as JSON with aligned provenance comments.

    Produces output like:
        {
          "project_dir": "/path/to/project",  // project_config
          "mode": "development",              // local_config
          "name": null                        // (not set)
        }
    """
    config_dict = config.to_dict()

    # Build lines with values and provenance
    lines: list[tuple[str, str, str]] = []  # (key, json_value, provenance)
    for key, value in config_dict.items():
        json_value = json.dumps(value)
        source = config.get_source(key)
        if source is not None:
            provenance = source.value
        else:
            provenance = "(not set)"
        lines.append((key, json_value, provenance))

    # Calculate alignment: find max length of "key": value portion
    key_value_parts = [f'  "{key}": {json_value}' for key, json_value, _ in lines]
    max_len = max(len(part) for part in key_value_parts)

    # Build output with aligned comments
    output_lines = ["{"]
    for i, ((key, json_value, provenance), kv_part) in enumerate(zip(lines, key_value_parts)):
        # Add comma for all but last line (extra space when no comma to keep alignment)
        comma = "," if i < len(lines) - 1 else " "
        # Pad to align comments
        padding = " " * (max_len - len(kv_part))
        output_lines.append(f"{kv_part}{comma}{padding}  // {provenance}")
    output_lines.append("}")

    return "\n".join(output_lines)


def _config_get_set_delete(
    config_ctx: CliConfigContext,
    field_name: str,
    value: Any | None,
    delete: bool,
    *,
    section_path: str | None = None,
) -> None:
    """Handle get/set/delete for a config field.

    Unified handler for both flat fields (e.g., seed_command) and nested fields
    (e.g., hetzner.default_server_type). Uses provenance-based write logic with
    --project/--local flag support.

    Supports arbitrary nesting depth via section_path (e.g., "hetzner.eu").

    Args:
        config_ctx: CLI config context with target file flags.
        field_name: Name of the field (for nested: the inner field name).
        value: New value to set, or None to show current.
        delete: If True, remove the field from config.
        section_path: For nested fields, the dotted section path (e.g., "hetzner.eu").
    """
    config = config_ctx.config
    project_root = config.project_dir
    mode = str(config.mode)
    target_file = config_ctx.target_file  # From --project/--local flags

    # Get current value and display key
    target_config = navigate_config_path(config, section_path)
    if target_config is None:
        raise click.ClickException(f"Unknown config section: {section_path}")
    current_value = getattr(target_config, field_name, None)
    display_key = f"{section_path}.{field_name}" if section_path else field_name

    # Show current value (GET operation)
    if value is None and not delete:
        if current_value is not None:
            logger.info(f"{display_key}: {current_value}")
        else:
            logger.info(f"{display_key}: (not set)")
        return

    # Determine target file for write/delete
    if target_file is None:
        # display_key is the field_path for the config module's resolve_write_target
        target_file = _resolve_write_target_cli(project_root, display_key, mode)

    # Format section info for logging
    section_info = f" in [{mode}]" if mode != "production" else ""

    if delete:
        # Delete from appropriate file and section
        delete_config_value_for_mode(
            target_file, project_root, field_name, mode, section_path=section_path
        )
        logger.done(f"{display_key} removed from {target_file}.toml{section_info}")
    else:
        # Normalize and validate using field metadata
        try:
            field_meta = get_field_descriptor(display_key)
            normalized_value = field_meta.normalize(value)
            field_meta.validate(normalized_value)
        except ConfigValidationError as e:
            raise click.ClickException(str(e))

        # Set new value
        save_config_value_for_mode(
            target_file, project_root, field_name, normalized_value, mode, section_path=section_path
        )
        logger.done(f"{display_key} set to: {normalized_value} in {target_file}.toml{section_info}")


@click.group("config", invoke_without_command=True)
@click.option(
    "--show",
    "show_config",
    is_flag=True,
    help="Print the merged configuration as JSON.",
)
@click.option(
    "--with-provenance",
    "with_provenance",
    is_flag=True,
    help="Include provenance comments showing where each value came from.",
)
@click.option(
    "--project",
    "target_project",
    is_flag=True,
    help="Write to project.toml (overrides provenance-based target).",
)
@click.option(
    "--local",
    "target_local",
    is_flag=True,
    help="Write to local.toml (overrides provenance-based target).",
)
@djb_pass_context
@click.pass_context
def config_group(
    ctx: click.Context,
    cli_ctx: CliContext,
    show_config: bool,
    with_provenance: bool,
    target_project: bool,
    target_local: bool,
) -> None:
    """Manage djb configuration.

    View and modify djb settings. Each subcommand manages a specific
    configuration option with its own documentation.

    Environment variables (DJB_*) are documented in each subcommand's help.

    \b
    Write target flags (--project, --local):
      By default, writes go to the file where the value currently resides.
      For core.toml defaults being overridden for the first time, use
      --project or --local to specify where to write.

    \b
    Examples:
      djb config --show                           # Show all config as JSON
      djb config --show --with-provenance         # Show config with sources
      djb config seed_command                     # Show current value
      djb config seed_command myapp.cli:seed      # Set seed command
      djb config hetzner.default_server_type cx32 --project  # Override core default
    """
    # Set up CliConfigContext for subcommands
    config_ctx = CliConfigContext()
    config_ctx.__dict__.update(cli_ctx.__dict__)
    config_ctx.target_project = target_project
    config_ctx.target_local = target_local
    ctx.obj = config_ctx

    if show_config or with_provenance:
        if with_provenance:
            logger.info(_format_json_with_provenance(ctx.obj.config))
        else:
            logger.info(ctx.obj.config.to_json())
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        # No subcommand and no --list, show help
        logger.info(ctx.get_help())


@config_group.command("seed_command")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the seed_command setting.",
)
@djb_pass_context(CliConfigContext)
def config_seed_command(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the host project's seed command.

    The seed command is a Click command from your project that djb will:

    \b
    * Register as 'djb seed' for manual execution
    * Run automatically during 'djb init' after migrations

    The value should be a module:attribute path to a Click command.
    Stored in .djb/project.yaml (shared, committed).

    Can also be set via the DJB_SEED_COMMAND environment variable.

    \b
    Examples:
      djb config seed_command                           # Show current
      djb config seed_command myapp.cli.seed:seed       # Set command
      djb config seed_command --delete                  # Remove setting

    \b
    Your seed command should:
      * Be a Click command (decorated with @click.command())
      * Handle Django setup internally (call django.setup())
      * Be idempotent (safe to run multiple times)
    """
    _config_get_set_delete(config_ctx, "seed_command", value, delete)


@config_group.command("project_name")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the project_name setting.",
)
@djb_pass_context(CliConfigContext)
def config_project_name(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the project name.

    The project name is used for deployment identifiers, Heroku app names,
    and Kubernetes labels. Must be a valid DNS label (lowercase alphanumeric
    with hyphens, max 63 chars, starts/ends with alphanumeric).

    If not set explicitly, defaults to the project name from pyproject.toml.

    Can also be set via the DJB_PROJECT_NAME environment variable.

    \b
    Examples:
      djb config project_name                  # Show current
      djb config project_name my-app           # Set name
      djb config project_name --delete         # Remove (use pyproject.toml)
    """
    _config_get_set_delete(config_ctx, "project_name", value, delete)


@config_group.command("name")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the name setting.",
)
@djb_pass_context(CliConfigContext)
def config_name(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the user name.

    The name is used for git commits and secrets management (GPG key
    generation). Stored in .djb/local.yaml (gitignored, per-user).

    Can also be set via the DJB_NAME environment variable.

    \b
    Examples:
      djb config name                          # Show current
      djb config name "Jane Doe"               # Set name
      djb config name --delete                 # Remove setting
    """
    _config_get_set_delete(config_ctx, "name", value, delete)


@config_group.command("email")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the email setting.",
)
@djb_pass_context(CliConfigContext)
def config_email(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the user email.

    The email is used for git commits and secrets management (GPG key
    generation). Stored in .djb/local.yaml (gitignored, per-user).

    Can also be set via the DJB_EMAIL environment variable.

    \b
    Examples:
      djb config email                         # Show current
      djb config email jane@example.com        # Set email
      djb config email --delete                # Remove setting
    """
    _config_get_set_delete(config_ctx, "email", value, delete)


@config_group.command("encrypt_development_secrets")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the setting (use default: true).",
)
@djb_pass_context(CliConfigContext)
def config_encrypt_development_secrets(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure encryption for development secrets.

    When enabled (default), development secrets are encrypted with SOPS/age.
    When disabled, secrets are stored as plaintext YAML, eliminating the need
    for age/GPG keys for local development.

    Stored in .djb/project.yaml (shared, committed).
    Can also be set via the DJB_ENCRYPT_DEVELOPMENT_SECRETS environment variable.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config encrypt_development_secrets           # Show current
      djb config encrypt_development_secrets false     # Disable encryption
      djb config encrypt_development_secrets true      # Enable encryption
      djb config encrypt_development_secrets --delete  # Use default (true)
    """
    _config_get_set_delete(config_ctx, "encrypt_development_secrets", value, delete)


@config_group.command("encrypt_staging_secrets")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the setting (use default: true).",
)
@djb_pass_context(CliConfigContext)
def config_encrypt_staging_secrets(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure encryption for staging secrets.

    When enabled (default), staging secrets are encrypted with SOPS/age.
    When disabled, secrets are stored as plaintext YAML.

    Stored in .djb/project.yaml (shared, committed).
    Can also be set via the DJB_ENCRYPT_STAGING_SECRETS environment variable.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config encrypt_staging_secrets           # Show current
      djb config encrypt_staging_secrets false     # Disable encryption
      djb config encrypt_staging_secrets true      # Enable encryption
      djb config encrypt_staging_secrets --delete  # Use default (true)
    """
    _config_get_set_delete(config_ctx, "encrypt_staging_secrets", value, delete)


@config_group.command("encrypt_production_secrets")
@click.argument("value", required=False)
@click.option(
    "--delete",
    is_flag=True,
    help="Remove the setting (use default: true).",
)
@djb_pass_context(CliConfigContext)
def config_encrypt_production_secrets(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure encryption for production secrets.

    When enabled (default), production secrets are encrypted with SOPS/age.
    When disabled, secrets are stored as plaintext YAML.

    WARNING: Disabling encryption for production secrets is NOT recommended
    as it exposes sensitive credentials in plaintext.

    Stored in .djb/project.yaml (shared, committed).
    Can also be set via the DJB_ENCRYPT_PRODUCTION_SECRETS environment variable.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config encrypt_production_secrets           # Show current
      djb config encrypt_production_secrets false     # Disable (not recommended)
      djb config encrypt_production_secrets true      # Enable encryption
      djb config encrypt_production_secrets --delete  # Use default (true)
    """
    _config_get_set_delete(config_ctx, "encrypt_production_secrets", value, delete)


# =============================================================================
# Nested config: hetzner.*
# =============================================================================


@config_group.command("hetzner.default_server_type")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_server_type(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner server type.

    Used when creating new servers with `djb deploy k8s materialize`.
    Can be overridden per-mode in [development.hetzner] or [staging.hetzner].

    Common server types: cx11, cx21, cx22, cx31, cx32, cx41, cx42, cx51, cx52

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_server_type                      # Show current
      djb config hetzner.default_server_type cx32 --project       # Override in project.toml
      djb config hetzner.default_server_type --delete             # Remove override
    """
    _config_get_set_delete(config_ctx, "default_server_type", value, delete, section_path="hetzner")


@config_group.command("hetzner.default_location")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_location(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner datacenter location.

    Used when creating new servers with `djb deploy k8s materialize`.

    Locations: nbg1 (Nuremberg), fsn1 (Falkenstein), hel1 (Helsinki),
               ash (Ashburn, VA), hil (Hillsboro, OR)

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_location                     # Show current
      djb config hetzner.default_location fsn1 --project      # Override in project.toml
      djb config hetzner.default_location --delete            # Remove override
    """
    _config_get_set_delete(config_ctx, "default_location", value, delete, section_path="hetzner")


@config_group.command("hetzner.default_image")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_default_image(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the default Hetzner OS image.

    Used when creating new servers with `djb deploy k8s materialize`.

    Common images: ubuntu-24.04, ubuntu-22.04, debian-12, debian-11,
                   fedora-40, rocky-9, alma-9

    Default is defined in core.toml. Use --project or --local to override.

    \b
    Examples:
      djb config hetzner.default_image                            # Show current
      djb config hetzner.default_image ubuntu-22.04 --project     # Override in project.toml
      djb config hetzner.default_image --delete                   # Remove override
    """
    _config_get_set_delete(config_ctx, "default_image", value, delete, section_path="hetzner")


# =============================================================================
# Nested config: hetzner.* (instance fields - set by materialize)
# =============================================================================


@config_group.command("hetzner.server_name")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_server_name(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the Hetzner server name.

    Set by `djb deploy k8s materialize`. Used to identify the provisioned server.
    Stored in .djb/project.toml under [hetzner] or [mode.hetzner].

    \b
    Examples:
      djb config hetzner.server_name                      # Show current
      djb config hetzner.server_name myproject-staging    # Set server name
      djb config hetzner.server_name --delete             # Remove setting
    """
    _config_get_set_delete(config_ctx, "server_name", value, delete, section_path="hetzner")


@config_group.command("hetzner.server_ip")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_server_ip(config_ctx: CliConfigContext, value: str | None, delete: bool) -> None:
    """Configure the Hetzner server IP address.

    Set by `djb deploy k8s materialize`. Used for SSH connections and deployments.
    Stored in .djb/project.toml under [hetzner] or [mode.hetzner].

    \b
    Examples:
      djb config hetzner.server_ip                    # Show current
      djb config hetzner.server_ip 116.203.x.x        # Set server IP
      djb config hetzner.server_ip --delete           # Remove setting
    """
    _config_get_set_delete(config_ctx, "server_ip", value, delete, section_path="hetzner")


@config_group.command("hetzner.ssh_key_name")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting.")
@djb_pass_context(CliConfigContext)
def config_hetzner_ssh_key_name(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure the Hetzner SSH key name.

    Set by `djb deploy k8s materialize`. The SSH key name registered in Hetzner Cloud.
    Stored in .djb/project.toml under [hetzner] or [mode.hetzner].

    \b
    Examples:
      djb config hetzner.ssh_key_name                 # Show current
      djb config hetzner.ssh_key_name my-key          # Set SSH key name
      djb config hetzner.ssh_key_name --delete        # Remove setting
    """
    _config_get_set_delete(config_ctx, "ssh_key_name", value, delete, section_path="hetzner")


# =============================================================================
# Nested config: k8s.backend.*
# =============================================================================


@config_group.command("k8s.backend.managed_dockerfile")
@click.argument("value", required=False)
@click.option("--delete", is_flag=True, help="Remove the setting (use default: true).")
@djb_pass_context(CliConfigContext)
def config_k8s_backend_managed_dockerfile(
    config_ctx: CliConfigContext, value: str | None, delete: bool
) -> None:
    """Configure whether djb manages the Dockerfile template.

    When enabled (default), djb will automatically create and update the
    Dockerfile template at deployment/k8s/backend/Dockerfile.j2 during deployment.
    When disabled, djb will not create or overwrite existing Dockerfiles,
    allowing you to maintain full control over the Dockerfile.

    Use this setting if you need custom build steps or dependencies that
    differ from the djb default Django deployment template.

    Stored in .djb/project.toml under [k8s.backend].
    Can also be set via the DJB_K8S_BACKEND_MANAGED_DOCKERFILE env var.

    Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).

    \b
    Examples:
      djb config k8s.backend.managed_dockerfile           # Show current
      djb config k8s.backend.managed_dockerfile false     # Disable auto-management
      djb config k8s.backend.managed_dockerfile true      # Enable (default)
      djb config k8s.backend.managed_dockerfile --delete  # Use default (true)
    """
    _config_get_set_delete(
        config_ctx, "managed_dockerfile", value, delete, section_path="k8s.backend"
    )
