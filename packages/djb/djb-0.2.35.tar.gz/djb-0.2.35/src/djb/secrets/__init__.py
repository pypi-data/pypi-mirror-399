"""
djb.secrets - Encrypted secrets management with SOPS.

Provides encrypted secrets storage using SOPS with age encryption.

Quick start:
    from djb.secrets import SecretsManager, SopsError

    try:
        manager = SecretsManager(runner, project_dir)
        secrets = manager.load_secrets("production")
        # or with Mode enum:
        secrets = manager.load_for_mode(Mode.PRODUCTION)
    except SopsError as e:
        print(f"Decryption failed: {e}")

Public API:
    Core:
        SecretsManager - High-level secrets management class (recommended)
            - load_secrets(env) - Load decrypted secrets (handles GPG protection)
            - load_for_mode(mode) - Load secrets for a Mode enum
            - save_secrets(env, data) - Save encrypted secrets
            - view_secrets(env, key) - View secrets or specific key
            - set_secret(env, key, value) - Set a secret value
            - edit_secrets(env) - Open secrets in SOPS editor
            - export_private_key() - Export private key for backup
            - get_public_key() - Get public key from private key
            - rotate_all_secrets(envs) - Re-encrypt for updated recipients
            - recipients - Property: dict of public_key -> identity
            - recipient_keys - Property: list of public keys
            - sops_config_path - Property: path to .sops.yaml
            - save_config(recipients) - Write .sops.yaml
        encrypt_file, decrypt_file - SOPS file encryption/decryption
        generate_age_key, AgeKeyPair - Create new age keypair
        parse_identity, ParsedIdentity - Parsed git-style identity strings
        SopsError - SOPS operation failures

    Django Integration:
        load_secrets_for_django - Load secrets with Django environment detection
        lazy_database_config - Lazy-loading database config (defers GPG decryption)

    Config:
        SECRETS_ENVIRONMENTS - Standard environment names

    Errors:
        GpgError, GpgTimeoutError, ProtectedFileError - Error classes

    Initialization:
        init_or_upgrade_secrets - Set up secrets infrastructure
        SecretsStatus - Initialization status enum

    Internal (not part of public API):
        protected_age_key - Use SecretsManager methods instead
        protect_age_key, unprotect_age_key - Use CLI commands instead
        is_age_key_protected - Use SecretsManager internally
        GPG functions - Internal to secrets module
"""

from __future__ import annotations

from djb.secrets.core import (
    SOPS_TIMEOUT,
    AgeKeyPair,
    ParsedIdentity,
    SecretsManager,
    SopsError,
    check_age_installed,
    check_sops_installed,
    decrypt_file,
    encrypt_file,
    find_placeholder_secrets,
    format_identity,
    generate_age_key,
    get_nested_value,
    get_public_key_from_private,
    is_placeholder_value,
    is_sops_encrypted,
    is_valid_age_public_key,
    load_secrets,
    load_secrets_for_mode,
    parse_identity,
    rotate_keys,
    set_nested_value,
    should_encrypt_secrets,
)
from djb.secrets.django import lazy_database_config, load_secrets_for_django
from djb.secrets.paths import (
    get_default_key_path,
    get_default_secrets_dir,
    get_encrypted_key_path,
)
from djb.secrets.gpg import (
    GPG_INTERACTIVE_TIMEOUT,
    GPG_TIMEOUT,
    GpgError,
    GpgTimeoutError,
    check_gpg_installed,
    ensure_loopback_pinentry,
    generate_gpg_key,
    gpg_decrypt_file,
    gpg_encrypt_file,
    has_gpg_secret_key,
    init_gpg_agent_config,
    is_gpg_encrypted,
)
from djb.secrets.init import (
    PROJECT_SECRETS_ENVIRONMENTS,
    SECRETS_ENVIRONMENTS,
    USER_SECRETS_ENVIRONMENTS,
    SecretsStatus,
    init_or_upgrade_secrets,
)
from djb.secrets.protected import (
    ProtectedFileError,
    is_age_key_protected,
    protect_age_key,
    protected_age_key,
    unprotect_age_key,
)

__all__ = [
    # Core SOPS functions
    "AgeKeyPair",
    "ParsedIdentity",
    "SOPS_TIMEOUT",
    "SecretsManager",
    "SopsError",
    "check_age_installed",
    "check_sops_installed",
    "decrypt_file",
    "encrypt_file",
    "find_placeholder_secrets",
    "format_identity",
    "generate_age_key",
    "get_default_key_path",
    "get_default_secrets_dir",
    "get_encrypted_key_path",
    "get_nested_value",
    "get_public_key_from_private",
    "is_placeholder_value",
    "is_sops_encrypted",
    "is_valid_age_public_key",
    "lazy_database_config",
    "load_secrets",
    "load_secrets_for_django",
    "load_secrets_for_mode",
    "parse_identity",
    "rotate_keys",
    "set_nested_value",
    "should_encrypt_secrets",
    # GPG - only errors and check functions in public API
    "GpgError",
    "GpgTimeoutError",
    "check_gpg_installed",
    "generate_gpg_key",
    "has_gpg_secret_key",
    "init_gpg_agent_config",
    # Protected file access - only error in public API
    "ProtectedFileError",
    # Initialization
    "PROJECT_SECRETS_ENVIRONMENTS",
    "SECRETS_ENVIRONMENTS",
    "USER_SECRETS_ENVIRONMENTS",
    "SecretsStatus",
    "init_or_upgrade_secrets",
]
