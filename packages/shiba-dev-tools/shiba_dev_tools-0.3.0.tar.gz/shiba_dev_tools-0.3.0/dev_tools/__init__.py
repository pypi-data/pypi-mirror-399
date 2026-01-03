"""shiba-dev-tools: Shiba dev tools."""

from __future__ import annotations

try:
    from importlib.metadata import version

    __version__ = version("shiba-dev-tools")
except Exception:
    # Fallback for development or editable installs
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
