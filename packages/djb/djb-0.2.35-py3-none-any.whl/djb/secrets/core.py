"""
Core secrets management using SOPS.

This module provides encrypted secrets storage compatible with Kubernetes
and cloud deployments, using SOPS with age encryption.

Key features:
- SOPS integration for multi-recipient encryption
- Age encryption (X25519 + ChaCha20-Poly1305)
- Subprocess timeouts to prevent hanging operations
- Atomic file writes for crash safety
"""

from __future__ import annotations

import os
import re
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, NamedTuple

import yaml

from djb.config import djb_get_config
from djb.core import CmdRunner, CmdTimeout


from djb.secrets.paths import (
    get_default_key_path,
    get_default_secrets_dir,
    get_encrypted_key_path,
)
from djb.secrets.protected import is_age_key_protected, protected_age_key

if TYPE_CHECKING:
    from djb.types import Mode


# Bech32 character set for age public key validation (excludes 1, b, i, o)
BECH32_CHARS = frozenset("023456789acdefghjklmnpqrstuvwxyz")

# Default timeout for SOPS/age operations (in seconds)
SOPS_TIMEOUT = 5


class AgeKeyPair(NamedTuple):
    """Result of generate_age_key() - an age public/private key pair."""

    public_key: str
    private_key: str


class ParsedIdentity(NamedTuple):
    """Result of parse_identity() - parsed name and email from identity string."""

    name: str | None
    email: str


class SopsError(Exception):
    """Error from SOPS command."""


def check_sops_installed() -> bool:
    """Check if SOPS is installed and available."""
    return shutil.which("sops") is not None


def check_age_installed() -> bool:
    """Check if age is installed and available."""
    return shutil.which("age-keygen") is not None


def generate_age_key(
    runner: CmdRunner,
    key_path: Path | None = None,
    project_dir: Path | None = None,
) -> AgeKeyPair:
    """Generate a new age key pair using age-keygen.

    Args:
        runner: CmdRunner instance for executing commands.
        key_path: Path to save the private key (defaults to project_dir/.age/keys.txt)
        project_dir: Project root directory. Required if key_path is not provided.

    Returns:
        AgeKeyPair with public_key and private_key.

    Raises:
        SopsError: If key generation fails or times out.
        ValueError: If neither key_path nor project_dir is provided.
    """
    if key_path is None:
        if project_dir is None:
            raise ValueError("Either key_path or project_dir must be provided")
        key_path = get_default_key_path(project_dir)

    # Generate key using age-keygen
    try:
        result = runner.run(
            ["age-keygen"],
            timeout=SOPS_TIMEOUT,
            fail_msg=SopsError("age-keygen failed"),
        )
    except CmdTimeout as e:
        raise SopsError(f"age-keygen timed out after {SOPS_TIMEOUT}s") from e

    # Parse output - age-keygen outputs:
    # # created: 2024-01-01T00:00:00Z
    # # public key: age1...
    # AGE-SECRET-KEY-...
    lines = result.stdout.strip().split("\n")
    public_key = None
    private_key = None

    for line in lines:
        if line.startswith("# public key: "):
            public_key = line.replace("# public key: ", "").strip()
        elif line.startswith("AGE-SECRET-KEY-"):
            private_key = line.strip()

    if not public_key or not private_key:
        raise SopsError(f"Failed to parse age-keygen output: {result.stdout}")

    # Save private key to file
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(result.stdout)
    key_path.chmod(0o600)

    return AgeKeyPair(public_key, private_key)


def is_valid_age_public_key(key: str) -> bool:
    """Check if a string is a valid age public key.

    Age public keys:
    - Start with "age1"
    - Are 62 characters long (Bech32 encoding)
    - Contain only lowercase letters and digits (no 1, b, i, o to avoid confusion)

    Args:
        key: String to validate

    Returns:
        True if the key appears to be a valid age public key
    """
    if not key.startswith("age1"):
        return False

    if len(key) != 62:
        return False

    # Check characters after "age1" prefix
    for char in key[4:]:
        if char not in BECH32_CHARS:
            return False

    return True


def get_public_key_from_private(
    runner: CmdRunner,
    key_path: Path | None = None,
    project_dir: Path | None = None,
) -> str:
    """Extract public key from a private key file.

    Args:
        runner: CmdRunner instance for executing commands.
        key_path: Path to the private key file
        project_dir: Project root directory. Required if key_path is not provided.

    Returns:
        The public key string

    Raises:
        FileNotFoundError: If key file doesn't exist.
        SopsError: If key is invalid, corrupted, or derivation times out.
        ValueError: If neither key_path nor project_dir is provided.
    """
    if key_path is None:
        if project_dir is None:
            raise ValueError("Either key_path or project_dir must be provided")
        key_path = get_default_key_path(project_dir)

    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")

    content = key_path.read_text()

    # Look for public key in comments
    for line in content.split("\n"):
        if line.startswith("# public key: "):
            return line.replace("# public key: ", "").strip()

    # If no comment, derive from private key using age-keygen -y
    # Find the private key line
    for line in content.split("\n"):
        if line.startswith("AGE-SECRET-KEY-"):
            try:
                result = runner.run(
                    ["age-keygen", "-y"],
                    input=line,
                    timeout=SOPS_TIMEOUT,
                )
            except CmdTimeout as e:
                raise SopsError(f"age-keygen -y timed out after {SOPS_TIMEOUT}s") from e
            if result.returncode == 0:
                return result.stdout.strip()
            raise SopsError(
                f"Failed to derive public key: {result.stderr}. " f"The key file may be corrupted."
            )

    raise SopsError(
        f"No valid age key found in {key_path}. "
        f"The file should contain a line starting with 'AGE-SECRET-KEY-'."
    )


def format_identity(name: str | None, email: str) -> str:
    """Format name and email into git-style identity string.

    Args:
        name: User's name (optional)
        email: User's email

    Returns:
        Identity string in format "Name <email>" or just "email" if no name.
    """
    if name:
        return f"{name} <{email}>"
    return email


def parse_identity(identity: str) -> ParsedIdentity:
    """Parse git-style identity string into name and email.

    Args:
        identity: Identity string like "Name <email>" or just "email"

    Returns:
        ParsedIdentity with name and email. Name may be None for legacy format.
    """
    # Try git-style format: "Name <email>"
    match = re.match(r"^(.+?)\s*<([^>]+)>$", identity)
    if match:
        return ParsedIdentity(match.group(1).strip(), match.group(2).strip())

    # Legacy format: just email
    return ParsedIdentity(None, identity)


# Placeholder pattern used in secrets templates (case-insensitive substring match)
PLACEHOLDER_PATTERN = "CHANGE-ME"


def is_placeholder_value(value: str) -> bool:
    """Check if a secret value is a placeholder that needs to be changed.

    Args:
        value: The secret value to check.

    Returns:
        True if the value contains CHANGE-ME (case-insensitive).
    """
    if not isinstance(value, str):
        return False

    return PLACEHOLDER_PATTERN.upper() in value.upper()


def find_placeholder_secrets(secrets: dict[str, Any], prefix: str = "") -> list[str]:
    """Find all secrets that have placeholder values.

    Args:
        secrets: Dictionary of secrets (can be nested).
        prefix: Key prefix for nested keys (used internally).

    Returns:
        List of key paths that have placeholder values (e.g., "api_keys.stripe").
    """
    placeholders = []

    for key, value in secrets.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            # Recurse into nested dicts
            placeholders.extend(find_placeholder_secrets(value, full_key))
        elif isinstance(value, str) and is_placeholder_value(value):
            placeholders.append(full_key)

    return placeholders


def set_nested_value(data: dict[str, Any], key_path: str, value: Any) -> None:
    """Set a value at a nested key path using dot-notation.

    Creates intermediate dictionaries as needed. Modifies data in place.

    Args:
        data: The dictionary to modify.
        key_path: Dot-separated key path (e.g., "hetzner.api_token").
        value: The value to set at the path.

    Examples:
        >>> data = {}
        >>> set_nested_value(data, "hetzner.api_token", "secret123")
        >>> data
        {'hetzner': {'api_token': 'secret123'}}

        >>> data = {"hetzner": {"location": "nbg1"}}
        >>> set_nested_value(data, "hetzner.api_token", "secret123")
        >>> data
        {'hetzner': {'location': 'nbg1', 'api_token': 'secret123'}}
    """
    parts = key_path.split(".")
    current = data

    # Navigate/create intermediate dicts
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]

    # Set the final value
    current[parts[-1]] = value


def get_nested_value(data: dict[str, Any], key_path: str) -> Any | None:
    """Get a value at a nested key path using dot-notation.

    Args:
        data: The dictionary to read from.
        key_path: Dot-separated key path (e.g., "hetzner.api_token").

    Returns:
        The value at the path, or None if any part of the path doesn't exist.

    Examples:
        >>> data = {"hetzner": {"api_token": "secret123"}}
        >>> get_nested_value(data, "hetzner.api_token")
        'secret123'

        >>> get_nested_value(data, "hetzner.missing")
        None
    """
    parts = key_path.split(".")
    current = data

    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]

    return current


def is_sops_encrypted(file_path: Path) -> bool:
    """Check if a YAML file is SOPS-encrypted.

    SOPS-encrypted files contain a 'sops' top-level key with encryption metadata.
    Plaintext YAML files don't have this key.

    Args:
        file_path: Path to the YAML file to check.

    Returns:
        True if the file is SOPS-encrypted, False if plaintext or doesn't exist.
    """
    if not file_path.exists():
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return isinstance(data, dict) and "sops" in data
    except (OSError, yaml.YAMLError):
        return False


def should_encrypt_secrets(environment: str, config: Any = None) -> bool:
    """Check if secrets should be encrypted for an environment.

    Uses the encrypt_{environment}_secrets config option, which defaults to True.
    This supports DJB_ENCRYPT_{ENVIRONMENT}_SECRETS environment variable overrides.

    Args:
        environment: Environment name (development, staging, production).
        config: Optional DjbConfig instance. If None, uses djb_get_config().

    Returns:
        True if secrets should be encrypted, False if plaintext is allowed.
    """
    if config is None:
        try:
            config = djb_get_config()
        except Exception:
            # If config can't be loaded (e.g., during init), default to encrypted
            return True

    field_name = f"encrypt_{environment}_secrets"
    return getattr(config, field_name, True)


def encrypt_file(
    runner: CmdRunner,
    input_path: Path,
    output_path: Path | None = None,
    public_keys: list[str] | None = None,
    sops_config: Path | None = None,
) -> None:
    """Encrypt a YAML file using SOPS.

    Args:
        runner: CmdRunner instance for executing commands.
        input_path: Path to plaintext YAML file
        output_path: Path for encrypted output (defaults to input_path)
        public_keys: Age public keys to encrypt for (overrides sops config)
        sops_config: Path to .sops.yaml config file

    Raises:
        SopsError: If encryption fails or times out.
    """
    if output_path is None:
        output_path = input_path

    cmd = ["sops", "--encrypt"]

    if public_keys:
        cmd.extend(["--age", ",".join(public_keys)])

    if sops_config:
        cmd.extend(["--config", str(sops_config)])

    cmd.extend(["--output", str(output_path), str(input_path)])

    try:
        result = runner.run(cmd, timeout=SOPS_TIMEOUT)
    except CmdTimeout as e:
        raise SopsError(f"SOPS encryption timed out after {SOPS_TIMEOUT}s") from e

    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Provide helpful suggestions based on common errors
        hint = ""
        if "no matching keys found" in stderr.lower():
            hint = " Check that public_keys are valid age public keys (starting with 'age1')."
        elif "could not find public key" in stderr.lower():
            hint = " Ensure the age public key is correct and in the .sops.yaml file."

        raise SopsError(f"SOPS encryption failed for {input_path.name}: {stderr}{hint}")


def decrypt_file(
    runner: CmdRunner,
    input_path: Path,
    output_path: Path | None = None,
    key_path: Path | None = None,
) -> str:
    """Decrypt a SOPS-encrypted YAML file, or read a plaintext YAML file.

    If the file is not SOPS-encrypted (no 'sops' metadata), it's assumed to be
    plaintext and the content is returned directly without calling SOPS.

    Args:
        runner: CmdRunner instance for executing commands.
        input_path: Path to encrypted or plaintext YAML file
        output_path: Path for decrypted output (if None, returns content)
        key_path: Path to age private key file (not needed for plaintext files)

    Returns:
        Decrypted/plaintext content as string (if output_path is None)

    Raises:
        SopsError: If decryption fails or times out.
    """
    # Check if file is plaintext (not SOPS-encrypted)
    if not is_sops_encrypted(input_path):
        content = input_path.read_text(encoding="utf-8")
        if output_path:
            output_path.write_text(content, encoding="utf-8")
        return content

    # File is SOPS-encrypted, use SOPS to decrypt
    env: dict[str, str] = {}
    if key_path:
        env["SOPS_AGE_KEY_FILE"] = str(key_path)

    cmd = ["sops", "--decrypt"]

    if output_path:
        cmd.extend(["--output", str(output_path)])

    cmd.append(str(input_path))

    try:
        result = runner.run(cmd, env=env, timeout=SOPS_TIMEOUT)
    except CmdTimeout as e:
        raise SopsError(
            f"SOPS decryption timed out after {SOPS_TIMEOUT}s. "
            f"Ensure your age key can decrypt {input_path.name}."
        ) from e

    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Provide helpful suggestions based on common errors
        hint = ""
        if "no key found in file" in stderr.lower() or "could not decrypt" in stderr.lower():
            hint = (
                " Your age key may not be authorized to decrypt this file. "
                "Ask a team member to add your key and run 'djb secrets rotate'."
            )
        elif "no such file" in stderr.lower() or "sops_age_key_file" in stderr.lower():
            hint = " Ensure your age key exists. Run 'djb init' to create one."

        raise SopsError(f"SOPS decryption failed for {input_path.name}: {stderr}{hint}")

    return result.stdout


def rotate_keys(
    runner: CmdRunner,
    input_path: Path,
    public_keys: list[str],
    key_path: Path | None = None,
    sops_config: Path | None = None,
) -> None:
    """Re-encrypt a file with new recipients.

    This decrypts the file and re-encrypts it with the new set of public keys.
    The new recipients are read from the .sops.yaml config file, not from
    command line arguments.

    Args:
        runner: CmdRunner instance for executing commands.
        input_path: Path to encrypted YAML file
        public_keys: New list of age public keys to encrypt for (unused, kept
                    for backwards compatibility - keys are read from config)
        key_path: Path to age private key file for decryption
        sops_config: Path to .sops.yaml config file (defaults to
                    input_path.parent / ".sops.yaml")

    Raises:
        SopsError: If key rotation fails or times out.
    """
    # Unused parameter kept for backwards compatibility
    _ = public_keys

    env: dict[str, str] = {}
    if key_path:
        env["SOPS_AGE_KEY_FILE"] = str(key_path)

    # Derive config path from input file location if not provided
    if sops_config is None:
        sops_config = input_path.parent / ".sops.yaml"

    # Use sops updatekeys to rotate recipients
    # Note: --config must come before the subcommand (it's a global flag)
    # Note: updatekeys reads recipients from config file, not --age flag
    cmd = [
        "sops",
        "--config",
        str(sops_config),
        "updatekeys",
        "--yes",
        str(input_path),
    ]

    try:
        result = runner.run(cmd, env=env, timeout=SOPS_TIMEOUT)
    except CmdTimeout as e:
        raise SopsError(
            f"SOPS key rotation timed out after {SOPS_TIMEOUT}s for {input_path.name}"
        ) from e

    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Provide helpful suggestions based on common errors
        hint = ""
        if "could not decrypt" in stderr.lower() or "no key found" in stderr.lower():
            hint = (
                " You may not have permission to decrypt this file. "
                "Another team member who can decrypt must perform the rotation."
            )
        elif "no such file" in stderr.lower():
            hint = f" Ensure {sops_config} exists and contains the new recipient keys."

        raise SopsError(f"SOPS key rotation failed for {input_path.name}: {stderr}{hint}")


class SecretsManager:
    """Manages encrypted secrets for different environments using SOPS.

    Automatically handles GPG-protected age keys. When the age private key
    is encrypted with GPG (.age/keys.txt.gpg), load_secrets will decrypt it
    temporarily and re-encrypt after use.

    Example:
        manager = SecretsManager(runner, project_dir)
        secrets = manager.load_secrets("production")
        # or with Mode enum:
        secrets = manager.load_for_mode(Mode.PRODUCTION)
    """

    def __init__(
        self,
        runner: CmdRunner,
        project_dir: Path,
        *,
        secrets_dir: Path | None = None,
        key_path: Path | None = None,
    ):
        """Initialize secrets manager.

        Args:
            runner: CmdRunner instance for executing commands.
            project_dir: Project root directory
            secrets_dir: Directory containing secrets (defaults to project_dir/secrets)
            key_path: Path to age private key (defaults to project_dir/.age/keys.txt).
                     If provided explicitly, GPG protection handling is skipped
                     (caller is assumed to manage the key themselves).
        """
        self.runner = runner
        self.project_dir = Path(project_dir)
        self.secrets_dir = secrets_dir or get_default_secrets_dir(project_dir)
        self._explicit_key_path = key_path
        self._default_key_path = get_default_key_path(project_dir)

    @property
    def key_path(self) -> Path:
        """Get the age private key path."""
        return self._explicit_key_path or self._default_key_path

    def _is_key_protected(self) -> bool:
        """Check if the age key is GPG-protected.

        Returns False if caller provided an explicit key_path (they're managing it).
        """
        if self._explicit_key_path is not None:
            return False
        return is_age_key_protected(self.project_dir, self.runner)

    @contextmanager
    def _with_protected_key(self) -> Generator[Path, None, None]:
        """Context manager for operations requiring the age private key.

        If the key is GPG-protected, decrypts it temporarily and re-encrypts
        on exit. If an explicit key_path was provided at init, uses that directly.

        Yields:
            Path to the usable (decrypted) key file.
        """
        if self._is_key_protected():
            with protected_age_key(self.project_dir, self.runner) as key_path:
                yield key_path
        else:
            yield self.key_path

    def load_secrets(self, environment: str) -> dict[str, Any]:
        """Load and decrypt secrets for a given environment.

        Automatically handles GPG-protected age keys. If the age private key
        is encrypted with GPG, it will be decrypted temporarily for the SOPS
        operation and re-encrypted afterward.

        Args:
            environment: Environment name (development, staging, production)

        Returns:
            Dictionary of decrypted secrets

        Raises:
            FileNotFoundError: If secrets file doesn't exist
            SopsError: If decryption fails
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        with self._with_protected_key() as key_path:
            decrypted = decrypt_file(self.runner, secrets_file, key_path=key_path)
            return yaml.safe_load(decrypted)

    def load_for_mode(self, mode: "Mode") -> dict[str, Any]:
        """Load secrets for a deployment mode.

        Convenience method that maps Mode enum to environment name.

        Args:
            mode: Deployment mode (Mode.DEVELOPMENT, Mode.STAGING, Mode.PRODUCTION)

        Returns:
            Dictionary of decrypted secrets
        """
        return self.load_secrets(mode.value)

    def save_secrets(
        self,
        environment: str,
        secrets: dict[str, Any],
        *,
        public_keys: list[str] | None = None,
    ) -> None:
        """Save secrets for a given environment.

        Automatically determines encryption based on config:
        - Whether to encrypt (via should_encrypt_secrets config)
        - Which keys to use:
          - Development: user's own key only
          - Staging/production: all team keys from .sops.yaml

        Args:
            environment: Environment name (development, staging, production)
            secrets: Dictionary of secrets to save
            public_keys: Override automatic key selection. When provided,
                        secrets are encrypted with these keys. Use for special
                        cases like initial setup or test fixtures.
        """
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        secrets_file = self.secrets_dir / f"{environment}.yaml"

        # Determine encryption keys if not explicitly provided
        if public_keys is None:
            public_keys = self._get_encryption_keys(environment)

        # Save as plaintext if no encryption needed
        if not public_keys:
            with open(secrets_file, "w", encoding="utf-8") as f:
                yaml.dump(secrets, f, default_flow_style=False, sort_keys=False)
            return

        # Encrypt with SOPS
        temp_file = self.secrets_dir / f".{environment}.tmp.yaml"

        try:
            # Write plaintext to temp file
            with open(temp_file, "w", encoding="utf-8") as f:
                yaml.dump(secrets, f, default_flow_style=False, sort_keys=False)

            # Encrypt to final location
            encrypt_file(self.runner, temp_file, secrets_file, public_keys=public_keys)
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()

    def _get_encryption_keys(self, environment: str) -> list[str] | None:
        """Get encryption keys for environment based on config.

        Returns:
            - None if encryption is disabled for this environment
            - [user_key] for development (user secrets)
            - [all_team_keys] or [user_key] for staging/production (project secrets)
        """
        if not should_encrypt_secrets(environment):
            return None

        user_public_key = get_public_key_from_private(self.runner, self.key_path)

        # Development secrets are encrypted with user's key only (not shared)
        if self._is_user_secret(environment):
            return [user_public_key]

        # Project secrets (staging/production) are encrypted for all team members
        all_keys = self.recipient_keys
        return all_keys if all_keys else [user_public_key]

    def _is_user_secret(self, environment: str) -> bool:
        """Check if environment is a user secret (development only)."""
        return environment == "development"

    @property
    def sops_config_path(self) -> Path:
        """Path to .sops.yaml configuration file."""
        return self.secrets_dir / ".sops.yaml"

    @property
    def recipients(self) -> dict[str, str]:
        """Get recipients from .sops.yaml.

        Returns:
            Dict mapping public_key -> identity (identity may be empty string).
            Identity format is "Name <email>" or just "email" for legacy configs.
        """
        if not self.sops_config_path.exists():
            return {}

        content = self.sops_config_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        recipients: dict[str, str] = {}
        current_identity = ""

        for line in lines:
            stripped = line.strip()
            # Look for identity comments (# Name <email> or # email@example.com)
            if stripped.startswith("# ") and "@" in stripped:
                current_identity = stripped[2:].strip()
            # Look for age public keys (- age1...)
            elif stripped.startswith("- age1"):
                key = stripped[2:].strip()
                recipients[key] = current_identity
                current_identity = ""
            # Reset identity if we hit something else
            elif stripped and not stripped.startswith("#"):
                current_identity = ""

        return recipients

    @property
    def recipient_keys(self) -> list[str]:
        """Get all public keys from .sops.yaml.

        Returns:
            List of public key strings
        """
        return list(self.recipients.keys())

    def add_recipient(self, public_key: str, identity: str) -> None:
        """Add a recipient to the configuration.

        Args:
            public_key: Age public key (age1...)
            identity: Identity string (e.g., "Name <email>" or "email")
        """
        recipients = self.recipients
        recipients[public_key] = identity
        self.save_config(recipients)

    def remove_recipient(self, public_key: str) -> bool:
        """Remove a recipient from the configuration.

        Args:
            public_key: Age public key to remove

        Returns:
            True if recipient was removed, False if not found
        """
        recipients = self.recipients
        if public_key not in recipients:
            return False
        del recipients[public_key]
        self.save_config(recipients)
        return True

    def save_config(self, recipients: dict[str, str] | list[str]) -> Path:
        """Save recipients to .sops.yaml configuration.

        Uses atomic write (temp file + rename) to prevent corruption.

        Args:
            recipients: Either a dict mapping public_key -> identity, or a list of keys.
                       Identity should be git-style: "Name <email>" or just "email".

        Returns:
            Path to the .sops.yaml file
        """
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        temp_config_path = self.secrets_dir / ".sops.yaml.tmp"

        # Normalize to dict
        if isinstance(recipients, list):
            recipients = {key: "" for key in recipients}

        # Build config content with identity comments above each key
        lines = [
            "creation_rules:",
            "  - path_regex: '.*\\.yaml$'",
            "    key_groups:",
            "      - age:",
        ]

        for key, identity in recipients.items():
            if identity:
                lines.append(f"          # {identity}")
            lines.append(f"          - {key}")

        # Atomic write: write to temp file, then rename
        try:
            with open(temp_config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            temp_config_path.rename(self.sops_config_path)
        except OSError:
            # Clean up temp file on failure
            if temp_config_path.exists():
                temp_config_path.unlink()
            raise

        return self.sops_config_path

    def rotate_keys(
        self,
        environment: str,
        public_keys: list[str],
    ) -> None:
        """
        Re-encrypt secrets with new set of public keys.

        Args:
            environment: Environment name
            public_keys: New list of age public keys to encrypt for
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        rotate_keys(self.runner, secrets_file, public_keys, self.key_path)

    def view_secrets(self, environment: str, key: str | None = None) -> dict[str, Any] | Any:
        """View decrypted secrets for an environment.

        Handles GPG-protected age keys automatically.

        Args:
            environment: Environment name (development, staging, production)
            key: Optional specific key to retrieve (supports dot-notation)

        Returns:
            Full secrets dict if key is None, otherwise the value at that key.

        Raises:
            FileNotFoundError: If secrets file doesn't exist
            SopsError: If decryption fails
            KeyError: If specified key doesn't exist
        """
        secrets_data = self.load_secrets(environment)

        if key is None:
            return secrets_data

        value = get_nested_value(secrets_data, key)
        if value is None and key not in secrets_data:
            raise KeyError(f"Key '{key}' not found in {environment} secrets")
        return value

    def set_secret(self, environment: str, key: str, value: str) -> None:
        """Set a single secret value using dot-notation key path.

        Loads existing secrets, updates the key, and saves.
        Handles GPG-protected age keys automatically.

        Args:
            environment: Environment name (development, staging, production)
            key: Key path in dot-notation (e.g., "hetzner.api_token")
            value: Value to set

        Raises:
            FileNotFoundError: If secrets file doesn't exist
            SopsError: If decryption or encryption fails
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"
        if not secrets_file.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_file}")

        secrets_data = self.load_secrets(environment)
        set_nested_value(secrets_data, key, value)
        self.save_secrets(environment, secrets_data)

    def edit_secrets(self, environment: str, *, interactive: bool = True) -> int:
        """Open secrets file in SOPS editor.

        Uses SOPS to decrypt the file, open $EDITOR, and re-encrypt on save.
        Handles GPG-protected age keys automatically.

        For unencrypted environments (encryption disabled via config), opens
        the file directly in the editor without SOPS.

        Args:
            environment: Environment name (development, staging, production)
            interactive: If True (default), runs editor interactively.

        Returns:
            Editor exit code (0 for success).

        Raises:
            FileNotFoundError: If secrets file doesn't exist
        """
        secrets_file = self.secrets_dir / f"{environment}.yaml"

        # Handle auto-transition from encrypted to plaintext
        if not should_encrypt_secrets(environment) and is_sops_encrypted(secrets_file):
            secrets_data = self.load_secrets(environment)
            self.save_secrets(environment, secrets_data, public_keys=[])

        # If encryption is disabled, use $EDITOR directly
        if not should_encrypt_secrets(environment):
            editor = os.environ.get("EDITOR", "vim")
            result = self.runner.run(
                [editor, str(secrets_file)],
                interactive=interactive,
            )
            return result.returncode

        # Use SOPS to edit the file (SOPS uses $EDITOR automatically)
        with self._with_protected_key() as key_path:
            result = self.runner.run(
                ["sops", "--config", str(self.sops_config_path), str(secrets_file)],
                env={"SOPS_AGE_KEY_FILE": str(key_path)},
                interactive=interactive,
            )
            return result.returncode

    def export_private_key(self) -> str:
        """Export the private key content for backup.

        Returns just the AGE-SECRET-KEY-... line suitable for storing
        in a password manager.

        Handles GPG-protected age keys automatically.

        Returns:
            The AGE-SECRET-KEY line.

        Raises:
            FileNotFoundError: If key file doesn't exist.
            SopsError: If no valid key found in file.
        """
        with self._with_protected_key() as key_path:
            if not key_path.exists():
                raise FileNotFoundError(f"Key file not found: {key_path}")

            content = key_path.read_text()
            for line in content.splitlines():
                if line.startswith("AGE-SECRET-KEY-"):
                    return line

            raise SopsError("No AGE-SECRET-KEY found in key file")

    def get_public_key(self) -> str:
        """Get the public key from the private key file.

        Handles GPG-protected age keys automatically.

        Returns:
            The public key string (age1...).

        Raises:
            FileNotFoundError: If key file doesn't exist.
            SopsError: If key derivation fails.
        """
        with self._with_protected_key() as key_path:
            return get_public_key_from_private(self.runner, key_path)

    def rotate_all_secrets(
        self,
        environments: list[str],
        *,
        skip_missing: bool = True,
    ) -> dict[str, Exception | None]:
        """Re-encrypt secrets for multiple environments with current recipients.

        Uses recipients from .sops.yaml and handles GPG-protected keys.

        Args:
            environments: List of environment names to re-encrypt
            skip_missing: If True, skip missing files instead of raising

        Returns:
            Dict mapping environment -> None (success) or Exception (failure)
        """
        results: dict[str, Exception | None] = {}
        public_keys = self.recipient_keys

        with self._with_protected_key() as key_path:
            for env in environments:
                secrets_file = self.secrets_dir / f"{env}.yaml"

                if not secrets_file.exists():
                    if skip_missing:
                        continue
                    results[env] = FileNotFoundError(f"Secrets file not found: {secrets_file}")
                    continue

                # Skip unencrypted environments
                if not should_encrypt_secrets(env):
                    continue

                try:
                    rotate_keys(
                        self.runner, secrets_file, public_keys, key_path, self.sops_config_path
                    )
                    results[env] = None
                except SopsError as e:
                    results[env] = e

        return results


def load_secrets(
    runner: CmdRunner,
    environment: str = "dev",
    secrets_dir: Path | None = None,
    key_path: Path | None = None,
    project_dir: Path | None = None,
    *,
    auto_transition: bool = True,
) -> dict[str, Any]:
    """
    Convenience function to load and decrypt secrets.

    Handles both plaintext and GPG-protected age keys. If the key is
    GPG-protected (.age/keys.txt.gpg), it will be temporarily decrypted
    for the duration of this call.

    If encryption is disabled for the environment (via encrypt_{env}_secrets config)
    and the file is currently SOPS-encrypted, auto_transition will decrypt it once
    and save it as plaintext for future loads.

    Args:
        runner: CmdRunner instance for executing commands.
        environment: Environment name (dev, staging, production)
        secrets_dir: Directory containing secrets (defaults to project_dir/secrets)
        key_path: Path to age key file (defaults to project_dir/.age/keys.txt)
        project_dir: Project root directory. Required if secrets_dir and key_path
            are not both provided. Can be inferred from secrets_dir.
        auto_transition: If True (default), automatically convert encrypted files
            to plaintext when encryption is disabled for the environment.

    Returns:
        Dictionary of decrypted secrets
    """
    # Infer project_dir from secrets_dir if not provided
    if project_dir is None and secrets_dir is not None:
        project_dir = secrets_dir.parent

    if secrets_dir is None:
        if project_dir is None:
            raise ValueError("Either secrets_dir or project_dir must be provided")
        secrets_dir = get_default_secrets_dir(project_dir)

    secrets_file = secrets_dir / f"{environment}.yaml"

    # Check if encryption is disabled for this environment
    encrypt_enabled = should_encrypt_secrets(environment)

    # If encryption is disabled and file is plaintext, no key needed
    if not encrypt_enabled and secrets_file.exists() and not is_sops_encrypted(secrets_file):
        with open(secrets_file, encoding="utf-8") as f:
            return yaml.safe_load(f)

    if key_path is None:
        if project_dir is None:
            raise ValueError("Either key_path or project_dir must be provided")
        key_path = get_default_key_path(project_dir)

    # Helper function to load and optionally transition to plaintext
    def _load_and_maybe_transition(manager: SecretsManager) -> dict[str, Any]:
        secrets_data = manager.load_secrets(environment)

        # Auto-transition: if encryption disabled but file is encrypted, save as plaintext
        if auto_transition and not encrypt_enabled and is_sops_encrypted(secrets_file):
            manager.save_secrets(environment, secrets_data, public_keys=[])

        return secrets_data

    # Check if we have a GPG-protected key
    encrypted_key_path = get_encrypted_key_path(key_path)
    if not key_path.exists() and encrypted_key_path.exists():
        # project_dir is guaranteed to be set here due to inference above
        assert project_dir is not None
        with protected_age_key(project_dir, runner) as actual_key_path:
            manager = SecretsManager(
                runner, project_dir, secrets_dir=secrets_dir, key_path=actual_key_path
            )
            return _load_and_maybe_transition(manager)

    # If encryption is disabled and file needs decryption, we still need the key
    # But if file is plaintext, we already returned above
    if not key_path.exists() and not encrypt_enabled:
        # File must be encrypted but no key available
        raise FileNotFoundError(
            f"Age key file not found: {key_path}. "
            f"Need key to decrypt {environment} secrets for transition to plaintext. "
            f"Generate one with: djb init"
        )

    if not key_path.exists():
        raise FileNotFoundError(
            f"Age key file not found: {key_path}. " f"Generate one with: djb init"
        )

    assert project_dir is not None  # Inferred or provided
    manager = SecretsManager(runner, project_dir, secrets_dir=secrets_dir, key_path=key_path)
    return _load_and_maybe_transition(manager)


def load_secrets_for_mode(
    runner: CmdRunner,
    mode: "Mode",
    secrets_dir: Path | None = None,
    key_path: Path | None = None,
    project_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Load secrets for a deployment mode.

    This is a convenience wrapper around load_secrets() that maps
    Mode to the corresponding secrets environment:
    - Mode.DEVELOPMENT -> development.yaml
    - Mode.STAGING -> staging.yaml
    - Mode.PRODUCTION -> production.yaml

    Args:
        runner: CmdRunner instance for executing commands.
        mode: Deployment mode (from djb.types.Mode)
        secrets_dir: Directory containing secrets (defaults to project_dir/secrets)
        key_path: Path to age key file (defaults to project_dir/.age/keys.txt)
        project_dir: Project root directory. Required if secrets_dir and key_path
            are not both provided.

    Returns:
        Dictionary of decrypted secrets

    Example:
        >>> from djb.types import Mode
        >>> secrets = load_secrets_for_mode(runner, Mode.PRODUCTION, project_dir=Path("/my/project"))
    """
    return load_secrets(
        runner,
        environment=mode.value,
        secrets_dir=secrets_dir,
        key_path=key_path,
        project_dir=project_dir,
    )
