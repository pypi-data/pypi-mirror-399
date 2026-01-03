"""Tests for djb.core.cmd_runner module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from djb.core.cmd_runner import (
    CmdError,
    CmdRunner,
    _get_env,
    _run_with_pipes,
)


@pytest.fixture
def runner():
    """Provide a CmdRunner for testing real command execution."""
    return CmdRunner(verbose=False)


class TestGetEnv:
    """Tests for _get_env helper."""

    def test_returns_none_when_no_cwd(self):
        """_get_env returns None when cwd is None."""
        result = _get_env(None, None)
        assert result is None

    def test_removes_virtual_env_when_cwd_provided(self, tmp_path):
        """_get_env removes VIRTUAL_ENV when cwd is provided."""
        with patch.dict(os.environ, {"VIRTUAL_ENV": "/some/venv", "OTHER_VAR": "value"}):
            result = _get_env(tmp_path, None)
            assert result is not None
            assert "VIRTUAL_ENV" not in result
            assert result["OTHER_VAR"] == "value"

    def test_works_without_virtual_env_set(self, tmp_path):
        """_get_env works when VIRTUAL_ENV is not in environment."""
        env_without_venv = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        with patch.dict(os.environ, env_without_venv, clear=True):
            result = _get_env(tmp_path, None)
            assert result is not None
            assert "VIRTUAL_ENV" not in result


class TestRunCmd:
    """Tests for CmdRunner.run method."""

    def test_successful_command(self, runner, tmp_path):
        """run returns success for successful command."""
        result = runner.run(["echo", "hello"], cwd=tmp_path)
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_successful_command_with_label(self, runner, tmp_path):
        """run with label logs correctly."""
        with patch("djb.core.cmd_runner.logger") as mock_logger:
            result = runner.run(["echo", "test"], cwd=tmp_path, label="Test command")
            assert result.returncode == 0
            mock_logger.next.assert_called_with("Test command")

    def test_successful_command_with_done_msg(self, runner, tmp_path):
        """run logs done_msg on success."""
        with patch("djb.core.cmd_runner.logger") as mock_logger:
            runner.run(["echo", "test"], cwd=tmp_path, done_msg="All done!")
            mock_logger.done.assert_called_with("All done!")

    def test_quiet_mode_suppresses_logging(self, runner, tmp_path):
        """run quiet mode suppresses label and done_msg logging."""
        with patch("djb.core.cmd_runner.logger") as mock_logger:
            runner.run(
                ["echo", "test"],
                cwd=tmp_path,
                label="Should not log",
                done_msg="Should not log either",
                quiet=True,
            )
            mock_logger.next.assert_not_called()
            mock_logger.done.assert_not_called()

    def test_failed_command_with_exception_fail_msg(self, runner, tmp_path):
        """run raises exception when fail_msg is an Exception and command fails."""
        with pytest.raises(CmdError):
            runner.run(["false"], cwd=tmp_path, fail_msg=CmdError("Command failed"))

    def test_failed_command_without_fail_msg(self, runner, tmp_path):
        """run returns result when no fail_msg and command fails."""
        result = runner.run(["false"], cwd=tmp_path)
        assert result.returncode != 0

    def test_failed_command_logs_string_fail_msg(self, runner, tmp_path):
        """run logs fail_msg when it's a string and command fails."""
        with patch("djb.core.cmd_runner.logger") as mock_logger:
            runner.run(
                ["false"],
                cwd=tmp_path,
                fail_msg="Command failed!",
            )
            mock_logger.fail.assert_called_with("Command failed!")

    def test_failed_command_logs_stderr(self, runner, tmp_path):
        """run logs stderr when fail_msg is set and command fails."""
        # Create a script that outputs to stderr
        script = tmp_path / "fail.sh"
        script.write_text("#!/bin/bash\necho 'error message' >&2\nexit 1")
        script.chmod(0o755)

        with patch("djb.core.cmd_runner.logger") as mock_logger:
            runner.run(
                [str(script)],
                cwd=tmp_path,
                fail_msg="Failed",
            )
            # Check that info was called with stderr content
            calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("error message" in call for call in calls)

    def test_failed_command_with_label_in_error(self, runner, tmp_path):
        """run includes label in error message when command fails."""
        with pytest.raises(CmdError) as exc_info:
            runner.run(
                ["false"],
                cwd=tmp_path,
                label="My command",
                fail_msg=CmdError("My command failed"),
            )
        assert "My command" in str(exc_info.value)


class TestCheckCmd:
    """Tests for CmdRunner.check method."""

    def test_returns_true_for_successful_command(self, runner, tmp_path):
        """check returns True when command succeeds."""
        result = runner.check(["true"], cwd=tmp_path)
        assert result is True

    def test_returns_false_for_failed_command(self, runner, tmp_path):
        """check returns False when command fails."""
        result = runner.check(["false"], cwd=tmp_path)
        assert result is False

    def test_works_with_real_command(self, runner, tmp_path):
        """check works with real command that produces output."""
        result = runner.check(["echo", "test"], cwd=tmp_path)
        assert result is True


class TestRunWithStreaming:
    """Tests for CmdRunner.run with show_output=True."""

    def test_captures_stdout(self, runner, tmp_path):
        """run(show_output=True) captures stdout from command."""
        result = runner.run(["echo", "hello world"], cwd=tmp_path, show_output=True)
        assert result.returncode == 0
        assert "hello world" in result.stdout

    def test_captures_stderr(self, runner, tmp_path):
        """run(show_output=True) captures stderr from command."""
        script = tmp_path / "stderr.sh"
        script.write_text("#!/bin/bash\necho 'error output' >&2")
        script.chmod(0o755)

        result = runner.run([str(script)], cwd=tmp_path, show_output=True)
        assert result.returncode == 0
        assert "error output" in result.stderr

    def test_returns_nonzero_for_failed_command(self, runner, tmp_path):
        """run(show_output=True) returns non-zero code for failed command."""
        result = runner.run(["false"], cwd=tmp_path, show_output=True)
        assert result.returncode != 0

    def test_logs_label_when_provided(self, runner, tmp_path):
        """run(show_output=True) logs label when provided."""
        with patch("djb.core.cmd_runner.logger") as mock_logger:
            runner.run(["echo", "test"], cwd=tmp_path, show_output=True, label="Running test")
            mock_logger.next.assert_called_with("Running test")

    def test_interleaves_stdout_and_stderr(self, runner, tmp_path):
        """run(show_output=True) handles interleaved stdout and stderr."""
        script = tmp_path / "mixed.sh"
        script.write_text(
            "#!/bin/bash\n"
            "echo 'stdout line 1'\n"
            "echo 'stderr line 1' >&2\n"
            "echo 'stdout line 2'\n"
        )
        script.chmod(0o755)

        result = runner.run([str(script)], cwd=tmp_path, show_output=True)
        assert result.returncode == 0
        assert "stdout line 1" in result.stdout
        assert "stdout line 2" in result.stdout
        assert "stderr line 1" in result.stderr


class TestRunWithPipes:
    """Tests for _run_with_pipes helper.

    This is the non-interactive streaming implementation that uses
    poll() on Unix or threads on Windows.
    """

    def test_captures_stdout(self, tmp_path):
        """_run_with_pipes captures stdout from command."""
        returncode, stdout, stderr = _run_with_pipes(
            ["echo", "hello world"], cwd=tmp_path, env=None
        )
        assert returncode == 0
        assert "hello world" in stdout

    def test_captures_stderr(self, tmp_path):
        """_run_with_pipes captures stderr from command."""
        script = tmp_path / "stderr.sh"
        script.write_text("#!/bin/bash\necho 'error output' >&2")
        script.chmod(0o755)

        returncode, stdout, stderr = _run_with_pipes([str(script)], cwd=tmp_path, env=None)
        assert returncode == 0
        assert "error output" in stderr

    def test_interleaves_stdout_and_stderr(self, tmp_path):
        """_run_with_pipes handles interleaved stdout and stderr."""
        script = tmp_path / "mixed.sh"
        script.write_text(
            "#!/bin/bash\n"
            "echo 'stdout line 1'\n"
            "echo 'stderr line 1' >&2\n"
            "echo 'stdout line 2'\n"
            "echo 'stderr line 2' >&2\n"
        )
        script.chmod(0o755)

        returncode, stdout, stderr = _run_with_pipes([str(script)], cwd=tmp_path, env=None)
        assert returncode == 0
        assert "stdout line 1" in stdout
        assert "stdout line 2" in stdout
        assert "stderr line 1" in stderr
