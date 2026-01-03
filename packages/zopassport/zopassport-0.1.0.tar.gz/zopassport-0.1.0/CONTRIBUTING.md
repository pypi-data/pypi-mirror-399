# Contributing to ZoPassport Python SDK

Thank you for your interest in contributing to the ZoPassport Python SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Python version** and SDK version
- **Code samples** if applicable
- **Error messages** and stack traces

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Rationale** for the enhancement
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** and code is formatted
6. **Commit with clear messages**
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/zopassport.git
cd zopassport

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/zopassport --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run with verbose output
pytest -v

# Run type checking
mypy src/
```

### Code Formatting and Linting

We use Black for formatting and Ruff for linting:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/
```

Pre-commit hooks will automatically run these tools before each commit.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 100)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints for all functions

### Code Structure

- **One class per file** (unless closely related)
- **Clear module organization**
- **Docstrings for all public APIs** (Google style)
- **Type hints throughout**
- **Meaningful variable names**

### Documentation

- Add docstrings to all public methods and classes
- Update README.md for new features
- Add examples for complex functionality
- Update CHANGELOG.md following Keep a Changelog format

### Testing

- Write tests for all new functionality
- Maintain >80% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add support for email authentication
fix(wallet): handle null wallet address gracefully
docs: update installation instructions
test(storage): add tests for encrypted storage
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a new tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will automatically publish to PyPI

## Questions?

Feel free to:
- Open an issue for questions
- Email us at dev@zo.xyz
- Join our Discord community

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
