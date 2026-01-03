"""
Microk8sProvider - Local or remote microk8s cluster implementation.

microk8s is a production-grade Kubernetes distribution from Canonical,
installed via snap. It provides:
- Production-like behavior
- Built-in addons (dns, storage, registry, ingress, cert-manager)
- Works both locally and on remote servers via SSH

This provider supports both local and remote operation:
- Local: Runs commands directly via subprocess
- Remote: Runs commands via SSH using SSHConfig
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from typing import TYPE_CHECKING

from djb.core import CmdTimeout
from djb.ssh import SSHClient, SSHError
from djb.k8s.cluster.provider import (
    ClusterAddonError,
    ClusterError,
    ClusterNotFoundError,
    ClusterProvisionError,
    SSHConfig,
)

if TYPE_CHECKING:
    from djb.core import CmdRunner


class Microk8sProvider:
    """Microk8s cluster provider - local or remote.

    Manages microk8s clusters for production-like Kubernetes environments.
    Can operate locally or remotely via SSH.

    Example (local):
        provider = Microk8sProvider(cmd_runner)
        provider.create("myapp")
        provider.enable_addons("myapp", ["dns", "storage", "registry"])

    Example (remote):
        ssh_config = SSHConfig(host="root@server")
        provider = Microk8sProvider(cmd_runner, ssh_config=ssh_config)
        provider.create("myapp")
    """

    # Timeouts in seconds
    CREATE_TIMEOUT = 300  # snap install can be slow
    ADDON_TIMEOUT = 120
    COMMAND_TIMEOUT = 60

    def __init__(self, cmd_runner: "CmdRunner", ssh_config: SSHConfig | None = None):
        """Initialize provider.

        Args:
            cmd_runner: Command runner instance for executing shell commands.
            ssh_config: SSH configuration for remote operation.
                        If None, operates locally.
        """
        self._cmd_runner = cmd_runner
        self._ssh_config = ssh_config
        self._ssh_client: SSHClient | None = None

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "microk8s"

    @property
    def registry_address(self) -> str:
        """Registry address for pushing images.

        microk8s registry runs on localhost:32000.
        For remote clusters, this needs SSH tunneling.
        """
        return "localhost:32000"

    @property
    def is_local(self) -> bool:
        """True if operating locally (no SSH config)."""
        return self._ssh_config is None

    def _get_ssh_client(self) -> SSHClient | None:
        """Get or create SSH client for remote operation."""
        if self._ssh_client is None and self._ssh_config is not None:
            self._ssh_client = SSHClient(
                host=self._ssh_config.host,
                cmd_runner=self._cmd_runner,
                port=self._ssh_config.port,
                key_path=self._ssh_config.key_path,
            )
        return self._ssh_client

    def _run_command(
        self,
        command: str,
        timeout: int | None = None,
        check: bool = True,
    ) -> tuple[int, str, str]:
        """Run a command locally or via SSH.

        Args:
            command: Command to execute.
            timeout: Command timeout in seconds.
            check: If True, raise on non-zero exit.

        Returns:
            Tuple of (returncode, stdout, stderr).

        Raises:
            ClusterError: If check=True and command fails.
        """
        timeout = timeout or self.COMMAND_TIMEOUT

        if self.is_local:
            # Local execution
            try:
                result = self._cmd_runner.run(command, shell=True, timeout=timeout)
                if check and result.returncode != 0:
                    raise ClusterError(f"Command failed: {command}\n{result.stderr}")
                return result.returncode, result.stdout, result.stderr
            except CmdTimeout:
                raise ClusterError(f"Command timed out: {command}")
        else:
            # Remote execution via SSH
            ssh = self._get_ssh_client()
            assert ssh is not None  # Not local means SSH config is present
            try:
                returncode, stdout, stderr = ssh.run(command, timeout=timeout)
                if check and returncode != 0:
                    raise ClusterError(f"Command failed: {command}\n{stderr}")
                return returncode, stdout, stderr
            except SSHError as e:
                raise ClusterError(str(e))

    def _run_microk8s(
        self,
        *args: str,
        timeout: int | None = None,
        check: bool = True,
    ) -> tuple[int, str, str]:
        """Run a microk8s command.

        Args:
            *args: microk8s subcommand and arguments.
            timeout: Command timeout in seconds.
            check: If True, raise on non-zero exit.

        Returns:
            Tuple of (returncode, stdout, stderr).
        """
        command = "microk8s " + " ".join(args)
        return self._run_command(command, timeout=timeout, check=check)

    def create(self, cluster_name: str) -> None:
        """Install and configure microk8s.

        For local operation, installs microk8s via snap.
        For remote operation, installs via SSH.

        Args:
            cluster_name: Name for the cluster (used for namespace).

        Raises:
            ClusterProvisionError: If installation fails.
        """
        # Check if already installed
        if self.exists(cluster_name):
            if self.is_running(cluster_name):
                return  # Already running
            # Installed but not running - start it
            try:
                self._run_microk8s("start", timeout=120)
                return
            except ClusterError as e:
                raise ClusterProvisionError(f"Failed to start microk8s: {e}")

        # Install microk8s via snap
        try:
            self._run_command(
                "snap install microk8s --classic",
                timeout=self.CREATE_TIMEOUT,
            )
        except ClusterError as e:
            if "already installed" in str(e).lower():
                pass  # Already installed, continue
            else:
                raise ClusterProvisionError(f"Failed to install microk8s: {e}")

        # Wait for microk8s to be ready
        try:
            self._run_microk8s("status", "--wait-ready", timeout=120)
        except ClusterError as e:
            raise ClusterProvisionError(f"microk8s not ready after install: {e}")

    def delete(self, cluster_name: str) -> None:
        """Remove microk8s.

        Note: This removes the entire microk8s installation,
        not just a namespace.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).

        Raises:
            ClusterError: If removal fails.
        """
        if not self.exists(cluster_name):
            return  # Already gone

        # Stop and remove microk8s
        self._run_command(
            "snap remove microk8s --purge",
            timeout=120,
            check=False,  # May fail if not installed
        )

    def exists(self, cluster_name: str) -> bool:
        """Check if microk8s is installed.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).

        Returns:
            True if microk8s is installed.
        """
        returncode, _, _ = self._run_command("which microk8s", check=False, timeout=10)
        return returncode == 0

    def is_running(self, cluster_name: str) -> bool:
        """Check if microk8s is running and healthy.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).

        Returns:
            True if microk8s is running.
        """
        returncode, stdout, _ = self._run_microk8s("status", check=False, timeout=30)
        if returncode != 0:
            return False
        return "microk8s is running" in stdout.lower()

    def get_kubeconfig(self, cluster_name: str) -> str:
        """Get kubeconfig for microk8s.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).

        Returns:
            Kubeconfig content.

        Raises:
            ClusterNotFoundError: If microk8s is not installed.
        """
        if not self.exists(cluster_name):
            raise ClusterNotFoundError("microk8s is not installed")

        _, stdout, _ = self._run_microk8s("config")
        return stdout

    def enable_addons(self, cluster_name: str, addons: list[str]) -> None:
        """Enable microk8s addons.

        Available addons:
        - dns: CoreDNS for cluster DNS
        - storage: Default storage class
        - registry: Container registry on localhost:32000
        - ingress: NGINX ingress controller
        - cert-manager: TLS certificate management

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).
            addons: List of addon names to enable.

        Raises:
            ClusterAddonError: If addon enablement fails.
        """
        for addon in addons:
            try:
                self._run_microk8s("enable", addon, timeout=self.ADDON_TIMEOUT)
            except ClusterError as e:
                raise ClusterAddonError(f"Failed to enable addon '{addon}': {e}")

    def kubectl(self, cluster_name: str, *args: str) -> tuple[int, str, str]:
        """Run kubectl command via microk8s.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).
            *args: kubectl arguments.

        Returns:
            Tuple of (returncode, stdout, stderr).
        """
        command = "microk8s kubectl " + " ".join(args)
        return self._run_command(command, check=False)

    def apply_manifests(self, cluster_name: str, manifests: dict[str, str]) -> None:
        """Apply K8s manifests to cluster.

        Args:
            cluster_name: Name of the cluster (ignored for microk8s).
            manifests: Dict of filename -> manifest content.

        Raises:
            ClusterError: If manifest application fails.
        """
        for filename, content in manifests.items():
            if self.is_local:
                # Local: write to temp file and apply
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                    f.write(content)
                    manifest_path = f.name

                try:
                    returncode, stdout, stderr = self.kubectl(
                        cluster_name, "apply", "-f", manifest_path
                    )
                    if returncode != 0:
                        raise ClusterError(f"Failed to apply manifest {filename}: {stderr}")
                finally:
                    Path(manifest_path).unlink(missing_ok=True)
            else:
                # Remote: use heredoc to apply
                # Escape content for shell
                escaped_content = content.replace("'", "'\"'\"'")
                command = f"echo '{escaped_content}' | microk8s kubectl apply -f -"
                returncode, stdout, stderr = self._run_command(command, check=False)
                if returncode != 0:
                    raise ClusterError(f"Failed to apply manifest {filename}: {stderr}")
