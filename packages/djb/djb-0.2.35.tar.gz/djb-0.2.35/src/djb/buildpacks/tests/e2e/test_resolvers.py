import pytest
from djb.buildpacks.metadata import resolve_version


from pathlib import Path


class TestResolveVersion:
    """Tests for resolve_version()."""

    def test_resolves_gdal(self, make_pyproject_with_gdal: Path) -> None:
        """resolve_version() resolves GDAL version from pyproject.toml."""
        version = resolve_version("gdal-slim-dynamic-v1", make_pyproject_with_gdal)
        assert version == "3.10.0"

    def test_unregistered_spec_raises(self, make_pyproject_with_gdal: Path) -> None:
        """resolve_version() raises KeyError for unregistered specs."""
        with pytest.raises(KeyError):
            resolve_version("unknown-dynamic-v1", make_pyproject_with_gdal)
