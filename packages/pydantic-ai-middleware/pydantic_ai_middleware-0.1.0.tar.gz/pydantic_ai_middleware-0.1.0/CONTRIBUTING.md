# Contributing to pydantic-ai-middleware

Thank you for your interest in contributing to pydantic-ai-middleware!

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/vstorm-co/pydantic-ai-middleware.git
   cd pydantic-ai-middleware
   ```

2. **Install dependencies:**

   ```bash
   make install
   ```

   This will:
   - Install all dependencies using uv
   - Set up pre-commit hooks

3. **Verify installation:**

   ```bash
   make test
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests and generate HTML coverage report
make testcov

# Run tests on all Python versions
make test-all-python
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Run all checks
make all
```

### Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
make docs-serve
```

## Code Style

- We use [Ruff](https://github.com/astral-sh/ruff) for formatting and linting
- Maximum line length is 100 characters
- We use [Pyright](https://github.com/microsoft/pyright) for type checking
- All code must have 100% test coverage

## Pull Request Process

1. **Create a branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write tests for new functionality
   - Ensure all tests pass
   - Update documentation if needed

3. **Run all checks:**

   ```bash
   make all
   ```

4. **Commit your changes:**
   - Use clear, descriptive commit messages
   - Reference any related issues

5. **Push and create a PR:**

   ```bash
   git push origin feature/your-feature-name
   ```

## Testing Guidelines

- All new features must have tests
- Tests should be in the `tests/` directory
- Use descriptive test names
- Use pytest fixtures for common setup
- Aim for 100% coverage

### Test Structure

```python
class TestFeatureName:
    """Tests for FeatureName."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality."""
        ...

    async def test_async_functionality(self) -> None:
        """Test async functionality."""
        ...
```

## Documentation Guidelines

- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings
- Update README.md for significant changes

## Questions?

If you have questions, please:

1. Check existing issues
2. Open a new issue with your question
3. Tag it with "question"

Thank you for contributing!
