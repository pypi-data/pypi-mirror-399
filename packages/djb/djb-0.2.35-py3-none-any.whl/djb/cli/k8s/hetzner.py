"""
Hetzner Cloud provisioning orchestration.

This module provides the high-level orchestration for provisioning
Hetzner Cloud servers for djb K8s deployments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from djb.core import CmdRunner
from djb.core.logging import get_logger
from djb.k8s.cloud import HetznerCloudProvider, HetznerError, ServerInfo
from djb.secrets import SecretsManager, SopsError

if TYPE_CHECKING:
    from djb.config import DjbConfig

logger = get_logger(__name__)


def _extract_email_from_public_key(public_key: str | None) -> str | None:
    """Extract email from SSH public key comment.

    SSH public keys typically end with a comment that may contain an email:
    "ssh-ed25519 AAAA... user@example.com"

    Args:
        public_key: The full public key string

    Returns:
        Email address if found, None otherwise
    """
    if not public_key:
        return None

    # Split on whitespace and check if last part looks like an email
    parts = public_key.strip().split()
    if len(parts) >= 3:
        comment = parts[-1]
        if "@" in comment and "." in comment.split("@")[-1]:
            return comment.lower()
    return None


def _resolve_ssh_key_name(
    provider: HetznerCloudProvider,
    ssh_key_name: str | None,
    config_email: str | None = None,
    auto_select: bool = False,
) -> str:
    """Resolve SSH key name, auto-selecting or prompting if needed.

    Resolution order:
    1. Explicitly specified ssh_key_name
    2. Single key available -> auto-select
    3. Match key by config email -> auto-select with note
    4. auto_select=True -> select first key
    5. Multiple keys -> prompt user to choose

    Args:
        provider: HetznerCloudProvider instance
        ssh_key_name: Explicitly specified SSH key name, or None to auto-detect
        config_email: Email from djb config to match against SSH key comments
        auto_select: If True, auto-select the first key without prompting

    Returns:
        SSH key name to use

    Raises:
        click.ClickException: If no SSH keys available or user aborts
    """
    if ssh_key_name:
        return ssh_key_name

    # Get all SSH keys with their public keys for email matching
    try:
        keys_with_details = provider.get_ssh_keys_with_details()
    except HetznerError as e:
        raise click.ClickException(f"Failed to list SSH keys: {e}")

    if not keys_with_details:
        raise click.ClickException(
            "No SSH keys found in Hetzner Cloud.\n"
            "Add an SSH key at: https://console.hetzner.cloud/projects/*/security/sshkeys"
        )

    all_key_names = [name for name, _ in keys_with_details]

    # Single key - auto-select
    if len(keys_with_details) == 1:
        key_name = keys_with_details[0][0]
        logger.info(f"Using SSH key: {key_name}")
        return key_name

    # Try to match by email from config
    if config_email:
        config_email_lower = config_email.lower()
        for key_name, public_key in keys_with_details:
            # Check if key name itself matches the email
            if key_name.lower() == config_email_lower:
                logger.note(f"Auto-selected SSH key '{key_name}' (matches config email)")
                return key_name
            # Check if email in public key comment matches
            key_email = _extract_email_from_public_key(public_key)
            if key_email and key_email == config_email_lower:
                logger.note(
                    f"Auto-selected SSH key '{key_name}' (matches config email: {config_email})"
                )
                return key_name

    # auto_select flag - select first key
    if auto_select:
        key_name = all_key_names[0]
        logger.info(f"Using SSH key: {key_name}")
        return key_name

    # Multiple keys - prompt user to choose
    logger.info("Multiple SSH keys found in Hetzner Cloud:")
    for i, key in enumerate(all_key_names, 1):
        click.echo(f"  {i}. {key}")

    while True:
        choice = click.prompt("Select SSH key", type=int, default=1)
        if 1 <= choice <= len(all_key_names):
            return all_key_names[choice - 1]
        click.echo(f"Invalid choice. Enter 1-{len(all_key_names)}")


def _get_hetzner_api_token(runner: CmdRunner, config: DjbConfig) -> str:
    """Get Hetzner API token from secrets.

    Args:
        runner: CmdRunner instance for executing commands.
        config: DjbConfig with current mode

    Returns:
        Hetzner API token

    Raises:
        click.ClickException: If token not found in secrets
    """
    try:
        manager = SecretsManager(runner, config.project_dir)
        secrets = manager.load_for_mode(config.mode)
    except SopsError as e:
        raise click.ClickException(
            f"Failed to load secrets: {e}\n"
            f"Add Hetzner API token to secrets/{config.mode}.yaml:\n"
            f"  hetzner:\n"
            f"    api_token: hc_xxx..."
        )

    if not secrets:
        raise click.ClickException(
            f"No secrets found for mode '{config.mode}'.\n"
            f"Add Hetzner API token to secrets/{config.mode}.yaml:\n"
            f"  hetzner:\n"
            f"    api_token: hc_xxx..."
        )

    # Try to get token from nested structure or flat key
    hetzner_section = secrets.get("hetzner", {})
    if isinstance(hetzner_section, dict):
        api_token = hetzner_section.get("api_token")
    else:
        api_token = None

    if not api_token:
        # Try flat key format
        api_token = secrets.get("hetzner_api_token")

    if not api_token:
        raise click.ClickException(
            f"Hetzner API token not found in secrets/{config.mode}.yaml.\n"
            f"Add it as:\n"
            f"  hetzner:\n"
            f"    api_token: hc_xxx..."
        )

    return api_token


def _generate_server_name(config: DjbConfig) -> str:
    """Generate server name from project name and mode.

    Args:
        config: DjbConfig with project_name and mode

    Returns:
        Server name like "myproject-staging" or "myproject" (for production)
    """
    base_name = config.project_name
    if config.mode.value == "production":
        return base_name
    return f"{base_name}-{config.mode.value}"


def provision_hetzner_server(
    runner: CmdRunner,
    config: DjbConfig,
    server_type: str,
    location: str,
    image: str,
    ssh_key_name: str | None,
    create: bool,
    yes: bool = False,
) -> ServerInfo:
    """Provision or retrieve Hetzner server for current mode.

    This function handles the full workflow:
    1. Check config for existing server (config.hetzner.server_ip, etc.)
    2. If config has server and not --create, verify server exists in Hetzner
    3. If --create with existing config, error
    4. Create new server via HetznerCloudProvider
    5. Wait for server to be ready
    6. Return ServerInfo (caller is responsible for saving to config)

    Args:
        runner: CmdRunner instance for executing commands.
        config: DjbConfig with current mode and existing hetzner.* values
        server_type: Hetzner server type (e.g., "cx23")
        location: Datacenter location (e.g., "nbg1")
        image: OS image (e.g., "ubuntu-24.04")
        ssh_key_name: Name of SSH key registered in Hetzner Cloud
        create: If True, force creation of new server (error if already configured)
        yes: If True, auto-select first SSH key without prompting

    Returns:
        ServerInfo with server details

    Raises:
        click.ClickException: On any error
    """
    api_token = _get_hetzner_api_token(runner, config)

    try:
        provider = HetznerCloudProvider(api_token)
    except HetznerError as e:
        raise click.ClickException(f"Failed to connect to Hetzner Cloud: {e}")

    # Check if server is already configured
    existing_ip = config.hetzner.server_ip
    existing_name = config.hetzner.server_name

    if existing_ip and existing_name:
        if create:
            raise click.ClickException(
                f"Server already configured for this mode ({config.mode.value}).\n"
                f"  Name: {existing_name}\n"
                f"  IP: {existing_ip}\n\n"
                f"Remove hetzner.server_* from config to create a new server."
            )

        # Verify server exists in Hetzner
        logger.next("Verifying existing server")
        try:
            server = provider.get_server(existing_name)
        except HetznerError as e:
            raise click.ClickException(f"Failed to verify server: {e}")

        if server is None:
            logger.warning(
                f"Server '{existing_name}' not found in Hetzner Cloud. "
                f"It may have been deleted. Creating a new one..."
            )
        else:
            logger.done(f"Server verified: {server.name} ({server.ip})")
            return server

    # Generate server name if not provided
    server_name = existing_name or _generate_server_name(config)

    # Check if server already exists in Hetzner (e.g., from a failed save)
    existing_server = provider.get_server(server_name)
    if existing_server is not None:
        logger.info(
            f"Found existing server in Hetzner: {existing_server.name} ({existing_server.ip})"
        )
        return existing_server

    # Resolve SSH key name - auto-detect from Hetzner if not specified
    effective_ssh_key = _resolve_ssh_key_name(
        provider,
        ssh_key_name or config.hetzner.ssh_key_name,
        config_email=config.email,
        auto_select=yes,
    )

    # Create the server
    logger.next(f"Creating Hetzner server: {server_name}")
    logger.info(f"  Type: {server_type}")
    logger.info(f"  Location: {location}")
    logger.info(f"  Image: {image}")
    logger.info(f"  SSH Key: {effective_ssh_key}")

    try:
        server = provider.create_server(
            name=server_name,
            server_type=server_type,
            location=location,
            image=image,
            ssh_key_name=effective_ssh_key,
        )
        logger.done(f"Server created: {server.name} (ID: {server.id})")
    except HetznerError as e:
        raise click.ClickException(f"Failed to create server: {e}")

    # Wait for server to be ready
    logger.next("Waiting for server to be ready")
    try:
        server = provider.wait_for_server(server_name, timeout=300)
        logger.done(f"Server ready: {server.ip}")
    except HetznerError as e:
        raise click.ClickException(f"Server did not become ready: {e}")

    return server
