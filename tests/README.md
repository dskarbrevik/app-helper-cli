# Tests

This directory contains the test suite for the DevHand CLI application.

## Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test configuration
├── test_cli.py              # Tests for CLI entry point
└── commands/
    ├── __init__.py
    ├── test_build.py        # Tests for build commands
    ├── test_clean.py        # Tests for clean commands
    ├── test_db.py           # Tests for database commands
    ├── test_dev.py          # Tests for dev commands
    ├── test_setup.py        # Tests for setup commands
    └── test_validate.py     # Tests for validate commands
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/commands/test_build.py
```

### Run specific test class
```bash
pytest tests/commands/test_build.py::TestBuildCommand
```

### Run specific test
```bash
pytest tests/commands/test_build.py::TestBuildCommand::test_build_frontend_regular
```

### Run with coverage report
```bash
pytest --cov=dh --cov-report=html
```

### Run tests in parallel
```bash
pytest -n auto
```

### Run only fast tests (exclude slow tests)
```bash
pytest -m "not slow"
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- **`runner`**: Typer CLI test runner for integration testing
- **`mock_context`**: Mock context with temporary project structure
- **`mock_run_command`**: Mock for command execution
- **`mock_check_command_exists`**: Mock for tool availability checks
- **`mock_check_tool_version`**: Mock for tool version checks
- **`mock_db_client`**: Mock database client
- **`mock_prompts`**: Mock user prompts

## Writing New Tests

When adding new tests:

1. Create test files with the `test_` prefix
2. Use the fixtures from `conftest.py`
3. Mock external dependencies (commands, file I/O, database)
4. Test both success and failure paths
5. Use descriptive test names that explain what's being tested

Example:
```python
def test_command_success(mock_context, mock_run_command):
    """Test that command executes successfully."""
    # Arrange
    mock_context.is_frontend = True
    
    # Act
    result = my_command()
    
    # Assert
    mock_run_command.assert_called_once()
```

## Coverage

Run tests with coverage to ensure comprehensive testing:

```bash
pytest --cov=dh --cov-report=term-missing
```

View HTML coverage report:
```bash
pytest --cov=dh --cov-report=html
open htmlcov/index.html
```

## CI/CD

These tests are designed to run in CI/CD pipelines. They:
- Mock all external dependencies
- Use temporary directories for file operations
- Don't require actual tool installations
- Run quickly (< 1 minute for full suite)
