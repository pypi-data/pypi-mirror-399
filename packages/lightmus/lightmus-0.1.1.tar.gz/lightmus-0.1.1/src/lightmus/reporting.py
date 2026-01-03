"""Output formatting and display."""
import sys
import traceback
from typing import Callable, TextIO

from .models import TestResult, TestOutcome, RunSummary, ExceptionInfo, SkipReason


class Reporter:
    """Format and print test results."""

    LINE_WIDTH = 60

    SYMBOLS = {
        TestOutcome.PASSED: ".",
        TestOutcome.FAILED: "F",
        TestOutcome.ERRORED: "E",
        TestOutcome.SKIPPED: "s",
    }

    SKIP_MESSAGES = {
        SkipReason.UNSUPPORTED_SIGNATURE: "unsupported signature",
        SkipReason.IMPORT_ERROR: "import error",
        SkipReason.SETUP_FAILED: "setup failed",
    }

    def __init__(self, output: TextIO | None = None, verbose: bool = False) -> None:
        self._output = output or sys.stdout
        self._verbose = verbose

    def _write(self, text: str, end: str = "\n") -> None:
        """Write text to output."""
        self._output.write(text + end)
        self._output.flush()

    def _write_section(
        self,
        title: str,
        results: list[TestResult],
        outcome_filter: TestOutcome,
        format_item: Callable[[TestResult], None],
    ) -> None:
        """Write a section header and formatted results filtered by outcome."""
        filtered = [r for r in results if r.outcome == outcome_filter]
        if not filtered:
            return

        self._write("")
        self._write("=" * self.LINE_WIDTH)
        self._write(f" {title} ".center(self.LINE_WIDTH, "="))
        self._write("=" * self.LINE_WIDTH)

        for result in filtered:
            format_item(result)

    def report_progress(self, result: TestResult) -> None:
        """Print single character for test result (or full line in verbose mode)."""
        symbol = self.SYMBOLS.get(result.outcome, "?")
        if self._verbose:
            status = result.outcome.name
            self._write(f"{symbol} {result.id} [{status}]")
        else:
            self._write(symbol, end="")

    def report_newline(self) -> None:
        """Print newline after progress characters."""
        if not self._verbose:
            self._write("")

    def _format_failure_or_error(self, result: TestResult) -> None:
        """Format a single failure or error result."""
        self._write("")
        self._write(f"__ {result.id} __")
        self._write("")
        if result.error:
            self._format_exception(result.error)

    def _format_skipped(self, result: TestResult) -> None:
        """Format a single skipped result."""
        reason = self.SKIP_MESSAGES.get(result.skip_reason, "unknown reason") if result.skip_reason else "unknown"
        message = f" - {result.skip_message}" if result.skip_message else ""
        self._write(f"{result.id} - {reason}{message}")

    def report_failures(self, results: list[TestResult]) -> None:
        """Print detailed failure information."""
        self._write_section("FAILURES", results, TestOutcome.FAILED, self._format_failure_or_error)

    def report_errors(self, results: list[TestResult]) -> None:
        """Print detailed error information."""
        self._write_section("ERRORS", results, TestOutcome.ERRORED, self._format_failure_or_error)

    def report_skipped(self, results: list[TestResult]) -> None:
        """Print skip reasons."""
        self._write_section("SKIPPED", results, TestOutcome.SKIPPED, self._format_skipped)

    def report_summary(self, summary: RunSummary) -> None:
        """Print final counts."""
        self._write("")
        self._write("=" * self.LINE_WIDTH)

        parts = []
        if summary.passed:
            parts.append(f"{summary.passed} passed")
        if summary.failed:
            parts.append(f"{summary.failed} failed")
        if summary.errored:
            parts.append(f"{summary.errored} error")
        if summary.skipped:
            parts.append(f"{summary.skipped} skipped")

        if not parts:
            parts.append("no tests ran")

        summary_text = ", ".join(parts)
        time_text = f"in {summary.duration_s:.2f}s"

        self._write(f" {summary_text} {time_text} ".center(self.LINE_WIDTH, "="))
        self._write("=" * self.LINE_WIDTH)

    def _format_exception(self, exc_info: ExceptionInfo) -> None:
        """Format exception with introspected values if available."""
        # Show exception type and message
        exc_name = exc_info.exc_type.__name__
        exc_msg = str(exc_info.exc_value)

        if exc_msg:
            self._write(f"    {exc_name}: {exc_msg}")
        else:
            self._write(f"    {exc_name}")

        # Show introspected values if available
        if exc_info.introspected_values:
            self._write("")
            for name, value in exc_info.introspected_values.items():
                self._write(f"    {name} = {repr(value)}")

        # Show source line if available
        if exc_info.source_line:
            self._write("")
            self._write(f"    > {exc_info.source_line}")

        # Show traceback
        if exc_info.exc_tb:
            self._write("")
            tb_lines = traceback.format_tb(exc_info.exc_tb)
            for line in tb_lines:
                for subline in line.rstrip().split("\n"):
                    self._write(f"    {subline}")
