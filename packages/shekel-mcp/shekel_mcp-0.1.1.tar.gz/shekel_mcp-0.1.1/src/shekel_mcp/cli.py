"""
CLI entry point for the Shekel MCP server.

Usage:
    shekel-mcp
    shekel-mcp --base-url http://localhost:8000
"""

import argparse
import sys

from . import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="shekel-mcp",
        description="MCP server for Shekel Mobility vehicle APIs",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://shekel-ai-estimator-4e9f4efc9094.herokuapp.com",
        help="Base URL of the Shekel Mobility API (default: production)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Import here to avoid circular imports
    from .tools import set_base_url, run_server

    # Set the base URL
    set_base_url(args.base_url)

    # Log to stderr (stdout is used for MCP communication)
    print(f"Starting Shekel MCP server v{__version__}", file=sys.stderr)
    print(f"API Base URL: {args.base_url}", file=sys.stderr)
    print("MCP server ready for connections", file=sys.stderr)

    # Run the server
    run_server()


if __name__ == "__main__":
    main()
