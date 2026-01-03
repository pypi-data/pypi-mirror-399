"""
HetznerConfig - Nested config for Hetzner Cloud settings.

This module defines the HetznerConfig dataclass used for configuring
Hetzner Cloud server provisioning defaults and instance state.

Fields are split into two categories:
- Default fields (config_file="core"): Provisioning defaults from core.toml
- Instance fields (config_file="project"): Server state from materialize command
"""

from __future__ import annotations

import attrs

from djb.config.constants import (
    HetznerImage,
    HetznerLocation,
    HetznerServerType,
)
from djb.config.field import StringField
from djb.config.fields.enum import EnumField
from djb.config.fields.ip import IPAddressField


@attrs.frozen
class HetznerConfig:
    """Nested config for Hetzner Cloud settings.

    Default fields (from core.toml, overridable via project/local):
        default_server_type - Server type for provisioning (e.g., "cx22")
        default_location - Datacenter location (e.g., "nbg1")
        default_image - OS image (e.g., "ubuntu-24.04")

    Instance fields (from project.toml, populated by materialize command):
        server_name - Name of the provisioned server
        server_ip - IP address of the provisioned server
        ssh_key_name - SSH key used for the server

    Configured via TOML sections:
        [hetzner]                    # Production defaults/instance
        default_server_type = "cx22"
        default_location = "nbg1"
        default_image = "ubuntu-24.04"
        server_name = "myproject-prod"
        server_ip = "116.203.x.x"

        [staging.hetzner]            # Staging overrides
        default_server_type = "cx32"
        server_name = "myproject-staging"
        server_ip = "116.203.y.y"

    Used in DjbConfig as:
        hetzner: HetznerConfig = NestedConfigField(HetznerConfig)()

    Access values via:
        config.hetzner.default_server_type  # "cx22" or overridden
        config.hetzner.server_name          # None or provisioned name
    """

    # === Default fields (config_file="core") ===
    # Defined in core.toml, can be overridden in project/local.
    # CLI writes require --project or --local flag.

    default_server_type: str = EnumField(
        HetznerServerType,
        strict=False,
        config_file="core",
        default=HetznerServerType.CX23,
    )()
    default_location: str = EnumField(
        HetznerLocation,
        strict=False,
        config_file="core",
        default=HetznerLocation.NBG1,
    )()
    default_image: str = EnumField(
        HetznerImage,
        strict=False,
        config_file="core",
        default=HetznerImage.UBUNTU_24_04,
    )()

    # === Instance fields (config_file="project") ===
    # Populated by `djb deploy k8s materialize` command.
    # Mode-specific (stored in [staging.hetzner] for staging mode, etc.)

    server_name: str | None = StringField(config_file="project", default=None)()
    server_ip: str | None = IPAddressField(config_file="project", default=None)()
    ssh_key_name: str | None = StringField(config_file="project", default=None)()
