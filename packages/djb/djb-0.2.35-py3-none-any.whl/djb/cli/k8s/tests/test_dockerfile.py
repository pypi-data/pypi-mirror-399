"""Unit tests for Dockerfile resolution and rendering functions.

Tests cover:
- _resolve_dockerfile: Dockerfile path resolution order
- _copy_dockerfile_template: Template copying from djb templates
- _render_dockerfile: Jinja2 template rendering with DjbConfig
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from djb.cli.k8s.deploy import (
    _copy_dockerfile_template,
    _render_dockerfile,
    _resolve_dockerfile,
)
from djb.templates import DJB_TEMPLATES_DIR

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from djb.config import DjbConfig


class TestResolveDockerfile:
    """Tests for _resolve_dockerfile() function."""

    def test_returns_none_when_no_dockerfile_exists(self, tmp_path: Path) -> None:
        """When no Dockerfile exists, returns None to trigger generation."""
        result = _resolve_dockerfile(tmp_path)
        assert result is None

    def test_prefers_j2_template_over_plain_dockerfile(self, tmp_path: Path) -> None:
        """Dockerfile.j2 takes priority over Dockerfile."""
        backend_dir = tmp_path / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        # Create both files
        template_path = backend_dir / "Dockerfile.j2"
        plain_path = backend_dir / "Dockerfile"
        template_path.write_text("FROM python:3.12-slim\n# template")
        plain_path.write_text("FROM python:3.12-slim\n# plain")

        result = _resolve_dockerfile(tmp_path)
        assert result == template_path

    def test_returns_plain_dockerfile_when_no_template(self, tmp_path: Path) -> None:
        """Falls back to Dockerfile when Dockerfile.j2 doesn't exist."""
        backend_dir = tmp_path / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        plain_path = backend_dir / "Dockerfile"
        plain_path.write_text("FROM python:3.12-slim")

        result = _resolve_dockerfile(tmp_path)
        assert result == plain_path

    def test_returns_template_path_when_only_template_exists(self, tmp_path: Path) -> None:
        """Returns Dockerfile.j2 when it's the only file present."""
        backend_dir = tmp_path / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        template_path = backend_dir / "Dockerfile.j2"
        template_path.write_text("FROM python:3.12-slim\n{{ deploy_ctx.project_name }}")

        result = _resolve_dockerfile(tmp_path)
        assert result == template_path


class TestCopyDockerfileTemplate:
    """Tests for _copy_dockerfile_template() function."""

    def test_copies_template_to_project(self, tmp_path: Path) -> None:
        """Copies djb template to deployment/k8s/backend/Dockerfile.j2."""
        result = _copy_dockerfile_template(tmp_path)

        expected_path = tmp_path / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        assert result == expected_path
        assert expected_path.exists()

    def test_creates_directory_structure(self, tmp_path: Path) -> None:
        """Creates deployment/k8s/backend/ directories if they don't exist."""
        # Ensure the directory doesn't exist
        backend_dir = tmp_path / "deployment" / "k8s" / "backend"
        assert not backend_dir.exists()

        _copy_dockerfile_template(tmp_path)

        assert backend_dir.exists()
        assert backend_dir.is_dir()

    def test_template_content_matches_source(self, tmp_path: Path) -> None:
        """Copied template matches the djb source template."""
        result_path = _copy_dockerfile_template(tmp_path)

        source_template = DJB_TEMPLATES_DIR / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        expected_content = source_template.read_text()
        actual_content = result_path.read_text()

        assert actual_content == expected_content

    def test_template_contains_jinja2_variables(self, tmp_path: Path) -> None:
        """Copied template contains Jinja2 variables for later rendering."""
        result_path = _copy_dockerfile_template(tmp_path)
        content = result_path.read_text()

        # Check for expected Jinja2 variables from the template
        assert "{{ djb_config.project_name }}" in content


class TestRenderDockerfile:
    """Tests for _render_dockerfile() function."""

    def test_renders_template_with_project_name(
        self, tmp_path: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Renders template and substitutes project_name variable."""
        template_path = tmp_path / "Dockerfile.j2"
        template_path.write_text(
            "ENV DJANGO_SETTINGS_MODULE={{ djb_config.project_name }}.settings"
        )

        djb_config = make_djb_config(project_name="myproject")
        result = _render_dockerfile(template_path, djb_config)

        assert result.exists()
        assert result.name == "Dockerfile"
        assert result.parent == tmp_path

        content = result.read_text()
        assert "ENV DJANGO_SETTINGS_MODULE=myproject.settings" in content
        assert "{{ djb_config.project_name }}" not in content

    def test_output_path_is_next_to_template(
        self, tmp_path: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Rendered Dockerfile is written next to the template file."""
        subdir = tmp_path / "deployment" / "k8s" / "backend"
        subdir.mkdir(parents=True)
        template_path = subdir / "Dockerfile.j2"
        template_path.write_text("FROM python:3.12-slim")

        djb_config = make_djb_config(project_name="myproject")
        result = _render_dockerfile(template_path, djb_config)

        assert result == subdir / "Dockerfile"
        assert result.exists()

    def test_renders_full_djb_template(
        self, tmp_path: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Renders the full djb Dockerfile template successfully."""
        # Copy the real template
        source = DJB_TEMPLATES_DIR / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        template_path = tmp_path / "Dockerfile.j2"
        template_path.write_text(source.read_text())

        djb_config = make_djb_config(project_name="testapp")
        result = _render_dockerfile(template_path, djb_config)
        content = result.read_text()

        # Verify key substitutions
        assert "DJANGO_SETTINGS_MODULE=testapp.settings" in content
        assert "testapp.wsgi:application" in content
        assert "{{ djb_config" not in content  # No unrendered variables


class TestProjectNameWithHyphens:
    """Edge case tests for project names containing hyphens."""

    def test_resolve_works_with_hyphenated_project_name(self, tmp_path: Path) -> None:
        """Dockerfile resolution works with hyphenated project names."""
        backend_dir = tmp_path / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)
        template = backend_dir / "Dockerfile.j2"
        template.write_text("FROM python:3.12-slim")

        # Project name with hyphens doesn't affect resolution
        result = _resolve_dockerfile(tmp_path)
        assert result == template

    def test_render_with_hyphenated_project_name(
        self, tmp_path: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Template rendering preserves hyphens in project name."""
        template_path = tmp_path / "Dockerfile.j2"
        template_path.write_text("PROJECT={{ djb_config.project_name }}")

        djb_config = make_djb_config(project_name="my-cool-project")
        result = _render_dockerfile(template_path, djb_config)
        content = result.read_text()

        assert "PROJECT=my-cool-project" in content
