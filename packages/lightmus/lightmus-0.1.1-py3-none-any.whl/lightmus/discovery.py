"""Test file discovery."""
from pathlib import Path
import fnmatch


class TestFileDiscoverer:
    """Find test files matching patterns."""

    PATTERNS = ("test_*.py", "*_test.py")
    EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".tox", ".pytest_cache"}

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def discover(self) -> list[Path]:
        """
        Return sorted list of test file paths.

        Finds all files matching test_*.py or *_test.py patterns,
        excluding common non-test directories.
        """
        if self._root.is_file():
            # Single file mode
            if self._is_test_file(self._root):
                return [self._root]
            return []

        test_files: set[Path] = set()

        for path in self._walk_directory(self._root):
            if self._is_test_file(path):
                test_files.add(path)

        # Sort by resolved absolute path for determinism
        return sorted(test_files, key=lambda p: str(p.resolve()))

    def _walk_directory(self, directory: Path) -> list[Path]:
        """Recursively walk directory, skipping excluded dirs."""
        files: list[Path] = []

        try:
            for entry in directory.iterdir():
                if entry.is_dir():
                    if entry.name not in self.EXCLUDE_DIRS:
                        files.extend(self._walk_directory(entry))
                elif entry.is_file():
                    files.append(entry)
        except PermissionError:
            # Skip directories we can't access
            pass

        return files

    def _is_test_file(self, path: Path) -> bool:
        """Check if a file matches test file patterns."""
        if not path.suffix == ".py":
            return False

        name = path.name
        return any(fnmatch.fnmatch(name, pattern) for pattern in self.PATTERNS)
