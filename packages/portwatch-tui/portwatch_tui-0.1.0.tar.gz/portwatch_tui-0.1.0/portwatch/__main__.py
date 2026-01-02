#!/usr/bin/env python3
"""
PORTWATCH - Entry Point
Run with: python -m portwatch
"""

import argparse
import logging
import sys

from portwatch.app import PortWatchApp


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="portwatch",
        description="Tactical port scanner dashboard for developers.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    """Configure logging based on verbose flag."""
    level = logging.DEBUG if verbose else logging.WARNING

    # Configure the portwatch logger
    logger = logging.getLogger("portwatch")
    logger.setLevel(level)

    # Create handler that logs to stderr (so it doesn't interfere with TUI)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)


def main():
    args = parse_args()
    configure_logging(args.verbose)

    logger = logging.getLogger("portwatch")
    logger.debug("Starting portwatch application")

    app = PortWatchApp()
    app.run()


if __name__ == "__main__":
    main()
