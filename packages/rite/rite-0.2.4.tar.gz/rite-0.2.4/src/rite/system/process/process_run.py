# =============================================================================
# Docstring
# =============================================================================

"""
Process Run Command
===================

Execute command in subprocess.

Examples
--------
>>> from rite.system.process import process_run
>>> code, out, err = process_run(["ls", "-la"], Path.cwd())

"""

# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from pathlib import Path
import subprocess

# =============================================================================
# Functions
# =============================================================================


def process_run(
    cmd: list[str],
    cwd: Path | str | None = None,
    check: bool = False,
    *,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
    stdin_text: str | None = None,
) -> tuple[int, str, str]:
    """
    Run command in subprocess and return result.

    Args:
        cmd: Command as list of strings.
        cwd: Working directory. Defaults to current.
        check: Raise exception on non-zero exit.
        timeout: Timeout in seconds. None means no timeout.
        env: Environment variables for the process.
        stdin_text: Text to send to stdin.

    Returns:
        Tuple of (return_code, stdout, stderr).

    Raises:
        CalledProcessError: If check=True and command fails.
        TimeoutExpired: If timeout is exceeded.

    Examples:
        >>> process_run(["echo", "hello"])
        (0, 'hello', '')
        >>> process_run(["ls"], Path("/tmp"))
        (0, '...', '')
        >>> process_run(["cat"], stdin_text="hello")
        (0, 'hello', '')

    Notes:
        Uses subprocess.run for execution.
        Output is text mode with UTF-8 encoding.
    """
    work_dir = str(cwd) if cwd else None

    result = subprocess.run(
        cmd,
        cwd=work_dir,
        capture_output=True,
        text=True,
        check=check,
        timeout=timeout,
        env=env,
        input=stdin_text,
    )

    return (
        result.returncode,
        (result.stdout or "").strip(),
        (result.stderr or "").strip(),
    )


# =============================================================================
# Exports
# =============================================================================

__all__: list[str] = [
    "process_run",
]
