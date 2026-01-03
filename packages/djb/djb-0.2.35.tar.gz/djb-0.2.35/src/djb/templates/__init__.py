"""
djb.templates - Template files for djb project scaffolding.

This module provides access to template files used by djb commands
for generating project files like Dockerfiles, K8s manifests, etc.

Exports:
    DJB_TEMPLATES_DIR - Path to the templates directory
"""

from __future__ import annotations

from pathlib import Path

# Path to the templates directory
DJB_TEMPLATES_DIR = Path(__file__).parent
