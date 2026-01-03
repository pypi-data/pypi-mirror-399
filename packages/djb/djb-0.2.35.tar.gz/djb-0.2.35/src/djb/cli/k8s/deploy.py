"""
djb deploy k8s - Kubernetes deployment command.

Builds, pushes, and deploys the application to a Kubernetes cluster.

Deployment Workflow:
1. Pre-flight checks (SSH, microk8s status)
2. Build container image
3. Push to cluster registry
4. Sync secrets from djb secrets
5. Apply K8s manifests
6. Wait for rollout
7. Run migrations
8. Tag deployment in git

Dockerfile Resolution:
The build process looks for a Dockerfile in this order:
1. deployment/k8s/backend/Dockerfile.j2 (project template, rendered at build time)
2. deployment/k8s/backend/Dockerfile (non-template)
3. Copy djb template to deployment/k8s/backend/Dockerfile.j2

The .j2 template allows customization while still using Jinja2 variables
like {{ config.project_name }} for project-specific values.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click
from jinja2 import Environment, FileSystemLoader

from djb.buildpacks import LocalBuildpackChain, RemoteBuildpackChain
from djb.cli.domain import _sync_k8s_domains, domain_init
from djb.cli.utils import CmdRunner
from djb.ssh import SSHClient, SSHError
from djb.config import DjbConfig
from djb.core.logging import get_logger
from djb.types import DomainNameManager
from djb.k8s import (
    DatabaseCtx,
    DeploymentCtx,
    K8sManifestGenerator,
    MigrationCtx,
    SecretsCtx,
)
from djb.secrets import SecretsManager
from djb.templates import DJB_TEMPLATES_DIR
from djb.types import Mode

if TYPE_CHECKING:
    from djb.cli.k8s.k8s import CliK8sContext

logger = get_logger(__name__)


def _resolve_dockerfile(project_dir: Path) -> Path | None:
    """Find the Dockerfile to use for building.

    Resolution order:
    1. deployment/k8s/backend/Dockerfile.j2 (project template)
    2. deployment/k8s/backend/Dockerfile (non-template)
    3. None (caller should generate from template)

    Args:
        project_dir: Project root directory

    Returns:
        Path to Dockerfile if found, None if should generate
    """
    backend_dir = project_dir / "deployment" / "k8s" / "backend"

    # Check for project template
    template_path = backend_dir / "Dockerfile.j2"
    if template_path.exists():
        logger.info(f"Using project Dockerfile: {template_path.relative_to(project_dir)}")
        return template_path

    # Check for non-template Dockerfile
    simple_path = backend_dir / "Dockerfile"
    if simple_path.exists():
        logger.info(f"Using project Dockerfile: {simple_path.relative_to(project_dir)}")
        return simple_path

    return None


def _copy_dockerfile_template(project_dir: Path) -> Path:
    """Copy the djb Dockerfile template to the project.

    Copies the raw template (not rendered) so users can customize it.
    The template will be rendered at build time.

    Args:
        project_dir: Project root directory

    Returns:
        Path to the copied template
    """
    logger.note("Creating Dockerfile template for Django deployment")

    # Copy raw template content
    source_template = DJB_TEMPLATES_DIR / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
    template_content = source_template.read_text()

    # Write to deployment/k8s/backend/Dockerfile.j2
    backend_dir = project_dir / "deployment" / "k8s" / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)

    dockerfile_path = backend_dir / "Dockerfile.j2"
    dockerfile_path.write_text(template_content)

    logger.info(f"Created {dockerfile_path.relative_to(project_dir)}")
    logger.info("  Customize this template for your project's needs")
    return dockerfile_path


def _render_dockerfile(template_path: Path, djb_config: DjbConfig) -> Path:
    """Render a Dockerfile template to a temporary file.

    Args:
        template_path: Path to the .j2 template
        djb_config: DjbConfig for template variables (project_name, etc.)

    Returns:
        Path to the rendered Dockerfile
    """
    # Create Jinja environment with the template's directory
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template(template_path.name)
    # Dockerfile template uses djb_config.project_name
    rendered_content = template.render(djb_config=djb_config)

    # Write rendered Dockerfile next to template for docker build
    rendered_path = template_path.parent / "Dockerfile"
    rendered_path.write_text(rendered_content)

    return rendered_path


def _get_git_commit_sha(runner: CmdRunner) -> str:
    """Get the current git commit SHA (short form)."""
    result = runner.run(
        ["git", "rev-parse", "--short", "HEAD"],
        quiet=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "latest"


def _get_project_info(k8s_ctx: "CliK8sContext") -> tuple[str, Path, bool, DjbConfig]:
    """Get project name, directory, managed_dockerfile, and config from context.

    Returns:
        Tuple of (project_name, project_dir, managed_dockerfile, djb_config)

    Raises:
        click.ClickException: If no djb configuration is found.
    """
    if k8s_ctx.config is not None:
        config = k8s_ctx.config
        return (
            config.project_name,
            config.project_dir,
            config.k8s.backend.managed_dockerfile,
            config,
        )

    raise click.ClickException(
        "No djb configuration found. Run from a directory with .djb/project.toml"
    )


def _verify_microk8s_ready(ssh: SSHClient) -> None:
    """Verify microk8s is running on the target host."""
    logger.next("Verifying microk8s status")
    returncode, stdout, stderr = ssh.run("microk8s status")
    if returncode != 0 or "microk8s is running" not in stdout:
        raise click.ClickException(
            "microk8s is not running on the target host.\n"
            "Run: djb deploy k8s terraform --host ... to provision first."
        )
    logger.done("microk8s is running")


def _build_container(
    runner: CmdRunner,
    djb_config: DjbConfig,
    commit_sha: str,
    buildpack_image: str,
    registry_host: str = "localhost:32000",
) -> str:
    """Build the container image locally.

    Dockerfile resolution order:
    1. deployment/k8s/backend/Dockerfile.j2 (project template, rendered at build time)
    2. deployment/k8s/backend/Dockerfile (non-template)
    3. Copy djb template to deployment/k8s/backend/Dockerfile.j2 (if managed_dockerfile=True)

    Args:
        runner: CmdRunner instance for executing commands.
        djb_config: DjbConfig for project settings.
        commit_sha: Git commit SHA for tagging
        buildpack_image: Pre-built buildpack chain image to use as base
        registry_host: Registry host:port for tagging

    Returns:
        The full image tag.
    """
    project_name = djb_config.project_name
    project_dir = djb_config.project_dir
    managed_dockerfile = djb_config.k8s.backend.managed_dockerfile

    image_tag = f"{registry_host}/{project_name}:{commit_sha}"

    logger.next(f"Building container image: {image_tag}")

    # Resolve Dockerfile
    dockerfile_path = _resolve_dockerfile(project_dir)

    # Copy template only if managed_dockerfile is True and no Dockerfile exists
    if dockerfile_path is None:
        if managed_dockerfile:
            dockerfile_path = _copy_dockerfile_template(project_dir)
        else:
            raise click.ClickException(
                "Dockerfile not found and k8s.backend.managed_dockerfile is False.\n"
                "Either create deployment/k8s/backend/Dockerfile.j2 manually,\n"
                "or set managed_dockerfile = true in .djb/project.toml [k8s.backend]."
            )

    # If it's a template, render it
    if dockerfile_path.suffix == ".j2":
        dockerfile_path = _render_dockerfile(dockerfile_path, djb_config)

    # Build with buildx for cross-platform support (target x86_64 for cloud servers)
    # Uses QEMU emulation when building on ARM Macs for x86_64 servers
    runner.run(
        [
            "docker",
            "buildx",
            "build",
            "--platform",
            "linux/amd64",
            "--load",  # Load into local docker images
            "--build-arg",
            f"BUILDPACK_IMAGE={buildpack_image}",
            "-f",
            str(dockerfile_path),
            "-t",
            image_tag,
            str(project_dir),
        ],
        label="Building container",
        done_msg="Image built",
        fail_msg=click.ClickException("Container build failed"),
        show_output=True,  # Stream build output for visibility during long builds
    )
    return image_tag


def _push_to_registry(
    runner: CmdRunner,
    ssh: SSHClient,
    image_tag: str,
    registry_port: int = 32000,
) -> None:
    """Push the container image to the cluster registry.

    Uses an SSH tunnel to forward the local Docker push to the
    microk8s registry on the remote host.
    """
    logger.next("Pushing image to cluster registry")

    # Save the image to a tarball and load it on the remote
    # This avoids the complexity of SSH tunneling to the registry
    tar_path = "/tmp/djb-deploy-image.tar"

    # Save image locally
    runner.run(
        ["docker", "save", "-o", tar_path, image_tag],
        label="Saving image",
        fail_msg=click.ClickException("Failed to save Docker image"),
    )

    # Copy to remote
    ssh.copy_to(Path(tar_path), "/tmp/djb-deploy-image.tar", timeout=600)

    # Import into microk8s containerd
    returncode, stdout, stderr = ssh.run(
        "microk8s ctr image import /tmp/djb-deploy-image.tar",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to import image: {stderr}")

    # Push to the microk8s registry so kubelet can pull it
    returncode, stdout, stderr = ssh.run(
        f"microk8s ctr image push --plain-http {image_tag}",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to push image to registry: {stderr}")

    # Cleanup
    ssh.run("rm -f /tmp/djb-deploy-image.tar")
    Path(tar_path).unlink(missing_ok=True)

    logger.done("Image pushed")


def _sync_project_to_remote(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
) -> Path:
    """Sync project files to remote server for building.

    Uses rsync with gitignore filtering for efficient transfer.
    Includes untracked files but excludes gitignored patterns.

    Args:
        runner: CmdRunner instance for executing commands.
        ssh: SSHClient for remote operations.
        djb_config: DjbConfig for project settings.

    Returns:
        Remote path where project was synced.
    """
    project_name = djb_config.project_name
    project_dir = djb_config.project_dir
    remote_build_dir = Path(f"/tmp/djb-build/{project_name}")

    logger.next("Syncing project to remote")

    # Create remote build directory
    ssh.run(f"mkdir -p {remote_build_dir}")

    # Build rsync command with gitignore filtering
    # Note: Order matters - excludes must come before includes for nested paths
    rsync_cmd = [
        "rsync",
        "-avz",
        "--delete",  # Remove files on remote that don't exist locally
        "--exclude=.git",  # Always exclude any .git directories first
        "--include=djb/",  # Include djb directory (may be gitignored but needed for build)
        "--include=djb/**",  # Include all contents of djb
        "--filter=:- .gitignore",  # Read .gitignore and exclude matching patterns
        "-e",
        f"ssh -p {ssh.port}",
        f"{project_dir}/",
        f"{ssh.host}:{remote_build_dir}/",
    ]

    runner.run(
        rsync_cmd,
        label="Syncing files",
        fail_msg=click.ClickException("Failed to sync files to remote"),
        show_output=True,
    )

    logger.done("Project synced")
    return remote_build_dir


def _build_container_remote(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
    commit_sha: str,
    buildpack_image: str,
    registry_host: str = "localhost:32000",
) -> str:
    """Build container image on remote server (native x86_64).

    Builds directly on the target server, avoiding QEMU emulation overhead
    when building on ARM Macs for x86_64 servers.

    Args:
        runner: CmdRunner instance for executing commands.
        ssh: SSHClient for remote operations.
        djb_config: DjbConfig for project settings.
        commit_sha: Git commit SHA for tagging.
        buildpack_image: Pre-built buildpack chain image to use as base.
        registry_host: Registry host:port for tagging.

    Returns:
        The full image tag.
    """
    project_name = djb_config.project_name
    managed_dockerfile = djb_config.k8s.backend.managed_dockerfile

    image_tag = f"{registry_host}/{project_name}:{commit_sha}"

    # Sync project files to remote
    remote_build_dir = _sync_project_to_remote(runner, ssh, djb_config)

    logger.next(f"Building container on remote: {image_tag}")

    # Resolve Dockerfile (check if exists on remote)
    dockerfile_rel = "deployment/k8s/backend/Dockerfile"
    dockerfile_j2_rel = "deployment/k8s/backend/Dockerfile.j2"

    # Check what exists on remote
    returncode, _, _ = ssh.run(f"test -f {remote_build_dir}/{dockerfile_j2_rel}")
    has_template = returncode == 0
    returncode, _, _ = ssh.run(f"test -f {remote_build_dir}/{dockerfile_rel}")
    has_dockerfile = returncode == 0

    if has_template:
        # Render the template on remote using Python
        render_script = f"""
import sys
sys.path.insert(0, "{remote_build_dir}")
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

template_path = Path("{remote_build_dir}/{dockerfile_j2_rel}")
env = Environment(loader=FileSystemLoader(str(template_path.parent)), trim_blocks=True, lstrip_blocks=True)
template = env.get_template(template_path.name)

# Simple config object for template
class Config:
    project_name = "{project_name}"
djb_config = Config()

rendered = template.render(djb_config=djb_config)
output_path = template_path.parent / "Dockerfile"
output_path.write_text(rendered)
print(f"Rendered: {{output_path}}")
"""
        returncode, stdout, stderr = ssh.run(f"python3 -c '{render_script}'")
        if returncode != 0:
            raise click.ClickException(f"Failed to render Dockerfile template: {stderr}")
        dockerfile_path = f"{remote_build_dir}/{dockerfile_rel}"
    elif has_dockerfile:
        dockerfile_path = f"{remote_build_dir}/{dockerfile_rel}"
    elif managed_dockerfile:
        # Copy djb template to remote (would need to be synced with project)
        raise click.ClickException(
            "No Dockerfile found on remote. Please ensure deployment/k8s/backend/Dockerfile "
            "or Dockerfile.j2 exists in your project."
        )
    else:
        raise click.ClickException(
            "Dockerfile not found and k8s.backend.managed_dockerfile is False.\n"
            "Either create deployment/k8s/backend/Dockerfile.j2 manually,\n"
            "or set managed_dockerfile = true in .djb/project.toml [k8s.backend]."
        )

    # Build on remote - native x86_64, no QEMU needed
    build_cmd = (
        f"cd {remote_build_dir} && "
        f"docker build --build-arg BUILDPACK_IMAGE={buildpack_image} "
        f"-f {dockerfile_path} -t {image_tag} ."
    )
    returncode, stdout, stderr = ssh.run(build_cmd, timeout=600)
    if returncode != 0:
        raise click.ClickException(f"Failed to build container on remote: {stderr}")

    logger.done("Container built on remote")

    # Import to containerd and push to registry
    logger.next("Pushing to registry")

    # Save and import to containerd
    returncode, _, stderr = ssh.run(
        f"docker save {image_tag} | microk8s ctr image import -",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to import image to containerd: {stderr}")

    # Push to microk8s registry
    returncode, _, stderr = ssh.run(
        f"microk8s ctr image push --plain-http {image_tag}",
        timeout=300,
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to push image to registry: {stderr}")

    logger.done("Image pushed to registry")

    # Cleanup remote build dir
    ssh.run(f"rm -rf {remote_build_dir}")

    return image_tag


def _sync_secrets(
    runner: CmdRunner,
    ssh: SSHClient,
    djb_config: DjbConfig,
) -> dict[str, str] | None:
    """Sync secrets from djb secrets to K8s cluster.

    Returns:
        The secrets dict if loaded, None if no secrets.
    """
    logger.next("Syncing secrets")

    try:
        # Load secrets for production mode (SecretsManager handles GPG-protected keys)
        manager = SecretsManager(runner, djb_config.project_dir)
        secrets = manager.load_for_mode(Mode.PRODUCTION)
        if not secrets:
            logger.skip("No secrets to sync")
            return None
    except Exception as e:
        logger.warning(f"Failed to load secrets: {e}")
        logger.skip("Secrets sync skipped")
        return None

    # Generate K8s secret manifest
    secrets_ctx = SecretsCtx(secrets=secrets)
    generator = K8sManifestGenerator()
    secret_manifest = generator.render("secrets.yaml.j2", djb_config, secrets_ctx)

    # Apply via kubectl (escape single quotes for shell)
    escaped_manifest = secret_manifest.replace("'", "'\"'\"'")
    returncode, stdout, stderr = ssh.run(
        f"echo '{escaped_manifest}' | microk8s kubectl apply -f -",
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to apply secrets: {stderr}")

    logger.done("Secrets synced")
    return secrets


def _apply_manifests(
    ssh: SSHClient,
    djb_config: DjbConfig,
    image_tag: str,
    has_secrets: bool = False,
    has_database: bool = True,
    env_vars: dict[str, str] | None = None,
) -> None:
    """Apply all K8s manifests to the cluster."""
    logger.next("Applying manifests")

    deployment_ctx = DeploymentCtx(
        image=image_tag,
        has_secrets=has_secrets,
        has_database=has_database,
        env_vars=env_vars or {},
    )
    database_ctx = DatabaseCtx() if has_database else None

    generator = K8sManifestGenerator()
    manifests = generator.render_all(
        djb_config,
        deployment=deployment_ctx,
        database=database_ctx,
    )

    # Apply in order: namespace, database, secrets, deployment, service, ingress
    order = [
        "namespace.yaml",
        "cnpg-cluster.yaml",
        "secrets.yaml",
        "deployment.yaml",
        "service.yaml",
        "ingress.yaml",
    ]

    for manifest_name in order:
        if manifest_name not in manifests:
            continue

        manifest_content = manifests[manifest_name]
        logger.info(f"  Applying {manifest_name}...")

        # Escape single quotes for shell
        escaped_content = manifest_content.replace("'", "'\"'\"'")
        returncode, _, stderr = ssh.run(
            f"echo '{escaped_content}' | microk8s kubectl apply -f -",
        )
        if returncode != 0:
            raise click.ClickException(f"Failed to apply {manifest_name}: {stderr}")

    logger.done("Manifests applied")


def _wait_for_rollout(
    ssh: SSHClient,
    project_name: str,
    timeout: int = 300,
) -> None:
    """Wait for the deployment rollout to complete."""
    logger.next("Waiting for rollout")

    returncode, stdout, stderr = ssh.run(
        f"microk8s kubectl rollout status deployment/{project_name} "
        f"-n {project_name} --timeout={timeout}s",
        timeout=timeout + 30,
    )

    if returncode != 0:
        raise click.ClickException(f"Rollout failed: {stderr}")

    logger.done("Rollout complete")


def _run_migrations(
    ssh: SSHClient,
    djb_config: DjbConfig,
    image_tag: str,
    has_secrets: bool = False,
    env_vars: dict[str, str] | None = None,
) -> None:
    """Run database migrations as a K8s Job."""
    logger.next("Running migrations")

    migration_ctx = MigrationCtx(
        image=image_tag,
        has_secrets=has_secrets,
        env_vars=env_vars or {},
    )
    generator = K8sManifestGenerator()
    job_manifest = generator.render("migration-job.yaml.j2", djb_config, migration_ctx)

    # Delete any existing migration job with the same name
    project_name = djb_config.project_name
    job_name = f"{project_name}-migrate-{image_tag.split(':')[-1][:8]}"
    ssh.run(
        f"microk8s kubectl delete job {job_name} -n {project_name} --ignore-not-found",
    )

    # Apply the migration job
    # Escape single quotes for shell
    escaped_manifest = job_manifest.replace("'", "'\"'\"'")
    returncode, _, stderr = ssh.run(
        f"echo '{escaped_manifest}' | microk8s kubectl apply -f -",
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to create migration job: {stderr}")

    # Wait for job to complete
    returncode, _, stderr = ssh.run(
        f"microk8s kubectl wait --for=condition=complete job/{job_name} "
        f"-n {project_name} --timeout=300s",
        timeout=330,
    )

    if returncode != 0:
        # Get job logs for debugging
        ssh.run(
            f"microk8s kubectl logs job/{job_name} -n {project_name}",
        )
        raise click.ClickException(f"Migration failed: {stderr}")

    logger.done("Migrations complete")


def _tag_deployment(runner: CmdRunner, commit_sha: str) -> None:
    """Tag the deployment in git."""
    tag_name = f"deploy-k8s-{commit_sha}"

    result = runner.run(
        ["git", "tag", "-f", tag_name],
        quiet=True,
    )

    if result.returncode == 0:
        logger.info(f"Tagged as {tag_name}")


def _ensure_domain_configured(ctx: click.Context, djb_config: DjbConfig) -> None:
    """Ensure at least one domain is configured for K8s deployment.

    If no domains exist, prompts the user to add one. This is a noop if
    domains are already configured (like beachresort.me).

    Args:
        ctx: Click context for invoking subcommands.
        djb_config: DjbConfig with domain configuration.
    """
    domains = djb_config.k8s.domain_names
    if domains:
        # Domains already configured, check if any are eligible for K8s
        cloudflare_domains = [
            d for d, cfg in domains.items() if cfg.manager == DomainNameManager.CLOUDFLARE
        ]
        if cloudflare_domains:
            logger.debug(f"Using configured domains: {', '.join(cloudflare_domains)}")
            return

        # Has domains but none managed by cloudflare
        logger.warning("No Cloudflare-managed domains configured for K8s deployment")
        logger.info("  Hint: Add a domain with: djb domain add example.com --manager cloudflare")
        return

    # No domains configured - prompt to add one
    logger.next("No domains configured for K8s deployment")
    if click.confirm("Would you like to add a domain now?"):
        # Invoke domain init
        ctx.invoke(domain_init)
    else:
        logger.warning("Skipping domain configuration")
        logger.info("  Add later with: djb domain add example.com --manager cloudflare")


def _sync_domain_dns(cli_ctx: "CliK8sContext") -> None:
    """Sync DNS records for all configured domains.

    Creates/updates Cloudflare A records pointing to the server IP.
    """
    domains = cli_ctx.config.k8s.domain_names
    cloudflare_domains = [
        d for d, cfg in domains.items() if cfg.manager == DomainNameManager.CLOUDFLARE
    ]

    if not cloudflare_domains:
        logger.debug("No Cloudflare-managed domains to sync")
        return

    _sync_k8s_domains(cli_ctx, dry_run=False)


def deploy_k8s(ctx: click.Context, k8s_ctx: "CliK8sContext") -> None:
    """Execute the K8s deployment workflow.

    This is called from the k8s command group when no subcommand is specified.

    Args:
        ctx: Click context for invoking subcommands.
        k8s_ctx: K8s CLI context with deployment options.
    """
    if k8s_ctx.host is None:
        raise click.ClickException("No host specified for deployment")

    # Create runner from context (CliK8sContext extends CliContext)
    runner = k8s_ctx.runner

    _, _, _, djb_config = _get_project_info(k8s_ctx)
    project_name = djb_config.project_name
    commit_sha = _get_git_commit_sha(runner)

    logger.info(f"Deploying {project_name} to {k8s_ctx.host}:{k8s_ctx.port}")

    # Ensure domain is configured (noop if already set up)
    _ensure_domain_configured(ctx, djb_config)

    # Create SSH client
    try:
        ssh = SSHClient(
            host=k8s_ctx.host,
            cmd_runner=runner,
            port=k8s_ctx.port,
            key_path=k8s_ctx.ssh_key,
        )
    except SSHError as e:
        raise click.ClickException(f"SSH connection failed: {e}")

    # Pre-flight checks
    _verify_microk8s_ready(ssh)

    # Build buildpack chain and container
    if not k8s_ctx.skip_build:
        buildpacks = djb_config.k8s.backend.buildpacks
        if not buildpacks:
            raise click.ClickException(
                "No buildpacks configured.\n"
                "Add buildpacks to .djb/project.toml under [k8s.backend]"
            )

        if djb_config.k8s.backend.remote_build:
            # Build buildpack chain on remote server
            logger.next("Building buildpack chain on remote")
            logger.info(f"Buildpacks: {' -> '.join(buildpacks)}")
            buildpack_chain = RemoteBuildpackChain(
                registry="localhost:32000",
                ssh=ssh,
                pyproject_path=djb_config.project_dir / "pyproject.toml",
            )
            buildpack_image = buildpack_chain.build(buildpacks)
            logger.done(f"Buildpack chain ready: {buildpack_image}")

            # Build app container on remote server (native x86_64, no QEMU)
            image_tag = _build_container_remote(
                runner, ssh, djb_config, commit_sha, buildpack_image
            )
        else:
            # Build buildpack chain locally
            logger.next("Building buildpack chain locally")
            logger.info(f"Buildpacks: {' -> '.join(buildpacks)}")
            buildpack_chain = LocalBuildpackChain(
                registry="localhost:32000",
                runner=runner,
                pyproject_path=djb_config.project_dir / "pyproject.toml",
            )
            buildpack_image = buildpack_chain.build(buildpacks)
            logger.done(f"Buildpack chain ready: {buildpack_image}")

            # Build locally and transfer (uses QEMU on ARM Macs)
            image_tag = _build_container(runner, djb_config, commit_sha, buildpack_image)
            _push_to_registry(runner, ssh, image_tag)
    else:
        image_tag = f"localhost:32000/{project_name}:{commit_sha}"
        logger.skip("Container build (--skip-build)")

    # Sync secrets (returns secrets dict if any exist)
    has_secrets = False
    if not k8s_ctx.skip_secrets:
        secrets = _sync_secrets(runner, ssh, djb_config)
        has_secrets = secrets is not None
    else:
        logger.skip("Secrets sync (--skip-secrets)")

    # Build environment variables for K8s deployment and migrations
    env_vars: dict[str, str] = {}
    # DJB_DOMAINS for ALLOWED_HOSTS configuration
    if domains := ",".join(djb_config.domain_names_list):
        env_vars["DJB_DOMAINS"] = domains
    # DJB_INTERNAL_HOST for K8s health probe Host header matching
    env_vars["DJB_INTERNAL_HOST"] = djb_config.project_name

    # Apply manifests
    _apply_manifests(ssh, djb_config, image_tag, has_secrets=has_secrets, env_vars=env_vars)

    # Wait for rollout
    _wait_for_rollout(ssh, project_name)

    # Run migrations
    if not k8s_ctx.skip_migrate:
        _run_migrations(ssh, djb_config, image_tag, has_secrets=has_secrets, env_vars=env_vars)
    else:
        logger.skip("Migrations (--skip-migrate)")

    # Tag deployment
    _tag_deployment(runner, commit_sha)

    # Sync DNS records for domains
    _sync_domain_dns(k8s_ctx)

    # Done
    logger.note()
    logger.done("Deployment complete!")
    for domain in djb_config.k8s.domain_names:
        logger.info(f"  URL: https://{domain}")
    logger.note()
