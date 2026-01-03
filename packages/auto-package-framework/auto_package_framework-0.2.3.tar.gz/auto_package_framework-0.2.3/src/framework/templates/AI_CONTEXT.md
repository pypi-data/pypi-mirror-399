# AI Context Guide - Project Development

> **Purpose**: This file provides comprehensive context for AI assistants (Claude, GPT, etc.) to understand and contribute to this project effectively.

> **👋 New to this project?** Start with **[START_HERE.md](./START_HERE.md)** for navigation guide!

## 🎯 Project Overview

**Project Name**: [Your Project Name]
**Mission**: [Brief description of what problem this project solves]
**Domain**: [Industry/Field: e.g., Software Engineering, Data Science, Web Development, etc.]

> **🚀 AI ASSISTANT START HERE**: If you're helping with a new or existing project, start by reading **[PROJECT_IDEA.md](./PROJECT_IDEA.md)** to understand the project vision, requirements, and current status. Then read this file for technical context.

### Core Philosophy

This project follows three key principles:

1. **Continuous AI Integration**: Use AI as a thinking partner and efficiency multiplier, not just a tool
2. **Community-First Approach**: Lower barriers to participation, respond quickly, let community amplify the project
3. **Platform Leverage**: Maximize use of existing tools and platforms, don't reinvent the wheel

---

## 📁 Project Structure

```
project-root/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/              # CI/CD automation
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── dependabot.yml          # Automated dependency updates
├── docs/                       # Documentation
│   ├── guide/                  # User guides
│   ├── api/                    # API documentation
│   └── DEVELOPMENT_PHILOSOPHY.md  # Development practices
├── src/                        # Source code
├── tests/                      # Test suites
├── examples/                   # Example code
├── scripts/                    # Utility scripts
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pyproject.toml              # Python project config (if applicable)
├── package.json                # Node.js project config (if applicable)
├── Cargo.toml                  # Rust project config (if applicable)
├── release-please-config.json  # Automated versioning
├── CODE_OF_CONDUCT.md          # Community standards
├── SECURITY.md                 # Security policy
├── CONTRIBUTING.md             # Contribution guidelines
└── AI_CONTEXT.md               # This file
```

---

## 🔧 Technology Stack

### Core Technologies
- **Language(s)**: [e.g., Python 3.8+, TypeScript, Rust]
- **Framework(s)**: [e.g., FastAPI, React, Vue]
- **Package Manager**: [e.g., pip, npm, cargo]
- **Testing**: [e.g., pytest, jest, cargo-test]

### Development Tools
- **Linter**: [ruff for Python, eslint for JS, clippy for Rust]
- **Formatter**: [ruff format, prettier, cargo fmt]
- **Type Checker**: [mypy, TypeScript, Rust built-in]
- **CI/CD**: GitHub Actions
- **Version Management**: release-please

### Platform & Services
- **Hosting**: GitHub
- **Package Registry**: [PyPI, npm, crates.io]
- **Documentation**: [GitHub Pages, VitePress, MkDocs]
- **Code Coverage**: Codecov
- **Dependency Updates**: Dependabot

---

## 🎨 Code Style & Standards

### General Principles

1. **AI-Friendly Code**
   - Clear naming conventions
   - Type annotations/hints
   - Modular design (easy for AI to understand local logic)
   - Comprehensive comments for complex logic

2. **Code Quality**
   - All code must pass linter checks
   - All code must be formatted consistently
   - Type checking enforced where applicable
   - Test coverage minimum: [specify percentage]

3. **Documentation**
   - Public APIs must have docstrings/TSDoc
   - Complex algorithms require explanation
   - Examples for non-obvious usage patterns

### Language-Specific Standards

#### Python
- Follow PEP 8 style guide
- Use type hints for all public functions
- Docstrings in Google style or NumPy style
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting
- Use `mypy` for type checking

#### TypeScript/JavaScript
- Use TypeScript for new code
- Follow ESLint configuration
- Use Prettier for formatting
- Prefer async/await over promises
- Document complex types with TSDoc

#### Rust
- Follow Rust style guide (`cargo fmt`)
- Run `cargo clippy` before committing
- Document public APIs with `///` comments
- Use meaningful error types

---

## 🔄 Workflow & Automation

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

**Examples:**
```
feat(api): add user authentication endpoint
fix(parser): handle edge case in CSV parsing
docs(readme): update installation instructions
```

### Pre-commit Hooks

Automatically run before each commit:
- Code formatting (ruff/prettier/cargo fmt)
- Linting (ruff/clippy/eslint)
- Type checking (mypy/tsc)
- Basic tests (smoke tests)

### CI/CD Pipeline

**On Pull Request:**
1. Lint and format check
2. Type checking
3. Unit tests
4. Integration tests (if applicable)
5. Code coverage report

**On Main Branch Push:**
1. All PR checks
2. Release-please check for version bump
3. Build artifacts

**On Release Tag:**
1. Build and publish to package registry
2. Create GitHub Release
3. Update CHANGELOG

### Version Management

- **Automated via release-please**
- Format: `MAJOR.MINOR.PATCH` (SemVer)
- CHANGELOG automatically generated from commit messages
- Version numbers updated in all relevant files automatically

---

## 🧪 Testing Strategy

### Test Levels

1. **Unit Tests**: Test individual functions/modules
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user workflows (if applicable)

### Test Coverage Goals

- Minimum coverage: [specify percentage]
- Critical paths: 100% coverage
- New code: Must maintain or improve coverage

### Running Tests

```bash
# Run all tests
make test  # or: pytest, npm test, cargo test

# Run with coverage
make test-coverage

# Run specific test suite
pytest tests/unit/
```

---

## 📚 Documentation Standards

### Code Documentation

- **Public APIs**: Must have comprehensive docstrings/TSDoc
- **Complex Logic**: Inline comments explaining "why", not "what"
- **Examples**: Include usage examples in docstrings

### Project Documentation

- **README.md**: Project overview, quick start, installation
- **docs/guide/**: User guides and tutorials
- **docs/api/**: API reference documentation
- **CONTRIBUTING.md**: How to contribute
- **CHANGELOG.md**: Version history (auto-generated)

### Documentation Generation

- API docs: Auto-generated from code comments
- CHANGELOG: Auto-generated from commit messages
- User guides: Manually maintained in `docs/guide/`

---

## 🤖 AI Assistant Guidelines

### When AI Should Be Used

1. **Code Review**
   - Explain complex logic
   - Suggest improvements
   - Identify potential bugs

2. **Refactoring**
   - Suggest optimizations
   - Improve code structure
   - Enhance readability

3. **Documentation Generation**
   - Generate API docs from code
   - Create examples from usage patterns
   - Update CHANGELOG descriptions

4. **Bug Analysis**
   - Analyze error logs
   - Suggest debugging strategies
   - Propose fixes

5. **Feature Planning**
   - Review requirements
   - Suggest architecture
   - Identify edge cases

### When Human Judgment Is Required

1. **Architecture Decisions**: Design patterns, system structure
2. **Business Logic**: Domain-specific requirements
3. **User Experience**: UI/UX decisions
4. **Security**: Security-critical code review
5. **Performance**: Performance-critical optimizations

### AI Code Quality Checklist

Before accepting AI-generated code:
- [ ] Code passes all linter checks
- [ ] Code follows project style guide
- [ ] All tests pass
- [ ] Code is properly typed
- [ ] Documentation is updated
- [ ] Edge cases are handled
- [ ] Security considerations addressed

---

## 🌐 Community Standards

### Communication

- **Issues**: Use issue templates for bugs and features
- **Pull Requests**: Provide clear description and context
- **Discussions**: Encourage open dialogue
- **Response Time**: Aim to respond within 48 hours

### Contribution Process

1. Fork repository
2. Create feature branch (`git checkout -b feat/my-feature`)
3. Make changes following code standards
4. Write/update tests
5. Update documentation
6. Commit using conventional commits
7. Push and create Pull Request
8. Respond to review feedback

### Code Review Standards

- Be respectful and constructive
- Focus on code quality, not personal preferences
- Explain reasoning for suggestions
- Approve when standards are met

---

## 🔒 Security Practices

### Security Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Dependencies regularly updated (Dependabot)
- [ ] Security vulnerabilities scanned (CodeQL)
- [ ] Input validation for all user inputs
- [ ] Secure defaults in configuration
- [ ] Security policy documented (SECURITY.md)

### Vulnerability Reporting

Report security issues privately:
- Email: [security contact]
- GitHub Security Advisory: https://github.com/[org]/[repo]/security/advisories/new

---

## 📊 Metrics & Monitoring

### Code Quality Metrics

- **Coverage**: Tracked via Codecov
- **Code Complexity**: Monitored via linters
- **Dependency Health**: Dependabot alerts

### Project Health Metrics

- **Issue Response Time**: Track via GitHub Insights
- **PR Merge Time**: Track via GitHub Insights
- **Release Frequency**: Track via GitHub Releases
- **Community Growth**: Stars, contributors, forks

---

## 🚀 Release Process

### Automated Release Flow

1. **Developers** commit changes with conventional commits
2. **release-please** creates/updates Release PR
3. **Maintainers** review and merge Release PR
4. **GitHub Actions** automatically:
   - Creates Git tag
   - Builds and publishes packages
   - Creates GitHub Release
   - Updates CHANGELOG

### Manual Release (if needed)

```bash
# 1. Update version in relevant files
# 2. Update CHANGELOG.md
# 3. Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 🛠️ Development Setup

### Prerequisites

- [List required tools and versions]
- Python 3.8+
- Node.js 18+
- Rust 1.75+ (if applicable)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/[org]/[repo].git
cd [repo]

# Install dependencies
pip install -e ".[dev]"
npm install  # if applicable
cargo build  # if applicable

# Install pre-commit hooks
pre-commit install

# Run tests
pytest  # or: npm test, cargo test
```

### Common Commands

```bash
# Format code
make format  # or: ruff format, prettier, cargo fmt

# Lint code
make lint  # or: ruff check, eslint, cargo clippy

# Type check
make type-check  # or: mypy, tsc, cargo check

# Run tests
make test

# Run all checks
make check-all
```

---

## 📖 Key Resources

### Internal Documentation

- [CONTRIBUTING.md](./CONTRIBUTING.md) - How to contribute
- [docs/DEVELOPMENT_PHILOSOPHY.md](./docs/DEVELOPMENT_PHILOSOPHY.md) - Development practices
- [docs/GITHUB_BADGES_GUIDE.md](./docs/GITHUB_BADGES_GUIDE.md) - GitHub badges guide

### External Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [release-please](https://github.com/googleapis/release-please)

---

## 🎯 Project-Specific Guidelines

### [Customize this section based on your project]

**Domain-Specific Rules:**
- [Add any industry or domain-specific coding standards]
- [Add any regulatory or compliance requirements]
- [Add any special testing requirements]

**Architecture Decisions:**
- [Document key architectural decisions]
- [Explain design patterns used]
- [Note any technical debt or future improvements]

---

## 🔄 Update History

- **2024-XX-XX**: Initial AI context guide created
- [Track updates to this guide]

---

## 💡 Quick Reference for AI Assistants

### 🎯 Project Kickoff Workflow

**For NEW Projects:**
1. **PROJECT_IDEA.md** ⭐ - Read FIRST to understand project vision and requirements
2. **AI_CONTEXT.md** (this file) - Technical context and standards
3. **QUICK_START.md** - Project setup instructions
4. Generate initial code structure based on PROJECT_IDEA.md

**For EXISTING Projects:**
1. **PROJECT_IDEA.md** - Current status and plans
2. **AI_CONTEXT.md** (this file) - Development standards
3. **README.md** - Current project state
4. **CONTRIBUTING.md** - Contribution guidelines

### Key Files to Read First

1. **PROJECT_IDEA.md** ⭐ - **START HERE** - Project vision, requirements, and status
2. **AI_CONTEXT.md** (this file) - Development context and technical standards
3. **README.md** - Project overview and current state
4. **CONTRIBUTING.md** - How to contribute
5. **docs/DEVELOPMENT_PHILOSOPHY.md** - Development practices (if exists)

### When Generating Code

**Before Starting:**
- ✅ Read PROJECT_IDEA.md to understand requirements
- ✅ Check existing code structure
- ✅ Understand the architecture outlined in PROJECT_IDEA.md

**When Coding:**
- ✅ Follow code style guidelines
- ✅ Include type hints/annotations
- ✅ Add docstrings/comments for complex logic
- ✅ Write tests for new features
- ✅ Update documentation
- ✅ Align with architecture in PROJECT_IDEA.md

### When Reviewing Code

- ✅ Check for security issues
- ✅ Verify test coverage
- ✅ Ensure code follows style guide
- ✅ Suggest improvements constructively

### When Responding to Issues

- ✅ Be helpful and clear
- ✅ Provide code examples when relevant
- ✅ Link to relevant documentation
- ✅ Follow project communication standards

---

**Last Updated**: [Date]
**Maintained By**: [Team/Individual]
**Questions?**: Open an issue or contact [contact info]

