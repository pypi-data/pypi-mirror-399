"""Command-line interface for pytrace-live."""

import argparse
import sys
import runpy
from pathlib import Path
from typing import NoReturn, Optional
from rich.console import Console

from pytrace_live.tracer import FunctionTracer

console = Console()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Live Python function execution tracing"
    )
    parser.add_argument(
        "script",
        help="Python script to trace"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Threshold in milliseconds for marking slow functions (default: 100)"
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private functions (starting with _) in trace"
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    script_path = Path(args.script)
    if not script_path.exists():
        console.print(f"[bold red]Error:[/bold red] Script not found: {args.script}")
        sys.exit(1)

    if not script_path.is_file():
        console.print(f"[bold red]Error:[/bold red] Not a file: {args.script}")
        sys.exit(1)

    tracer = FunctionTracer(threshold_ms=args.threshold)
    tracer.set_traced_file(str(script_path.resolve()))

    console.print(f"[bold cyan]Tracing:[/bold cyan] {args.script}")
    console.print(f"[bold cyan]Threshold:[/bold cyan] {args.threshold} ms\n")

    tracer.start()
    try:
        sys.argv = [str(script_path)]
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit:
        pass
    except Exception as e:
        console.print(f"\n[bold red]Script error:[/bold red] {e}")
    finally:
        tracer.stop()


if __name__ == "__main__":
    main()