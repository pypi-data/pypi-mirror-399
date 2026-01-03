"""Assertion value extraction from failed asserts."""
import ast
import linecache
from types import FrameType, TracebackType
from typing import Any

from .models import ExceptionInfo


class AssertionIntrospector:
    """Extract variable values from failed assertions."""

    def introspect(
        self,
        exc_info: tuple[type[BaseException], BaseException, TracebackType | None],
    ) -> ExceptionInfo:
        """
        Analyze an assertion failure and extract variable values.

        Falls back to basic ExceptionInfo if introspection fails.
        """
        exc_type, exc_value, exc_tb = exc_info

        if exc_tb is None:
            return ExceptionInfo.from_exc_info(exc_info)

        # Try to extract assertion details
        try:
            frame_info = self._find_assertion_frame(exc_tb)
            if frame_info is None:
                return ExceptionInfo.from_exc_info(exc_info)

            frame, lineno = frame_info
            source_line = linecache.getline(frame.f_code.co_filename, lineno).strip()

            if not source_line.startswith("assert "):
                return ExceptionInfo.from_exc_info(exc_info, source_line=source_line)

            # Check if assertion has explicit message (don't override)
            if str(exc_value).strip():
                return ExceptionInfo.from_exc_info(exc_info, source_line=source_line)

            # Extract the assertion expression
            expr_source = self._extract_assertion_expr(source_line)
            if expr_source is None:
                return ExceptionInfo.from_exc_info(exc_info, source_line=source_line)

            # Parse and extract names
            values = self._extract_values(expr_source, frame)

            return ExceptionInfo.from_exc_info(
                exc_info,
                source_line=source_line,
                introspected_values=values if values else None,
            )

        except Exception:
            # Silent fallback - never crash on introspection failure
            return ExceptionInfo.from_exc_info(exc_info)

    def _find_assertion_frame(
        self, tb: TracebackType
    ) -> tuple[FrameType, int] | None:
        """Walk traceback to find innermost test frame with the assertion."""
        result: tuple[FrameType, int] | None = None

        current: TracebackType | None = tb
        while current is not None:
            frame = current.tb_frame
            lineno = current.tb_lineno
            result = (frame, lineno)
            current = current.tb_next

        return result

    def _extract_assertion_expr(self, source_line: str) -> str | None:
        """Extract the expression from an assert statement."""
        if not source_line.startswith("assert "):
            return None

        # Remove 'assert ' prefix
        rest = source_line[7:]

        # Handle multi-line or message case
        # Split on comma to separate expression from optional message
        # But we need to handle nested commas in expressions
        try:
            # Try to parse just the expression
            tree = ast.parse(f"assert {rest}", mode="exec")
            if isinstance(tree.body[0], ast.Assert):
                # Get just the test expression
                return ast.unparse(tree.body[0].test)
        except SyntaxError:
            pass

        return rest.split(",")[0].strip()

    def _extract_values(
        self, expr_source: str, frame: FrameType
    ) -> dict[str, Any]:
        """Extract variable names from expression and evaluate them."""
        values: dict[str, Any] = {}

        try:
            tree = ast.parse(expr_source, mode="eval")
            names = self._extract_names(tree.body)

            for name in names:
                value = self._eval_name(name, frame.f_locals, frame.f_globals)
                if value is not None:
                    values[name] = value

        except Exception:
            pass

        return values

    def _extract_names(self, node: ast.AST) -> list[str]:
        """Extract unique variable names from AST nodes."""
        names: set[str] = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.add(child.id)
            elif isinstance(child, ast.Attribute):
                # Get the full attribute path like obj.value
                attr_path = self._get_attribute_path(child)
                if attr_path:
                    names.add(attr_path)

        return list(names)

    def _get_attribute_path(self, node: ast.Attribute) -> str | None:
        """Get the full path of an attribute access (e.g., 'obj.value')."""
        parts: list[str] = [node.attr]

        current: ast.expr = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)
            parts.reverse()
            return ".".join(parts)

        return None

    def _eval_name(
        self, name: str, locals_: dict[str, Any], globals_: dict[str, Any]
    ) -> Any | None:
        """Safely evaluate a name in given scope."""
        try:
            # Handle dotted names (attributes)
            parts = name.split(".")
            base_name = parts[0]

            if base_name in locals_:
                value = locals_[base_name]
            elif base_name in globals_:
                value = globals_[base_name]
            else:
                return None

            # Navigate attribute path
            for attr in parts[1:]:
                value = getattr(value, attr)

            return value

        except Exception:
            return None
