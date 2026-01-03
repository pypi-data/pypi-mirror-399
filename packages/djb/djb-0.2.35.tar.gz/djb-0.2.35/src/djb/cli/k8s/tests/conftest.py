"""Shared fixtures for deploy_k8s tests.

Provides common fixtures for testing K8s deployment commands.
"""

from __future__ import annotations

from djb.testing.fixtures import make_cli_runner, make_cmd_runner

__all__ = ["make_cli_runner", "make_cmd_runner"]
