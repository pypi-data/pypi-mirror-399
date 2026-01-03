# lightmus

A minimal Python testing framework. Standard library only.

## Installation

```bash
pip install lightmus
```

Or install from source:

```bash
pip install .
```

## Usage

```bash
# Run tests in current directory
lightmus

# Run tests in specific path
lightmus tests/

# Run a single test file
lightmus tests/test_example.py

# Randomize test order (reproducible with seed)
lightmus --random --seed 42

# Stop after first failure
lightmus --max-fail 1

# Verbose output
lightmus -v
```

## Writing Tests

```python
# test_example.py

def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"

class TestMath:
    def test_multiply(self):
        assert 2 * 3 == 6
```

## Setup and Teardown

```python
def setup_module():
    print("Before all tests in this file")

def teardown_module():
    print("After all tests in this file")

class TestWithHooks:
    @classmethod
    def setup_class(cls):
        print("Before all methods in this class")

    def setup_method(self):
        print("Before each test method")

    def teardown_method(self):
        print("After each test method")

    def test_something(self):
        assert True
```

## pytest Compatibility Mode

By default, lightmus distinguishes between:
- **FAILED**: AssertionError (test logic failure)
- **ERROR**: Other exceptions (test code bug)

Use `--pytest-compat` to match pytest behavior where all exceptions are FAILED:

```bash
lightmus --pytest-compat
```

## Graceful Import Error Handling

Unlike pytest, lightmus continues running when a test file has import errors:

```
# pytest: Halts collection entirely
ERROR collecting test_broken.py

# lightmus: Marks as skipped, continues
test_broken.py - import error - No module named 'missing'
...remaining tests run...
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | At least one failure or error |
| 2 | Invalid arguments or framework error |

## License

MIT
