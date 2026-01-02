"""Command-line interface for Fluxibly framework.

This module provides the CLI entry point for the framework.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        prog="fluxibly",
        description="MCP-Native Agentic Framework for General-Purpose Task Automation",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config"),
        help="Path to configuration directory (default: config)",
    )

    parser.add_argument(
        "--profile",
        type=str,
        help="Configuration profile to use",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="fluxibly 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the agent framework")
    run_parser.add_argument(
        "--input",
        type=Path,
        help="Path to input JSON file with UnifiedInput schema",
    )

    # List servers command
    subparsers.add_parser("list-servers", help="List available MCP servers")

    # Health check command
    subparsers.add_parser("health", help="Check health of all MCP servers")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Command execution will be implemented
    print(f"Command '{args.command}' not yet implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
