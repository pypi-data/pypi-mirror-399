import argparse
import sys

from . import __version__
from .maskers import mask_phone_number


def main():
    """A simple python sanitizer kickoff cli tool."""
    parser = argparse.ArgumentParser(
        description="A simple python sanitizer kickoff cli tool."
    )
    # Version argument
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version and exit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Command: mask ---
    mask_parser = subparsers.add_parser("mask-phone-number", help="Mask phone number")
    mask_parser.add_argument("phone", help="The phone number to mask")

    args = parser.parse_args()
    if args.command == "mask-phone-number":
        try:
            print(mask_phone_number(args.phone))
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
