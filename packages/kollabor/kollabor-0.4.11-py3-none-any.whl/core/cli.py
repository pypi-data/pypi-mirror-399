"""CLI entry point for kollab command."""

import asyncio
import argparse
import logging
import sys
import re
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

# Import from the same directory
from .application import TerminalLLMChat
from .logging import setup_bootstrap_logging

def _get_version_from_pyproject() -> str:
    """Read version from pyproject.toml for development mode."""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            for line in content.splitlines():
                if line.startswith("version ="):
                    # Extract version from: version = "0.4.10"
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return None  # Return None if not found

def _is_running_from_source() -> bool:
    """Check if we're running from source (development mode) vs installed package."""
    try:
        # If pyproject.toml exists in parent directory, we're running from source
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        return pyproject_path.exists()
    except Exception:
        return False

# Get version: prefer pyproject.toml when running from source, otherwise use installed version
if _is_running_from_source():
    # Development mode: use pyproject.toml
    __version__ = _get_version_from_pyproject() or "0.0.0"
else:
    # Production mode: use installed package version
    try:
        __version__ = version("kollabor")
    except PackageNotFoundError:
        __version__ = "0.0.0"


def parse_timeout(timeout_str: str) -> int:
    """Parse timeout string into seconds.

    Args:
        timeout_str: Timeout string like "30s", "2min", "1h"

    Returns:
        Timeout in seconds

    Raises:
        ValueError: If timeout format is invalid
    """
    timeout_str = timeout_str.strip().lower()

    # Match pattern like "30s", "2min", "1h"
    match = re.match(
        r"^(\d+(?:\.\d+)?)(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)$",
        timeout_str,
    )
    if not match:
        raise ValueError(
            f"Invalid timeout format: {timeout_str}. Use format like '30s', '2min', or '1h'"
        )

    value = float(match.group(1))
    unit = match.group(2)

    # Convert to seconds
    if unit in ("s", "sec", "second", "seconds"):
        return int(value)
    elif unit in ("m", "min", "minute", "minutes"):
        return int(value * 60)
    elif unit in ("h", "hour", "hours"):
        return int(value * 3600)
    else:
        raise ValueError(f"Unknown time unit: {unit}")


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Kollab - Terminal-based LLM chat interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kollab                                    # Start interactive mode
  kollab "what is 1+1?"                     # Pipe mode with query
  kollab -p "what is 1+1?"                  # Pipe mode with query
  kollab --timeout 30s "complex query"      # Custom timeout (30 seconds)
  kollab --timeout 5min "long task"         # Custom timeout (5 minutes)
  echo "hello" | kollab -p                  # Pipe input from stdin
  cat file.txt | kollab -p --timeout 1h     # Process file with 1 hour timeout
  kollab --system-prompt my-prompt.md       # Use custom system prompt
  kollab --agent lint-editor               # Use specific agent
  kollab -a lint-editor                    # Short form for agent
  kollab --profile claude                  # Use specific LLM profile
        """,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit",
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process in pipe mode (if not provided, reads from stdin)",
    )

    parser.add_argument(
        "-p",
        "--pipe",
        action="store_true",
        help="Pipe mode: process input and exit (automatically enabled if query is provided)",
    )

    parser.add_argument(
        "--timeout",
        type=str,
        default="2min",
        help="Timeout for pipe mode processing (e.g., 30s, 2min, 1h). Default: 2min",
    )

    parser.add_argument(
        "--system-prompt",
        type=str,
        default=None,
        metavar="FILE",
        help="Use a custom system prompt file (e.g., --system-prompt my-prompt.md)",
    )

    parser.add_argument(
        "-a",
        "--agent",
        type=str,
        default=None,
        metavar="AGENT",
        help="Use a specific agent (e.g., --agent lint-editor)",
    )

    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        metavar="PROFILE",
        help="Use a specific LLM profile (e.g., --profile claude, --profile openai)",
    )

    return parser.parse_args()


async def async_main() -> None:
    """Main async entry point for the application with proper error handling."""
    # Setup bootstrap logging before application starts
    setup_bootstrap_logging()
    logger = logging.getLogger(__name__)

    args = parse_arguments()

    # Determine if we're in pipe mode and what the input is
    piped_input = None

    # If query argument is provided, use it (automatically enables pipe mode)
    if args.query:
        piped_input = args.query.strip()
    # Otherwise, check if stdin is being piped or -p flag is set
    elif args.pipe or not sys.stdin.isatty():
        # Read from stdin
        piped_input = sys.stdin.read().strip()
        if not piped_input:
            print("Error: No input received from pipe", file=sys.stderr)
            sys.exit(1)

    app = None
    try:
        logger.info("Creating application instance...")
        app = TerminalLLMChat(
            system_prompt_file=args.system_prompt,
            agent_name=args.agent,
            profile_name=args.profile,
        )
        logger.info("Starting application...")

        if piped_input:
            # Parse timeout for pipe mode
            try:
                timeout_seconds = parse_timeout(args.timeout)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

            # Pipe mode: send input and exit after response
            await app.start_pipe_mode(piped_input, timeout=timeout_seconds)
        else:
            # Interactive mode
            await app.start()
    except KeyboardInterrupt:
        # print("\n\nApplication interrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"\n\nApplication failed to start: {e}")
        logger.error(f"Application startup failed: {type(e).__name__}: {e}")
        # Print helpful error message for common issues
        if "permission" in str(e).lower():
            print(
                "\nTip: Check file permissions and try running with appropriate privileges"
            )
        elif "already in use" in str(e).lower():
            print(
                "\nTip: Another instance may be running. Try closing other applications."
            )
        elif "not found" in str(e).lower():
            print("\nTip: Check that all required dependencies are installed.")
        raise  # Re-raise for full traceback in debug mode
    finally:
        # Ensure cleanup happens even if startup fails (skip if in pipe mode and already cleaned up)
        pipe_mode = getattr(app, "pipe_mode", False) if app else False
        if app and not app._startup_complete and not pipe_mode:
            logger.info("Performing emergency cleanup after startup failure...")
            try:
                await app.cleanup()
            except Exception as cleanup_error:
                logger.error(f"Emergency cleanup failed: {cleanup_error}")
                # print("Warning: Some resources may not have been cleaned up properly")


def cli_main() -> None:
    """Synchronous entry point for pip-installed CLI command."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        # print("\n\nExited cleanly!")
        pass
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        # Exit with error code for scripts that depend on it
        sys.exit(1)
