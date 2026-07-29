"""Filesystem path safety policy shared by Project Forge discovery tools."""

from __future__ import annotations

import os
from pathlib import Path


PROTECTED_FILESYSTEM_PATHS = (
    Path("/home/cole/cerberus"),
    Path("/mnt/storage/Cole/cerberus"),
)


def normalize_path_without_access(path: Path) -> Path:
    """Normalize a path lexically without reading or resolving its contents."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def is_protected_filesystem_path(path: Path) -> bool:
    """Return true for either protected path or anything beneath it."""

    candidate = normalize_path_without_access(path)
    for protected in PROTECTED_FILESYSTEM_PATHS:
        normalized_protected = normalize_path_without_access(protected)
        if candidate == normalized_protected or normalized_protected in candidate.parents:
            return True
    return False
