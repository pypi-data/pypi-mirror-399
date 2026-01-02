# =============================================================================
# Docstring
# =============================================================================

"""
Rite CLI Module
===============

Command-line interface for Rite utility functions.

"""

# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import argparse
from pathlib import Path
import sys

# Import | Local Modules
import rite
from rite.crypto.hash import hash_md5, hash_sha256
from rite.crypto.uuid import uuid_hex, uuid_random
from rite.filesystem import (
    file_read_text,
    file_write_text,
    path_exists,
)
from rite.text import (
    slugify,
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)

# =============================================================================
# CLI Functions
# =============================================================================


def cmd_version(args: argparse.Namespace) -> int:
    """Display version information."""
    print(f"rite v{rite.__version__}")
    return 0


def cmd_hash(args: argparse.Namespace) -> int:
    """Hash input text."""
    text = args.text
    algorithm = args.algorithm.lower()

    if algorithm == "sha256":
        result = hash_sha256(text)
    elif algorithm == "md5":
        result = hash_md5(text)
    else:
        print(f"Error: Unknown algorithm '{algorithm}'", file=sys.stderr)
        return 1

    print(result)
    return 0


def cmd_uuid(args: argparse.Namespace) -> int:
    """Generate a UUID."""
    if args.count < 1:
        print("Error: Count must be at least 1", file=sys.stderr)
        return 1

    for _ in range(args.count):
        if args.hex:
            print(uuid_hex())
        else:
            uid = uuid_random()
            print(str(uid))

    return 0


def cmd_slug(args: argparse.Namespace) -> int:
    """Generate a slug from text."""
    text = args.text
    result = slugify(text)
    print(result)
    return 0


def cmd_case(args: argparse.Namespace) -> int:
    """Convert text case."""
    text = args.text
    case_type = args.type.lower()

    converters = {
        "snake": to_snake_case,
        "camel": to_camel_case,
        "pascal": to_pascal_case,
        "kebab": to_kebab_case,
    }

    if case_type not in converters:
        print(f"Error: Unknown case type '{case_type}'", file=sys.stderr)
        return 1

    result = converters[case_type](text)
    print(result)
    return 0


def cmd_file_hash(args: argparse.Namespace) -> int:
    """Hash file contents."""
    file_path = Path(args.file)

    if not path_exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        content = file_read_text(file_path)
        algorithm = args.algorithm.lower()

        if algorithm == "sha256":
            result = hash_sha256(content)
        elif algorithm == "md5":
            result = hash_md5(content)
        else:
            print(f"Error: Unknown algorithm '{algorithm}'", file=sys.stderr)
            return 1

        print(f"{result}  {file_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """Display package information."""
    print(f"rite v{rite.__version__}")
    print(f"\nA pure Python utility library with zero dependencies.")
    print(f"\nAvailable modules:")
    modules = [
        "collections",
        "conversion",
        "crypto",
        "diagnostics",
        "filesystem",
        "functional",
        "markup",
        "net",
        "numeric",
        "reflection",
        "serialization",
        "system",
        "temporal",
        "text",
    ]
    for module in modules:
        print(f"  - rite.{module}")
    print(f"\nFor more information, visit: https://www.pyrites.dev")
    return 0


# =============================================================================
# CLI Parser
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="rite",
        description="Rite - Python Utility Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {rite.__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Info command
    parser_info = subparsers.add_parser(
        "info", help="Show package information"
    )
    parser_info.set_defaults(func=cmd_info)

    # Hash command
    parser_hash = subparsers.add_parser("hash", help="Hash text")
    parser_hash.add_argument("text", help="Text to hash")
    parser_hash.add_argument(
        "-a",
        "--algorithm",
        choices=["sha256", "md5"],
        default="sha256",
        help="Hash algorithm (default: sha256)",
    )
    parser_hash.set_defaults(func=cmd_hash)

    # UUID command
    parser_uuid = subparsers.add_parser("uuid", help="Generate UUID")
    parser_uuid.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        help="Number of UUIDs to generate (default: 1)",
    )
    parser_uuid.add_argument(
        "--hex",
        action="store_true",
        help="Output in hex format",
    )
    parser_uuid.set_defaults(func=cmd_uuid)

    # Slug command
    parser_slug = subparsers.add_parser("slug", help="Generate URL slug")
    parser_slug.add_argument("text", help="Text to slugify")
    parser_slug.set_defaults(func=cmd_slug)

    # Case command
    parser_case = subparsers.add_parser("case", help="Convert text case")
    parser_case.add_argument("text", help="Text to convert")
    parser_case.add_argument(
        "-t",
        "--type",
        choices=["snake", "camel", "pascal", "kebab"],
        required=True,
        help="Target case type",
    )
    parser_case.set_defaults(func=cmd_case)

    # File hash command
    parser_file_hash = subparsers.add_parser(
        "file-hash", help="Hash file contents"
    )
    parser_file_hash.add_argument("file", help="File to hash")
    parser_file_hash.add_argument(
        "-a",
        "--algorithm",
        choices=["sha256", "md5"],
        default="sha256",
        help="Hash algorithm (default: sha256)",
    )
    parser_file_hash.set_defaults(func=cmd_file_hash)

    return parser


def cli_main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


# =============================================================================
# Exports
# =============================================================================


__all__: list[str] = [
    "cli_main",
    "create_parser",
    "cmd_info",
    "cmd_hash",
    "cmd_uuid",
    "cmd_slug",
    "cmd_case",
    "cmd_file_hash",
]
