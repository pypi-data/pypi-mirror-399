"""
djb - Django + Bun deployment platform.

Quick start:
    from djb import djb_get_config, get_logger, setup_logging

    setup_logging()
    logger = get_logger(__name__)
    config = djb_get_config()
    logger.info(f"Running in {config.mode} mode")

Public API:
    __version__ - Package version string

    Logging:
        setup_logging - Initialize the djb logging system
        get_logger - Get a logger instance for a module
        Level - Enum of log levels (DEBUG, INFO, etc.)
        DjbLogger - Logger class for CLI output formatting

    Configuration:
        djb_get_config - Get config instance (cached per-process, _bypass_cache for tests)
        DjbConfig - Immutable configuration dataclass

    CLI:
        get_cli_epilog - Get djb epilog text for embedding in host project CLIs

See Also:
    djb/README.md - Full documentation
    djb.secrets - Encrypted secrets management
    djb.core - Exception hierarchy
"""

from __future__ import annotations

from djb._version import __version__

from djb.config import DjbConfig, djb_get_config
from djb.cli.epilog import get_cli_epilog
from djb.core.logging import DjbLogger, Level, get_logger, setup_logging
from djb.types import DomainNameManager

__all__ = [
    "__version__",
    # Logging
    "DjbLogger",
    "Level",
    "get_logger",
    "setup_logging",
    # Configuration
    "djb_get_config",
    "DjbConfig",
    # Types
    "DomainNameManager",
    # CLI
    "get_cli_epilog",
]
