"""Base classes for buildpacks module.

This module provides the abstract base class for buildpack chain builders.
The ABC defines the interface and shared logic for building buildpack chains.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from djb.buildpacks.constants import DOCKERFILES_DIR, BuildpackError
from djb.buildpacks.metadata import (
    PUBLIC_IMAGE_BUILD_TIMEOUT_SECONDS,
    get_build_timeout,
    has_version_resolver,
    resolve_version,
)
from djb.buildpacks.specs import BuildpackChainSpec
from djb.core.logging import get_logger

logger = get_logger(__name__)


class BuildpackChain(ABC):
    """Abstract base class for buildpack chain builders.

    Subclasses implement the execution environment (remote SSH or local Docker).
    The chain building logic is shared in `build()`.

    Attributes:
        registry: Docker registry host (e.g., "localhost:32000")
        pyproject_path: Path to pyproject.toml for dynamic version resolution
    """

    def __init__(
        self,
        registry: str,
        pyproject_path: Path | None = None,
    ) -> None:
        """Initialize the buildpack chain builder.

        Args:
            registry: Docker registry host (e.g., "localhost:32000")
            pyproject_path: Path to pyproject.toml for dynamic version resolution
        """
        self.registry = registry
        self.pyproject_path = pyproject_path

    @abstractmethod
    def image_exists(self, image_tag: str) -> bool:
        """Check if an image exists.

        Args:
            image_tag: Full image tag to check

        Returns:
            True if image exists, False otherwise
        """

    @abstractmethod
    def _build_image(
        self,
        dockerfile_path: Path,
        cured_image_tag: str,
        composite_image: str | None,
        laminate_image: str | None = None,
        buildpack_version: str | None = None,
    ) -> str:
        """Build a Docker image.

        Args:
            dockerfile_path: Path to the Dockerfile
            cured_image_tag: Tag for the built image (the new cured composite)
            composite_image: Existing composite to build on (COMPOSITE_IMAGE build arg)
            laminate_image: Layer being laminated in (LAMINATE_IMAGE build arg)
            buildpack_version: BUILDPACK_VERSION build arg value (for dynamic buildpacks)

        Returns:
            The cured_image_tag

        Raises:
            BuildpackError: If build fails
        """

    @staticmethod
    def _buildpack_spec_from_dockerfile(dockerfile_path: Path) -> str | None:
        """Extract buildpack spec from a Dockerfile path."""
        name = dockerfile_path.name
        if name == "Dockerfile.glue":
            return None
        if name.startswith("Dockerfile."):
            return name.split("Dockerfile.", 1)[1]
        return None

    def _estimate_build_timeout_seconds(
        self,
        dockerfile_path: Path,
        glue_image: str | None,
    ) -> int:
        """Estimate build timeout for a buildpack Dockerfile."""
        if glue_image:
            return PUBLIC_IMAGE_BUILD_TIMEOUT_SECONDS

        spec = self._buildpack_spec_from_dockerfile(dockerfile_path)
        if spec is not None:
            return get_build_timeout(spec)

        return get_build_timeout("")

    def build(
        self,
        buildpacks: list[str],
        force_rebuild: bool = False,
    ) -> str:
        """Build the buildpack chain, returning the final composite image tag.

        Each buildpack builds FROM the previous one in the chain:
        - Public images (with `:`) are used as-is if first, merged via glue otherwise
        - Custom buildpacks (without `:`) use their Dockerfile.{spec}
        - Dynamic buildpacks resolve their version from pyproject.toml

        Args:
            buildpacks: List of buildpack specs
            force_rebuild: If True, rebuild even if image exists

        Returns:
            The final composite image tag

        Raises:
            BuildpackError: If any buildpack fails to build
        """
        if not buildpacks:
            raise BuildpackError("No buildpacks specified")

        # Parse specs and resolve versions for dynamic buildpacks
        chain = BuildpackChainSpec.from_strings(buildpacks, self.registry)
        for spec in chain.specs:
            if has_version_resolver(spec.raw):
                if self.pyproject_path is None:
                    raise BuildpackError(
                        f"Dynamic buildpack '{spec.raw}' requires pyproject_path for version resolution"
                    )
                version = resolve_version(spec.raw, self.pyproject_path)
                chain.set_resolved_version(spec.raw, version)

        # Check if final composite already exists
        final_image_tag = chain.cured_image_tag()
        if not force_rebuild and self.image_exists(final_image_tag):
            logger.info(f"Composite image already exists: {final_image_tag}")
            return final_image_tag

        composite_image: str | None = None

        for spec, cured_image_tag in chain:
            if spec.is_public:
                if composite_image is None:
                    # First in chain - use as-is, no build needed
                    logger.info(f"Using public image: {spec.raw}")
                    composite_image = spec.raw
                    continue

                # Not first - use glue to merge
                logger.next(f"Gluing public image: {spec.raw}")

                # Check if already exists
                if not force_rebuild and self.image_exists(cured_image_tag):
                    logger.info(f"Composite image exists: {cured_image_tag}")
                    composite_image = cured_image_tag
                    continue

                # Use Dockerfile.glue
                glue_dockerfile = DOCKERFILES_DIR / "Dockerfile.glue"
                if not glue_dockerfile.exists():
                    raise BuildpackError(f"Dockerfile.glue not found in {DOCKERFILES_DIR}")

                self._build_image(
                    dockerfile_path=glue_dockerfile,
                    cured_image_tag=cured_image_tag,
                    composite_image=composite_image,
                    laminate_image=spec.raw,
                )
                composite_image = cured_image_tag
                logger.done(f"Glued: {spec.raw}")
            else:
                # Custom buildpack - use Dockerfile.{spec}
                logger.next(f"Building buildpack: {spec.raw}")

                # Check if already exists
                if not force_rebuild and self.image_exists(cured_image_tag):
                    logger.info(f"Composite image exists: {cured_image_tag}")
                    composite_image = cured_image_tag
                    continue

                if spec.dockerfile_path is None:
                    raise BuildpackError(f"No Dockerfile path for spec: {spec.raw}")

                buildpack_version = chain._resolved_versions.get(spec.raw)
                self._build_image(
                    dockerfile_path=spec.dockerfile_path,
                    cured_image_tag=cured_image_tag,
                    composite_image=composite_image,
                    buildpack_version=buildpack_version,
                )
                composite_image = cured_image_tag
                logger.done(f"Built: {spec.raw}")

        if composite_image is None:
            raise BuildpackError("No buildpack images were built")

        return composite_image
