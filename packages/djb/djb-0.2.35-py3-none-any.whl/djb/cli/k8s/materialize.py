"""
djb deploy k8s materialize - Cloud VPS provisioning command.

Creates cloud VPS instances for Kubernetes deployments. This command handles
the physical/virtual machine creation step, storing server info in project
config for subsequent terraform and deploy commands.

Supported Providers
-------------------
- hetzner: Hetzner Cloud (requires API token in secrets)

Usage Examples
--------------
# Create Hetzner VPS for staging
djb -m staging deploy k8s materialize --provider hetzner --ssh-key-name my-key

# Force create new server (errors if already configured)
djb -m staging deploy k8s materialize --provider hetzner --create

Design Philosophy
-----------------
"Materialize" means to make physical/real - bringing a virtual machine into
existence. This is distinct from "terraform" which shapes/provisions the
machine with K8s infrastructure.

The command is idempotent: if a server is already configured and exists,
it verifies the server and returns. Use --create to force new server creation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from djb.cli.context import CliK8sContext, djb_pass_context
from djb.cli.k8s.hetzner import provision_hetzner_server
from djb.config.file import PROJECT, save_config_value_for_mode
from djb.core.logging import get_logger

if TYPE_CHECKING:
    from djb.config import DjbConfig

logger = get_logger(__name__)


def is_server_materialized(config: DjbConfig, provider: str) -> bool:
    """Check if a cloud server is configured for the current mode.

    Args:
        config: DjbConfig with current mode
        provider: Cloud provider name (e.g., "hetzner")

    Returns:
        True if server is configured (has IP and name)
    """
    if provider == "hetzner":
        return bool(config.hetzner.server_ip and config.hetzner.server_name)
    return False


@click.command("materialize")
@click.option(
    "--provider",
    type=click.Choice(["hetzner"]),
    required=True,
    help="Cloud provider for VPS provisioning.",
)
@click.option(
    "--create",
    "force_create",
    is_flag=True,
    help="Force creation of new server (errors if already configured).",
)
@click.option(
    "--server-type",
    default=None,
    help="Server type for cloud provisioning (default from config: hetzner.default_server_type).",
)
@click.option(
    "--location",
    default=None,
    help="Datacenter location for cloud provisioning (default from config: hetzner.default_location).",
)
@click.option(
    "--image",
    default=None,
    help="OS image for cloud provisioning (default from config: hetzner.default_image).",
)
@click.option(
    "--ssh-key-name",
    default=None,
    help="SSH key name registered with cloud provider.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm prompts (e.g., auto-select first SSH key).",
)
@djb_pass_context(CliK8sContext)
@click.pass_context
def materialize(
    ctx: click.Context,
    cli_ctx: CliK8sContext,
    provider: str,
    force_create: bool,
    server_type: str | None,
    location: str | None,
    image: str | None,
    ssh_key_name: str | None,
    yes: bool,
) -> None:
    """Create cloud VPS for K8s deployment.

    Creates a server using the specified cloud provider and stores
    the server info in project config for the current mode.

    This command is typically invoked automatically by `terraform` when
    no server is configured, but can be run directly for explicit control.

    \\b
    Hetzner Cloud mode:
      djb -m staging deploy k8s materialize --provider hetzner \\
          --server-type cx22 --location nbg1 --ssh-key-name my-key

    \\b
    The command stores server info in project config [hetzner] section:
      server_name = "myproject-staging"
      server_ip = "116.203.x.x"

    \\b
    Subsequent commands use this config automatically:
      djb -m staging deploy k8s terraform  # Uses stored server
      djb -m staging deploy k8s            # Deploys to stored server
    """
    if cli_ctx.config is None:
        raise click.ClickException("Config not available. Run from a djb project directory.")
    config = cli_ctx.config

    # Apply config defaults for unspecified options
    resolved_server_type = server_type or config.hetzner.default_server_type
    resolved_location = location or config.hetzner.default_location
    resolved_image = image or config.hetzner.default_image

    if provider == "hetzner":
        _materialize_hetzner(
            cli_ctx=cli_ctx,
            force_create=force_create,
            server_type=resolved_server_type,
            location=resolved_location,
            image=resolved_image,
            ssh_key_name=ssh_key_name,
            yes=yes,
        )
    else:
        raise click.ClickException(f"Unknown provider: {provider}")


def _materialize_hetzner(
    cli_ctx: CliK8sContext,
    force_create: bool,
    server_type: str,
    location: str,
    image: str,
    ssh_key_name: str | None,
    yes: bool = False,
) -> None:
    """Create or retrieve Hetzner VPS.

    Args:
        cli_ctx: CLI context with runner and config
        force_create: If True, force creation (error if already configured)
        server_type: Hetzner server type (e.g., "cx23")
        location: Datacenter location (e.g., "nbg1")
        image: OS image (e.g., "ubuntu-24.04")
        ssh_key_name: SSH key name in Hetzner Cloud
        yes: If True, auto-select first SSH key without prompting
    """
    config = cli_ctx.config
    server = provision_hetzner_server(
        runner=cli_ctx.runner,
        config=config,
        server_type=server_type,
        location=location,
        image=image,
        ssh_key_name=ssh_key_name,
        create=force_create,
        yes=yes,
    )

    # Save server info to project config for the current mode
    _save_hetzner_server_to_config(config, server.name, server.ip, ssh_key_name)

    logger.note()
    logger.done(f"Server materialized: {server.name} ({server.ip})")
    logger.note()
    logger.info("Next steps:")
    logger.info(f"  Provision infrastructure: djb -m {config.mode.value} deploy k8s terraform")


def _save_hetzner_server_to_config(
    config: DjbConfig,
    server_name: str,
    server_ip: str,
    ssh_key_name: str | None,
) -> None:
    """Save Hetzner server info to project config [hetzner] section.

    Args:
        config: DjbConfig with current mode and project_dir
        server_name: Server name (e.g., "myproject-staging")
        server_ip: Server IP address
        ssh_key_name: SSH key name used for the server
    """
    mode_str = config.mode.value

    save_config_value_for_mode(
        config_type=PROJECT,
        project_root=config.project_dir,
        key="server_name",
        value=server_name,
        mode=mode_str,
        section_path="hetzner",
    )
    save_config_value_for_mode(
        config_type=PROJECT,
        project_root=config.project_dir,
        key="server_ip",
        value=server_ip,
        mode=mode_str,
        section_path="hetzner",
    )
    if ssh_key_name:
        save_config_value_for_mode(
            config_type=PROJECT,
            project_root=config.project_dir,
            key="ssh_key_name",
            value=ssh_key_name,
            mode=mode_str,
            section_path="hetzner",
        )

    logger.info(f"Server info saved to .djb/project.toml [{mode_str}.hetzner]")
