# Python Package Template

> A comprehensive, production-ready template for creating Python packages with modern best practices, AI-assisted development, and automated CI/CD.

<p align="center">
  <a href="https://github.com/flashpoint493/python-package-template"><img src="https://img.shields.io/github/stars/flashpoint493/python-package-template?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/flashpoint493/python-package-template/commits/main"><img src="https://img.shields.io/github/last-commit/flashpoint493/python-package-template" alt="Last Commit"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"></a>
  <a href="https://pre-commit.com/"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg" alt="pre-commit"></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code Style: ruff"></a>
  <a href="http://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checked-mypy-2A6DB0.svg" alt="Type Checked: mypy"></a>
</p>

---

## 🎯 Purpose

This is a **template repository** designed to be used with [`auto-package-framework`](https://github.com/flashpoint493/auto-package-framework) or as a standalone starting point for Python package development.

## ✨ Features

- **Complete Project Structure**: Pre-configured with best practices
- **CI/CD Ready**: GitHub Actions workflows for testing and releasing
- **AI-Assisted Development**: Includes `AI_CONTEXT.md` and `llms.txt.template` for AI assistants
- **Code Quality**: Pre-configured with ruff, mypy, pytest, and pre-commit
- **Documentation**: Comprehensive documentation templates
- **Release Automation**: Release-please for automated versioning and changelog

## Quick Try

Try {{ cookiecutter.project_name }} instantly without installation using `uvx`:

```bash
uvx {{ cookiecutter.package_name }} --help
```

## Overview

[Detailed description of the project, its purpose, and key features. Explain what problem it solves and why it matters.]

### Key Features

- **Feature 1**: [Description]
- **Feature 2**: [Description]
- **Feature 3**: [Description]
- **Feature 4**: [Description]

## Architecture

<p align="center">
  <img src="assets/images/architecture.png" alt="Project Architecture" width="800">
</p>

### Technical Framework

- **Core Stack**: [List main technologies]
- **Key Libraries**: [List important dependencies]
- **Build System**: [Build tool and configuration]
- **Testing**: [Testing framework and approach]

### Technical Details

- **API Design**: [Describe API approach]
- **Performance**: [Performance characteristics]
- **Security**: [Security considerations]
- **Testing**: [Testing strategy]

## Features

### Core Features

- [OK] **Feature Name**: [Description]
- [OK] **Feature Name**: [Description]
- [OK] **Feature Name**: [Description]

### Advanced Features

- [OK] **Feature Name**: [Description]
- [OK] **Feature Name**: [Description]
- [OK] **Feature Name**: [Description]

### Integration Features

- [OK] **Integration Name**: [Description]
- [OK] **Integration Name**: [Description]

## Quick Start

### Installation

#### Basic Installation

```bash
pip install {{ cookiecutter.package_name }}
```

#### With Optional Dependencies

```bash
pip install {{ cookiecutter.package_name }}[extra]
```

#### From Source

```bash
git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.git
cd {{ cookiecutter.project_slug }}
pip install -e ".[dev]"
```

### Basic Usage

**Simple Example:**

```python
from {{ cookiecutter.package_name }} import main_function

result = main_function()
print(result)
```

**Advanced Example:**

```python
from {{ cookiecutter.package_name }} import AdvancedClass

# Create instance
instance = AdvancedClass(config={"key": "value"})

# Use features
result = instance.process_data(data)
```

### Command-Line Interface

```bash
# Basic usage
{{ cookiecutter.package_name }} --help

# With options
[package-name] --input file.txt --output result.json

# Using with uvx (no installation required)
uvx {{ cookiecutter.package_name }} --help
```

## Usage Patterns

{{ cookiecutter.project_name }} supports multiple usage patterns to fit different workflows:

### Pattern 1: Simple Usage (Recommended for Beginners)

Best for: **Quick prototypes, simple tasks**

```python
from {{ cookiecutter.package_name }} import simple_function

result = simple_function(input_data)
```

### Pattern 2: Advanced Usage (Recommended for Production)

Best for: **Production applications, complex workflows**

```python
from {{ cookiecutter.package_name }} import AdvancedClass

class MyApplication(AdvancedClass):
    def __init__(self):
        super().__init__(config={"setting": "value"})
    
    def process(self, data):
        return self.advanced_method(data)
```

### Pattern Comparison

| Aspect | Simple Usage | Advanced Usage |
|--------|--------------|----------------|
| **Complexity** | ⭐ Simple | ⭐⭐ Medium |
| **Best For** | Prototypes | Production |
| **Features** | Basic | Full |
| **Customization** | Limited | Extensive |

## Advanced Usage

### Custom Configuration

```python
from {{ cookiecutter.package_name }} import configure

config = {
    "setting1": "value1",
    "setting2": "value2",
}

configure(config)
```

### Integration Examples

**Integration with [Tool/Service]:**

```python
from {{ cookiecutter.package_name }} import integrate_with_tool

result = integrate_with_tool(tool_config)
```

## Documentation

### llms.txt - LLM 上下文文件

`llms.txt` 是一个专门为 AI 助手（如 Claude、GPT 等）设计的上下文文件，包含项目的完整 API 参考文档。

**用途**:
- 为 AI 助手提供项目 API 的完整上下文
- 帮助 AI 生成符合项目风格的代码和文档
- 确保代码和文档的一致性

**生成方式**:
- 框架会自动从 `llms.txt.template` 生成 `llms.txt`
- 使用 Jinja2 模板引擎替换项目特定变量
- 可以根据项目实际情况自定义内容

**使用建议**:
- 在 Cursor IDE 或其他 AI 助手中，可以引用此文件作为上下文
- 帮助 AI 理解项目的 API 结构和用法
- 生成代码时保持风格一致

## Documentation

- [Full Documentation](https://your-docs-site.com)
- [API Reference](docs/api/)
- [llms.txt](llms.txt) - LLM 上下文文件（AI 助手参考文档）
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Development Philosophy](docs/DEVELOPMENT_PHILOSOPHY.md)
- [Quick Start Guide](./QUICK_START.md)

## Requirements

- Python 3.8+
- [Other requirements]

## Development

### Prerequisites

- Python 3.8+
- [Other development tools]

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.git
cd {{ cookiecutter.project_slug }}

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy .
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Security

Please report security issues privately. See [SECURITY.md](./SECURITY.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

This project template is inspired by and references the structure of the 
[AuroraView](https://github.com/loonghao/auroraview) project by Hal Long (@loonghao).

While this template has been significantly modified and generalized for general 
Python package development, we acknowledge the valuable inspiration from AuroraView's 
project structure, documentation patterns, and development practices.

## Contact

- **Author**: [Your Name]
- **Email**: [your-email@example.com]
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Issues**: [GitHub Issues](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/issues)

---

**Made with ❤️ by [Your Name/Team]**
