"""CLI runner fixtures for E2E tests.

These fixtures provide Click test runners and logging setup.

Note: E2E tests pass --project-dir explicitly to CLI commands to specify
the project directory. This enables parallel test execution without
shared global state.

Shared fixtures re-exported:
    configure_logging - Initializes djb CLI logging system (session-scoped, autouse)
    make_cli_runner - Click CLI test runner (function-scoped)
"""

from __future__ import annotations

from djb.cli.tests import make_cli_runner
from djb.testing.fixtures import configure_logging

# Re-export for pytest to discover
__all__ = ["configure_logging", "make_cli_runner"]
