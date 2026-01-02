# =============================================================================
# Docstring
# =============================================================================

"""
Rite CLI Entry Point
====================

Command-line interface entry point for the rite package.

Usage:
    python -m rite [command] [options]
    rite [command] [options]

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import sys

# Import | Local Modules
from .cli import cli_main

# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Main entry point for rite CLI."""
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
