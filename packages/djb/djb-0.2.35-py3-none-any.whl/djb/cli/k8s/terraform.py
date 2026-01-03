"""
djb deploy k8s terraform - Infrastructure provisioning command.

Provisions Kubernetes infrastructure using the ClusterProvider abstraction.
Supports local (k3d/microk8s), remote (SSH-based), and cloud (Hetzner) clusters.

This is a declarative, idempotent command - each execution checks the
health of all infrastructure components and only provisions/fixes what's
missing or unhealthy.

Local Mode (k3d or microk8s):
-----------------------------
$ djb deploy k8s terraform --local              # k3d (default)
$ djb deploy k8s terraform --local --microk8s   # local microk8s

Remote Mode (SSH-based microk8s):
---------------------------------
$ djb deploy k8s terraform --host root@server

Hetzner Cloud Mode:
-------------------
$ djb -m staging deploy k8s terraform --provider hetzner \\
    --server-type cx23 --location nbg1 --ssh-key-name my-key

Checking microk8s...           ✓ installed and running
Checking dns addon...          ✓ enabled
Checking storage addon...      ✓ enabled
Checking registry addon...     ✗ not enabled -> enabling...
Checking ingress addon...      ✓ enabled
Checking cert-manager addon... ✓ enabled
Checking CloudNativePG...      ✓ installed
Checking ClusterIssuer...      ✓ configured

Infrastructure ready.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.k8s.constants import KUBECTL_WAIT_TIMEOUT
from djb.cli.k8s.k8s import CliK8sContext
from djb.cli.k8s.materialize import is_server_materialized, materialize
from djb.cli.utils import CmdRunner
from djb.core.logging import get_logger
from djb.k8s import (
    ClusterError,
    SSHConfig,
    get_cluster_provider,
)

if TYPE_CHECKING:
    from djb.k8s.cluster.provider import ClusterProvider

logger = get_logger(__name__)


# CloudNativePG operator version
CNPG_VERSION = "1.22.0"
CNPG_URL = f"https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-{CNPG_VERSION}.yaml"


def _get_project_name_from_context(ctx: click.Context) -> str:
    """Get project name from Click context if available."""
    cli_ctx = ctx.find_object(CliContext)
    if cli_ctx is not None and cli_ctx.config is not None:
        return cli_ctx.config.project_name
    return "djb-project"


def _get_base_addons(cluster_type: str, remote: bool) -> list[str]:
    """Get the list of addons to enable based on cluster type and mode."""
    if cluster_type == "k3d":
        # k3d includes most addons by default, only need registry
        return ["dns", "registry"]
    else:
        # microk8s needs explicit addon enablement
        addons = ["dns", "storage", "registry", "ingress"]
        if remote:
            # Remote clusters get cert-manager for TLS
            addons.append("cert-manager")
        return addons


def _check_cloudnativepg(provider: ClusterProvider, cluster_name: str) -> tuple[bool, str]:
    """Check if CloudNativePG operator is installed."""
    try:
        returncode, stdout, _ = provider.kubectl(
            cluster_name,
            "get",
            "deployment",
            "-n",
            "cnpg-system",
            "cnpg-controller-manager",
        )
        if returncode == 0 and "cnpg-controller-manager" in stdout:
            return True, "installed"
        return False, "not installed"
    except ClusterError:
        return False, "not installed"


def _install_cloudnativepg(provider: ClusterProvider, cluster_name: str) -> None:
    """Install CloudNativePG operator."""
    logger.info("Installing CloudNativePG operator...")

    # Apply the CloudNativePG operator manifest
    returncode, stdout, stderr = provider.kubectl(
        cluster_name,
        "apply",
        "-f",
        CNPG_URL,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to install CloudNativePG: {stderr}")

    # Wait for the operator to be ready
    logger.info("Waiting for CloudNativePG operator to be ready...")
    returncode, stdout, stderr = provider.kubectl(
        cluster_name,
        "wait",
        "--for=condition=available",
        f"--timeout={KUBECTL_WAIT_TIMEOUT // 1000}s",
        "deployment/cnpg-controller-manager",
        "-n",
        "cnpg-system",
    )
    if returncode != 0:
        logger.warning(f"CloudNativePG operator may not be fully ready: {stderr}")


def _check_clusterissuer(
    provider: ClusterProvider, cluster_name: str, email: str
) -> tuple[bool, str]:
    """Check if Let's Encrypt ClusterIssuer is configured."""
    try:
        returncode, stdout, _ = provider.kubectl(
            cluster_name, "get", "clusterissuer", "letsencrypt-prod"
        )
        if returncode == 0 and "letsencrypt-prod" in stdout:
            return True, "configured"
        return False, "not configured"
    except ClusterError:
        return False, "not configured"


def _create_clusterissuer(provider: ClusterProvider, cluster_name: str, email: str) -> None:
    """Create Let's Encrypt ClusterIssuer."""
    logger.info("Creating Let's Encrypt ClusterIssuer...")

    issuer_manifest = {
        "clusterissuer.yaml": f"""apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: {email}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
"""
    }

    try:
        provider.apply_manifests(cluster_name, issuer_manifest)
    except ClusterError as e:
        raise click.ClickException(f"Failed to create ClusterIssuer: {e}")


@click.command("terraform")
@click.option(
    "--local",
    "local_mode",
    is_flag=True,
    help="Provision local cluster (k3d by default, or microk8s with --microk8s).",
)
@click.option(
    "--microk8s",
    "use_microk8s",
    is_flag=True,
    help="Use microk8s instead of k3d for local cluster.",
)
@click.option(
    "--host",
    default=None,
    help="SSH target (user@hostname) for remote provisioning.",
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
    help="Path to SSH private key.",
)
@click.option(
    "--provider",
    type=click.Choice(["manual", "hetzner"]),
    default="manual",
    help="Cloud provider for VPS provisioning (default: manual = requires --host).",
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
    "--domain",
    default=None,
    help="Domain for Let's Encrypt TLS certificates (remote only).",
)
@click.option(
    "--email",
    default=None,
    help="Email for Let's Encrypt (required for TLS on remote).",
)
@click.option(
    "--skip-cloudnativepg",
    is_flag=True,
    help="Skip CloudNativePG operator installation.",
)
@click.option(
    "--skip-tls",
    is_flag=True,
    help="Skip Let's Encrypt ClusterIssuer setup (remote only).",
)
@djb_pass_context(CliK8sContext)
@click.pass_context
def terraform(
    ctx: click.Context,
    cli_ctx: CliK8sContext,
    local_mode: bool,
    use_microk8s: bool,
    host: str | None,
    port: int,
    ssh_key: Path | None,
    provider: str,  # CLI option for cloud provider name
    force_create: bool,
    server_type: str | None,
    location: str | None,
    image: str | None,
    ssh_key_name: str | None,
    domain: str | None,
    email: str | None,
    skip_cloudnativepg: bool,
    skip_tls: bool,
) -> None:
    """Provision Kubernetes infrastructure.

    Supports local clusters (for development), remote clusters (via SSH),
    and cloud-provisioned clusters (Hetzner). Uses the ClusterProvider
    abstraction to encapsulate differences between k3d and microk8s.

    This command is idempotent - each execution checks the health of all
    infrastructure components and only provisions/fixes what's missing.

    \b
    Local mode (development):
      djb deploy k8s terraform --local              # k3d (fast, ~30s)
      djb deploy k8s terraform --local --microk8s   # microk8s

    \b
    Remote mode (production, manual host):
      djb deploy k8s terraform --host root@server --email admin@example.com

    \b
    Hetzner Cloud mode (creates VPS + provisions):
      djb -m staging deploy k8s terraform --provider hetzner \\
          --server-type cx23 --location nbg1 --ssh-key-name my-key

    \b
    Infrastructure provisioned:
    * K8s cluster (k3d, microk8s, or remote microk8s)
    * Addons: dns, storage, registry, ingress
    * CloudNativePG operator (PostgreSQL)
    * Let's Encrypt ClusterIssuer (remote only, for TLS)
    """
    # Get config from context
    config = cli_ctx.config
    cmd_runner = cli_ctx.runner

    # Validate options
    if local_mode and host:
        raise click.ClickException("Cannot use both --local and --host. Choose one mode.")

    if local_mode and provider == "hetzner":
        raise click.ClickException("Cannot use --local with --provider hetzner.")

    # Handle Hetzner provider - provisions a VPS then SSHs to it
    if provider == "hetzner":
        if host:
            raise click.ClickException(
                "Cannot use --host with --provider hetzner. "
                "Hetzner mode provisions and connects to the VPS automatically."
            )

        if config is None:
            raise click.ClickException("Config not available. Run from a djb project directory.")

        # Check if server is already materialized
        if not is_server_materialized(config, provider):
            # Prompt user to create server
            if not click.confirm(
                f"No {provider.title()} server configured for {config.mode.value}.\n"
                "Create one now?"
            ):
                raise click.ClickException(
                    f"Server required. Run 'djb deploy k8s materialize --provider {provider}' first."
                )

            # Invoke materialize command
            ctx.invoke(
                materialize,
                provider=provider,
                force_create=force_create,
                server_type=server_type,
                location=location,
                image=image,
                ssh_key_name=ssh_key_name,
            )

            # Reload config to get new server info
            from djb.config import djb_get_config  # noqa: PLC0415

            config = djb_get_config(mode=config.mode)
            cli_ctx.config = config

        # Use the server IP from config
        if not config.hetzner.server_ip:
            raise click.ClickException(
                "Server materialization failed - no IP in config.\n"
                f"Run 'djb deploy k8s materialize --provider {provider}' to debug."
            )

        host = f"root@{config.hetzner.server_ip}"
        logger.info(
            f"Using Hetzner server: {config.hetzner.server_name} ({config.hetzner.server_ip})"
        )

    if not local_mode and not host:
        raise click.ClickException(
            "No host specified. Use --local for local cluster, --host for remote,\n"
            "or --provider hetzner for cloud provisioning.\n"
            "Examples:\n"
            "  djb deploy k8s terraform --local\n"
            "  djb deploy k8s terraform --host root@server --email admin@example.com\n"
            "  djb -m staging deploy k8s terraform --provider hetzner --ssh-key-name my-key"
        )

    # Remote mode requires email for TLS
    remote_mode = host is not None
    if remote_mode and not skip_tls and not email:
        raise click.ClickException(
            "Email is required for Let's Encrypt TLS.\n"
            "Use --email admin@example.com or --skip-tls to skip TLS setup."
        )

    # Get project name for cluster naming
    project_name = _get_project_name_from_context(ctx)
    cluster_name = f"djb-{project_name}"

    # Determine cluster type and get cluster provider
    cluster_provider: ClusterProvider
    if local_mode:
        cluster_type = "microk8s" if use_microk8s else "k3d"
        logger.info(f"Provisioning local {cluster_type} cluster: {cluster_name}")
        try:
            cluster_provider = get_cluster_provider(cluster_type, cmd_runner)
        except ClusterError as e:
            raise click.ClickException(str(e))
    else:
        cluster_type = "microk8s"
        assert host is not None  # Validated above
        logger.info(f"Provisioning remote microk8s on {host}:{port}")
        ssh_config = SSHConfig(
            host=host,
            port=port,
            key_path=ssh_key,
        )
        try:
            cluster_provider = get_cluster_provider(cluster_type, cmd_runner, ssh_config=ssh_config)
        except ClusterError as e:
            raise click.ClickException(f"Failed to connect: {e}")

    # Check/create cluster
    logger.next(f"Checking {cluster_type}")
    try:
        if cluster_provider.exists(cluster_name) and cluster_provider.is_running(cluster_name):
            logger.done(f"{cluster_type}: running")
        else:
            logger.info(f"{cluster_type}: not running -> creating...")
            cluster_provider.create(cluster_name)
            logger.done(f"{cluster_type} cluster created")
    except ClusterError as e:
        raise click.ClickException(str(e))

    # Enable addons
    addons = _get_base_addons(cluster_type, remote=remote_mode)
    logger.next("Enabling addons")
    try:
        cluster_provider.enable_addons(cluster_name, addons)
        logger.done(f"Addons enabled: {', '.join(addons)}")
    except ClusterError as e:
        raise click.ClickException(f"Failed to enable addons: {e}")

    # Check/install CloudNativePG
    if not skip_cloudnativepg:
        logger.next("Checking CloudNativePG")
        is_installed, status_msg = _check_cloudnativepg(cluster_provider, cluster_name)
        if is_installed:
            logger.done(f"CloudNativePG: {status_msg}")
        else:
            logger.info(f"CloudNativePG: {status_msg} -> installing...")
            _install_cloudnativepg(cluster_provider, cluster_name)
            logger.done("CloudNativePG installed")
    else:
        logger.skip("CloudNativePG (--skip-cloudnativepg)")

    # Check/create ClusterIssuer (remote only)
    if remote_mode and not skip_tls and email:
        logger.next("Checking ClusterIssuer")
        is_configured, status_msg = _check_clusterissuer(cluster_provider, cluster_name, email)
        if is_configured:
            logger.done(f"ClusterIssuer: {status_msg}")
        else:
            logger.info(f"ClusterIssuer: {status_msg} -> creating...")
            _create_clusterissuer(cluster_provider, cluster_name, email)
            logger.done("ClusterIssuer created")
    elif remote_mode:
        logger.skip("ClusterIssuer (--skip-tls or no email)")

    # Done
    logger.note()
    logger.done("Infrastructure ready!")
    logger.note()
    logger.info("Next steps:")
    if local_mode:
        logger.info("  Start dev loop: djb deploy k8s local dev")
    else:
        logger.info(
            f"  Deploy app: djb deploy k8s --host {host}"
            + (f" --port {port}" if port != 22 else "")
        )
