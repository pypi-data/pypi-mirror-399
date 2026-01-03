"""Tests for djb deploy k8s commands.

This package contains unit tests and E2E tests for Kubernetes deployment commands.

Test organization:
- Unit tests: test_*.py files in this directory
- E2E tests: e2e/ subdirectory (tests with real Docker containers)

Fixtures:
- make_cli_runner: Click test runner
- require_docker: Skip marker if Docker unavailable
- local_vps_container: Docker container with SSH for E2E testing
"""
