"""djb init config - Configure project settings and sync git identity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import tomli_w
import yaml

from djb.cli.context import djb_pass_context
from djb.cli.init.shared import InitContext
from djb.config import DjbConfig, LOCAL, get_config_dir, get_config_path
from djb.config.acquisition import GitConfigSource, acquire_all_fields
from djb.core import CmdRunner
from djb.core.logging import get_logger

logger = get_logger(__name__)


def migrate_yaml_to_toml(project_root: Path) -> bool:
    """Migrate .djb/*.yaml files to .djb/*.toml format.

    Detects old YAML config files and converts them to TOML format,
    then removes the old YAML files.

    Args:
        project_root: Project root directory.

    Returns:
        True if any files were migrated, False otherwise.
    """
    config_dir = get_config_dir(project_root)
    if not config_dir.exists():
        return False

    migrated_any = False
    yaml_files = [
        ("local.yaml", "local.toml"),
        ("project.yaml", "project.toml"),
    ]

    for yaml_name, toml_name in yaml_files:
        yaml_path = config_dir / yaml_name
        toml_path = config_dir / toml_name

        if not yaml_path.exists():
            continue

        # Don't overwrite existing TOML files
        if toml_path.exists():
            logger.warning(f"Both {yaml_name} and {toml_name} exist, skipping migration")
            continue

        # Load YAML
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            logger.warning(f"Failed to parse {yaml_name}: {exc}")
            continue

        # Write TOML
        try:
            with open(toml_path, "wb") as f:
                tomli_w.dump(data, f)
        except (OSError, TypeError) as exc:
            logger.warning(f"Failed to write {toml_name}: {exc}")
            continue

        # Remove old YAML file
        yaml_path.unlink()
        logger.info(f"Migrated {yaml_name} -> {toml_name}")
        migrated_any = True

    return migrated_any


def _set_git_config(runner: CmdRunner, key: str, value: str) -> bool:
    """Set a value in git config (global)."""
    result = runner.run(["git", "config", "--global", key, value])
    return result.returncode == 0


def validate_project(project_root: Path) -> None:
    """Validate we're in a Python project with pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise click.ClickException(
            f"No pyproject.toml found in {project_root}. "
            "Run 'djb init' from your project root directory."
        )


def configure_all_fields(project_dir: Path, config: DjbConfig) -> dict[str, Any]:
    """Configure all config fields using the acquisition generator.

    Field order is determined by declaration order in DjbConfig.
    Acquirable fields are those with an acquire() method and prompt_text.

    Args:
        project_dir: Project root directory.
        config: Current DjbConfig instance.

    Returns:
        Dict of configured field values.
    """
    configured: dict[str, Any] = {}
    copied_from_git: list[str] = []

    logger.next("Configuring project settings")

    for field_name, result in acquire_all_fields(project_dir, config):
        configured[field_name] = result.value

        # Track git config sources for summary message
        if result.source_name == "git config":
            copied_from_git.append(field_name)

    # Summary message for git config copies
    if copied_from_git:
        logger.info(f"Copied {' and '.join(copied_from_git)} from git config")

    # Log config file location
    config_path = get_config_path(LOCAL, project_dir)
    if any(f in configured for f in ("name", "email")):
        logger.info(f"Config saved to: {config_path}")

    return configured


def sync_identity_to_git(runner: CmdRunner, config: DjbConfig) -> None:
    """Sync name/email from djb config to git global config if needed.

    If name/email are in djb config but not from git config, sync them
    so users don't have to configure git separately.

    Args:
        runner: CmdRunner instance for executing commands.
        config: Current DjbConfig instance.
    """
    for field_name in ("name", "email"):
        source = config.get_source(field_name)
        value = getattr(config, field_name, None)

        # Only sync if we have a value from djb config (not from git)
        if value and source is not None and source.is_explicit():
            git_key = "user.name" if field_name == "name" else "user.email"
            git_source = GitConfigSource(git_key)
            # Only sync if git config doesn't already have this value
            if git_source.get() != value:
                _set_git_config(runner, git_key, value)


@click.command("config")
@djb_pass_context(InitContext)
@click.pass_context
def config(ctx: click.Context, init_ctx: InitContext) -> None:
    """Configure project settings and sync git identity.

    Validates pyproject.toml exists, prompts for name/email if needed,
    and syncs identity to git global config.
    """
    djb_config = init_ctx.config
    project_dir = djb_config.project_dir

    runner = init_ctx.runner

    validate_project(project_dir)

    # Migrate YAML config files to TOML if needed
    migrate_yaml_to_toml(project_dir)

    logger.info("Configuring project settings")

    # Configure all fields using the acquisition generator
    configured = configure_all_fields(project_dir, djb_config)
    sync_identity_to_git(runner, djb_config)

    # Store results in context for other subcommands
    init_ctx.configured_values = configured
    init_ctx.user_name = configured.get("name")
    init_ctx.user_email = configured.get("email")
    init_ctx.project_name = configured.get("project_name", djb_config.project_name)
