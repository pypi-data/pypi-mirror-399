"""Command line interface."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .models import RunConfig
from .runner import TestRunner
from .reporting import Reporter


def parse_args(args: list[str] | None = None) -> RunConfig:
    """
    Parse CLI arguments into RunConfig.
    Raises SystemExit for invalid input.
    """
    parser = argparse.ArgumentParser(
        prog="lightmus",
        description="A minimal Python testing framework",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory for test discovery (default: current directory)",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Shuffle test execution order",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for shuffling (requires --random or implies it)",
    )
    parser.add_argument(
        "--max-fail",
        type=int,
        metavar="N",
        default=0,
        help="Stop after N failures (0 = unlimited)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--pytest-compat",
        action="store_true",
        help="Use pytest-compatible behavior (exceptions=FAILED, bad signatures=ERROR)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parsed = parser.parse_args(args)

    # Validate path
    root_path = Path(parsed.path)
    if not root_path.exists():
        print(f"Error: Path does not exist: {parsed.path}", file=sys.stderr)
        sys.exit(2)

    # Handle seed implying random
    random_order = parsed.random
    if parsed.seed is not None:
        random_order = True

    # Normalize max_fail
    max_fail = parsed.max_fail if parsed.max_fail > 0 else None

    return RunConfig(
        root_path=root_path,
        random_order=random_order,
        seed=parsed.seed,
        max_fail=max_fail,
        verbose=parsed.verbose,
        pytest_compat=parsed.pytest_compat,
    )


def main(args: list[str] | None = None) -> int:
    """
    Entry point. Returns exit code.
    0 = all passed
    1 = failures/errors
    2 = framework error
    """
    try:
        config = parse_args(args)
        reporter = Reporter(verbose=config.verbose)

        # Create runner with progress callback
        runner = TestRunner(config, on_result=reporter.report_progress)

        summary = runner.run()

        # End the progress line
        reporter.report_newline()

        # Report details
        reporter.report_failures(list(summary.results))
        reporter.report_errors(list(summary.results))
        reporter.report_skipped(list(summary.results))
        reporter.report_summary(summary)

        if summary.failed > 0 or summary.errored > 0:
            return 1
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 2

    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    except Exception as e:
        print(f"Framework error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
