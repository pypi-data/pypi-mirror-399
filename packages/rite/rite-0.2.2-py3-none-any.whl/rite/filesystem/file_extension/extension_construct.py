# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Construct File Extension Module
===============================

Provides functionality to extract and normalize file extensions.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import os
from pathlib import PurePath

# =============================================================================
# Construction
# =============================================================================

# Common multi-part extensions you might care about
_COMPOUND_TAR_SUFFIXES: set[str] = {
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
    ".tar.zst",
}

# =============================================================================
# Functions
# =============================================================================


def extension_construct(
    filename: str,
    *,
    leading_dot: bool = True,
    compound: bool = True,
) -> str:
    """
    Extract a normalized file extension from `filename`.

    - Returns lowercase extension.
    - Returns "" if no extension.
    - Hidden files like ".env" have no extension.
    - If `compound=True`, merges well-known compound extensions
      (e.g. ".tar.gz").

    Parameters
    ----------
    filename : str
        Path or filename to inspect.
    leading_dot : bool, default True
        If True, result includes the leading dot; otherwise it's omitted.
    compound : bool, default True
        If True, return compound extensions (".tar.gz"). If False, only
        the last suffix (".gz").

    Examples
    --------
    extension_construct("photo.JPG")                      -> ".jpg"
    extension_construct("archive.tar.gz")                 -> ".tar.gz"
    extension_construct("archive.tar.gz", compound=False) -> ".gz"
    extension_construct(".env")                           -> ""
    extension_construct("/tmp/noext")                     -> ""

    """

    if not filename:
        return ""

    # Work with the basename only
    name: str = os.fspath(filename)
    base: str = os.path.basename(name).strip()

    if not base or (base.startswith(".") and base.count(".") == 1):
        # ".env", ".gitignore" -> no extension
        return ""

    p = PurePath(base)
    suffixes: list[str] = [
        s.lower() for s in p.suffixes
    ]  # each includes its dot

    if not suffixes:
        return ""

    ext = suffixes[-1]  # default: last suffix only

    if compound:
        # Join all suffixes if they match a known compound tar* pattern
        joined: str = "".join(suffixes)
        if any(joined.endswith(c) for c in _COMPOUND_TAR_SUFFIXES):
            ext = joined

    if not leading_dot:
        return ext.lstrip(".")

    return ext


# =============================================================================
# Exports
# =============================================================================

__all__: list[str] = [
    "extension_construct",
]
