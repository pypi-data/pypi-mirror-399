"""Tests for RemoteBuildpackChain."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.remote import RemoteBuildpackChain

# Note: TestRemoteBuildpackChainBuildImage moved to e2e/test_remote_chain.py


class TestRemoteBuildpackChainImageExists:
    """Tests for RemoteBuildpackChain.image_exists()."""

    def test_image_exists_returns_true(self, mock_ssh: MagicMock) -> None:
        """image_exists() returns True when grep succeeds."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        assert chain.image_exists("localhost:32000/test:latest") is True

    def test_image_exists_returns_false(self, mock_ssh: MagicMock) -> None:
        """image_exists() returns False when grep fails."""
        mock_ssh.run.return_value = (1, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        assert chain.image_exists("localhost:32000/test:latest") is False

    def test_image_exists_uses_microk8s_ctr(self, mock_ssh: MagicMock) -> None:
        """image_exists() uses microk8s ctr to check containerd registry."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        chain.image_exists("localhost:32000/test:latest")

        mock_ssh.run.assert_called_once()
        call_args = mock_ssh.run.call_args[0][0]
        assert "microk8s ctr image ls" in call_args
        assert "localhost:32000/test:latest" in call_args


class TestRemoteBuildpackChainBuild:
    """Tests for RemoteBuildpackChain.build()."""

    def test_build_returns_cached_image(
        self, mock_ssh: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() returns existing image without rebuilding."""
        # Image exists
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        assert result == "localhost:32000/python3.14-slim:latest"
        # Only called once to check if image exists
        assert mock_ssh.run.call_count == 1

    def test_build_empty_buildpacks_raises(self, mock_ssh: MagicMock) -> None:
        """build() raises BuildpackError for empty buildpack list."""
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        with pytest.raises(BuildpackError, match="No buildpacks specified"):
            chain.build([])

    def test_build_first_public_image_not_built(
        self, mock_ssh: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() uses first public image as-is without building."""
        # Image doesn't exist
        mock_ssh.run.return_value = (1, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        # Should return the public image directly
        assert result == "python:3.14-slim"
