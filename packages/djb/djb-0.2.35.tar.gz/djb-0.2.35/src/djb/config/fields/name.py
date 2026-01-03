"""
NameField - Field for user name with git config fallback.

Uses git config user.name as an external source for value acquisition
and as a resolution fallback.
"""

from __future__ import annotations

from typing import Any

from djb.config.acquisition import GitConfigSource
from djb.config.field import ConfigFieldABC
from djb.config.resolution import ConfigSource, ResolutionContext


class NameField(ConfigFieldABC):
    """Field for user name with git config fallback.

    Uses git config user.name as an external source and resolution fallback.
    """

    def __init__(self, **kwargs):
        """Initialize with git config fallback source."""
        self._git_source = GitConfigSource("user.name")
        super().__init__(
            prompt_text="Enter your name",
            external_sources=[self._git_source],
            **kwargs,
        )

    def resolve(self, ctx: ResolutionContext) -> tuple[Any, ConfigSource | None]:
        """Resolve name from config layers, then git config as fallback."""
        # First try config layers (cli > env > local > project)
        if self.config_file_key:
            raw, source = ctx.configs.get(self.config_file_key, self.env_key)
            if raw is not None:
                return (self.normalize(raw), source)

        # Try git config as fallback (from project's local git config)
        git_value = self._git_source.get(ctx.project_root)
        if git_value:
            return (git_value, ConfigSource.GIT)

        # Default
        default_value = self.get_default()
        if default_value is not None:
            return (default_value, ConfigSource.DEFAULT)
        return (None, None)
