"""Constants and base exception for buildpacks module."""

from __future__ import annotations

from pathlib import Path

from djb.core import DjbError

# Directory containing buildpack Dockerfiles
DOCKERFILES_DIR = Path(__file__).parent / "dockerfiles"


class BuildpackError(DjbError):
    """Exception raised for buildpack-related errors."""
