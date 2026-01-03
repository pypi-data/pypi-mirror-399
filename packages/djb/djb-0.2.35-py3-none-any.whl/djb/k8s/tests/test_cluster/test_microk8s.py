"""Tests for Microk8sProvider.

These tests mock CmdRunner to avoid requiring microk8s to be installed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from djb.k8s.cluster import Microk8sProvider, SSHConfig
from djb.k8s.cluster.provider import (
    ClusterAddonError,
    ClusterNotFoundError,
    ClusterProvisionError,
)


class TestMicrok8sProviderProperties:
    """Tests for Microk8sProvider properties."""

    def test_name(self, mock_cmd_runner) -> None:
        """Test name property."""
        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.name == "microk8s"

    def test_registry_address(self, mock_cmd_runner) -> None:
        """Test registry_address property."""
        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.registry_address == "localhost:32000"

    def test_is_local_without_ssh(self, mock_cmd_runner) -> None:
        """Test is_local returns True without SSH config."""
        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.is_local is True

    def test_is_local_with_ssh(self, mock_cmd_runner) -> None:
        """Test is_local returns False with SSH config."""
        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(mock_cmd_runner, ssh_config=ssh_config)
        assert provider.is_local is False


class TestMicrok8sProviderLocal:
    """Tests for local Microk8sProvider operations."""

    def test_exists_true(self, mock_cmd_runner) -> None:
        """Test exists returns True when microk8s is installed."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.exists("cluster") is True

    def test_exists_false(self, mock_cmd_runner) -> None:
        """Test exists returns False when microk8s is not installed."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")

        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.exists("cluster") is False

    def test_is_running_true(self, mock_cmd_runner) -> None:
        """Test is_running returns True when microk8s is running."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=0, stdout="microk8s is running", stderr=""
        )

        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.is_running("cluster") is True

    def test_is_running_false(self, mock_cmd_runner) -> None:
        """Test is_running returns False when microk8s is not running."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=0, stdout="microk8s is not running", stderr=""
        )

        provider = Microk8sProvider(mock_cmd_runner)
        assert provider.is_running("cluster") is False

    def test_create_installs_microk8s(self, mock_cmd_runner) -> None:
        """Test create installs microk8s via snap."""
        mock_cmd_runner.run.side_effect = [
            Mock(returncode=1, stdout="", stderr=""),  # which microk8s (not installed)
            Mock(returncode=0, stdout="", stderr=""),  # snap install
            Mock(returncode=0, stdout="microk8s is running", stderr=""),  # status
        ]

        provider = Microk8sProvider(mock_cmd_runner)
        provider.create("cluster")

        # Verify snap install was called
        calls = mock_cmd_runner.run.call_args_list
        assert any("snap install" in str(call) for call in calls)

    def test_create_when_already_running(self, mock_cmd_runner) -> None:
        """Test create does nothing when microk8s is already running."""
        mock_cmd_runner.run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # which microk8s (installed)
            Mock(returncode=0, stdout="microk8s is running", stderr=""),  # status
        ]

        provider = Microk8sProvider(mock_cmd_runner)
        provider.create("cluster")

        # Should only check existence and status, not install
        assert mock_cmd_runner.run.call_count == 2

    def test_enable_addons(self, mock_cmd_runner) -> None:
        """Test enabling addons."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

        provider = Microk8sProvider(mock_cmd_runner)
        provider.enable_addons("cluster", ["dns", "storage", "registry"])

        # Verify enable was called for each addon
        calls = mock_cmd_runner.run.call_args_list
        assert len(calls) == 3
        for call, addon in zip(calls, ["dns", "storage", "registry"]):
            assert addon in str(call)

    def test_enable_addons_failure(self, mock_cmd_runner) -> None:
        """Test addon enablement failure raises error."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="addon failed")

        provider = Microk8sProvider(mock_cmd_runner)
        with pytest.raises(ClusterAddonError):
            provider.enable_addons("cluster", ["dns"])

    def test_get_kubeconfig(self, mock_cmd_runner) -> None:
        """Test getting kubeconfig."""
        kubeconfig = "apiVersion: v1\nclusters: []"
        mock_cmd_runner.run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # which microk8s
            Mock(returncode=0, stdout=kubeconfig, stderr=""),  # config
        ]

        provider = Microk8sProvider(mock_cmd_runner)
        result = provider.get_kubeconfig("cluster")
        assert result == kubeconfig

    def test_get_kubeconfig_not_installed(self, mock_cmd_runner) -> None:
        """Test get_kubeconfig when not installed."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")

        provider = Microk8sProvider(mock_cmd_runner)
        with pytest.raises(ClusterNotFoundError):
            provider.get_kubeconfig("cluster")

    def test_kubectl(self, mock_cmd_runner) -> None:
        """Test running kubectl command."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="pods list", stderr="")

        provider = Microk8sProvider(mock_cmd_runner)
        returncode, stdout, stderr = provider.kubectl("cluster", "get", "pods")

        assert returncode == 0
        assert stdout == "pods list"
        # Verify microk8s kubectl was used
        call_args = mock_cmd_runner.run.call_args
        cmd = call_args[0][0]  # First positional arg
        assert "microk8s kubectl" in cmd

    def test_delete(self, mock_cmd_runner) -> None:
        """Test deleting microk8s."""
        mock_cmd_runner.run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # which microk8s
            Mock(returncode=0, stdout="", stderr=""),  # snap remove
        ]

        provider = Microk8sProvider(mock_cmd_runner)
        provider.delete("cluster")

        # Verify snap remove was called
        calls = mock_cmd_runner.run.call_args_list
        assert any("snap remove" in str(call) for call in calls)


class TestMicrok8sProviderRemote:
    """Tests for remote Microk8sProvider operations via SSH."""

    @patch("djb.k8s.cluster.microk8s.Microk8sProvider._get_ssh_client")
    def test_exists_via_ssh(self, mock_get_ssh: MagicMock, mock_cmd_runner) -> None:
        """Test exists check via SSH."""
        mock_ssh = MagicMock()
        mock_ssh.run.return_value = (0, "/snap/bin/microk8s", "")
        mock_get_ssh.return_value = mock_ssh

        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(mock_cmd_runner, ssh_config=ssh_config)
        assert provider.exists("cluster") is True

        # Verify SSH was used
        mock_ssh.run.assert_called()

    @patch("djb.k8s.cluster.microk8s.Microk8sProvider._get_ssh_client")
    def test_is_running_via_ssh(self, mock_get_ssh: MagicMock, mock_cmd_runner) -> None:
        """Test is_running via SSH."""
        mock_ssh = MagicMock()
        mock_ssh.run.return_value = (0, "microk8s is running", "")
        mock_get_ssh.return_value = mock_ssh

        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(mock_cmd_runner, ssh_config=ssh_config)
        assert provider.is_running("cluster") is True

    @patch("djb.k8s.cluster.microk8s.Microk8sProvider._get_ssh_client")
    def test_enable_addons_via_ssh(self, mock_get_ssh: MagicMock, mock_cmd_runner) -> None:
        """Test enabling addons via SSH."""
        mock_ssh = MagicMock()
        mock_ssh.run.return_value = (0, "", "")
        mock_get_ssh.return_value = mock_ssh

        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(mock_cmd_runner, ssh_config=ssh_config)
        provider.enable_addons("cluster", ["dns", "registry"])

        # Verify SSH was called for each addon
        assert mock_ssh.run.call_count == 2

    @patch("djb.k8s.cluster.microk8s.Microk8sProvider._get_ssh_client")
    def test_apply_manifests_via_ssh(self, mock_get_ssh: MagicMock, mock_cmd_runner) -> None:
        """Test applying manifests via SSH."""
        mock_ssh = MagicMock()
        mock_ssh.run.return_value = (0, "applied", "")
        mock_get_ssh.return_value = mock_ssh

        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(mock_cmd_runner, ssh_config=ssh_config)
        provider.apply_manifests(
            "cluster",
            {"namespace.yaml": "apiVersion: v1\nkind: Namespace"},
        )

        # Verify heredoc approach was used
        mock_ssh.run.assert_called()
        call_args = mock_ssh.run.call_args
        assert "kubectl apply" in str(call_args)
