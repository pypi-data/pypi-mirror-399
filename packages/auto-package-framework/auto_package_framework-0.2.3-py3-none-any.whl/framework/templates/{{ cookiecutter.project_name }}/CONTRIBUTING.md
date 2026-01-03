# Contributing Guide

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- [List required tools and versions]
- Python 3.8+
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PROJECT_NAME.git
   cd PROJECT_NAME
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch Naming Convention:**
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test updates

### 2. Make Changes

- Follow the project's code style
- Write/update tests
- Update documentation
- Ensure all tests pass

### 3. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git commit -m "feat(module): add new feature"
git commit -m "fix(module): fix bug description"
git commit -m "docs(readme): update installation"
```

### 4. Push and Create Pull Request

```bash
git push origin feat/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python

- Follow PEP 8
- Use type hints for all public functions
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

### General

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Write tests for new features

## Testing

### Writing Tests

- Write tests for all new features
- Aim for high test coverage
- Test edge cases and error conditions
- Keep tests fast and isolated

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_module.py

# Run specific test
pytest tests/test_module.py::test_function
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Use Google or NumPy style docstrings
- Include examples for complex functions

### Project Documentation

- Update README.md if needed
- Add/update guides in `docs/guide/`
- Update API documentation in `docs/api/`

## Pull Request Process

1. **Ensure Tests Pass**: All tests must pass
2. **Update Documentation**: Update relevant documentation
3. **Follow Style Guide**: Code must pass linting checks
4. **Write Clear Description**: Describe what and why
5. **Link Issues**: Reference related issues

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts

## Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged
4. Thank you for contributing!

## Reporting Issues

### Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) and include:

- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment information
- Error messages/logs

### Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) and include:

- Problem statement
- Proposed solution
- Use cases
- Alternatives considered

## Questions?

- Open an issue for questions
- Check existing issues first
- Be patient and respectful

Thank you for contributing! 🎉


