"""
K3dProvider - Local k3d cluster implementation.

k3d is a lightweight wrapper to run k3s (Rancher's minimal Kubernetes)
in Docker. It provides:
- Fast startup (~30 seconds)
- Built-in registry support
- Optimized for local development with Skaffold

This provider is local-only and does not support SSH connections.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from typing import TYPE_CHECKING

from djb.core import CmdTimeout
from djb.k8s.cluster.provider import (
    ClusterAddonError,
    ClusterError,
    ClusterNotFoundError,
    ClusterProvisionError,
)

if TYPE_CHECKING:
    from djb.core import CmdRunner


class K3dProvider:
    """Local k3d cluster provider.

    Manages k3d clusters for local Kubernetes development.
    Optimized for use with Skaffold for hot-reload workflows.

    Example:
        provider = K3dProvider(cmd_runner)
        provider.create("myapp-dev")
        provider.enable_addons("myapp-dev", ["registry"])
    """

    # k3d cluster creation timeout in seconds
    CREATE_TIMEOUT = 120

    # Registry name suffix
    REGISTRY_SUFFIX = "-registry"

    def __init__(self, cmd_runner: "CmdRunner"):
        """Initialize provider.

        Args:
            cmd_runner: Command runner instance for executing shell commands.
        """
        self._cmd_runner = cmd_runner

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "k3d"

    @property
    def registry_address(self) -> str:
        """Registry address for pushing images.

        k3d uses a registry running on a predictable address.
        """
        return "k3d-registry.localhost:5000"

    @property
    def is_local(self) -> bool:
        """k3d is always local."""
        return True

    def _run_k3d(
        self,
        *args: str,
        check: bool = True,
        timeout: int | None = None,
    ) -> tuple[int, str, str]:
        """Run a k3d command.

        Args:
            *args: k3d subcommand and arguments.
            check: If True, raise on non-zero exit.
            timeout: Command timeout in seconds.

        Returns:
            Tuple of (returncode, stdout, stderr).

        Raises:
            ClusterError: If check=True and command fails.
        """
        cmd = ["k3d", *args]
        try:
            result = self._cmd_runner.run(cmd, timeout=timeout)
            if check and result.returncode != 0:
                raise ClusterError(f"k3d command failed: {' '.join(cmd)}\n{result.stderr}")
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            raise ClusterError("k3d not found. Install with: brew install k3d")
        except CmdTimeout:
            raise ClusterError(f"k3d command timed out: {' '.join(cmd)}")

    def create(self, cluster_name: str) -> None:
        """Create a k3d cluster with registry.

        Creates a new k3d cluster with:
        - A local registry for image pushes
        - Port mappings for ingress
        - Reasonable resource limits

        Args:
            cluster_name: Name for the cluster.

        Raises:
            ClusterProvisionError: If cluster creation fails.
        """
        if self.exists(cluster_name):
            if self.is_running(cluster_name):
                return  # Already running, nothing to do
            # Exists but stopped - start it
            self._run_k3d("cluster", "start", cluster_name, timeout=60)
            return

        # Create new cluster with registry
        try:
            self._run_k3d(
                "cluster",
                "create",
                cluster_name,
                "--registry-create",
                f"{cluster_name}{self.REGISTRY_SUFFIX}",
                # Map ports for ingress
                "-p",
                "8080:80@loadbalancer",
                "-p",
                "8443:443@loadbalancer",
                # Wait for cluster to be ready
                "--wait",
                timeout=self.CREATE_TIMEOUT,
            )
        except ClusterError as e:
            raise ClusterProvisionError(f"Failed to create k3d cluster: {e}")

    def delete(self, cluster_name: str) -> None:
        """Delete a k3d cluster.

        Args:
            cluster_name: Name of the cluster to delete.

        Raises:
            ClusterError: If deletion fails.
        """
        if not self.exists(cluster_name):
            return  # Already gone

        self._run_k3d("cluster", "delete", cluster_name, timeout=60)

    def exists(self, cluster_name: str) -> bool:
        """Check if cluster exists.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            True if the cluster exists.
        """
        returncode, stdout, _ = self._run_k3d("cluster", "list", "-o", "json", check=False)
        if returncode != 0:
            return False

        # Parse JSON output to check for cluster name
        try:
            clusters = json.loads(stdout)
            return any(c.get("name") == cluster_name for c in clusters)
        except json.JSONDecodeError:
            return False

    def is_running(self, cluster_name: str) -> bool:
        """Check if cluster is running.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            True if the cluster is running.
        """
        returncode, stdout, _ = self._run_k3d("cluster", "list", "-o", "json", check=False)
        if returncode != 0:
            return False

        try:
            clusters = json.loads(stdout)
            for cluster in clusters:
                if cluster.get("name") == cluster_name:
                    # Check if all nodes are running
                    nodes = cluster.get("nodes", [])
                    return all(node.get("State", {}).get("Running", False) for node in nodes)
            return False
        except json.JSONDecodeError:
            return False

    def get_kubeconfig(self, cluster_name: str) -> str:
        """Get kubeconfig for the cluster.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            Kubeconfig content.

        Raises:
            ClusterNotFoundError: If cluster doesn't exist.
        """
        if not self.exists(cluster_name):
            raise ClusterNotFoundError(f"Cluster '{cluster_name}' not found")

        _, stdout, _ = self._run_k3d("kubeconfig", "get", cluster_name)
        return stdout

    def enable_addons(self, cluster_name: str, addons: list[str]) -> None:
        """Enable cluster addons.

        k3d has built-in registry support via --registry-create.
        Other addons are handled by k3s/kubectl.

        Args:
            cluster_name: Name of the cluster.
            addons: List of addon names to enable.

        Raises:
            ClusterAddonError: If addon enablement fails.
        """
        # k3d handles most things via k3s
        # The main "addon" is the registry, which is created with the cluster
        for addon in addons:
            if addon == "registry":
                # Registry is created with the cluster
                continue
            if addon == "ingress":
                # k3d uses traefik by default
                continue
            # For other addons, we might need to apply manifests
            # This is a placeholder for future addon support
            pass

    def kubectl(self, cluster_name: str, *args: str) -> tuple[int, str, str]:
        """Run kubectl command against cluster.

        Args:
            cluster_name: Name of the cluster.
            *args: kubectl arguments.

        Returns:
            Tuple of (returncode, stdout, stderr).
        """
        # Get kubeconfig and write to temp file
        kubeconfig = self.get_kubeconfig(cluster_name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(kubeconfig)
            kubeconfig_path = f.name

        try:
            result = self._cmd_runner.run(["kubectl", "--kubeconfig", kubeconfig_path, *args])
            return result.returncode, result.stdout, result.stderr
        finally:
            Path(kubeconfig_path).unlink(missing_ok=True)

    def apply_manifests(self, cluster_name: str, manifests: dict[str, str]) -> None:
        """Apply K8s manifests to cluster.

        Args:
            cluster_name: Name of the cluster.
            manifests: Dict of filename -> manifest content.

        Raises:
            ClusterError: If manifest application fails.
        """
        for filename, content in manifests.items():
            # Write manifest to temp file
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
