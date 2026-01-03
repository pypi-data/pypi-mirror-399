"""E2E fixtures for buildpack tests."""

from __future__ import annotations

import subprocess  # noqa: TID251 - cleanup_docker_images needs subprocess
from pathlib import Path
from typing import Generator

import pytest

from djb.testing import is_docker_available, require_docker

__all__ = [
    "cleanup_docker_images",
    "is_docker_available",
    "make_buildpack_dockerfiles",
    "require_docker",
]


@pytest.fixture
def make_buildpack_dockerfiles(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary dockerfiles directory with real buildable Dockerfiles."""
    dockerfiles_dir = tmp_path / "dockerfiles"
    dockerfiles_dir.mkdir()

    # Dockerfile.glue - merges layers from two images
    (dockerfiles_dir / "Dockerfile.glue").write_text(
        """\
ARG COMPOSITE_IMAGE
ARG LAMINATE_IMAGE
ARG NAMESPACE

FROM ${LAMINATE_IMAGE} AS laminate-source
FROM ${COMPOSITE_IMAGE}
COPY --from=laminate-source / /buildpacks/${NAMESPACE}/
"""
    )

    # Dockerfile.test-buildpack-v1 - simple test buildpack
    (dockerfiles_dir / "Dockerfile.test-buildpack-v1").write_text(
        """\
ARG COMPOSITE_IMAGE
FROM ${COMPOSITE_IMAGE}
RUN echo "test buildpack installed" > /buildpack-marker.txt
"""
    )

    # Dockerfile.gdal-slim-dynamic-v1 - dynamic version buildpack
    (dockerfiles_dir / "Dockerfile.gdal-slim-dynamic-v1").write_text(
        """\
ARG COMPOSITE_IMAGE
ARG BUILDPACK_VERSION
FROM ${COMPOSITE_IMAGE}
RUN echo "GDAL version ${BUILDPACK_VERSION}"
"""
    )

    yield dockerfiles_dir


@pytest.fixture
def cleanup_docker_images() -> Generator[list[str], None, None]:
    """Track and cleanup Docker images created during test."""
    images_to_cleanup: list[str] = []
    yield images_to_cleanup

    # Cleanup after test
    for image in images_to_cleanup:
        subprocess.run(
            ["docker", "rmi", "-f", image],
            capture_output=True,
        )
