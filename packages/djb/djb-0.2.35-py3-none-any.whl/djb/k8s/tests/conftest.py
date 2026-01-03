"""
Shared test fixtures for djb k8s tests.

Fixtures from djb.testing are imported for test usage.
"""

from djb.testing.fixtures import make_cli_ctx, mock_cli_ctx, make_cmd_runner, mock_cmd_runner

__all__ = ["make_cli_ctx", "mock_cli_ctx", "make_cmd_runner", "mock_cmd_runner"]
