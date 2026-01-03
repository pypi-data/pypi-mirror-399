"""Shared fixtures for djb CLI E2E tests.

See __init__.py for the full list of available fixtures and utilities.

Key Difference from Unit Tests:
===============================

E2E tests use the `project_dir` fixture (which defaults to tmp_path) to create
real project directories. The `djb_config` fixture here resolves config from
the actual project_dir, reading pyproject.toml and .djb/*.toml files.

Use `make_config_file` to create .djb/local.toml and .djb/project.toml:
    make_config_file({"seed_command": "myapp:seed"}, config_type="project")

Unit tests (cli/tests/*.py) should prefer patching over real files.
E2E tests should use real project structures.

Fixture Layering:
- This conftest inherits from cli/tests/conftest.py (clear_config_cache, make_cli_runner, etc.)
- E2E-specific fixtures are in fixtures/*.py modules

Fixtures are organized into focused modules under fixtures/:
- prerequisites.py: Tool availability checks (require_gpg, require_age, etc.)
- cli.py: CLI runner setup (make_cli_runner, logging/config fixtures)
- environment.py: Environment isolation (gpg_home, age_key_dir, etc.)
- project.py: Project structure (project_dir, pyproject_dir_with_git, make_config_file, etc.)
- database.py: PostgreSQL fixtures (make_pg_test_database)
- mocks.py: External service mocking (mock_heroku_cli, mock_pypi_publish)
- git.py: Git repository fixtures (make_project_with_git_repo, make_project_with_git_repo_with_commits,
           make_pyproject_toml_with_git_repo, make_project_with_editable_djb_repo)

See fixtures/__init__.py for the full list of exports.

Environment Isolation:
- GPG: Uses --homedir or GNUPGHOME to avoid touching ~/.gnupg
- Age: Keys generated in tmp_path, never ~/.age
- SOPS: Uses --config flag and SOPS_AGE_KEY_FILE env var
- PostgreSQL: Creates unique test databases, cleaned up after tests
- Git: Initializes repos in tmp_path with test-specific identity

Requirements:
- GPG must be installed (brew install gnupg)
- age must be installed (brew install age)
- SOPS must be installed (brew install sops)
- PostgreSQL must be running locally

Run with: pytest (add --no-e2e to skip)
"""

from __future__ import annotations

# Import all fixtures from the fixtures package
# Note: Unit test fixtures are inherited from parent conftest (cli/tests/conftest.py)
from djb.cli.tests.e2e.fixtures import (
    # Prerequisites
    check_age_installed,
    check_postgres_available,
    check_sops_installed,
    require_age,
    require_gpg,
    require_postgres,
    require_sops,
    # CLI
    configure_logging,
    make_cli_runner,
    # Environment
    gpg_home,
    TEST_PASSPHRASE,
    TEST_SECRET_VALUE,
    # Project
    age_key_dir,
    django_project,
    deploy_project,
    deps_project,
    djb_package_dir,
    djb_project_with_src,
    health_project,
    host_project,
    k8s_project,
    make_cmd_runner,
    project_with_djb,
    DJB_PYPROJECT_CONTENT,
    EDITABLE_PYPROJECT_TEMPLATE,
    make_config_file,
    make_editable_pyproject,
    project_dir,
    project_with_editable_djb,
    pyproject_dir_with_git,
    pyproject_dir_with_git_with_secrets,
    secrets_dir,
    setup_sops_config,
    # Database
    make_pg_test_database,
    # Mocks
    mock_cloudflare_provider,
    mock_heroku_cli,
    mock_hetzner_provider,
    mock_pypi_publish,
    # Git
    make_project_with_editable_djb_repo,
    make_project_with_git_repo,
    make_project_with_git_repo_with_commits,
    make_pyproject_toml_with_git_repo,
)

# Re-export shared fixtures from djb.testing.fixtures
from djb.testing.fixtures import alice_key, bob_key, make_age_key

# Re-export for pytest discovery
__all__ = [
    # Helper functions
    "check_age_installed",
    "check_sops_installed",
    "check_postgres_available",
    # Prerequisites
    "require_gpg",
    "require_age",
    "require_sops",
    "require_postgres",
    # CLI
    "configure_logging",
    "make_cli_runner",
    # Environment
    "gpg_home",
    "TEST_PASSPHRASE",
    "TEST_SECRET_VALUE",
    # Project
    "age_key_dir",
    "djb_project_with_src",
    "k8s_project",
    "make_cmd_runner",
    "project_with_djb",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_config_file",
    "make_editable_pyproject",
    "project_dir",
    "project_with_editable_djb",
    "pyproject_dir_with_git",
    "pyproject_dir_with_git_with_secrets",
    "secrets_dir",
    "setup_sops_config",
    # Database
    "make_pg_test_database",
    # Mocks
    "mock_cloudflare_provider",
    "mock_heroku_cli",
    "mock_hetzner_provider",
    "mock_pypi_publish",
    # Git
    "make_project_with_editable_djb_repo",
    "make_project_with_git_repo",
    "make_project_with_git_repo_with_commits",
    "make_pyproject_toml_with_git_repo",
    # Age keys (re-exported from djb.testing.fixtures)
    "make_age_key",
    "alice_key",
    "bob_key",
]
