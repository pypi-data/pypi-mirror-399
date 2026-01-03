"""
djb deploy k8s - Main Kubernetes command group.

Provides the `djb deploy k8s` command group for Kubernetes deployments.

Auto-provisioning workflow:
When no --host is specified, the command automatically:
1. Materializes a cloud server (if not already configured)
2. Provisions K8s infrastructure via terraform
3. Deploys the application

This enables simple deployment with just: djb deploy k8s
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click

from djb.buildpacks import BuildpackError, RemoteBuildpackChain
from djb.cli.context import CliContext, CliK8sContext, djb_pass_context
from djb.cli.domain import domain_sync
from djb.cli.k8s.buildpack import buildpack
from djb.cli.k8s.deploy import deploy_k8s
from djb.cli.k8s.local import local
from djb.cli.k8s.materialize import is_server_materialized, materialize
from djb.cli.k8s.terraform import terraform
from djb.config import djb_get_config
from djb.core.logging import get_logger
from djb.ssh import SSHClient, SSHError

if TYPE_CHECKING:
    from djb.config import DjbConfig

logger = get_logger(__name__)


def _get_config_from_context(ctx: click.Context) -> DjbConfig | None:
    """Get DjbConfig from Click context if available."""
    cli_ctx = ctx.find_object(CliContext)
    if cli_ctx is None or cli_ctx.config is None:
        return None
    return cli_ctx.config


def _ensure_server_materialized(ctx: click.Context, yes: bool = False) -> str:
    """Ensure a cloud server is materialized, creating one if needed.

    Args:
        ctx: Click context for invoking subcommands
        yes: If True, skip confirmation prompts

    Returns:
        SSH host string (e.g., "root@116.203.x.x")

    Raises:
        click.ClickException: If materialization fails or user declines
    """
    config = ctx.obj.config
    provider = "hetzner"  # Currently only supported provider

    if is_server_materialized(config, provider):
        logger.info(
            f"Using existing server: {config.hetzner.server_name} ({config.hetzner.server_ip})"
        )
        return f"root@{config.hetzner.server_ip}"

    # No server configured - need to materialize
    logger.info(f"No server configured for mode '{config.mode.value}'")

    if not yes and not click.confirm(f"Create a new {provider.title()} server?", default=True):
        raise click.ClickException(
            "Server required for deployment.\n"
            f"Run 'djb -m {config.mode.value} deploy k8s materialize --provider {provider}' "
            "to create one manually."
        )

    # Invoke materialize command
    ctx.invoke(
        materialize,
        provider=provider,
        force_create=False,
        server_type=None,  # Use defaults from config
        location=None,
        image=None,
        ssh_key_name=None,
        yes=yes,
    )

    # Reload config to get new server info (bypass cache since config files changed)
    config = djb_get_config(mode=config.mode, _bypass_cache=True)

    # Update context with new config
    cli_ctx = ctx.find_object(CliContext)
    if cli_ctx is not None:
        cli_ctx.config = config

    if not config.hetzner.server_ip:
        raise click.ClickException(
            "Server materialization failed - no IP in config.\n"
            "Check the error messages above and try again."
        )

    return f"root@{config.hetzner.server_ip}"


def _ensure_infrastructure_provisioned(
    ctx: click.Context,
    host: str,
    port: int,
    ssh_key: Path | None,
    email: str | None,
) -> None:
    """Ensure K8s infrastructure is provisioned on the target host.

    Args:
        ctx: Click context for invoking subcommands
        host: SSH host string (e.g., "root@116.203.x.x")
        port: SSH port
        ssh_key: Path to SSH private key
        email: Email for Let's Encrypt (optional)
    """
    logger.info(f"Ensuring infrastructure is provisioned on {host}...")

    # Invoke terraform command - it's idempotent and will skip what's already done
    ctx.invoke(
        terraform,
        local_mode=False,
        use_microk8s=False,
        host=host,
        port=port,
        ssh_key=ssh_key,
        provider="manual",  # We already have the host
        force_create=False,
        server_type=None,
        location=None,
        image=None,
        ssh_key_name=None,
        domain=None,
        email=email,
        skip_cloudnativepg=False,
        skip_tls=email is None,
    )


def _ensure_dns_configured(ctx: click.Context) -> None:
    """Configure Cloudflare DNS if auto_dns is enabled and domains are set.

    Args:
        ctx: Click context for invoking subcommands
    """
    config = ctx.obj.config
    # Only configure if auto_dns is enabled
    if not config.cloudflare.auto_dns:
        logger.debug("Cloudflare auto_dns disabled, skipping DNS configuration")
        return

    # Only configure if K8s domain names are set
    if not config.k8s.domain_names:
        logger.debug("No K8s domain names configured, skipping DNS configuration")
        return

    # Only configure if we have a server IP
    if not config.hetzner.server_ip:
        logger.debug("No server IP available, skipping DNS configuration")
        return

    logger.info("Configuring Cloudflare DNS...")

    try:
        ctx.invoke(domain_sync, dry_run=False)
    except click.ClickException as e:
        # DNS configuration is optional - warn but don't fail deploy
        logger.warning(f"DNS configuration skipped: {e}")


def _ensure_buildpacks_built(
    ctx: click.Context,
    host: str,
    port: int,
    ssh_key: Path | None,
) -> None:
    """Ensure buildpack chain is built, building missing images.

    Args:
        ctx: Click context
        host: SSH host string (e.g., "root@116.203.x.x")
        port: SSH port
        ssh_key: Path to SSH private key
    """
    config = ctx.obj.config
    buildpacks = config.k8s.backend.buildpacks
    registry = config.k8s.backend.buildpack_registry

    if not buildpacks:
        logger.debug("No buildpacks configured, skipping")
        return

    logger.info(f"Ensuring buildpack chain is built: {' -> '.join(buildpacks)}")

    # Create SSH client
    try:
        ssh = SSHClient(
            host=host,
            cmd_runner=ctx.obj.runner,
            port=port,
            key_path=ssh_key,
        )
    except SSHError as e:
        raise click.ClickException(f"SSH connection failed: {e}")

    try:
        chain = RemoteBuildpackChain(
            registry=registry,
            ssh=ssh,
            pyproject_path=config.project_dir / "pyproject.toml",
        )
        final_image = chain.build(buildpacks, force_rebuild=False)
        logger.info(f"Buildpack chain ready: {final_image}")
    except BuildpackError as e:
        raise click.ClickException(f"Buildpack build failed: {e}")


@click.group("k8s", invoke_without_command=True)
@click.option(
    "--host",
    default=None,
    help="SSH target (user@hostname or hostname). Required for deployment.",
)
@click.option(
    "--port",
    default=22,
    help="SSH port (default: 22).",
)
@click.option(
    "--ssh-key",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to SSH private key (default: ~/.ssh/id_ed25519 or ~/.ssh/id_rsa).",
)
@click.option(
    "--skip-build",
    is_flag=True,
    help="Skip building and pushing container image.",
)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations.",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip syncing secrets to Kubernetes.",
)
@click.option(
    "--email",
    default=None,
    help="Email for Let's Encrypt TLS certificates.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm prompts.",
)
@djb_pass_context
@click.pass_context
def k8s(
    ctx: click.Context,
    cli_ctx: CliContext,
    host: str | None,
    port: int,
    ssh_key: Path | None,
    skip_build: bool,
    skip_migrate: bool,
    skip_secrets: bool,
    email: str | None,
    yes: bool,
):
    """Deploy to Kubernetes or manage K8s deployment.

    When invoked without a subcommand, deploys the application to the
    Kubernetes cluster on the specified host.

    \b
    Auto-provisioning (no --host):
    When no host is specified, the command automatically:
    1. Materializes a cloud server (prompts to create if needed)
    2. Provisions K8s infrastructure via terraform
    3. Configures DNS (if cloudflare.auto_dns enabled)
    4. Builds missing buildpacks (if configured)
    5. Deploys the application

    \b
    Deployment workflow:
    * Verifies SSH connectivity and cluster health
    * Builds container image locally
    * Pushes to cluster's local registry
    * Syncs secrets from djb secrets to K8s Secret
    * Applies Kubernetes manifests (Deployment, Service, Ingress)
    * Runs database migrations
    * Tags the deployment for tracking

    \b
    Examples:
      djb deploy k8s                             # Auto-provision and deploy
      djb deploy k8s --host root@server          # Deploy to existing server
      djb deploy k8s terraform --host root@server  # Provision infrastructure only
      djb deploy k8s local start                 # Start local VPS for testing
    """
    # Specialize context for k8s subcommands
    k8s_ctx = CliK8sContext()
    k8s_ctx.__dict__.update(cli_ctx.__dict__)
    ctx.obj = k8s_ctx
    k8s_ctx.host = host
    k8s_ctx.port = port
    k8s_ctx.ssh_key = ssh_key
    k8s_ctx.skip_build = skip_build
    k8s_ctx.skip_migrate = skip_migrate
    k8s_ctx.skip_secrets = skip_secrets

    # Only run deployment if no subcommand was invoked
    if ctx.invoked_subcommand is not None:
        return

    # Get config for auto-provisioning
    config = _get_config_from_context(ctx)

    # Auto-provision if no host specified
    if host is None:
        if config is None:
            raise click.ClickException(
                "No host specified and not in a djb project directory.\n"
                "Either specify --host or run from a project directory for auto-provisioning."
            )

        # Step 1: Ensure server is materialized
        host = _ensure_server_materialized(ctx, yes=yes)
        k8s_ctx.host = host  # Update context with resolved host

        # Step 2: Ensure infrastructure is provisioned (idempotent)
        _ensure_infrastructure_provisioned(ctx, host, port, ssh_key, email)

        # Step 3: Configure DNS (if cloudflare.auto_dns enabled)
        _ensure_dns_configured(ctx)

    # Step 4: Ensure buildpacks are built (runs for both --host and auto-provisioning)
    # k8s_ctx.host is set either from --host or from materialization above
    if k8s_ctx.host is None:
        raise click.ClickException(
            "No host available for buildpack build.\n"
            "Specify --host or ensure server materialization succeeded."
        )
    _ensure_buildpacks_built(ctx, k8s_ctx.host, port, ssh_key)

    deploy_k8s(ctx, k8s_ctx)


k8s.add_command(buildpack)
k8s.add_command(local)
k8s.add_command(materialize)
k8s.add_command(terraform)
