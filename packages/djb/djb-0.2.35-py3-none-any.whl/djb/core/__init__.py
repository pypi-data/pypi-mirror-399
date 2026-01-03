"""
djb.core - Core utilities and exception hierarchy.

Example:
    from djb.core import DjbError, SecretsError, get_logger

    logger = get_logger(__name__)

    try:
        secrets = load_secrets("production")
    except SecretsError as e:
        logger.error(f"Secrets error: {e}")
    except DjbError as e:
        logger.error(f"djb error: {e}")

Logging:
    setup_logging - Initialize the djb logging system
    get_logger - Get a logger instance for a module
    Level - Enum of log levels (DEBUG, INFO, etc.)
    DjbLogger - Logger class for output formatting

File locking:
    FileLockTimeout - Raised when unable to acquire file lock within timeout
    get_lock_for_path - Get or create a FileLock for the given path
    atomic_write - Write content atomically using temp file + rename
    locked_write - Convenience function combining lock + atomic write
    file_lock - Context manager with automatic lock file cleanup
    LOCK_TIMEOUT_SECONDS - Default timeout for lock acquisition (5.0 seconds)

Command runner:
    CmdRunner - Class for executing subprocess commands with CLI context
    RunResult - Dataclass containing returncode, stdout, stderr
    CmdError - Exception raised when command fails (with check=True)
    CmdTimeout - Exception raised when command times out

Exception hierarchy:
    DjbError (base)
    ├── ImproperlyConfigured - Invalid configuration
    ├── ProjectNotFound - Project directory not found
    ├── SecretsError - Secrets-related errors
    │   ├── SecretsKeyNotFound - Age key file missing
    │   ├── SecretsDecryptionFailed - Decryption failed
    │   └── SecretsFileNotFound - Secrets file missing
    ├── DeploymentError - Deployment-related errors
    │   ├── HerokuAuthError - Heroku authentication failed
    │   └── HerokuPushError - Heroku push failed
    └── CmdError - Command execution errors
        └── CmdTimeout - Command timed out
"""

from __future__ import annotations

from djb.core.cmd_runner import (
    CmdError,
    CmdRunner,
    CmdTimeout,
    RunResult,
)
from djb.core.exceptions import (
    DeploymentError,
    DjbError,
    HerokuAuthError,
    HerokuPushError,
    ImproperlyConfigured,
    ProjectNotFound,
    SecretsDecryptionFailed,
    SecretsError,
    SecretsFileNotFound,
    SecretsKeyNotFound,
)
from djb.core.locking import (
    LOCK_TIMEOUT_SECONDS,
    FileLockTimeout,
    atomic_write,
    file_lock,
    get_lock_for_path,
    locked_write,
)
from djb.core.logging import DjbLogger, Level, get_logger, setup_logging

__all__ = [
    # Logging
    "DjbLogger",
    "Level",
    "get_logger",
    "setup_logging",
    # File locking
    "LOCK_TIMEOUT_SECONDS",
    "FileLockTimeout",
    "atomic_write",
    "file_lock",
    "get_lock_for_path",
    "locked_write",
    # Command runner
    "CmdError",
    "CmdRunner",
    "CmdTimeout",
    "RunResult",
    # Base exceptions
    "DjbError",
    "ImproperlyConfigured",
    "ProjectNotFound",
    # Secrets exceptions
    "SecretsDecryptionFailed",
    "SecretsError",
    "SecretsFileNotFound",
    "SecretsKeyNotFound",
    # Deployment exceptions
    "DeploymentError",
    "HerokuAuthError",
    "HerokuPushError",
]
