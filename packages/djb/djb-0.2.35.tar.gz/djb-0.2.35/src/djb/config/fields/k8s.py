"""
K8sConfig - Nested config for Kubernetes deployment settings.

This module defines K8s deployment configuration with domain names and backend settings.

Structure:
    [k8s]
    domain_names = { "example.com" = { manager = "cloudflare" } }

    [k8s.backend]
    managed_dockerfile = true
    remote_build = true
    buildpacks = ["python:3.14-slim", "gdal:v1"]
    buildpack_registry = "localhost:32000"
"""

from __future__ import annotations

import attrs

from djb.config.field import StringField
from djb.config.fields.bool import BoolField
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.domain_names import DomainNamesMapField
from djb.config.fields.list import ListField
from djb.config.fields.nested import NestedConfigField


@attrs.frozen
class K8sBackendConfig:
    """Nested config for K8s backend deployment settings.

    Fields:
        managed_dockerfile - If True, djb manages the Dockerfile template
            and will copy/update it. If False, djb won't overwrite an
            existing Dockerfile.
        remote_build - If True, build Docker images on the remote server
            (native x86_64, no QEMU). If False, build locally and transfer.
        buildpacks - List of buildpack images to chain (e.g., ["python:3.14-slim", "gdal:v1"]).
            Each buildpack builds FROM the previous one. The final image becomes
            the base for the application layer.
        buildpack_registry - Registry host for buildpack images (default: localhost:32000).

    Configured via TOML sections:
        [k8s.backend]
        managed_dockerfile = true
        remote_build = true
        buildpacks = ["python:3.14-slim", "gdal:v1", "postgresql:v1"]
        buildpack_registry = "localhost:32000"

    Access values via:
        config.k8s.backend.managed_dockerfile  # True by default
        config.k8s.backend.remote_build  # True by default
        config.k8s.backend.buildpacks  # ["python:3.14-slim"] by default
        config.k8s.backend.buildpack_registry  # "localhost:32000" by default
    """

    # If True, djb manages the Dockerfile template and can update it.
    # If False, djb won't overwrite an existing Dockerfile.
    managed_dockerfile: bool = BoolField(config_file="project", default=True)()

    # If True, build on remote server (native x86_64). If False, build locally.
    remote_build: bool = BoolField(config_file="project", default=True)()

    # Chained buildpack images. Each builds FROM the previous.
    # Format: ["name:version", ...] e.g., ["python:3.14-slim", "gdal:v1"]
    buildpacks: list[str] = ListField(
        StringField, config_file="project", default=["python:3.14-slim"]
    )()

    # Registry for buildpack images.
    buildpack_registry: str = StringField(config_file="project", default="localhost:32000")()


@attrs.frozen
class K8sConfig:
    """Nested config for Kubernetes deployment settings.

    Fields:
        domain_names - Map of domain names to their configuration.
            Keys are domain names, values contain metadata (manager, etc.).
            Configured via `djb domain add` with Cloudflare DNS.
        db_name - Optional PostgreSQL database/owner name override.
            If not set, derived from project_name by replacing hyphens
            with underscores (PostgreSQL identifier requirement).

    Contains sub-configs for backend and (future) frontend deployments.

    Configured via TOML inline table:
        [k8s]
        domain_names = { "example.com" = { manager = "cloudflare" } }
        db_name = "custom_db_name"  # optional

        [k8s.backend]
        managed_dockerfile = true

    Used in DjbConfig as:
        k8s: K8sConfig = NestedConfigField(K8sConfig)()

    Access values via:
        config.k8s.domain_names  # dict[str, DomainNameConfig]
        config.k8s.domain_names["example.com"].manager  # DomainNameManager.CLOUDFLARE
        config.k8s.backend.managed_dockerfile  # True by default
        config.k8s.db_name  # "" (empty means derive from project_name)
    """

    # Map of domain names to their configuration
    # Keys are domain names, values contain metadata (manager, etc.)
    domain_names: dict[str, DomainNameConfig] = DomainNamesMapField(config_file="project")()

    # Backend deployment settings (Django/Python)
    backend: K8sBackendConfig = NestedConfigField(K8sBackendConfig)()

    # Optional PostgreSQL database/owner name override
    # If empty, derived from project_name (hyphens replaced with underscores)
    db_name: str = StringField(config_file="project", default="")()
