"""
Kubernetes manifest generator using Jinja2 templates.

Renders K8s manifests from templates with project-specific configuration.
Templates are stored in the templates/ subdirectory.

Template Variables:
    Templates receive two context variables:
    - deploy_ctx: Template-specific runtime context (DeploymentCtx, SecretsCtx, etc.)
    - djb_config: DjbConfig with user configuration (project_name, db_name, email, etc.)

    Templates access config values from djb_config:
    - {{ djb_config.project_name }}, {{ djb_config.db_name }}
    - {{ djb_config.k8s.domain_names }}, {{ djb_config.email }}

    Runtime values come from deploy_ctx:
    - {{ deploy_ctx.image }}, {{ deploy_ctx.replicas }}
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

if TYPE_CHECKING:
    from djb.config import DjbConfig


# Template directory path
TEMPLATES_DIR = Path(__file__).parent / "templates"


# =============================================================================
# Template-specific context dataclasses
# =============================================================================


@dataclass
class DeploymentCtx:
    """Runtime context for deployment.yaml template.

    Config values like project_name come from djb_config.
    """

    image: str
    replicas: int = 1
    port: int = 8000
    resources: dict[str, Any] = field(
        default_factory=lambda: {
            "requests": {"memory": "256Mi", "cpu": "100m"},
            "limits": {"memory": "512Mi", "cpu": "500m"},
        }
    )
    health_path: str = "/health/"
    env_vars: dict[str, str] = field(default_factory=dict)
    # Boolean flags for conditional rendering (actual secrets are in SecretsCtx)
    has_secrets: bool = False
    has_database: bool = False


@dataclass
class ServiceCtx:
    """Runtime context for service.yaml template."""

    port: int = 8000


@dataclass
class SecretsCtx:
    """Runtime context for secrets.yaml template."""

    secrets: dict[str, str] = field(default_factory=dict)


@dataclass
class DatabaseCtx:
    """Runtime context for cnpg-cluster.yaml template."""

    instances: int = 1
    size: str = "10Gi"
    storage_class: str | None = None
    memory: str = "256Mi"
    cpu: str = "100m"
    memory_limit: str = "512Mi"
    cpu_limit: str = "500m"


@dataclass
class MigrationCtx:
    """Runtime context for migration-job.yaml template."""

    image: str
    command: str = "python manage.py migrate --noinput"
    has_secrets: bool = False
    env_vars: dict[str, str] = field(default_factory=dict)


class K8sManifestGenerator:
    """Generator for Kubernetes manifests using Jinja2 templates.

    Templates receive two context variables:
    - deploy_ctx: Template-specific runtime context (DeploymentCtx, SecretsCtx, etc.)
    - djb_config: DjbConfig with user configuration (project_name, db_name, email, etc.)

    Example:
        generator = K8sManifestGenerator()
        deployment_ctx = DeploymentCtx(image="localhost:32000/myapp:abc123")
        deployment = generator.render("deployment.yaml.j2", deployment_ctx, djb_config)
    """

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the generator.

        Args:
            templates_dir: Custom templates directory (default: built-in templates).
        """
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["yaml", "yml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        self.env.filters["b64encode"] = self._b64encode

    @staticmethod
    def _b64encode(value: str | dict | list) -> str:
        """Base64 encode a value for K8s secrets.

        Handles both strings and nested structures (dicts/lists) by
        JSON-encoding non-string values first.
        """
        if isinstance(value, str):
            data = value
        else:
            # Serialize nested structures to JSON
            data = json.dumps(value, separators=(",", ":"))
        return base64.b64encode(data.encode()).decode()

    def render(
        self,
        template_name: str,
        djb_config: DjbConfig,
        deploy_ctx: Any = None,
    ) -> str:
        """Render a single template.

        Args:
            template_name: Name of the template file (e.g., "deployment.yaml.j2").
            djb_config: User configuration (project_name, db_name, email, etc.).
            deploy_ctx: Template-specific runtime context. Can be None for templates
                that only use djb_config (e.g., namespace.yaml.j2).

        Returns:
            Rendered YAML manifest.
        """
        template = self.env.get_template(template_name)
        return template.render(deploy_ctx=deploy_ctx, djb_config=djb_config)

    def render_all(
        self,
        djb_config: DjbConfig,
        *,
        deployment: DeploymentCtx,
        service: ServiceCtx | None = None,
        secrets: SecretsCtx | None = None,
        database: DatabaseCtx | None = None,
    ) -> dict[str, str]:
        """Render all manifests for a deployment.

        Args:
            djb_config: User configuration (project_name, db_name, email, etc.).
            deployment: Runtime context for deployment.yaml (required).
            service: Runtime context for service.yaml. Defaults to using deployment.port.
            secrets: Runtime context for secrets.yaml. Only rendered if provided.
            database: Runtime context for cnpg-cluster.yaml. Only rendered if provided.

        Returns:
            Dict mapping manifest names to rendered YAML.
        """
        manifests = {}

        # Namespace (only needs djb_config)
        manifests["namespace.yaml"] = self.render("namespace.yaml.j2", djb_config)

        # Deployment
        manifests["deployment.yaml"] = self.render("deployment.yaml.j2", djb_config, deployment)

        # Service (default to deployment port if not specified)
        service_ctx = service or ServiceCtx(port=deployment.port)
        manifests["service.yaml"] = self.render("service.yaml.j2", djb_config, service_ctx)

        # Secrets (if provided)
        if secrets and secrets.secrets:
            manifests["secrets.yaml"] = self.render("secrets.yaml.j2", djb_config, secrets)

        # Ingress (if domain names configured, only needs djb_config)
        if djb_config.k8s.domain_names:
            manifests["ingress.yaml"] = self.render("ingress.yaml.j2", djb_config)

        # Database (CloudNativePG)
        if database:
            manifests["cnpg-cluster.yaml"] = self.render(
                "cnpg-cluster.yaml.j2", djb_config, database
            )

        return manifests


def render_manifest(
    template_name: str,
    djb_config: DjbConfig,
    deploy_ctx: Any = None,
) -> str:
    """Convenience function to render a single manifest.

    Args:
        template_name: Name of the template file.
        djb_config: User configuration (project_name, db_name, email, etc.).
        deploy_ctx: Template-specific runtime context.

    Returns:
        Rendered YAML manifest.
    """
    generator = K8sManifestGenerator()
    return generator.render(template_name, djb_config, deploy_ctx)


def render_all_manifests(
    djb_config: DjbConfig,
    *,
    deployment: DeploymentCtx,
    service: ServiceCtx | None = None,
    secrets: SecretsCtx | None = None,
    database: DatabaseCtx | None = None,
) -> dict[str, str]:
    """Convenience function to render all manifests.

    Args:
        djb_config: User configuration (project_name, db_name, email, etc.).
        deployment: Runtime context for deployment.yaml (required).
        service: Runtime context for service.yaml. Defaults to using deployment.port.
        secrets: Runtime context for secrets.yaml. Only rendered if provided.
        database: Runtime context for cnpg-cluster.yaml. Only rendered if provided.

    Returns:
        Dict mapping manifest names to rendered YAML.
    """
    generator = K8sManifestGenerator()
    return generator.render_all(
        djb_config,
        deployment=deployment,
        service=service,
        secrets=secrets,
        database=database,
    )
