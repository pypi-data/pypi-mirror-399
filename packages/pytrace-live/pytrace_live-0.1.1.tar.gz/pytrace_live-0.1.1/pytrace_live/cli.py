"""Command-line interface for pytrace-live."""

import argparse
import runpy
import sys
from pathlib import Path

from pytrace_live.tracer import FunctionTracer


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pytrace-live",
        description="Live Python function execution tracer with timing",
    )
    parser.add_argument(
        "script",
        type=str,
        help="Python script to trace",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Milliseconds threshold for marking functions as slow (default: 100)",
    )

    args = parser.parse_args()

    script_path = Path(args.script)

    if not script_path.exists():
        print(f"Error: Script '{args.script}' not found", file=sys.stderr)
        sys.exit(1)

    if not script_path.is_file():
        print(f"Error: '{args.script}' is not a file", file=sys.stderr)
        sys.exit(1)

    # Get absolute path for filtering
    absolute_script_path = str(script_path.resolve())

    tracer = FunctionTracer(threshold_ms=args.threshold)

    try:
        tracer.start(target_file=absolute_script_path)
        runpy.run_path(str(script_path), run_name="__main__")
    except Exception as e:
        print(f"\nScript raised exception: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        tracer.stop()


if __name__ == "__main__":
    main()