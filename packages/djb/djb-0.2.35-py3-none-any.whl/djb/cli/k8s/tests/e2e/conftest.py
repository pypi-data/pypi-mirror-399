"""E2E test configuration for deploy_k8s.

All tests in this directory are marked as e2e_marker and require Docker.
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - invoking docker directly
import time
from pathlib import Path
from typing import Generator

import pytest

from djb.testing import (
    is_docker_available,
    make_cli_ctx,
    make_cli_runner,
    make_cmd_runner,
    require_docker,
)

# Mark all tests in this directory as E2E tests
pytestmark = pytest.mark.e2e_marker

__all__ = [
    "is_docker_available",
    "make_cli_runner",
    "make_local_vps_container",
    "make_cli_ctx",
    "make_cmd_runner",
    "require_docker",
]


@pytest.fixture
def make_local_vps_container(
    request: pytest.FixtureRequest,
    tmp_path: Path,
) -> Generator[dict[str, str | int | Path], None, None]:
    """Create a Docker container with SSH for E2E testing.

    This fixture:
    1. Generates a temporary SSH key pair
    2. Starts the djb-local-vps Docker container
    3. Waits for SSH to be ready
    4. Yields connection info for tests
    5. Cleans up container after tests

    Returns a dict with:
        host: SSH host (localhost)
        port: SSH port (randomly assigned)
        ssh_key: Path to the private SSH key
        container_name: Name of the container
    """
    if not is_docker_available():
        pytest.skip("Docker not available")

    # Generate temporary SSH key pair
    ssh_key_path = tmp_path / "test_id_ed25519"
    ssh_pubkey_path = tmp_path / "test_id_ed25519.pub"

    subprocess.run(
        [
            "ssh-keygen",
            "-t",
            "ed25519",
            "-f",
            str(ssh_key_path),
            "-N",
            "",  # No passphrase
            "-C",
            "djb-e2e-test",
        ],
        capture_output=True,
        check=True,
    )

    ssh_pubkey_content = ssh_pubkey_path.read_text().strip()

    # Use a unique container name for test isolation
    container_name = f"djb-e2e-test-{tmp_path.name}"

    # Find the Dockerfile
    dockerfile_dir = Path(__file__).parent.parent.parent / "docker"
    dockerfile_path = dockerfile_dir / "Dockerfile.local-vps"

    if not dockerfile_path.exists():
        pytest.skip(f"Dockerfile not found at {dockerfile_path}")

    # Build the image
    image_name = "djb-local-vps-test:latest"
    build_result = subprocess.run(
        [
            "docker",
            "build",
            "-t",
            image_name,
            "-f",
            str(dockerfile_path),
            str(dockerfile_dir),
        ],
        capture_output=True,
        text=True,
    )
    if build_result.returncode != 0:
        pytest.skip(f"Failed to build Docker image: {build_result.stderr}")

    # Start container with random port mapping
    run_result = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--privileged",
            "-p",
            "0:22",  # Random port
            "--tmpfs",
            "/run",
            "--tmpfs",
            "/run/lock",
            "-e",
            f"SSH_PUBKEY={ssh_pubkey_content}",
            image_name,
        ],
        capture_output=True,
        text=True,
    )

    if run_result.returncode != 0:
        pytest.skip(f"Failed to start container: {run_result.stderr}")

    try:
        # Get the assigned port
        port_result = subprocess.run(
            ["docker", "port", container_name, "22"],
            capture_output=True,
            text=True,
        )

        if port_result.returncode != 0:
            raise RuntimeError(f"Failed to get container port: {port_result.stderr}")

        # Parse port from output like "0.0.0.0:32768" or ":::32768"
        port_output = port_result.stdout.strip()
        ssh_port = int(port_output.split(":")[-1])

        # Wait for SSH to be ready (with timeout)
        max_wait = 30
        start_time = time.time()
        ssh_ready = False

        while time.time() - start_time < max_wait:
            try:
                check_result = subprocess.run(
                    [
                        "ssh",
                        "-o",
                        "StrictHostKeyChecking=no",
                        "-o",
                        "UserKnownHostsFile=/dev/null",
                        "-o",
                        "ConnectTimeout=2",
                        "-o",
                        "BatchMode=yes",
                        "-i",
                        str(ssh_key_path),
                        "-p",
                        str(ssh_port),
                        "root@localhost",
                        "echo ok",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if check_result.returncode == 0:
                    ssh_ready = True
                    break
            except subprocess.TimeoutExpired:
                pass
            time.sleep(1)

        if not ssh_ready:
            raise RuntimeError("SSH did not become ready in time")

        yield {
            "host": "localhost",
            "port": ssh_port,
            "ssh_key": ssh_key_path,
            "container_name": container_name,
        }

    finally:
        # Cleanup container
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
        )
