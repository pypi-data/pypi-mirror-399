"""Immutable data structures for the framework."""
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from types import ModuleType, TracebackType
from typing import Callable, Any


# Version constant - single source of truth
__version__ = "0.1.0"


class TestOutcome(Enum):
    """Possible outcomes for a test execution."""
    PASSED = auto()
    FAILED = auto()
    ERRORED = auto()
    SKIPPED = auto()


class SkipReason(Enum):
    """Reasons why a test might be skipped."""
    UNSUPPORTED_SIGNATURE = auto()
    IMPORT_ERROR = auto()
    SETUP_FAILED = auto()


@dataclass(frozen=True)
class TestId:
    """Unique identifier for a test."""
    module_path: str
    class_name: str | None
    function_name: str

    def __str__(self) -> str:
        """Format: module::Class::method or module::function"""
        if self.class_name:
            return f"{self.module_path}::{self.class_name}::{self.function_name}"
        return f"{self.module_path}::{self.function_name}"


@dataclass(frozen=True)
class ExceptionInfo:
    """Information about a captured exception."""
    exc_type: type[BaseException]
    exc_value: BaseException
    exc_tb: TracebackType | None
    source_line: str | None = None
    introspected_values: dict[str, Any] | None = None

    @classmethod
    def from_exc_info(
        cls,
        exc_info: tuple[type[BaseException], BaseException, TracebackType | None],
        source_line: str | None = None,
        introspected_values: dict[str, Any] | None = None,
    ) -> "ExceptionInfo":
        """Create ExceptionInfo from sys.exc_info() tuple."""
        return cls(
            exc_type=exc_info[0],
            exc_value=exc_info[1],
            exc_tb=exc_info[2],
            source_line=source_line,
            introspected_values=introspected_values,
        )


@dataclass(frozen=True)
class TestItem:
    """A discovered test to be executed."""
    id: TestId
    callable: Callable[[], None] | None  # None if skipped
    skip_reason: SkipReason | None
    is_method: bool
    skip_message: str | None = None  # Additional context for skip


@dataclass(frozen=True)
class TestResult:
    """Result of executing a test."""
    id: TestId
    outcome: TestOutcome
    duration_ms: float
    error: ExceptionInfo | None = None
    skip_reason: SkipReason | None = None
    skip_message: str | None = None


@dataclass(frozen=True)
class RunConfig:
    """Configuration for a test run."""
    root_path: Path
    random_order: bool = False
    seed: int | None = None
    max_fail: int | None = None
    verbose: bool = False
    pytest_compat: bool = False


@dataclass(frozen=True)
class RunSummary:
    """Summary of a completed test run."""
    total: int
    passed: int
    failed: int
    errored: int
    skipped: int
    duration_s: float
    results: tuple[TestResult, ...] = field(default_factory=tuple)


# Internal dataclasses for test collection and execution


@dataclass
class ModuleInfo:
    """Information about a loaded test module."""
    module: ModuleType
    path: Path
    setup_module: Callable[[], None] | None
    teardown_module: Callable[[], None] | None


@dataclass
class ClassInfo:
    """Information about a test class."""
    cls: type
    name: str
    setup_class: Callable[[], None] | None
    teardown_class: Callable[[], None] | None
    setup_method: Callable[[Any], None] | None
    teardown_method: Callable[[Any], None] | None


@dataclass
class ModuleTests:
    """Tests collected from a module."""
    module_info: ModuleInfo | None
    path: Path
    functions: list[TestItem]
    classes: list[tuple[ClassInfo, list[TestItem]]]
    import_error: Exception | None = None
