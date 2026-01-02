# =============================================================================
# Docstring
# =============================================================================

"""
Version Information
===================

Single source of truth for package version.

The version is read from package metadata when installed,
with a fallback for development environments.

"""

# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from importlib.metadata import PackageNotFoundError, version

# =============================================================================
# Version
# =============================================================================

try:
    __version__ = version("rite")
except PackageNotFoundError:
    # Package is not installed (development mode)
    __version__ = "0.2.2"  # Keep in sync with pyproject.toml

# =============================================================================
# Exports
# =============================================================================

__all__: list[str] = ["__version__"]
