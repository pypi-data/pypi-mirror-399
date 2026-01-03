"""
SSH client using system ssh command.

Provides a simple SSH client using subprocess calls to the system ssh command.
This avoids the need for paramiko and uses the same SSH configuration as the
user's command line.

The SSHClient class provides:
- Command execution with output capture
- Configurable timeouts
- Key-based authentication
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

from djb.core import CmdTimeout

if TYPE_CHECKING:
    from djb.core import CmdRunner

# SSH timeouts (seconds)
SSH_CONNECT_TIMEOUT: Final[int] = 10
SSH_DEFAULT_CMD_TIMEOUT: Final[int] = 60
SSH_FILE_TRANSFER_TIMEOUT: Final[int] = 300

# Buffer added to connect timeout for verification
SSH_VERIFY_BUFFER: Final[int] = 5


class SSHError(Exception):
    """SSH operation failed."""


class SSHClient:
    """Simple SSH client using subprocess.

    Uses the system ssh command for compatibility with user's SSH config
    and key management.

    Example:
        ssh = SSHClient(host="root@server", cmd_runner=cmd_runner, port=22)
        returncode, stdout, stderr = ssh.run("microk8s status")
    """

    def __init__(
        self,
        host: str,
        cmd_runner: "CmdRunner",
        port: int = 22,
        key_path: Path | None = None,
        connect_timeout: int = SSH_CONNECT_TIMEOUT,
    ):
        """Initialize SSH client.

        Args:
            host: SSH target in format "user@hostname" or just "hostname".
            cmd_runner: Command runner instance for executing shell commands.
            port: SSH port (default: 22).
            key_path: Path to SSH private key (optional, uses ssh-agent if not specified).
            connect_timeout: Connection timeout in seconds.
        """
        self.host = host
        self.cmd_runner = cmd_runner
        self.port = port
        self.key_path = key_path
        self.connect_timeout = connect_timeout

        # Verify connectivity
        self._verify_connection()

    def _build_ssh_command(self, command: str | None = None) -> list[str]:
        """Build the ssh command with options.

        Args:
            command: Remote command to execute (optional).

        Returns:
            List of command arguments.
        """
        cmd = ["ssh"]

        # Connection options
        cmd.extend(["-o", f"ConnectTimeout={self.connect_timeout}"])
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
        cmd.extend(["-o", "BatchMode=yes"])  # Fail instead of prompting for password

        # Port
        cmd.extend(["-p", str(self.port)])

        # Key path
        if self.key_path:
            cmd.extend(["-i", str(self.key_path)])

        # Host
        cmd.append(self.host)

        # Command
        if command:
            cmd.append(command)

        return cmd

    def _verify_connection(self) -> None:
        """Verify SSH connectivity.

        Raises:
            SSHError: If connection fails.
        """
        try:
            result = self.cmd_runner.run(
                self._build_ssh_command("echo ok"),
                timeout=self.connect_timeout + SSH_VERIFY_BUFFER,
            )
            if result.returncode != 0:
                raise SSHError(f"SSH connection failed: {result.stderr.strip() or 'unknown error'}")
        except CmdTimeout:
            raise SSHError(f"SSH connection timed out after {self.connect_timeout}s")
        except FileNotFoundError:
            raise SSHError("ssh command not found. Is OpenSSH installed?")

    def run(
        self,
        command: str,
        timeout: int = SSH_DEFAULT_CMD_TIMEOUT,
        check: bool = False,
    ) -> tuple[int, str, str]:
        """Execute a command over SSH.

        Args:
            command: Command to execute on the remote host.
            timeout: Command timeout in seconds.
            check: If True, raise SSHError on non-zero exit code.

        Returns:
            Tuple of (returncode, stdout, stderr).

        Raises:
            SSHError: If check=True and command fails, or on timeout.
        """
        try:
            result = self.cmd_runner.run(
                self._build_ssh_command(command),
                timeout=timeout,
            )

            if check and result.returncode != 0:
                raise SSHError(
                    f"Command failed with exit code {result.returncode}: "
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )

            return result.returncode, result.stdout, result.stderr

        except CmdTimeout:
            raise SSHError(f"Command timed out after {timeout}s: {command}")

    def run_streaming(
        self,
        command: str,
    ) -> int:
        """Execute a command over SSH with streaming output.

        Output is printed directly to stdout/stderr. Use this for
        long-running commands where you want to see progress.

        Note: Streaming mode does not support timeout. For commands that
        may hang, use run() with check=False instead.

        Args:
            command: Command to execute on the remote host.

        Returns:
            Exit code.
        """
        result = self.cmd_runner.run(
            self._build_ssh_command(command),
            show_output=True,
        )
        return result.returncode

    def copy_to(
        self,
        local_path: Path,
        remote_path: str,
        timeout: int = SSH_FILE_TRANSFER_TIMEOUT,
    ) -> None:
        """Copy a file to the remote host.

        Args:
            local_path: Local file path.
            remote_path: Remote destination path.
            timeout: Transfer timeout in seconds.

        Raises:
            SSHError: If copy fails.
        """
        cmd = ["scp"]

        # Options
        cmd.extend(["-o", f"ConnectTimeout={self.connect_timeout}"])
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
        cmd.extend(["-P", str(self.port)])

        if self.key_path:
            cmd.extend(["-i", str(self.key_path)])

        # Source and destination
        cmd.append(str(local_path))
        cmd.append(f"{self.host}:{remote_path}")

        try:
            result = self.cmd_runner.run(cmd, timeout=timeout)
            if result.returncode != 0:
                raise SSHError(f"SCP failed: {result.stderr.strip()}")

        except CmdTimeout:
            raise SSHError(f"SCP timed out after {timeout}s")

    def copy_from(
        self,
        remote_path: str,
        local_path: Path,
        timeout: int = SSH_FILE_TRANSFER_TIMEOUT,
    ) -> None:
        """Copy a file from the remote host.

        Args:
            remote_path: Remote file path.
            local_path: Local destination path.
            timeout: Transfer timeout in seconds.

        Raises:
            SSHError: If copy fails.
        """
        cmd = ["scp"]

        # Options
        cmd.extend(["-o", f"ConnectTimeout={self.connect_timeout}"])
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
        cmd.extend(["-P", str(self.port)])

        if self.key_path:
            cmd.extend(["-i", str(self.key_path)])

        # Source and destination
        cmd.append(f"{self.host}:{remote_path}")
        cmd.append(str(local_path))

        try:
            result = self.cmd_runner.run(cmd, timeout=timeout)
            if result.returncode != 0:
                raise SSHError(f"SCP failed: {result.stderr.strip()}")

        except CmdTimeout:
            raise SSHError(f"SCP timed out after {timeout}s")
