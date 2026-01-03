from __future__ import annotations

import os
import sys
from pathlib import Path


def get_sdt_home() -> Path:
    """
    Get the base .sdt directory location.

    The directory location is determined by:
    1. SDT_HOME environment variable (if set)
    2. Platform-specific default:
       - Windows: %LOCALAPPDATA%/sdt (e.g., C:/Users/username/AppData/Local/sdt)
       - macOS/Linux: ~/.sdt

    Returns:
        Path: The base .sdt directory path.

    Examples:
        >>> # Default behavior
        >>> get_sdt_home()
        PosixPath('/Users/username/.sdt')

        >>> # With SDT_HOME override
        >>> os.environ['SDT_HOME'] = '/custom/path'
        >>> get_sdt_home()
        PosixPath('/custom/path')
    """
    # Allow override via environment variable
    sdt_home = os.environ.get("SDT_HOME", "").strip()
    if sdt_home:
        return Path(sdt_home).expanduser().resolve()

    # Use platform-appropriate default
    if sys.platform == "win32":
        # Windows: C:\Users\username\AppData\Local\sdt
        localappdata = os.environ.get("LOCALAPPDATA", "").strip()
        # Fallback to home directory if LOCALAPPDATA not set or empty
        base = Path(localappdata) if localappdata else Path.home() / "AppData" / "Local"
        return base / "sdt"
    else:
        # macOS/Linux: ~/.sdt
        return Path.home() / ".sdt"


def get_configs_dir() -> Path:
    """
    Get the configs directory path.

    Returns:
        Path: Path to the configs directory (e.g., ~/.sdt/configs).
    """
    return get_sdt_home() / "configs"


def get_notebooks_dir() -> Path:
    """
    Get the notebooks directory path.

    Returns:
        Path: Path to the notebooks directory (e.g., ~/.sdt/notebooks).
    """
    return get_sdt_home() / "notebooks"


def get_default_config_path() -> Path:
    """
    Get the default configuration file path.

    Returns:
        Path: Path to the default config file (e.g., ~/.sdt/configs/config.json).
    """
    return get_configs_dir() / "config.json"
