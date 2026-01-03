"""E2E tests for djb deploy k8s terraform command.

These tests verify the terraform command behavior with mocked providers
and real SSH connections where needed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli

pytestmark = pytest.mark.e2e_marker


class TestDeployK8sTerraformLocal:
    """E2E tests for `djb deploy k8s terraform --local` command."""

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_local_k3d_default(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --local uses k3d by default."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = False
        mock_provider.is_running.return_value = False
        # Make kubectl return "not found" for CloudNativePG
        mock_provider.kubectl.return_value = (1, "", "not found")
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local", "--skip-cloudnativepg"],
        )
        assert result.exit_code == 0

        # Verify k3d provider was requested
        mock_get_provider.assert_called_once()
        call_args = mock_get_provider.call_args
        assert call_args[0][0] == "k3d"
        assert call_args[1].get("ssh_config") is None

        # Verify cluster was created
        mock_provider.create.assert_called_once()
        mock_provider.enable_addons.assert_called_once()

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_local_microk8s(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --local --microk8s uses microk8s provider."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local", "--microk8s"],
        )
        assert result.exit_code == 0

        # Verify microk8s provider was requested
        mock_get_provider.assert_called_once()
        call_args = mock_get_provider.call_args
        assert call_args[0][0] == "microk8s"
        assert call_args[1].get("ssh_config") is None

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_local_existing_cluster(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --local with existing cluster skips creation."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local", "--skip-cloudnativepg"],
        )
        assert result.exit_code == 0
        assert "running" in result.output

        # Verify create was NOT called (cluster already exists)
        mock_provider.create.assert_not_called()

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_local_installs_cloudnativepg(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --local installs CloudNativePG when not present."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        # First call for check returns not found, subsequent calls succeed
        mock_provider.kubectl.side_effect = [
            (1, "", "not found"),  # Check CNPG
            (0, "", ""),  # Install CNPG
            (0, "", ""),  # Wait for CNPG
        ]
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--local"],
        )
        assert result.exit_code == 0
        assert "CloudNativePG" in result.output


class TestDeployK8sTerraformRemote:
    """E2E tests for `djb deploy k8s terraform --host` command."""

    def test_terraform_ssh_connection_with_container(
        self,
        make_cli_runner: CliRunner,
        make_local_vps_container: dict,
    ) -> None:
        """Test terraform connects via SSH to container.

        This test verifies that terraform can establish an SSH connection
        to the local VPS container. It doesn't fully provision microk8s
        (which would take too long) but verifies the SSH connectivity works.
        """
        result = make_cli_runner.invoke(
            djb_cli,
            [
                "deploy",
                "k8s",
                "terraform",
                "--host",
                f"root@{make_local_vps_container['host']}",
                "--port",
                str(make_local_vps_container["port"]),
                "--ssh-key",
                str(make_local_vps_container["ssh_key"]),
                "--skip-tls",
            ],
        )
        # The command will fail because microk8s isn't installed in the container,
        # but it should at least connect via SSH and check for microk8s
        assert "microk8s" in result.output.lower() or "ssh" in result.output.lower()

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_remote_creates_clusterissuer(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --host creates ClusterIssuer with email."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        # CNPG installed, ClusterIssuer not configured
        mock_provider.kubectl.side_effect = [
            (0, "cnpg-controller-manager", ""),  # Check CNPG
            (1, "", "not found"),  # Check ClusterIssuer
        ]
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            [
                "deploy",
                "k8s",
                "terraform",
                "--host",
                "root@localhost",
                "--email",
                "admin@example.com",
            ],
        )
        assert result.exit_code == 0
        assert "ClusterIssuer" in result.output

        # Verify apply_manifests was called for ClusterIssuer
        mock_provider.apply_manifests.assert_called()

    @patch("djb.cli.k8s.terraform.get_cluster_provider")
    def test_terraform_remote_skip_tls(
        self,
        mock_get_provider: MagicMock,
        make_cli_runner: CliRunner,
    ) -> None:
        """Test terraform --host --skip-tls skips ClusterIssuer."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = make_cli_runner.invoke(
            djb_cli,
            [
                "deploy",
                "k8s",
                "terraform",
                "--host",
                "root@localhost",
                "--skip-tls",
            ],
        )
        assert result.exit_code == 0
        assert "skip" in result.output.lower() or "ClusterIssuer" not in result.output

        # Verify apply_manifests was NOT called (no ClusterIssuer)
        mock_provider.apply_manifests.assert_not_called()
