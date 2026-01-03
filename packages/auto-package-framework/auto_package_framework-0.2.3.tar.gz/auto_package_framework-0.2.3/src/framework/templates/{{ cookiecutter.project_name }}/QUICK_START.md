# Quick Start Guide

This guide will help you set up a new project using this template.

> **👋 New here?** Read **[START_HERE.md](./START_HERE.md)** first for navigation!

## Step 1: Copy Template

```bash
# Copy the PROJECT_TEMPLATE directory
cp -r PROJECT_TEMPLATE your-project-name
cd your-project-name
```

## Step 2: Write Your Project Idea

**🎯 IMPORTANT: Start here before customizing other files!**

1. **Open PROJECT_IDEA.md**
   - Fill in your project concept and problem statement
   - List core features and requirements
   - Sketch out architecture ideas
   - Define success criteria

2. **This is your AI entry point!**
   - AI assistants will read this file first
   - Keep it updated as your project evolves
   - Use it to guide development decisions

## Step 3: Customize Project Files

1. **README.md**
   - Replace `[Project Name]` with your project name
   - Update description, features, installation instructions
   - Update badge URLs with your GitHub username/repo

2. **pyproject.toml** (or equivalent)
   - Update `name = "your-package-name"`
   - Update author information
   - Update dependencies
   - Update project URLs

3. **release-please-config.json**
   - Update `package-name` and `component` fields

4. **AI_CONTEXT.md**
   - Customize project overview (reference PROJECT_IDEA.md)
   - Update technology stack
   - Add project-specific guidelines
   - Ensure it aligns with PROJECT_IDEA.md

5. **.github/workflows/*.yml**
   - Update repository references
   - Configure for your specific needs

### Replace Placeholders

Run a find-and-replace for:
- `[Project Name]` → Your actual project name
- `USERNAME` → Your GitHub username
- `PROJECT_NAME` → Your repository name
- `your-package-name` → Your package name
- `your.email@example.com` → Your email

**After replacing, ensure PROJECT_IDEA.md and AI_CONTEXT.md are consistent!**

## Step 3: Initialize Git

```bash
git init
git add .
git commit -m "chore: initial project setup from template"
```

## Step 4: Set Up GitHub

1. Create a new repository on GitHub
2. Add remote:
   ```bash
   git remote add origin https://github.com/USERNAME/PROJECT_NAME.git
   git push -u origin main
   ```

## Step 5: Configure Secrets

In GitHub repository settings → Secrets and variables → Actions:

1. **PYPI_API_TOKEN**: For publishing to PyPI (if applicable)
   - Create token at https://pypi.org/manage/account/token/
   - Add as repository secret

2. **CODECOV_TOKEN**: For code coverage (optional)
   - Get from https://codecov.io
   - Add as repository secret

## Step 6: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install project
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Step 7: Verify Setup

```bash
# Run linter
ruff check .

# Run formatter
ruff format .

# Run type checker
mypy .

# Run tests
pytest
```

## Step 8: Create Initial Structure

```bash
# Create source directory
mkdir -p src/your_package_name
touch src/your_package_name/__init__.py

# Create tests directory
mkdir -p tests
touch tests/__init__.py
touch tests/test_example.py

# Create examples directory
mkdir -p examples
```

## Step 9: Write Initial Code

Create your first module:

```python
# src/your_package_name/main.py
def hello_world() -> str:
    """Return a greeting message."""
    return "Hello, World!"
```

Create a test:

```python
# tests/test_main.py
from your_package_name.main import hello_world

def test_hello_world():
    assert hello_world() == "Hello, World!"
```

## Step 10: Make First Commit

```bash
git add .
git commit -m "feat: initial implementation"
```

## Next Steps

1. ✅ **Write PROJECT_IDEA.md** - Document your project vision and requirements
2. ✅ Update `AI_CONTEXT.md` with your specific requirements (reference PROJECT_IDEA.md)
3. ✅ Customize `.pre-commit-config.yaml` for your stack
4. ✅ Use `AI_START_PROMPT.md` when asking AI for help
5. ✅ Set up documentation (if needed)
6. ✅ Configure CI/CD workflows for your needs
7. ✅ Add more examples and documentation

## 🤖 Working with AI Assistants

When you want AI to help with your project:

1. **First time**: Use the prompt from `AI_START_PROMPT.md` - "Project Kickoff Prompt"
2. **Ongoing work**: Reference `AI_START_PROMPT.md` for appropriate prompts
3. **Always**: Make sure PROJECT_IDEA.md is up to date - AI reads it first!

Example:
```
I'm starting a new project. Please read PROJECT_IDEA.md and AI_CONTEXT.md, 
then help me create an implementation plan.
```

## Helpful Commands

```bash
# Development
make format      # Format code
make lint        # Lint code
make type-check  # Type check
make test        # Run tests

# Or directly
ruff format .
ruff check .
mypy .
pytest

# Before committing
pre-commit run --all-files
```

## Troubleshooting

### Pre-commit hooks fail
- Run `pre-commit install` again
- Check if all dependencies are installed

### Tests fail
- Verify virtual environment is activated
- Install all dev dependencies: `pip install -e ".[dev]"`

### CI fails
- Check GitHub Actions logs
- Verify secrets are set correctly
- Ensure workflow files have correct paths

---

**Congratulations!** Your project is ready for development. 🎉

For more details, see:
- **[START_HERE.md](./START_HERE.md)** - Navigation guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [AI_CONTEXT.md](AI_CONTEXT.md) - Technical standards
- [docs/DEVELOPMENT_PHILOSOPHY.md](docs/DEVELOPMENT_PHILOSOPHY.md) - Development practices

