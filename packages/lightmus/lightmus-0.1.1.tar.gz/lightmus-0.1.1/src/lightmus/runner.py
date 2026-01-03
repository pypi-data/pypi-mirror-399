"""Test execution engine."""
import importlib.util
import inspect
import random
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Callable, Any, Iterator

from .models import (
    TestId, TestItem, TestResult, TestOutcome,
    ExceptionInfo, SkipReason, RunConfig, RunSummary,
    ModuleInfo, ClassInfo, ModuleTests,
)
from .introspection import AssertionIntrospector
from .discovery import TestFileDiscoverer


class TestRunner:
    """Execute tests with isolation and lifecycle management."""

    def __init__(
        self,
        config: RunConfig,
        on_result: Callable[[TestResult], None] | None = None,
    ) -> None:
        self._config = config
        self._introspector = AssertionIntrospector()
        self._fail_count = 0
        self._on_result = on_result

    def run(self) -> RunSummary:
        """Execute all tests and return summary."""
        start_time = time.time()

        discoverer = TestFileDiscoverer(self._config.root_path)
        test_files = discoverer.discover()

        # Collect all modules
        modules: list[ModuleTests] = []
        for file_path in test_files:
            modules.append(self._load_module(file_path))

        # Apply random ordering if requested
        if self._config.random_order:
            if self._config.seed is not None:
                random.seed(self._config.seed)
            random.shuffle(modules)
            for module in modules:
                random.shuffle(module.functions)
                for class_info, methods in module.classes:
                    random.shuffle(methods)

        # Run all tests
        results: list[TestResult] = []
        for result in self._run_modules(modules):
            results.append(result)

            # Call progress callback if provided
            if self._on_result:
                self._on_result(result)

            # Check max_fail limit
            if result.outcome in (TestOutcome.FAILED, TestOutcome.ERRORED):
                self._fail_count += 1
                if self._config.max_fail and self._fail_count >= self._config.max_fail:
                    break

        end_time = time.time()

        return RunSummary(
            total=len(results),
            passed=sum(1 for r in results if r.outcome == TestOutcome.PASSED),
            failed=sum(1 for r in results if r.outcome == TestOutcome.FAILED),
            errored=sum(1 for r in results if r.outcome == TestOutcome.ERRORED),
            skipped=sum(1 for r in results if r.outcome == TestOutcome.SKIPPED),
            duration_s=end_time - start_time,
            results=tuple(results),
        )

    def _run_modules(self, modules: list[ModuleTests]) -> Iterator[TestResult]:
        """Execute all modules, yielding results."""
        for module in modules:
            if self._should_stop():
                break

            yield from self._run_module(module)

    def _run_module(self, module_tests: ModuleTests) -> Iterator[TestResult]:
        """Execute a single module's tests."""
        # Handle import errors
        if module_tests.import_error:
            # In pytest-compat mode, import errors are ERROR; otherwise SKIPPED
            outcome = TestOutcome.ERRORED if self._config.pytest_compat else TestOutcome.SKIPPED
            yield TestResult(
                id=TestId(
                    module_path=str(module_tests.path),
                    class_name=None,
                    function_name="<module>",
                ),
                outcome=outcome,
                duration_ms=0.0,
                skip_reason=SkipReason.IMPORT_ERROR,
                skip_message=str(module_tests.import_error),
            )
            return

        if module_tests.module_info is None:
            return

        module_info = module_tests.module_info

        # Run setup_module
        setup_succeeded = True
        if module_info.setup_module:
            try:
                module_info.setup_module()
            except Exception as e:
                setup_succeeded = False
                # Mark all tests as error
                for item in module_tests.functions:
                    if self._should_stop():
                        break
                    yield self._make_error_result(
                        item, e, SkipReason.SETUP_FAILED, "setup_module failed"
                    )
                for class_info, methods in module_tests.classes:
                    for item in methods:
                        if self._should_stop():
                            break
                        yield self._make_error_result(
                            item, e, SkipReason.SETUP_FAILED, "setup_module failed"
                        )

        if setup_succeeded:
            # Run function tests
            for item in module_tests.functions:
                if self._should_stop():
                    break
                yield self._run_test_item(item)

            # Run class tests
            for class_info, methods in module_tests.classes:
                if self._should_stop():
                    break
                yield from self._run_class(class_info, methods)

            # Run teardown_module
            if module_info.teardown_module:
                try:
                    module_info.teardown_module()
                except Exception:
                    # Teardown failures are logged but don't fail already-passed tests
                    pass

    def _run_class(
        self,
        class_info: ClassInfo,
        methods: list[TestItem],
    ) -> Iterator[TestResult]:
        """Execute a class's test methods."""
        # Run setup_class
        setup_class_succeeded = True
        if class_info.setup_class:
            try:
                class_info.setup_class()
            except Exception as e:
                setup_class_succeeded = False
                for item in methods:
                    if self._should_stop():
                        break
                    yield self._make_error_result(
                        item, e, SkipReason.SETUP_FAILED, "setup_class failed"
                    )

        if setup_class_succeeded:
            for item in methods:
                if self._should_stop():
                    break

                # Create fresh instance for each test
                try:
                    instance = class_info.cls()
                except Exception as e:
                    yield self._make_error_result(
                        item, e, SkipReason.SETUP_FAILED, "class instantiation failed"
                    )
                    continue

                # Run setup_method
                setup_method_succeeded = True
                if class_info.setup_method:
                    try:
                        class_info.setup_method(instance)
                    except Exception as e:
                        setup_method_succeeded = False
                        yield self._make_error_result(
                            item, e, SkipReason.SETUP_FAILED, "setup_method failed"
                        )

                if setup_method_succeeded:
                    # Run the test
                    result = self._run_test_item(item, instance)

                    # Run teardown_method (only if setup succeeded)
                    teardown_error: Exception | None = None
                    if class_info.teardown_method:
                        try:
                            class_info.teardown_method(instance)
                        except Exception as e:
                            teardown_error = e

                    if teardown_error:
                        if self._config.pytest_compat:
                            # pytest-compat: yield original result, then separate error
                            yield result
                            yield self._make_error_result(
                                item, teardown_error, None, "teardown_method failed"
                            )
                        else:
                            # Default: teardown failure makes test ERROR if it passed
                            if result.outcome == TestOutcome.PASSED:
                                yield self._make_error_result(
                                    item, teardown_error, None, "teardown_method failed"
                                )
                            else:
                                yield result
                    else:
                        yield result

            # Run teardown_class (only if setup_class succeeded)
            if class_info.teardown_class:
                try:
                    class_info.teardown_class()
                except Exception:
                    pass

    def _run_test_item(
        self,
        item: TestItem,
        instance: Any | None = None,
    ) -> TestResult:
        """Execute a single test."""
        # Handle already-skipped items
        if item.callable is None or item.skip_reason:
            # In pytest-compat mode, unsupported signatures are ERROR (like pytest fixture not found)
            if self._config.pytest_compat and item.skip_reason == SkipReason.UNSUPPORTED_SIGNATURE:
                outcome = TestOutcome.ERRORED
            else:
                outcome = TestOutcome.SKIPPED
            return TestResult(
                id=item.id,
                outcome=outcome,
                duration_ms=0.0,
                skip_reason=item.skip_reason,
                skip_message=item.skip_message,
            )

        start_time = time.time()

        try:
            if instance is not None:
                item.callable(instance)
            else:
                item.callable()

            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                id=item.id,
                outcome=TestOutcome.PASSED,
                duration_ms=duration_ms,
            )

        except AssertionError:
            duration_ms = (time.time() - start_time) * 1000
            exc_info = sys.exc_info()
            error = self._introspector.introspect(exc_info)  # type: ignore
            return TestResult(
                id=item.id,
                outcome=TestOutcome.FAILED,
                duration_ms=duration_ms,
                error=error,
            )

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception:
            duration_ms = (time.time() - start_time) * 1000
            exc_info = sys.exc_info()
            error = ExceptionInfo.from_exc_info(exc_info)  # type: ignore
            # In pytest-compat mode, all exceptions are FAILED; otherwise ERRORED
            outcome = TestOutcome.FAILED if self._config.pytest_compat else TestOutcome.ERRORED
            return TestResult(
                id=item.id,
                outcome=outcome,
                duration_ms=duration_ms,
                error=error,
            )

    def _make_error_result(
        self,
        item: TestItem,
        exception: Exception,
        skip_reason: SkipReason | None = None,
        message: str | None = None,
    ) -> TestResult:
        """Create an error result."""
        exc_info = (type(exception), exception, exception.__traceback__)
        error = ExceptionInfo.from_exc_info(exc_info)

        return TestResult(
            id=item.id,
            outcome=TestOutcome.ERRORED,
            duration_ms=0.0,
            error=error,
            skip_reason=skip_reason,
            skip_message=message,
        )

    def _should_stop(self) -> bool:
        """Check if we should stop running tests."""
        if self._config.max_fail:
            return self._fail_count >= self._config.max_fail
        return False

    def _load_module(self, file_path: Path) -> ModuleTests:
        """Load a module and extract tests."""
        module_name = f"_lightmus_test_{file_path.stem}_{id(file_path)}"

        spec = importlib.util.spec_from_file_location(
            module_name,
            file_path,
            submodule_search_locations=[str(file_path.parent)],
        )

        if spec is None or spec.loader is None:
            return ModuleTests(
                module_info=None,
                path=file_path,
                functions=[],
                classes=[],
                import_error=ValueError(f"Cannot create spec for {file_path}"),
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        original_path = sys.path.copy()
        sys.path.insert(0, str(self._config.root_path.resolve()))

        try:
            spec.loader.exec_module(module)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            return ModuleTests(
                module_info=None,
                path=file_path,
                functions=[],
                classes=[],
                import_error=e,
            )
        finally:
            sys.path[:] = original_path
            sys.modules.pop(module_name, None)

        # Extract module-level hooks
        module_info = ModuleInfo(
            module=module,
            path=file_path,
            setup_module=getattr(module, "setup_module", None),
            teardown_module=getattr(module, "teardown_module", None),
        )

        # Extract tests
        functions, classes = self._extract_tests(module, file_path)

        return ModuleTests(
            module_info=module_info,
            path=file_path,
            functions=functions,
            classes=classes,
        )

    def _extract_tests(
        self,
        module: ModuleType,
        file_path: Path,
    ) -> tuple[list[TestItem], list[tuple[ClassInfo, list[TestItem]]]]:
        """Extract test functions and classes from module."""
        functions: list[TestItem] = []
        classes: list[tuple[ClassInfo, list[TestItem]]] = []

        for name in sorted(dir(module)):
            if name.startswith("_"):
                continue

            obj = getattr(module, name)

            # Test functions
            if name.startswith("test_") and callable(obj) and not inspect.isclass(obj):
                item = self._make_test_item(
                    func=obj,
                    module_path=str(file_path),
                    class_name=None,
                    func_name=name,
                    is_method=False,
                )
                functions.append(item)

            # Test classes
            elif name.startswith("Test") and inspect.isclass(obj):
                class_info, methods = self._extract_class_tests(obj, file_path)
                if methods:
                    classes.append((class_info, methods))

        return functions, classes

    def _extract_class_tests(
        self,
        cls: type,
        file_path: Path,
    ) -> tuple[ClassInfo, list[TestItem]]:
        """Extract tests from a class."""
        class_info = ClassInfo(
            cls=cls,
            name=cls.__name__,
            setup_class=getattr(cls, "setup_class", None),
            teardown_class=getattr(cls, "teardown_class", None),
            setup_method=getattr(cls, "setup_method", None),
            teardown_method=getattr(cls, "teardown_method", None),
        )

        methods: list[TestItem] = []

        for name in sorted(dir(cls)):
            if name.startswith("_"):
                continue

            if not name.startswith("test_"):
                continue

            obj = getattr(cls, name)
            if not callable(obj):
                continue

            item = self._make_test_item(
                func=obj,
                module_path=str(file_path),
                class_name=cls.__name__,
                func_name=name,
                is_method=True,
            )
            methods.append(item)

        return class_info, methods

    def _make_test_item(
        self,
        func: Callable[..., Any],
        module_path: str,
        class_name: str | None,
        func_name: str,
        is_method: bool,
    ) -> TestItem:
        """Create a TestItem, checking signature validity."""
        test_id = TestId(
            module_path=module_path,
            class_name=class_name,
            function_name=func_name,
        )

        if not self._is_valid_signature(func, is_method):
            return TestItem(
                id=test_id,
                callable=None,
                skip_reason=SkipReason.UNSUPPORTED_SIGNATURE,
                is_method=is_method,
                skip_message="function requires arguments",
            )

        return TestItem(
            id=test_id,
            callable=func,
            skip_reason=None,
            is_method=is_method,
        )

    def _is_valid_signature(self, func: Callable[..., Any], is_method: bool) -> bool:
        """Check if callable has no required args (except self)."""
        try:
            sig = inspect.signature(func)
        except (ValueError, TypeError):
            return False

        for name, param in sig.parameters.items():
            if name == "self" and is_method:
                continue

            # Skip *args and **kwargs - they never require values
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            # Any parameter without a default is required
            if param.default is inspect.Parameter.empty:
                return False

        return True
