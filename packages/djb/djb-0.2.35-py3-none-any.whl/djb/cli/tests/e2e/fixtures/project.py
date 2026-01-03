"""Project structure fixtures for E2E tests.

These fixtures create isolated project directories with secrets configuration.
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - invokes git directly to set up test repos
from collections.abc import Callable
from pathlib import Path
from typing import Literal, NamedTuple

import pytest
import tomli_w

from djb.cli.utils import CmdRunner
from djb.secrets import (
    SecretsManager,
    generate_age_key,
)
from djb.testing.fixtures import (
    DJB_PYPROJECT_CONTENT,
    EDITABLE_PYPROJECT_TEMPLATE,
    make_cmd_runner,
    make_editable_pyproject,
)

from djb.cli.tests.e2e.utils import (
    add_django_settings_from_startproject,
    add_frontend_package,
    add_python_package,
    create_pyproject_toml,
)


class ProjectWithSecrets(NamedTuple):
    """An isolated project directory with secrets configured."""

    project_dir: Path
    key_path: Path


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Empty project directory. djb should work in the simplest case."""
    return tmp_path


@pytest.fixture
def age_key_dir(project_dir: Path) -> Path:
    """Create an isolated .age directory for keys.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    age_dir = project_dir / ".age"
    age_dir.mkdir(mode=0o700)
    return age_dir


@pytest.fixture
def pyproject_dir_with_git(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Project with pyproject.toml and git initialized.

    Creates:
    - pyproject.toml with minimal config
    - Initialized git repo with test identity

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    # Create minimal pyproject.toml
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "test-project"\nversion = "0.1.0"\n'
        '\n[tool.djb]\nproject_name = "test-project"\n'
    )

    # Initialize git (no initial commit)
    make_project_with_git_repo(
        repo_path=project_dir,
        with_initial_commit=False,
    )

    return project_dir


@pytest.fixture
def pyproject_dir_with_git_with_secrets(
    pyproject_dir_with_git: Path, age_key_dir: Path, make_cmd_runner: CmdRunner
) -> ProjectWithSecrets:
    """Create an isolated project with secrets directory, age key, and encrypted secrets files.

    Creates:
    - secrets/ directory with .sops.yaml config
    - Encrypted development.yaml, staging.yaml, production.yaml files
    - Age key at age_key_dir/keys.txt

    Returns a ProjectWithSecrets named tuple.
    """
    # Create secrets directory
    secrets_dir = pyproject_dir_with_git / "secrets"
    secrets_dir.mkdir()

    # Generate age key
    key_path = age_key_dir / "keys.txt"
    public_key, _ = generate_age_key(make_cmd_runner, key_path)

    # Create encrypted secrets files for each environment
    manager = SecretsManager(make_cmd_runner, pyproject_dir_with_git, key_path=key_path)

    # Create .sops.yaml
    manager.save_config({public_key: "test@example.com"})

    for env in ["development", "staging", "production"]:
        # Create a simple secrets template
        template = {
            "django_secret_key": f"test-secret-key-for-{env}",
            "database_url": f"postgres://localhost/{env}_db",
        }
        # Explicitly pass public_keys to avoid config lookup (which triggers cache issues)
        manager.save_secrets(env, template, public_keys=[public_key])

    return ProjectWithSecrets(pyproject_dir_with_git, key_path)


# DJB_PYPROJECT_CONTENT, EDITABLE_PYPROJECT_TEMPLATE, and make_editable_pyproject
# are imported from djb.testing.fixtures


@pytest.fixture
def project_with_djb(project_dir: Path) -> Path:
    """Create a minimal djb project directory.

    Creates project_dir/djb/ with a valid pyproject.toml.
    Returns the djb directory path.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    djb_dir = project_dir / "djb"
    djb_dir.mkdir()
    (djb_dir / "pyproject.toml").write_text(DJB_PYPROJECT_CONTENT)
    return djb_dir


@pytest.fixture
def djb_project_with_src(project_with_djb: Path) -> Path:
    """Create a djb package with src structure for version testing.

    Builds on project_with_djb fixture, adding:
    - Version in pyproject.toml
    - src/djb/_version.py with __version__

    Uses project_with_djb for fixture layering.
    """
    # Update pyproject.toml with version and dependencies
    pyproject = project_with_djb / "pyproject.toml"
    pyproject.write_text(
        """\
[project]
name = "djb"
version = "0.2.0"
dependencies = ["click>=8.0"]
"""
    )

    # Create src/djb/_version.py (djb-specific structure)
    src_dir = project_with_djb / "src" / "djb"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text("")
    (src_dir / "_version.py").write_text('__version__ = "0.2.0"\n')

    return project_with_djb


@pytest.fixture
def project_with_editable_djb(project_dir: Path, project_with_djb: Path) -> Path:
    """Create a host project with djb in editable mode.

    Creates:
    - project_dir/djb/ (via project_with_djb fixture)
    - project_dir/pyproject.toml with [tool.uv.sources] pointing to djb

    Returns the host project path (project_dir).

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(make_editable_pyproject("djb"))
    return project_dir


@pytest.fixture
def make_config_file(project_dir: Path) -> Callable[..., Path]:
    """Factory for creating config files in .djb directory.

    Returns a factory function that creates config files with the given content.

    Args:
        content: YAML content to write to the config file
        config_type: Either "local" or "project" (default: "local")

    Returns:
        Path to the created config file

    Usage:
        def test_something(make_config_file):
            config_path = make_config_file({"name": "John", "email": "john@example.com"})
            # Creates .djb/local.toml with the given content

            # For project config:
            config_path = make_config_file({"seed_command": "myapp.cli:seed"}, config_type="project")
            # Creates .djb/project.toml

            # You can also pass a TOML string:
            config_path = make_config_file('name = "John"')
    """
    config_dir = project_dir / ".djb"

    def _create(
        content: str | dict,
        config_type: Literal["local", "project"] = "local",
    ) -> Path:
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / f"{config_type}.toml"

        if isinstance(content, dict):
            with open(config_file, "wb") as f:
                tomli_w.dump(content, f)
        else:
            config_file.write_text(content)

        return config_file

    return _create


# =============================================================================
# Shared Project Fixtures
# =============================================================================


@pytest.fixture
def django_project(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Django project with settings via django-admin startproject.

    Creates:
    - pyproject.toml with minimal config
    - manage.py and myproject/ package (via startproject)
    - .gitignore (without .djb/local.toml for testing)
    - Initialized git repo with initial commit

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    create_pyproject_toml(project_dir, name="myproject")
    add_django_settings_from_startproject(project_dir)

    # Create .gitignore (without .djb/local.toml so we can test adding it)
    gitignore = project_dir / ".gitignore"
    gitignore.write_text("# Python\n*.pyc\n__pycache__/\n")

    # Initialize git and commit all content
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=True,
    )

    return project_dir


@pytest.fixture
def deploy_project(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Project with git repo and heroku remote for deployment tests.

    Creates:
    - pyproject.toml with minimal config
    - manage.py stub
    - Initialized git repo with heroku remote
    - Multiple commits for revert testing

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    create_pyproject_toml(project_dir, name="myproject")

    # Create manage.py (Django entrypoint stub)
    manage_py = project_dir / "manage.py"
    manage_py.write_text('#!/usr/bin/env python\nprint("manage.py")\n')

    # Initialize git and commit all content
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=True,
    )

    # Add heroku remote
    subprocess.run(
        [
            "git",
            "-C",
            str(project_dir),
            "remote",
            "add",
            "heroku",
            "https://git.heroku.com/myproject.git",
        ],
        capture_output=True,
    )

    # Add another commit for revert testing
    readme = project_dir / "README.md"
    readme.write_text("# My Project\n")
    subprocess.run(["git", "-C", str(project_dir), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(project_dir), "commit", "-m", "Add README"],
        capture_output=True,
    )

    return project_dir


@pytest.fixture
def health_project(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Project with Python package and frontend for health check tests.

    Creates:
    - pyproject.toml with minimal config
    - myproject/__init__.py (Python package)
    - frontend/ directory with package.json
    - Initialized git repo

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    create_pyproject_toml(project_dir, name="myproject")
    add_python_package(project_dir)
    add_frontend_package(project_dir, name="myproject-frontend")

    # Initialize git (no initial commit)
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=False,
    )

    return project_dir


@pytest.fixture
def deps_project(project_dir: Path) -> Path:
    """Project with dependencies for dependency refresh tests.

    Creates:
    - pyproject.toml with Django dependency
    - frontend/ directory with package.json containing scripts
    - .djb/local.toml with name and email config

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    create_pyproject_toml(
        project_dir,
        name="myproject",
        extra_content='dependencies = ["django>=4.0"]',
    )

    # Create frontend directory with custom package.json (scripts needed)
    frontend_dir = project_dir / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package.json").write_text(
        '{"name": "myproject", "scripts": {"refresh-deps": "echo ok"}}'
    )

    # Create djb config with required name and email
    config_dir = project_dir / ".djb"
    config_dir.mkdir()
    (config_dir / "local.toml").write_text('name = "Test User"\nemail = "test@example.com"\n')

    return project_dir


@pytest.fixture
def host_project(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Host project that depends on djb (for editable-djb tests).

    Creates:
    - pyproject.toml with djb dependency
    - Initialized git repo

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    (project_dir / "pyproject.toml").write_text(
        """\
[project]
name = "myproject"
version = "0.1.0"
dependencies = ["djb>=0.2.0"]

[tool.djb]
project_name = "myproject"
"""
    )

    # Initialize git (no initial commit)
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=False,
    )

    return project_dir


@pytest.fixture
def djb_package_dir(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """djb package directory (for editable-djb tests).

    Creates project_dir/djb/ with a valid djb pyproject.toml.
    Returns the djb directory path.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    djb_path = project_dir / "djb"
    djb_path.mkdir()

    (djb_path / "pyproject.toml").write_text(
        """\
[project]
name = "djb"
version = "0.2.0"
dependencies = ["click>=8.0"]
"""
    )

    # Initialize git (no initial commit)
    make_project_with_git_repo(
        repo_path=djb_path,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=False,
    )

    return djb_path


@pytest.fixture
def k8s_project(
    project_dir: Path,
    age_key_dir: Path,
    make_cmd_runner: CmdRunner,
    make_project_with_git_repo: Callable[..., Path],
) -> ProjectWithSecrets:
    """Project configured for K8s deployment with Hetzner.

    Creates:
    - pyproject.toml with project config
    - .djb/project.toml with hetzner, k8s, and cloudflare config
    - secrets/development.yaml with hetzner.api_token and cloudflare.api_token
    - Initialized git repo

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.

    Returns a ProjectWithSecrets named tuple with (project_dir, key_path).
    """
    create_pyproject_toml(project_dir, name="myproject")

    # Create .djb/project.toml with Hetzner/K8s/Cloudflare config
    djb_dir = project_dir / ".djb"
    djb_dir.mkdir()
    (djb_dir / "project.toml").write_text(
        """\
project_name = "myproject"

[hetzner]
default_server_type = "cx22"
default_location = "nbg1"
default_image = "ubuntu-24.04"

[k8s]
domains = ["example.com"]

[cloudflare]
auto_dns = true
ttl = 300
proxied = false
"""
    )

    # Set up secrets with API tokens
    secrets_dir = project_dir / "secrets"
    secrets_dir.mkdir()

    key_path = age_key_dir / "keys.txt"
    public_key, _ = generate_age_key(make_cmd_runner, key_path)

    manager = SecretsManager(make_cmd_runner, project_dir, key_path=key_path)
    manager.save_config({public_key: "test@example.com"})
    # Explicitly pass public_keys to avoid config lookup (which triggers cache issues)
    manager.save_secrets(
        "development",
        {
            "hetzner": {"api_token": "test-hetzner-token"},
            "cloudflare": {"api_token": "test-cloudflare-token"},
        },
        public_keys=[public_key],
    )

    # Initialize git and commit all content
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=True,
    )

    return ProjectWithSecrets(project_dir, key_path)
