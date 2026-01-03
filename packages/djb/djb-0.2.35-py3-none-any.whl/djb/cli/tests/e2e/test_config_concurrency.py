"""Concurrency tests for djb_get_config cache initialization.

Tests verify that multiple threads calling djb_get_config() concurrently
all receive the same cached instance, and that _bypass_cache properly
isolates threads.

Design notes:
- Python's GIL provides some protection for simple operations like dict access
  and attribute assignment, but this is an implementation detail
- The config cache uses a module-level global (_cached_config) with
  simple assignment, which is GIL-protected in CPython
- These tests document the expected behavior and verify it holds
- Uses _bypass_cache=True in fixtures to avoid polluting the real cache

Threading notes:
- CPython's GIL makes single bytecode operations atomic
- Assignment to _cached_config is a single STORE_GLOBAL operation
- However, this is implementation-specific and not a language guarantee
- These tests verify current behavior works correctly under concurrency
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from djb.config import DjbConfig, djb_get_config
from djb.types import Mode

pytestmark = pytest.mark.e2e_marker


class TestConcurrentConfigCache:
    """Test concurrent access to djb_get_config cache.

    These tests verify that the config cache behaves correctly when
    accessed from multiple threads simultaneously. All tests use
    _bypass_cache=True to avoid polluting the module-level cache.
    """

    def test_bypass_cache_isolates_threads(self, pyproject_dir_with_git: Path) -> None:
        """Each thread with _bypass_cache=True gets a fresh config instance.

        When using _bypass_cache=True, each call creates a new config
        instance. This test verifies that concurrent calls with bypass
        all get distinct (but equivalent) instances.
        """
        configs: list[DjbConfig] = []
        configs_lock = threading.Lock()

        def get_config(n: int) -> None:
            cfg = djb_get_config(
                project_dir=pyproject_dir_with_git,
                env={},  # Isolate from environment
                _bypass_cache=True,
            )
            with configs_lock:
                configs.append(cfg)

        # Launch 5 threads
        threads = [threading.Thread(target=get_config, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(configs) == 5, "All threads should complete"

        # Each config should be a distinct object
        config_ids = [id(cfg) for cfg in configs]
        assert len(set(config_ids)) == 5, (
            "Each _bypass_cache call should create a new instance. "
            f"Got {len(set(config_ids))} unique objects instead of 5"
        )

        # But all should have the same values
        first = configs[0]
        for i, cfg in enumerate(configs[1:], start=2):
            assert (
                cfg.project_name == first.project_name
            ), f"Config {i} has different project_name: {cfg.project_name} vs {first.project_name}"
            assert (
                cfg.project_dir == first.project_dir
            ), f"Config {i} has different project_dir: {cfg.project_dir} vs {first.project_dir}"

    def test_concurrent_bypass_no_interference(self, pyproject_dir_with_git: Path) -> None:
        """Concurrent _bypass_cache calls with different overrides don't interfere.

        Each thread can request a config with different override values,
        and each should get its own instance with the correct values.
        """
        results: dict[int, DjbConfig] = {}
        results_lock = threading.Lock()
        modes = [Mode.DEVELOPMENT, Mode.STAGING, Mode.PRODUCTION]

        def get_config_with_mode(n: int, mode: Mode) -> None:
            cfg = djb_get_config(
                project_dir=pyproject_dir_with_git,
                mode=mode,
                env={},
                _bypass_cache=True,
            )
            with results_lock:
                results[n] = cfg

        # Each thread gets a config with a different mode
        threads = [
            threading.Thread(target=get_config_with_mode, args=(i, modes[i % len(modes)]))
            for i in range(6)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 6, "All threads should complete"

        # Verify each thread got the mode it requested
        for i, cfg in results.items():
            expected_mode = modes[i % len(modes)]
            assert (
                cfg.mode == expected_mode
            ), f"Thread {i} expected mode {expected_mode}, got {cfg.mode}"


class TestConfigCacheEdgeCases:
    """Edge case tests for djb_get_config.

    Tests document expected behavior for edge cases like empty config,
    invalid inputs, and error conditions.
    """

    def test_nonexistent_project_dir_creates_minimal_config(self, project_dir: Path) -> None:
        """djb_get_config with nonexistent project_dir still creates config.

        The config system is designed to be resilient - it falls back to
        defaults when files don't exist. This documents that behavior.

        Note: The project_name will be derived from the directory name
        when no pyproject.toml exists.
        """
        nonexistent = project_dir / "does-not-exist"

        # Should not raise - falls back to defaults
        cfg = djb_get_config(
            project_dir=nonexistent,
            env={},
            _bypass_cache=True,
        )

        # Config is created with the specified project_dir
        assert cfg.project_dir == nonexistent
        # project_name is derived from directory name when no pyproject.toml
        assert cfg.project_name == "does-not-exist"

    def test_empty_env_isolates_from_system(self, pyproject_dir_with_git: Path) -> None:
        """Passing empty env dict isolates from system environment.

        This is important for test isolation. When env={} is passed,
        no DJB_* environment variables should affect the config.
        """
        cfg = djb_get_config(
            project_dir=pyproject_dir_with_git,
            env={},  # Explicitly empty, ignoring system env
            _bypass_cache=True,
        )

        # Should use defaults, not environment values
        assert cfg.project_name == "test-project"
        assert cfg.project_dir == pyproject_dir_with_git

    def test_env_override_takes_precedence(self, pyproject_dir_with_git: Path) -> None:
        """Environment variables override file config.

        When env contains DJB_* variables, they should take precedence
        over values in config files.
        """
        cfg = djb_get_config(
            project_dir=pyproject_dir_with_git,
            env={"DJB_MODE": "production"},
            _bypass_cache=True,
        )

        assert (
            cfg.mode == Mode.PRODUCTION
        ), f"DJB_MODE env var should set mode to production, got {cfg.mode}"
