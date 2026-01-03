"""Unit tests for djb deploy k8s commands.

These tests don't require Docker and test command structure, help text,
and argument validation.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli


class TestDeployK8sLocal:
    """Tests for `djb deploy k8s local` subcommands (Skaffold-based)."""

    def test_local_help(self, make_cli_runner: CliRunner) -> None:
        """Test that local help is displayed."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "--help"])
        assert result.exit_code == 0
        assert "Manage local Kubernetes development with Skaffold" in result.output
        assert "cluster" in result.output
        assert "dev" in result.output
        assert "build" in result.output
        assert "shell" in result.output

    def test_cluster_help(self, make_cli_runner: CliRunner) -> None:
        """Test that cluster subcommand help is displayed."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "--help"])
        assert result.exit_code == 0
        assert "Manage local Kubernetes cluster lifecycle" in result.output
        assert "create" in result.output
        assert "delete" in result.output
        assert "status" in result.output

    def test_cluster_create_help(self, make_cli_runner: CliRunner) -> None:
        """Test cluster create command options."""
        result = make_cli_runner.invoke(
            djb_cli, ["deploy", "k8s", "local", "cluster", "create", "--help"]
        )
        assert result.exit_code == 0
        assert "--type" in result.output
        assert "k3d" in result.output
        assert "microk8s" in result.output

    def test_dev_help(self, make_cli_runner: CliRunner) -> None:
        """Test dev command options."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "dev", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output
        assert "--trigger" in result.output
        assert "notify" in result.output
        assert "polling" in result.output


class TestDeployK8sTerraform:
    """Tests for `djb deploy k8s terraform` command."""

    def test_terraform_help(self, make_cli_runner: CliRunner) -> None:
        """Test that terraform help is displayed."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "terraform", "--help"])
        assert result.exit_code == 0
        assert "Provision Kubernetes infrastructure" in result.output
        assert "--local" in result.output
        assert "--host" in result.output
        assert "--email" in result.output
        assert "--skip-tls" in result.output
        assert "--microk8s" in result.output

    def test_terraform_requires_local_or_host(self, make_cli_runner: CliRunner) -> None:
        """Test that terraform requires --local or --host option."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "terraform"])
        assert result.exit_code != 0
        assert "No host specified" in result.output
        assert "--local" in result.output

    def test_terraform_local_and_host_mutually_exclusive(self, make_cli_runner: CliRunner) -> None:
        """Test that --local and --host cannot be used together."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local", "--host", "root@localhost"],
        )
        assert result.exit_code != 0
        assert "Cannot use both" in result.output

    def test_terraform_requires_email_for_remote_tls(self, make_cli_runner: CliRunner) -> None:
        """Test that terraform requires email for TLS unless --skip-tls."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--host", "root@localhost"],
        )
        assert result.exit_code != 0
        assert "email" in result.output.lower() or "skip-tls" in result.output.lower()

    def test_terraform_hetzner_options(self, make_cli_runner: CliRunner) -> None:
        """Test that Hetzner-related options are in terraform help."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "terraform", "--help"])
        assert result.exit_code == 0
        assert "--provider" in result.output
        assert "hetzner" in result.output
        assert "--server-type" in result.output
        assert "--location" in result.output
        assert "--image" in result.output
        assert "--ssh-key-name" in result.output

    def test_terraform_local_and_hetzner_mutually_exclusive(
        self, make_cli_runner: CliRunner
    ) -> None:
        """Test that --local and --provider hetzner cannot be used together."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local", "--provider", "hetzner"],
        )
        assert result.exit_code != 0
        assert "Cannot use --local with --provider hetzner" in result.output

    def test_terraform_host_and_hetzner_mutually_exclusive(
        self, make_cli_runner: CliRunner
    ) -> None:
        """Test that --host and --provider hetzner cannot be used together."""
        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--host", "root@server", "--provider", "hetzner"],
        )
        assert result.exit_code != 0
        assert "Cannot use --host with --provider hetzner" in result.output


class TestDeployK8sMaterialize:
    """Tests for `djb deploy k8s materialize` command."""

    def test_materialize_help(self, make_cli_runner: CliRunner) -> None:
        """Test that materialize help is displayed."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize", "--help"])
        assert result.exit_code == 0
        assert "Create cloud VPS for K8s deployment" in result.output
        assert "--provider" in result.output
        assert "--create" in result.output
        assert "--server-type" in result.output
        assert "--location" in result.output
        assert "--image" in result.output
        assert "--ssh-key-name" in result.output

    def test_materialize_requires_provider(self, make_cli_runner: CliRunner) -> None:
        """Test that materialize requires --provider option."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_materialize_hetzner_provider(self, make_cli_runner: CliRunner) -> None:
        """Test that hetzner is a valid provider choice."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize", "--help"])
        assert result.exit_code == 0
        assert "hetzner" in result.output


class TestDeployK8sMainCommand:
    """Tests for `djb deploy k8s` main deployment command."""

    def test_k8s_help(self, make_cli_runner: CliRunner) -> None:
        """Test that k8s help is displayed."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "--help"])
        assert result.exit_code == 0
        assert "Deploy to Kubernetes" in result.output
        assert "--host" in result.output
        assert "--skip-build" in result.output
        assert "--skip-migrate" in result.output
        # Note: --domain was removed; domains are now configured via k8s.domain_names in config

    def test_k8s_without_host_triggers_auto_provisioning(self, make_cli_runner: CliRunner) -> None:
        """Test that deploy k8s without --host attempts auto-provisioning.

        When run from a djb project directory with Hetzner config, the command
        will attempt to auto-provision using the configured server. This test
        verifies that the auto-provisioning flow is triggered.
        """
        # Mock the auto-provisioning functions to verify they're called
        # without actually connecting to infrastructure
        with (
            patch(
                "djb.cli.k8s.k8s._ensure_server_materialized",
                return_value="root@test-server",
            ) as mock_materialize,
            patch("djb.cli.k8s.k8s._ensure_infrastructure_provisioned") as mock_provision,
            patch("djb.cli.k8s.k8s._ensure_dns_configured"),  # Avoid secrets loading
            patch("djb.cli.k8s.k8s._ensure_buildpacks_built"),  # Avoid buildpack building
            patch(
                "djb.cli.k8s.k8s.deploy_k8s",
                side_effect=Exception("Mock deploy error"),
            ),
        ):
            result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s"])

            # Verify auto-provisioning was triggered (not a "missing --host" error)
            assert result.exit_code != 0
            assert "Mock deploy error" in str(result.exception)

            # The auto-provisioning functions should have been called
            mock_materialize.assert_called_once()
            mock_provision.assert_called_once()

    def test_k8s_subcommands_available(self, make_cli_runner: CliRunner) -> None:
        """Test that subcommands are registered."""
        result = make_cli_runner.invoke(djb_cli, ["deploy", "k8s", "--help"])
        assert result.exit_code == 0
        assert "local" in result.output
        assert "materialize" in result.output
        assert "terraform" in result.output
